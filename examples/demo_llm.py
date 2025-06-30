import sys
import os

# Configuration du path pour exécution depuis examples/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_grok import AgentGrok

def main():
    # Remplacez par votre clé API ou assurez-vous que XAI_API_KEY est dans l'environnement
    api_key = "xai-bR6Kfi62TidkJabSxciAft1vik1vYkAWjxHZmXPjFs7kurA2PCj8LuTt4DHARADaFgFWf2cJEuWPZfRB"
    
    try:
        agent = AgentGrok(api_key=api_key)
    except ValueError as e:
        print(f"Erreur d'initialisation de l'agent: {e}")
        print("Veuillez vous assurer que la clé API est fournie soit directement, soit via la variable d'environnement XAI_API_KEY.")
        return

    questions = [
        "Quelle est la capitale de la France?",
        "Qui a peint la Mona Lisa?",
        "Raconte-moi une blague courte en français.",
        "Testing. Just say hi and hello world and nothing else.",
    ]
    for q in questions:
        print(f">> {q}")
        try:
            answer = agent.query(q)
            print(f"Grok: {answer}")
        except Exception as e:
            print(f"Erreur lors de la requête: {e}")
        print("-" * 20)

if __name__ == "__main__":
    main() 