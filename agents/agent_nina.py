#!/usr/bin/env python3
"""
🤖 Agent Nina - Version corrigée

L'agent principal qui orchestre tous les autres agents de manière intelligente.
"""

import sys
import os
import time
import json
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Ajout du chemin racine pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_chercheur_v3 import AgentChercheurV3
from agents.agent_analyste import AgentAnalyste, AgentApprentissage
from agents.agent_redacteur import AgentRedacteur
from agents.agent_planificateur import AgentPlanificateur
from agents.agent_news import AgentNews
from tools.vector_db import VectorDB
from tools.sql_db import SQLDatabase
from agents.agent_llm_local import AgentLLMLocal  # Assurer que l'import est présent

class TaskType(Enum):
    """Types de tâches que Nina peut traiter."""
    RECHERCHE_INFORMATION = "recherche_information"
    RAISONNEMENT_PUR = "raisonnement_pur"
    CONVERSATION_SIMPLE = "conversation_simple"
    ACTUALITES = "actualites"
    ANALYSE = "analyse"
    PLANIFICATION = "planification"
    CONVERSATION = "conversation"
    APPRENTISSAGE = "apprentissage"

class TaskComplexity(Enum):
    """Complexité des tâches."""
    SIMPLE = "simple"      # 1-2 agents
    MODERATE = "moderate"  # 2-4 agents
    COMPLEX = "complex"    # 4+ agents

@dataclass
class TaskPlan:
    """Plan d'exécution d'une tâche."""
    task_type: TaskType
    complexity: TaskComplexity
    agents_needed: List[str]
    estimated_time: float
    priority: int
    reasoning: str

class AgentNina:
    """
    🤖 Agent Nina - Le cerveau de l'orchestrateur
    
    Nina analyse les requêtes, planifie l'exécution et coordonne
    tous les agents spécialisés pour fournir des réponses intelligentes.
    """
    
    def __init__(self):
        # Agents spécialisés
        self.chercheur = AgentChercheurV3()
        self.analyste = AgentAnalyste()
        self.apprenant = AgentApprentissage()
        self.redacteur = AgentRedacteur()
        self.planificateur = AgentPlanificateur()
        self.news_agent = AgentNews()
        
        # Classe ObjectifAgent simulée
        class ObjectifAgent:
            def planifier(self): pass
        self.objectif = ObjectifAgent()
        
        # Base de données vectorielle
        self.vectordb = VectorDB()
        
        # Historique et statistiques
        self.conversation_history = []
        self.task_stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "avg_response_time": 0.0,
            "agent_usage": {},
            "user_satisfaction": []
        }
        # Charger le profil utilisateur depuis crew_config.yaml
        try:
            import yaml  # type: ignore
            cfg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'configs', 'crew_config.yaml')
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
            self.user_profile = cfg.get('parameters', {})
        except Exception:
            self.user_profile = {}
        # Intégration SQL pour la mémoire relationnelle
        db_url = os.getenv('DATABASE_URL', 'sqlite:///data/nina_memory.db')
        self.sql_db = SQLDatabase(db_url)
        # Charger historique de conversation et profil utilisateur depuis la BDD SQL
        self.conversation_history = self.sql_db.load_conversations()
        db_profile = self.sql_db.load_user_profile()
        self.user_profile = {**self.user_profile, **db_profile}
        # Initialiser l'agent LLM local avec Mixtral, tag 'instruct'
        try:
            self.local_llm = AgentLLMLocal(model="mixtral:instruct")
            print("[AgentNina] LLM local (AgentLLMLocal) initialisé avec le modèle 'mixtral:instruct'.")
        except Exception as e:
            print(f"[AgentNina] ⚠️ Impossible d'initialiser le LLM local : {e}")
            self.local_llm = None
    
    def analyze_request(self, query: str) -> TaskPlan:
        """🧠 Nina utilise le LLM pour classifier la requête et choisir la stratégie."""
        
        if not self.local_llm:
            print("[AgentNina] LLM local non disponible, fallback sur une recherche par défaut.")
            return TaskPlan(TaskType.RECHERCHE_INFORMATION, TaskComplexity.MODERATE, ["chercheur", "analyste"], 5.0, 1, "Fallback: LLM local indisponible.")

        # Prompt pour le LLM routeur avec des exemples encore plus variés
        routing_prompt = f"""Tu es un routeur intelligent. Classifie la requête de l'utilisateur en UNE des catégories suivantes : 'raisonnement_pur', 'recherche_information', ou 'conversation_simple'.

### EXEMPLES ###
Requête : "Quelle est la capitale de la France ?"
Catégorie : recherche_information

Requête : "Si un train part à 8h et roule à 100km/h, où sera-t-il à 10h ?"
Catégorie : raisonnement_pur

Requête : "Bonjour, comment vas-tu ?"
Catégorie : conversation_simple

Requête : "Quelle est la suite logique : 2, 4, 6, 8, ?"
Catégorie : raisonnement_pur

Requête : "Peux-tu me parler de la théorie de la relativité ?"
Catégorie : recherche_information

Requête : "Merci beaucoup !"
Catégorie : conversation_simple
### FIN DES EXEMPLES ###

Maintenant, classifie la requête suivante. Ne réponds PAS à la question. Retourne UNIQUEMENT la catégorie choisie.

Requête de l'utilisateur : "{query}"

Catégorie:"""

        try:
            response_text = self.local_llm.generate(routing_prompt).strip().lower()
            
            if 'raisonnement_pur' in response_text:
                best_type = TaskType.RAISONNEMENT_PUR
            elif 'conversation_simple' in response_text:
                best_type = TaskType.CONVERSATION_SIMPLE
            else:
                best_type = TaskType.RECHERCHE_INFORMATION

        except Exception as e:
            print(f"[AgentNina] Erreur du LLM routeur: {e}. Fallback sur recherche.")
            best_type = TaskType.RECHERCHE_INFORMATION

        # Configuration du plan de tâche en fonction de la classification
        if best_type == TaskType.RAISONNEMENT_PUR:
            return TaskPlan(
                task_type=TaskType.RAISONNEMENT_PUR,
                complexity=TaskComplexity.SIMPLE,
                agents_needed=["local_llm"],
                estimated_time=3.0,
                priority=1,
                reasoning="La requête est un problème de raisonnement pur, appel direct au LLM."
            )
        elif best_type == TaskType.CONVERSATION_SIMPLE:
            return TaskPlan(
                task_type=TaskType.CONVERSATION_SIMPLE,
                complexity=TaskComplexity.SIMPLE,
                agents_needed=["local_llm"],
                estimated_time=1.0,
                priority=1,
                reasoning="La requête est une conversation simple, réponse directe."
            )
        else: # RECHERCHE_INFORMATION
            return TaskPlan(
                task_type=TaskType.RECHERCHE_INFORMATION,
                complexity=TaskComplexity.MODERATE,
                agents_needed=["chercheur", "analyste", "vectordb", "redacteur"],
                estimated_time=7.0,
                priority=1,
                reasoning="La requête nécessite une recherche d'information, activation du pipeline RAG."
            )
    
    def _execute_search_task(self, query: str) -> Dict[str, Any]:
        """Exécution optimisée pour la recherche."""
        # 1. Recherche dans la mémoire d'abord
        memory_results = self.vectordb.similarity_search(query, top_k=3)
        
        # 2. Recherche web
        web_results = self.chercheur.collect_data("web", query)
        
        # 3. Combinaison et analyse
        all_data = web_results + [r["text"] for r in memory_results]
        insights = self.analyste.analyze_data(all_data) if all_data else {}
        
        # 4. Mise à jour de la mémoire
        if web_results:
            self.vectordb.add_documents(web_results)
        
        return {
            "web_results": web_results,
            "memory_results": memory_results,
            "insights": insights,
            "total_sources": len(all_data)
        }
    
    def _summarize_history(self) -> str:
        """Crée un résumé de l'historique de conversation."""
        if not self.local_llm or not self.conversation_history:
            return "Aucun historique de conversation."

        # Concaténer les échanges pour le prompt de résumé
        full_history = "\n".join([f"Utilisateur: {e.get('query', '')}\nNina: {e.get('response', '')}" for e in self.conversation_history])

        summary_prompt = f"""Tu es un expert en synthèse. Résume la conversation suivante en quelques points clés pour donner un contexte à un autre agent IA. Ne dépasse pas 100 mots.

Conversation :
{full_history}

Résumé contextuel :"""

        try:
            summary = self.local_llm.generate(summary_prompt)
            return summary
        except Exception as e:
            print(f"[AgentNina] Erreur lors du résumé de l'historique : {e}")
            return "Le résumé de l'historique n'a pas pu être généré."

    def think_and_respond(self, query: str) -> str:
        """🤖 Méthode principale : Nina réfléchit et répond en suivant le plan."""
        start_time = time.time()
        
        plan = self.analyze_request(query)
        print(f"[AgentNina] Plan d'action : {plan.reasoning}")

        if plan.task_type == TaskType.RAISONNEMENT_PUR:
            if not self.local_llm:
                return "Désolé, mon module de raisonnement n'est pas disponible pour le moment."
            
            # Prompt de résolution avec Chaîne de Pensée et Few-Shot
            reasoning_prompt = f"""Tu es une experte en résolution de problèmes. Décompose la question en étapes logiques, explique ton raisonnement, puis donne la réponse finale.

### EXEMPLE ###
Question : "Si 3 chats attrapent 3 souris en 3 minutes, combien de temps faut-il à 100 chats pour attraper 100 souris ?"
Raisonnement étape par étape :
1. Analyser le taux de travail. Si 3 chats attrapent 3 souris en 3 minutes, cela signifie que chaque chat met 3 minutes pour attraper 1 souris.
2. Le nombre de chats n'affecte pas le temps nécessaire pour qu'un chat individuel attrape une souris.
3. Donc, si nous avons 100 chats, chaque chat attrapera sa souris en 3 minutes.
Réponse finale : Il faudra 3 minutes à 100 chats pour attraper 100 souris.
### FIN DE L'EXEMPLE ###

Maintenant, résous la question suivante :

Question : "{query}"

Raisonnement étape par étape :
"""
            
            try:
                response = self.local_llm.generate(reasoning_prompt)
            except Exception as e:
                response = f"J'ai rencontré une erreur en essayant de résoudre le problème : {e}"
        
        elif plan.task_type == TaskType.CONVERSATION_SIMPLE:
            if not self.local_llm:
                return "Bonjour ! Comment puis-je vous aider ?"
            
            conversation_prompt = f"Tu es Nina, une assistante IA amicale et serviable. Réponds de manière naturelle à l'utilisateur.\n\nUtilisateur: {query}\nNina:"
            response = self.local_llm.generate(conversation_prompt)

        else: # RECHERCHE_INFORMATION
            # Créer un résumé de l'historique pour maintenir le contexte
            conversation_summary = self._summarize_history()
            
            # Exécution du pipeline RAG (recherche, analyse, rédaction)
            search_results = self._execute_search_task(query)
            
            # Enrichir les résultats avec le résumé pour le rédacteur
            context_data = {
                "query": query,
                "search_results": search_results,
                "conversation_summary": conversation_summary
            }
            
            response = self._generate_data_rich_response(context_data, plan)

        # Mise à jour de l'historique et des stats
        self.conversation_history.append({'query': query, 'response': response})
        self.sql_db.save_interaction(query, response, summary=conversation_summary if plan.task_type == TaskType.RECHERCHE_INFORMATION else "")
        
        end_time = time.time()
        # ... (logique de stats)

        return response
    
    def _generate_data_rich_response(self, context_data: Dict[str, Any], plan: TaskPlan) -> str:
        """✨ Nina génère un rapport synthétique via AgentRedacteur."""
        # L'historique et la requête sont maintenant dans context_data
        report = self.redacteur.generate_report(
            context_data, 
            reasoning=plan.reasoning, 
            profile=self.user_profile
        )
        return report
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de Nina."""
        return {
            "total_tasks": self.task_stats["total_tasks"],
            "successful_tasks": self.task_stats["successful_tasks"],
            "avg_response_time": self.task_stats["avg_response_time"],
            "agent_usage": self.task_stats["agent_usage"],
            "success_rate": "100.0%",
            "conversation_length": len(self.conversation_history),
            "memory_size": 0
        }
    
    # Anciennes méthodes metadata SQLite supprimées
    
    # Plus de metadata SQLite via tools.db : tout géré par tools/sql_db.py 