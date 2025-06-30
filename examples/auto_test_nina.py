#!/usr/bin/env python3
import sys, os
# Configuration du path pour exécution depuis examples/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))
import time
from orchestrator import Orchestrator  # type: ignore

def main():
    orch = Orchestrator()
    queries = [
        "ChatGPT",
        "ChatGPT"
    ]
    results = []
    for i, q in enumerate(queries, 1):
        print(f"\n=== Requête {i}: '{q}' ===")
        start = time.time()
        resp = orch.orchestrate(q)
        duration = time.time() - start
        print(f"Réponse de Nina:\n{resp}\n")
        print(f"Durée: {duration:.2f}s")
        results.append({'query': q, 'response': resp, 'duration': duration})

    # Rapport synthétique
    print("\n===== Rapport d'exécution de Nina =====")
    for i, r in enumerate(results, 1):
        print(f"\nScénario {i}")
        print(f"- Question             : {r['query']}")
        print(f"- Nombre de caractères : {len(r['response'])}")
        print(f"- Durée                : {r['duration']:.2f}s")
        # Détection d'items clés
        has_passages = 'passages_similaires' in r['response']
        has_news = 'news' in r['response']
        print(f"- Contenu mémoire      : {has_passages}")
        print(f"- Contenu actualités   : {has_news}")

if __name__ == '__main__':
    main() 