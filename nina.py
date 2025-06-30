#!/usr/bin/env python3
"""
🤖 Nina - Assistant IA Intelligent & Autonome

Point d'entrée principal pour lancer Nina en différents modes.
"""

import sys
import os
import argparse

# Configuration du path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Point d'entrée principal avec gestion des arguments."""
    parser = argparse.ArgumentParser(
        description="🤖 Nina - Assistant IA Intelligent & Autonome",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python nina.py                 # Interface CLI interactive
  python nina.py --test          # Test de fonctionnement
  python nina.py --web           # Interface web (en développement)
  python nina.py --version       # Version et informations
        """
    )
    
    parser.add_argument(
        '--test', 
        action='store_true',
        help='Lance un test de fonctionnement'
    )
    
    parser.add_argument(
        '--web', 
        action='store_true',
        help='Lance l\'interface web (nécessite streamlit)'
    )
    
    parser.add_argument(
        '--version', 
        action='store_true',
        help='Affiche la version et les informations système'
    )
    
    parser.add_argument(
        '--query', 
        type=str,
        help='Pose une question directement en ligne de commande'
    )
    
    args = parser.parse_args()
    
    # Mode test
    if args.test:
        print("🧪 Lancement du test de Nina...")
        try:
            from app.orchestrator import Orchestrator
            print("✅ Import de l'Orchestrator réussi")
            
            orch = Orchestrator()
            print("✅ Création de l'Orchestrator réussie")
            
            result = orch.orchestrate("Test rapide de fonctionnement")
            print("✅ Test d'orchestration réussi")
            print("✅ Nina fonctionne parfaitement !")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Erreur lors du test : {e}")
            sys.exit(1)
    
    # Mode version
    if args.version:
        print("""
🤖 Nina - Assistant IA v0.2.0
╔════════════════════════════════════════╗
║ 🧠 Agents : 6 actifs                   ║
║ 🔍 Collecte : Web + APIs              ║
║ 📊 Analyse : RAG + Vectoriel          ║
║ 🗄️ Mémoire : Qdrant + Apprentissage   ║
║ 📰 News : DuckDuckGo + NewsAPI        ║
╚════════════════════════════════════════╝

🐍 Python : {}.{}.{}
📂 Répertoire : {}
        """.format(
            sys.version_info.major,
            sys.version_info.minor, 
            sys.version_info.micro,
            os.getcwd()
        ))
        return
    
    # Mode requête directe
    if args.query:
        print(f"🤖 Nina traite votre requête : {args.query}")
        try:
            from app.orchestrator import Orchestrator
            orch = Orchestrator()
            response = orch.orchestrate(args.query)
            print(f"\n📝 Réponse :\n{response}")
        except Exception as e:
            print(f"❌ Erreur : {e}")
            sys.exit(1)
        return
    
    # Mode interface
    if args.web:
        from app.interface import NinaInterface
        interface = NinaInterface()
        interface.start_web()
    else:
        # Mode CLI par défaut
        from app.interface import NinaInterface
        interface = NinaInterface()
        interface.start_cli()


if __name__ == "__main__":
    main() 