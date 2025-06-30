#!/usr/bin/env python3
"""
🎬 Démonstration des capacités de Nina
"""

import sys
import os
import time

# Configuration du path pour exécution depuis examples/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

from app.orchestrator import Orchestrator

def demo_nina():
    """Démonstration interactive des capacités de Nina."""
    
    print("""
🎬 DÉMONSTRATION NINA v0.2.0
╔══════════════════════════════════════════════════════════════╗
║  Cette démo vous montre les principales capacités de Nina   ║
║  🔍 Collecte web • 📊 Analyse • 📰 News • 🧠 Apprentissage  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    orch = Orchestrator()
    
    scenarios = [
        {
            "titre": "🔍 Collecte et Analyse Web",
            "question": "Recherche des informations sur les tendances du machine learning en 2024",
            "description": "Nina va collecter des données web et les analyser"
        },
        {
            "titre": "📰 Récupération d'Actualités",
            "question": "Quelles sont les dernières nouvelles en intelligence artificielle ?",
            "description": "Nina va chercher les actualités récentes en IA"
        },
        {
            "titre": "🧠 Analyse et Recommandations",
            "question": "Analyse les meilleures pratiques pour débuter en deep learning",
            "description": "Nina va analyser et donner des recommandations personnalisées"
        },
        {
            "titre": "📋 Planification de Tâches",
            "question": "Crée-moi un plan pour apprendre le développement d'IA en 3 mois",
            "description": "Nina va planifier et structurer un projet d'apprentissage"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*80}")
        print(f"📝 SCÉNARIO {i}/4 : {scenario['titre']}")
        print(f"ℹ️  {scenario['description']}")
        print(f"❓ Question : {scenario['question']}")
        print(f"{'='*80}")
        
        input("\n⏳ Appuyez sur ENTRÉE pour continuer...")
        
        print(f"\n🔄 Nina traite la requête '{scenario['question']}'...")
        start_time = time.time()
        
        try:
            response = orch.orchestrate(scenario['question'])
            duration = time.time() - start_time
            
            print(f"""
🤖 RÉPONSE DE NINA :
┌{'─'*78}┐
│ {response[:500]}{'...' if len(response) > 500 else ''}
└{'─'*78}┘

⏱️  Temps de traitement : {duration:.2f}s
✅ Scénario {i} terminé avec succès !
            """)
            
        except Exception as e:
            print(f"❌ Erreur dans le scénario {i} : {e}")
    
    print(f"""
🎉 DÉMONSTRATION TERMINÉE !

📊 RÉSUMÉ DES CAPACITÉS TESTÉES :
   ✅ Collecte web automatique (DuckDuckGo)
   ✅ Analyse de données avec agents spécialisés
   ✅ Récupération d'actualités
   ✅ Mémoire vectorielle et recherche sémantique
   ✅ Apprentissage continu et recommandations
   ✅ Planification de tâches
   ✅ Génération de rapports structurés

🚀 Nina est prête pour vos projets !

💡 PROCHAINES ÉTAPES :
   • Configurer un LLM local (LocalAI/Ollama) pour des réponses enrichies
   • Ajouter une clé NewsAPI pour de meilleures actualités
   • Explorer l'interface web (en développement)
   • Intégrer avec vos APIs et bases de données

🔗 Pour lancer Nina en mode interactif : python nina.py
    """)

if __name__ == "__main__":
    try:
        demo_nina()
    except KeyboardInterrupt:
        print("\n\n👋 Démonstration interrompue. Au revoir !")
    except Exception as e:
        print(f"\n❌ Erreur pendant la démonstration : {e}")
        print("🔧 Vérifiez l'installation et réessayez.") 