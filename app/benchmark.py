import time
import sys
import os

# Ajout du chemin racine pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_nina import AgentNina

def run_benchmark(query: str, agent: AgentNina):
    """Exécute une requête et mesure le temps de réponse."""
    start_time = time.time()
    response = agent.think_and_respond(query)
    end_time = time.time()
    
    duration = end_time - start_time
    num_tokens = len(response.split())
    tokens_per_second = num_tokens / duration if duration > 0 else 0
    
    print("\n--- Résultat du Benchmark ---")
    print(f"Requête: {query}")
    print(f"Réponse: {response}")
    print("-----------------------------")
    print(f"Temps total de réponse: {duration:.2f} secondes")
    print(f"Nombre de tokens générés: {num_tokens}")
    print(f"Vitesse: {tokens_per_second:.2f} tokens/seconde")
    print("-----------------------------")
    
    return {"duration": duration, "tokens": num_tokens, "tps": tokens_per_second}

def main():
    print("🚀 Lancement du benchmark de performance de Nina...")
    
    # Assurez-vous qu'Ollama et Qdrant sont lancés
    os.environ['QDRANT_URL'] = 'http://localhost:6333'
    
    try:
        print("\nInitialisation de l'agent Nina...")
        nina_agent = AgentNina()
        print("Agent initialisé.")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de Nina : {e}")
        return

    queries = [
        "Quelle est la capitale de l'Australie ?",
        "Explique-moi le principe de la photosynthèse en trois phrases.",
        "Si je mélange de la peinture bleue et de la peinture jaune, quelle couleur j'obtiens ?"
    ]
    
    all_results = []
    for query in queries:
        all_results.append(run_benchmark(query, nina_agent))
        
    # Calcul des moyennes
    avg_duration = sum(r['duration'] for r in all_results) / len(all_results)
    avg_tps = sum(r['tps'] for r in all_results) / len(all_results)
    
    print("\n\n--- 🔥 Rapport de Benchmark Final 🔥 ---")
    print(f"Temps de réponse moyen: {avg_duration:.2f} secondes")
    print(f"Vitesse moyenne de génération: {avg_tps:.2f} tokens/seconde")
    print("----------------------------------------")

if __name__ == "__main__":
    main() 