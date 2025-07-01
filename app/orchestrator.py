from typing import Dict, Any, List
import sys
import os
import json
import re # Importer le module pour les expressions régulières

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_openrouter import AgentOpenRouter
from duckduckgo_search import DDGS

# --- Définition des Outils ---

class FileSystemTool:
    """Outil pour lire et écrire dans des fichiers locaux dans un 'workspace' sécurisé."""
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = os.path.abspath(workspace_dir)
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir)

    def _get_safe_path(self, filename: str) -> str:
        """Valide et retourne un chemin de fichier sécurisé à l'intérieur du workspace."""
        # Empêche le path traversal (ex: ../../.../fichier_sensible)
        if ".." in filename or filename.startswith("/"):
            raise ValueError("Accès non autorisé au fichier.")
        
        return os.path.join(self.workspace_dir, filename)

    def read_file(self, filename: str) -> str:
        """Lit le contenu d'un fichier dans le workspace."""
        try:
            safe_path = self._get_safe_path(filename)
            with open(safe_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Erreur: Le fichier '{filename}' n'a pas été trouvé."
        except Exception as e:
            return f"Erreur lors de la lecture du fichier: {e}"

    def write_file(self, filename: str, content: str) -> str:
        """Écrit du contenu dans un fichier du workspace."""
        try:
            safe_path = self._get_safe_path(filename)
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Le fichier '{filename}' a été écrit avec succès."
        except Exception as e:
            return f"Erreur lors de l'écriture du fichier: {e}"

class WebSearchTool:
    """Un outil qui effectue une véritable recherche sur le web avec DuckDuckGo."""
    def run(self, query: str) -> str:
        """Exécute la recherche et retourne les 3 premiers résultats."""
        print(f"--- TOOL: WebSearchTool, QUERY: '{query}' ---")
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=3)]
                if not results:
                    return "Aucun résultat trouvé."
                
                # Formatter les résultats pour le LLM
                formatted_results = "\n".join([
                    f"- Titre: {res.get('title', 'N/A')}\n"
                    f"  Extrait: {res.get('body', 'N/A')}\n"
                    f"  Source: {res.get('href', 'N/A')}"
                    for res in results
                ])
                return formatted_results
        except Exception as e:
            return f"Erreur lors de la recherche web: {e}"

# --- Orchestrateur ReAct ---
class Orchestrator:
    """Orchestre une tâche complexe en utilisant un raisonnement ReAct."""

    MAX_ITERATIONS = 5

    def __init__(self, openrouter_api_key: str):
        """Initialise l'orchestrateur avec le moteur LLM et les outils."""
        self.llm = AgentOpenRouter(api_key=openrouter_api_key)
        self.tools = {
            "web_search": WebSearchTool().run,
            "read_file": FileSystemTool().read_file,
            "write_file": FileSystemTool().write_file,
        }

    def _build_react_prompt(self, task: str, history: List[str]) -> List[Dict[str, str]]:
        """Construit le prompt pour le LLM en incluant l'historique de la boucle ReAct."""
        system_prompt = f"""
        Vous êtes un assistant IA. Votre unique but est de retourner un bloc de code JSON valide sans aucun autre texte, en-tête ou explication.
        Le JSON doit contenir une 'pensée' et soit une 'action' pour utiliser un outil, soit 'finish' avec la réponse finale.

        Exemple de format d'action:
        ```json
        {{"thought": "Je dois chercher des informations.", "action": {{"tool_name": "web_search", "query": "requête"}}}}
        ```
        ou pour écrire un fichier:
        ```json
        {{"thought": "Je vais sauvegarder ce texte.", "action": {{"tool_name": "write_file", "filename": "nom_du_fichier.txt", "content": "contenu du fichier"}}}}
        ```

        Exemple de format de réponse finale:
        ```json
        {{"thought": "J'ai toutes les informations.", "finish": "Ceci est la réponse finale."}}
        ```

        **Outils disponibles**:
        - `web_search`: Utile pour trouver des informations récentes sur un sujet. Prend un `query` en paramètre.
        - `read_file`: Pour lire le contenu d'un fichier. Prend un `filename` en paramètre.
        - `write_file`: Pour écrire dans un fichier. Prend un `filename` et `content` en paramètres.

        Ne répondez RIEN d'autre que le bloc JSON.
        """
        messages = [{"role": "system", "content": system_prompt}]
        history_str = "\n".join(history)
        
        # Le contexte est construit en ajoutant la tâche initiale et l'historique des actions/observations
        user_content = f"Tâche à accomplir: {task}\n\nVoici l'historique des étapes précédentes:\n{history_str}\n\nQuelle est votre prochaine action ou votre réponse finale ? Répondez uniquement avec un bloc JSON."
        
        messages.append({"role": "user", "content": user_content})
        return messages

    def run(self, task: str) -> str:
        """Exécute la boucle ReAct pour accomplir une tâche."""
        history = []
        for i in range(self.MAX_ITERATIONS):
            print(f"\n--- Itération {i+1}/{self.MAX_ITERATIONS} ---")

            # 1. Reason
            messages = self._build_react_prompt(task, history)
            llm_response_str = self.llm.invoke("anthropic/claude-3-haiku", messages, temperature=0.0) # Température à 0 pour moins de créativité
            print(f"DEBUG: Réponse brute du LLM:\n---\n{llm_response_str}\n---")

            # Utiliser une regex pour extraire le bloc JSON de manière plus robuste
            json_match = re.search(r'\{.*\}', llm_response_str, re.DOTALL)
            
            if not json_match:
                print(f"Erreur: Aucun bloc JSON trouvé dans la réponse du LLM.")
                history.append(f"Observation: Erreur de formatage, aucun JSON détecté.")
                continue

            json_str = json_match.group(0)

            try:
                llm_response_json = json.loads(json_str)
                thought = llm_response_json.get("thought", "(Pas de pensée formulée)")
                print(f"Pensée: {thought}")
                history.append(f"Pensée: {thought}")

                # 2. Act
                if "action" in llm_response_json:
                    action = llm_response_json["action"]
                    tool_name = action.get("tool_name")
                    
                    if tool_name in self.tools:
                        # Préparer les arguments pour l'outil
                        tool_args = action.copy()
                        del tool_args["tool_name"]
                        
                        observation = self.tools[tool_name](**tool_args)
                        history.append(f"Observation: {observation}")
                        print(f"Observation: {observation}")
                    else:
                        observation = f"Outil '{tool_name}' non trouvé."
                        history.append(f"Observation: {observation}")
                
                elif "finish" in llm_response_json:
                    final_answer = llm_response_json.get("finish")
                    print(f"--- Tâche terminée ---")
                    return final_answer
                
                else:
                    history.append("Observation: Le JSON ne contenait ni 'action' ni 'finish'.")

            except json.JSONDecodeError:
                print(f"Erreur: La sortie du LLM n'est pas un JSON valide. Sortie: {llm_response_str}")
                history.append(f"Observation: Erreur de formatage, le LLM n'a pas retourné un JSON valide.")
            except Exception as e:
                print(f"Une erreur inattendue est survenue: {e}")
                history.append(f"Observation: Erreur système inattendue.")


        return "La tâche n'a pas pu être terminée dans le nombre d'itérations imparti." 