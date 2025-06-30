import sys
import os

# Configuration du path pour exécution depuis examples/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_llm_local import AgentLLMLocal

def main():
    agent = AgentLLMLocal()
    questions = [
        "Quelle est la capitale de la France?",
        "Qui a peint la Mona Lisa?",
        "Raconte-moi une blague courte en français.",
    ]
    for q in questions:
        print(f">> {q}")
        try:
            answer = agent.generate(q)
            print(answer)
        except Exception as e:
            print(f"Erreur: {e}")
        print()

if __name__ == "__main__":
    main() 