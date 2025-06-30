import sys
import os

# Configuration du path pour exécution depuis examples/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.orchestrator import Orchestrator

def main():
    """
    Script de démonstration pour le nouvel Orchestrateur ReAct.
    """
    # --- Configuration ---
    # IMPORTANT: Remplacez par votre clé API OpenRouter.
    # Vous pouvez aussi la définir dans vos variables d'environnement comme OPENROUTER_API_KEY
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "sk-or-v1-...") 
    
    if not openrouter_api_key or "sk-or-v1-..." in openrouter_api_key:
        print("Erreur: Clé API OpenRouter non configurée.")
        print("Veuillez la définir dans le script ou via la variable d'environnement OPENROUTER_API_KEY.")
        return

    # --- Initialisation ---
    try:
        orchestrator = Orchestrator(openrouter_api_key=openrouter_api_key)
    except Exception as e:
        print(f"Erreur lors de l'initialisation de l'orchestrateur: {e}")
        return

    # --- Tâche à accomplir ---
    task = "Fais une recherche sur les dernières nouvelles concernant le modèle AI 'Claude 3.5 Sonnet' et résume les points clés."

    print("="*50)
    print(f"Tâche à accomplir: {task}")
    print("="*50)

    # --- Exécution ---
    try:
        final_response = orchestrator.run(task)
        print("\n" + "="*50)
        print("Réponse Finale de l'Orchestrateur:")
        print(final_response)
        print("="*50)
    except Exception as e:
        print(f"\nUne erreur est survenue pendant l'exécution de l'orchestrateur: {e}")

if __name__ == "__main__":
    main() 