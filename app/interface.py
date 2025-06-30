#!/usr/bin/env python3
"""Interface utilisateur améliorée pour Nina.

Supporte CLI enrichi et interface web basique.
"""

import sys
import os
import time
from typing import Optional

# Configuration du path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from orchestrator import Orchestrator


class NinaInterface:
    """Interface utilisateur moderne pour Nina."""
    
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.session_history = []
        
    def print_banner(self):
        """Affiche le banner Nina."""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🤖 NINA - Assistant IA Intelligent & Autonome v0.2      ║
║                                                              ║
║    🧠 Agents : Chercheur • Analyste • Planificateur         ║
║    🔍 Capacités : Web • RAG • News • Mémoire vectorielle    ║
║    ⚡ Status : Opérationnel                                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
    def print_commands(self):
        """Affiche les commandes disponibles."""
        print("""
💬 Commandes disponibles :
   📝 Tapez votre question naturellement
   📊 /stats  - Statistiques d'usage
   📚 /help   - Aide détaillée  
   🔄 /reset  - Nouvelle session
   🚪 /exit   - Quitter

🎯 Exemples de questions :
   • "Quelles sont les dernières actualités en IA ?"
   • "Analyse-moi les tendances du machine learning"
   • "Peux-tu planifier un projet d'automatisation ?"
        """)
    
    def handle_command(self, user_input: str) -> bool:
        """Gère les commandes spéciales. Retourne True si c'est une commande."""
        cmd = user_input.strip().lower()
        
        if cmd in ['/exit', '/quit', 'exit', 'quit']:
            print("\n👋 Au revoir ! Merci d'avoir utilisé Nina.")
            return True
            
        elif cmd == '/help':
            self.print_commands()
            return False
            
        elif cmd == '/stats':
            self.show_stats()
            return False
            
        elif cmd == '/reset':
            self.session_history.clear()
            print("🔄 Session réinitialisée.")
            return False
            
        return False
    
    def show_stats(self):
        """Affiche les statistiques de la session."""
        print(f"""
📊 Statistiques de la session :
   💬 Questions posées : {len(self.session_history)}
   🧠 Agents actifs : 6 (Chercheur, Analyste, News, Planificateur, Rédacteur, Apprentissage)
   🔍 Recherches web : Activées (DuckDuckGo)
   📰 Actualités : Activées (DuckDuckGo fallback)
   🗄️ Mémoire vectorielle : Activée (Qdrant in-memory)
        """)
    
    def format_response(self, response: str) -> str:
        """Formate la réponse de Nina."""
        return f"""
🤖 Nina répond :
{'='*60}
{response}
{'='*60}
        """
    
    def start_cli(self):
        """Lance l'interface CLI interactive."""
        self.print_banner()
        self.print_commands()
        
        print("\n🚀 Nina est prête ! Posez votre première question :")
        
        while True:
            try:
                # Prompt coloré
                user_input = input("\n💬 Vous : ").strip()
                
                if not user_input:
                    continue
                    
                # Gestion des commandes
                if self.handle_command(user_input):
                    break
                    
                # Traitement de la requête
                print("\n🔄 Nina réfléchit...")
                start_time = time.time()
                
                try:
                    response = self.orchestrator.orchestrate(user_input)
                    duration = time.time() - start_time
                    
                    # Sauvegarde dans l'historique
                    self.session_history.append({
                        'question': user_input,
                        'response': response,
                        'duration': duration
                    })
                    
                    # Affichage de la réponse
                    print(self.format_response(response))
                    print(f"⏱️ Temps de traitement : {duration:.2f}s")
                    
                except Exception as e:
                    print(f"❌ Erreur lors du traitement : {e}")
                    print("🔧 Vérifiez la configuration et réessayez.")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 Interruption détectée. Au revoir !")
                break
    
    def start_web(self, port: int = 8501):
        """Lance l'interface web avec Streamlit."""
        try:
            import streamlit as st
            print(f"🌐 Lancement de l'interface web sur le port {port}...")
            # TODO: Implémenter l'interface Streamlit
            print("⚠️ Interface web en cours de développement.")
        except ImportError:
            print("❌ Streamlit non installé. Utilisez : pip install streamlit")


def main():
    """Point d'entrée principal."""
    interface = NinaInterface()
    
    # Choix de l'interface
    if len(sys.argv) > 1 and sys.argv[1] == '--web':
        interface.start_web()
    else:
        interface.start_cli()


if __name__ == "__main__":
    main() 