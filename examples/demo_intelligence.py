import sys
import os

# Configuration du path pour exécution depuis examples/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_llm_local import AgentLLMLocal

SYSTEM_PREFACE = (
    "Vous êtes Nina, une assistante IA locale. Vous répondez exclusivement en français, de manière concise et précise, "
    "sans mentionner votre statut d'IA ni afficher de logs techniques."
)

def main():
    agent = AgentLLMLocal()
    tests = {
        "Science": "Quel gaz les plantes produisent-elles lors de la photosynthèse ?",
        "Mathématique": "Si x + y = 10 et x - y = 4, quelles sont les valeurs de x et y ?",
        "Commonsense": "Le trophée ne rentre pas dans la boîte car il est trop ____. Complétez le mot manquant.",
        "Explication": "Expliquez brièvement pourquoi le ciel est bleu.",
        "Arithmétique": "Jean a 3 pommes, Marie en a 2 de plus que Jean. Combien en ont-ils au total ?",
        # Benchmarks supplémentaires
        "TruthfulQA": "Quel est le plus grand océan sur Terre ?",
        "Histoire": "Qui a écrit 'La Peste' ?",
        "LAMBADA": "Le chat a sauté sur le ___ pour attraper la souris.",
        "Winogrande": "Le trophée ne rentre pas dans la boîte car il est trop ____. Complétez le mot manquant.",
        "MMLU": "Combien de planètes y a-t-il dans le système solaire ?",
        "Explication Rayleigh": "Expliquez en deux phrases pourquoi le ciel est bleu en vous basant sur l'effet Rayleigh."
    }
    for name, question in tests.items():
        print(f"\n>> Test {name}: {question}")
        messages = [
            {"role": "system", "content": SYSTEM_PREFACE},
            {"role": "user", "content": question}
        ]
        try:
            answer = agent.chat(messages)
        except Exception as e:
            answer = f"Erreur: {e}"
        print(answer)

if __name__ == "__main__":
    main() 