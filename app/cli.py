"""CLI pour interroger Nina en local.

Assume que LocalAI ou Ollama tourne en local et expose une API OpenAI
compatible (par défaut http://localhost:8080/v1).

Variables d'environnement utilisables :
  OPENAI_API_BASE  URL de l'endpoint (défaut : http://localhost:8080/v1)
  OPENAI_API_KEY   Clé fictive (LocalAI n'en vérifie pas la valeur)
  OPENAI_MODEL     Nom du modèle (ex. "mistral-7b")
"""
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Ajouter le répertoire parent au path pour trouver les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.orchestrator import Orchestrator
from agents.agent_openrouter import AgentOpenRouter
from tools.vector_db import VectorDB

def classify_intent(query: str, llm: AgentOpenRouter) -> str:
    """Classifie l'intention de l'utilisateur en 'conversation' ou 'tâche'."""
    prompt = f"""
    Analysez la demande de l'utilisateur suivante.
    Est-ce une simple question, une salutation ou une phrase de conversation courante ? Ou est-ce une tâche complexe qui nécessite de faire une recherche web ou d'interagir avec des fichiers ?
    Répondez uniquement par le mot "conversation" ou "tâche".

    Demande de l'utilisateur: "{query}"
    """
    messages = [{"role": "user", "content": prompt}]
    # On utilise le modèle le plus rapide et le moins cher pour cette classification
    response = llm.invoke("anthropic/claude-3-haiku", messages, temperature=0.0, max_tokens=10)
    
    # Nettoyage de la réponse pour être sûr
    if "tâche" in response.lower():
        return "tâche"
    return "conversation"

def main():
    """
    Lance une conversation interactive avec Nina, propulsée par l'orchestrateur ReAct.
    """
    print("Initialisation de Nina...")
    
    # Récupérer la clé API et initialiser l'orchestrateur
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or "sk-or-v1-..." in api_key:
        print("\nERREUR: Clé API OpenRouter non configurée.")
        print("Veuillez créer un fichier .env à la racine du projet avec la ligne :")
        print('OPENROUTER_API_KEY="votre_cle"')
        return
        
    try:
        orchestrator = Orchestrator(openrouter_api_key=api_key)
        conversational_agent = AgentOpenRouter(api_key)
        vector_db = VectorDB() # Initialisation de la mémoire vectorielle
    except Exception as e:
        print(f"Erreur lors de l'initialisation des composants : {e}")
        return

    print("\n---")
    print("🤖 Nina est prête. Je suis à votre écoute.")
    print("   Tapez 'exit' ou 'quit' pour terminer la conversation.")
    print("---\n")

    while True:
        try:
            user_input = input("Vous > ")
        except (KeyboardInterrupt, EOFError):
            print("\n\nAu revoir !\n")
            break

        if user_input.lower().strip() in {"exit", "quit"}:
            print("\nAu revoir !\n")
            break
        
        if not user_input.strip():
            continue

        # --- ÉTAGE 1: INTERROGATION DE LA MÉMOIRE ---
        print("Nina cherche dans sa mémoire...")
        # On cherche les 2 documents les plus pertinents
        memory_results = vector_db.similarity_search(user_input, top_k=2) 
        
        # On garde seulement les résultats non-vides
        meaningful_results = [res['text'] for res in memory_results if res.get('text')]

        if meaningful_results:
            print("Nina a trouvé des informations pertinentes dans sa mémoire.")
            context = f"Contexte trouvé dans ma mémoire :\n--- {' '.join(meaningful_results)}\n---\n\nEn te basant UNIQUEMENT sur ce contexte, réponds à la question de l'utilisateur : '{user_input}'"
            messages = [{"role": "user", "content": context}]
            response = conversational_agent.invoke("anthropic/claude-3-haiku", messages)
            print("\nNina >", response, "\n")
            continue # On passe à la prochaine itération de la boucle

        # --- ÉTAGE 2: ROUTEUR D'INTENTION (si la mémoire est vide) ---
        print("Rien dans la mémoire, Nina analyse la demande...")
        intent = classify_intent(user_input, conversational_agent)
        print(f"(Intention détectée: {intent})")

        if intent == "tâche":
            print("Nina réfléchit à une tâche complexe...")
            try:
                final_response = orchestrator.run(user_input)
                print("\nNina >", final_response, "\n")
            except Exception as e:
                print(f"\nUne erreur est survenue : {e}\n")
        else: # 'conversation'
            print("Nina prépare une réponse...")
            try:
                # Appel direct pour une réponse conversationnelle
                messages = [{"role": "user", "content": user_input}]
                response = conversational_agent.invoke("anthropic/claude-3-haiku", messages)
                print("\nNina >", response, "\n")
            except Exception as e:
                print(f"\nUne erreur est survenue : {e}\n")

if __name__ == "__main__":
    main() 