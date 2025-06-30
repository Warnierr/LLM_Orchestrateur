"""CLI pour interroger Nina en local.

Assume que LocalAI ou Ollama tourne en local et expose une API OpenAI
compatible (par défaut http://localhost:8080/v1).

Variables d'environnement utilisables :
  OPENAI_API_BASE  URL de l'endpoint (défaut : http://localhost:8080/v1)
  OPENAI_API_KEY   Clé fictive (LocalAI n'en vérifie pas la valeur)
  OPENAI_MODEL     Nom du modèle (ex. "mistral-7b")
"""
import os
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ImportError:
    pass

# Configure rapidement pour l'utilisateur
os.environ.setdefault("OPENAI_API_BASE", "http://localhost:8080/v1")
os.environ.setdefault("OPENAI_API_KEY", "local-ai-key")

from orchestrator import Orchestrator  # noqa: E402


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Nina CLI")
    parser.add_argument(
        '--nina',
        action='store_true',
        help="Mode Nina direct : mémoire + orchestrateur interne"
    )
    parser.add_argument(
        '--direct',
        action='store_true',
        help="Mode direct : parler au LLM local Mistral sans passer par l'orchestrateur"
    )
    args = parser.parse_args()
    if args.nina:
        from agents.agent_nina import AgentNina  # noqa: E402
        nina = AgentNina()
        print("Nina interactive – tapez 'exit' pour quitter.")
        while True:
            try:
                user_input = input("> ")
            except (KeyboardInterrupt, EOFError):
                print("\nFermeture…")
                break
            if user_input.lower().strip() in {"exit", "quit"}:
                break
            response = nina.think_and_respond(user_input)
            print(f"Nina : {response}")
        return
    if args.direct:
        # Mode direct via Orchestrateur (utilise LLM local si configuré)
        orch = Orchestrator()
        print("CLI LLM direct via orchestrateur – tapez 'exit' pour quitter.")
        while True:
            try:
                user_input = input("> ")
            except (KeyboardInterrupt, EOFError):
                print("\nFermeture…")
                break
            if user_input.lower().strip() in {"exit", "quit"}:
                break
            
            # Traiter les salutations simples directement avec Nina
            simple_greetings = ["salut", "bonjour", "hello", "hi", "bonsoir"]
            simple_questions = ["qui es-tu", "ton nom", "tu es qui", "comment tu t'appelles"]
            
            user_lower = user_input.lower().strip()
            is_simple = any(greeting in user_lower for greeting in simple_greetings)
            is_identity = any(question in user_lower for question in simple_questions)
            
            if is_simple or is_identity:
                # Réponse directe de Nina sans orchestrateur
                from agents.agent_llm_local import AgentLLMLocal
                llm_agent = AgentLLMLocal()
                response = llm_agent.generate(user_input)
                print(f"Nina: {response}")
            else:
                # Utiliser l'orchestrateur pour les requêtes complexes
                result = orch.orchestrate(user_input)
                print(result)
    else:
        # Mode orchestrateur
        orch = Orchestrator()
        print("Nina CLI – tapez 'exit' pour quitter.")
        while True:
            try:
                user_input = input("> ")
            except (KeyboardInterrupt, EOFError):
                print("\nFermeture…")
                break
            if user_input.lower().strip() in {"exit", "quit"}:
                break
            response = orch.orchestrate(user_input)
            print("\n" + response + "\n")


if __name__ == "__main__":
    main() 