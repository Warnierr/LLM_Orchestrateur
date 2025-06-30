from typing import Dict, Any, List
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_openrouter import AgentOpenRouter

# --- Définition des Outils ---
class WebSearchTool:
    """Un outil qui simule une recherche sur le web."""
    def run(self, query: str) -> str:
        """Exécute la recherche et retourne un résultat simulé."""
        print(f"--- TOOL: WebSearchTool, QUERY: '{query}' ---")
        return f"Résultats de recherche simulés pour '{query}': [Donnée 1, Donnée 2, Donnée 3]"

# --- Orchestrateur ReAct ---
class Orchestrator:
    """Orchestre une tâche complexe en utilisant un raisonnement ReAct."""

    MAX_ITERATIONS = 5

    def __init__(self, openrouter_api_key: str):
        """Initialise l'orchestrateur avec le moteur LLM et les outils."""
        self.llm = AgentOpenRouter(api_key=openrouter_api_key)
        self.tools = {
            "web_search": WebSearchTool()
        }

    def _build_react_prompt(self, task: str, history: List[str]) -> List[Dict[str, str]]:
        """Construit le prompt pour le LLM en incluant l'historique de la boucle ReAct."""
        system_prompt = f"""
        Vous êtes un assistant capable de décomposer une tâche complexe en utilisant une boucle Pensée-Action-Observation.

        Votre but est d'accomplir la tâche demandée par l'utilisateur en utilisant les outils à votre disposition.

        A chaque étape, vous devez retourner un bloc JSON contenant soit une 'pensée' et une 'action', soit une 'pensée' et une 'réponse finale'.

        1.  **Action**: Pour utiliser un outil. Le format doit être:
            `{{"thought": "votre réflexion sur ce que vous allez faire", "action": {{"tool_name": "nom_de_l_outil", "query": "votre_requête"}}}}`

        2.  **Réponse Finale**: Lorsque vous avez assez d'information pour répondre. Le format doit être:
            `{{"thought": "votre réflexion finale", "finish": "votre_réponse_complète_à_l_utilisateur"}}`

        **Outils disponibles**:
        - `web_search`: Utile pour trouver des informations récentes sur un sujet. Prend un `query` en paramètre.

        Commencez !
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
            llm_response_str = self.llm.invoke("anthropic/claude-3-haiku", messages, temperature=0.1)
            
            try:
                llm_response_json = json.loads(llm_response_str)
                thought = llm_response_json.get("thought", "(Pas de pensée formulée)")
                print(f"Pensée: {thought}")
                history.append(f"Pensée: {thought}")

                # 2. Act
                if "action" in llm_response_json:
                    action = llm_response_json["action"]
                    tool_name = action.get("tool_name")
                    query = action.get("query")
                    
                    if tool_name in self.tools:
                        observation = self.tools[tool_name].run(query)
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