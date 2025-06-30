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

class TaskType(Enum):
    """Types de tâches que Nina peut traiter."""
    RECHERCHE = "recherche"
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
        # Initialiser l'agent LLM local si configuré
        self.local_llm = None
        if self.user_profile.get('use_local_llm'):
            try:
                model_path = self.user_profile.get('local_llm_model')
                if not isinstance(model_path, str) or not model_path:
                    raise ValueError("Clé 'local_llm_model' invalide ou manquante")
                from agents.agent_llm_local import AgentLLMLocal  # type: ignore
                self.local_llm = AgentLLMLocal(model_path)
                print(f"[AgentNina] LLM local chargé: {model_path}")
            except Exception as e:
                print(f"[AgentNina] Impossible d'initialiser LLM local: {e}")
    
    def analyze_request(self, query: str) -> TaskPlan:
        """🧠 Nina analyse la requête et décide de la stratégie optimale."""
        query_lower = query.lower()
        
        # Mots-clés pour classification (étendus et améliorés)
        news_keywords = [
            "actualité", "news", "dernière", "récent", "nouveau", "neuf", 
            "quoi de neuf", "nouveauté", "tendance", "développement",
            "avancée", "évolution", "mise à jour", "sortie", "lancement"
        ]
        search_keywords = [
            "recherche", "trouve", "cherche", "information", "qu'est-ce que",
            "comment", "pourquoi", "définition", "explication", "détail",
            "ressource", "source", "donnée", "fait", "statistique"
        ]
        analysis_keywords = [
            "analyse", "explique", "compare", "évalue", "décortique",
            "approfondie", "détaillée", "critique", "opinion", "avis",
            "avantages", "inconvénients", "pour/contre", "implications"
        ]
        planning_keywords = [
            "plan", "étape", "projet", "organise", "planification",
            "stratégie", "roadmap", "méthode", "processus", "guide",
            "comment faire", "tutoriel", "marche à suivre"
        ]
        
        # Classification intelligente avec scoring
        scores = {
            TaskType.ACTUALITES: sum(1 for kw in news_keywords if kw in query_lower),
            TaskType.RECHERCHE: sum(1 for kw in search_keywords if kw in query_lower),
            TaskType.ANALYSE: sum(1 for kw in analysis_keywords if kw in query_lower),
            TaskType.PLANIFICATION: sum(1 for kw in planning_keywords if kw in query_lower)
        }
        
        # Bonus de contexte pour certains sujets
        if any(topic in query_lower for topic in ["ia", "intelligence artificielle", "chatgpt", "llm", "ai"]):
            scores[TaskType.RECHERCHE] += 2  # Favorise la recherche pour les sujets IA
        
        if any(pattern in query_lower for pattern in ["quelles sont", "liste", "types de"]):
            scores[TaskType.RECHERCHE] += 1
            
        if "?" in query and len(query.split()) > 3:
            scores[TaskType.RECHERCHE] += 1  # Questions complexes = recherche
        
        # Sélectionner le type avec le meilleur score
        max_score = max(scores.values()) if scores.values() else 0
        best_type = max(scores, key=lambda k: scores[k]) if max_score > 0 else TaskType.CONVERSATION
        
        # Configuration selon le type détecté
        if best_type == TaskType.ACTUALITES:
            task_type = TaskType.ACTUALITES
            agents = ["news", "analyste", "redacteur"]
            complexity = TaskComplexity.MODERATE
            reasoning = f"Actualités détectées (score: {scores[best_type]}) - récupération news + analyse"
            
        elif best_type == TaskType.RECHERCHE:
            task_type = TaskType.RECHERCHE
            agents = ["chercheur", "analyste", "vectordb", "redacteur"]
            complexity = TaskComplexity.MODERATE
            reasoning = f"Recherche détectée (score: {scores[best_type]}) - collecte web + RAG + analyse"
            
        elif best_type == TaskType.ANALYSE:
            task_type = TaskType.ANALYSE
            agents = ["chercheur", "analyste", "apprenant", "redacteur"]
            complexity = TaskComplexity.COMPLEX
            reasoning = f"Analyse détectée (score: {scores[best_type]}) - recherche approfondie + insights"
            
        elif best_type == TaskType.PLANIFICATION:
            task_type = TaskType.PLANIFICATION
            agents = ["planificateur", "objectif", "analyste", "redacteur"]
            complexity = TaskComplexity.COMPLEX
            reasoning = f"Planification détectée (score: {scores[best_type]}) - structuration + étapes"
            
        else:
            task_type = TaskType.CONVERSATION
            agents = ["vectordb", "apprenant", "redacteur"]
            complexity = TaskComplexity.SIMPLE
            reasoning = "Conversation générale - mémoire + réponse contextuelle"
        
        # Estimation du temps basée sur la complexité
        time_estimates = {
            TaskComplexity.SIMPLE: 2.0,
            TaskComplexity.MODERATE: 5.0,
            TaskComplexity.COMPLEX: 8.0
        }
        
        return TaskPlan(
            task_type=task_type,
            complexity=complexity,
            agents_needed=agents,
            estimated_time=time_estimates[complexity],
            priority=1,
            reasoning=reasoning
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
    
    def think_and_respond(self, query: str) -> str:
        """🤖 Méthode principale : Nina réfléchit et répond via Function Calling LLM."""
        import json
        # Stocker la requête dans l'historique
        self.conversation_history.append({'query': query})
        # Vérifier si le module openai est disponible
        try:
            import openai
            from openai.error import APIConnectionError  # type: ignore
        except ImportError:
            print("[Nina FunctionCalling] Module openai manquant, fallback pipeline Nina")
            # Fallback Nina pipeline (sans function calling)
            plan = self.analyze_request(query)
            results = self._execute_search_task(query)
            # Apprentissage continu
            if results.get("web_results"):
                self.apprenant.apprendre(results["web_results"])
            if results.get("memory_results"):
                self.apprenant.apprendre([p["text"] for p in results.get("memory_results", [])])
            # Génération de la réponse : rapport pour recherche, LLM local pour conversation
            if self.local_llm and plan.task_type == TaskType.CONVERSATION:
                # Construire un prompt pour synthèse
                system_msg = {"role": "system", "content": "Vous êtes Nina, une assistante IA. Formulez une réponse claire et synthétique à la requête de l'utilisateur."}
                user_msg = {"role": "user", "content": f"Requête: {query}\nDonnées: {results}"}
                response = self.local_llm.chat([system_msg, user_msg])
            else:
                # Tâches de recherche et autres utilisent le rapport traditionnel
                response = self._generate_data_rich_response(query, results, plan)
            self.conversation_history[-1]['response'] = response
            # Persister l'interaction dans la BDD SQL
            self.sql_db.save_interaction(query, response)
            return response
        # Déterminer le plan de tâche pour choisir la stratégie
        plan = self.analyze_request(query)
        # Construire le prompt initial avec contexte système
        system_msg = {
            "role": "system",
            "content": (
                "Vous êtes Nina, une assistante IA qui orchestre plusieurs agents pour répondre aux requêtes utilisateurs. "
                "Pour chaque requête, fournissez d'abord votre raisonnement détaillé (chain-of-thought), puis la réponse finale. "
                "Utilisez uniquement les fonctions fournies."
            )
        }
        user_msg = {"role": "user", "content": query}
        # Préparer la liste de messages, en injectant la mémoire pour les conversations
        messages = [system_msg]
        if plan.task_type == TaskType.CONVERSATION:
            # Récupérer les passages mémorisés les plus pertinents
            memory_results = self.vectordb.similarity_search(query, top_k=3)
            for mem in memory_results:
                messages.append({
                    "role": "system",
                    "content": f"Contexte mémoire : {mem['text']}"
                })
        messages.append(user_msg)
        # Si un LLM local est configuré, l'utiliser en priorité
        if self.local_llm:
            try:
                response = self.local_llm.chat(messages)
                self.conversation_history[-1]['response'] = response
                # Mise à jour de la mémoire conversationnelle
                from datetime import datetime
                ts = datetime.utcnow().isoformat()
                # Indexer la requête et la réponse pour enrichir la mémoire
                self.vectordb.add_documents(
                    [query, response],
                    [{"timestamp": ts}, {"timestamp": ts}]
                )
                # Persister l'interaction dans la BDD SQL
                self.sql_db.save_interaction(query, response)
                return response
            except Exception as e:
                print(f"[AgentNina] Erreur LLM local: {e}, bascule vers OpenAI(FunctionCalling)")
        # Fonction d'appel LLM via OpenAI (LocalAI ou cloud)
        try:
            # Essayer LLM local
            completion = openai.chat.completions.create(  # type: ignore
                model=self.redacteur.model,
                messages=messages,  # type: ignore
                functions=function_defs,  # type: ignore
                function_call="auto",
                temperature=0
            )
        except APIConnectionError as e:
            print(f"[Nina FunctionCalling] Local LLM inaccessible ({e}), bascule vers OpenAI cloud")
            # Bascule vers OpenAI cloud
            openai.base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")  # type: ignore
            openai.api_key = os.getenv("OPENAI_API_KEY")
            completion = openai.chat.completions.create(  # type: ignore
                model=self.redacteur.model,
                messages=messages,  # type: ignore
                functions=function_defs,  # type: ignore
                function_call="auto",
                temperature=0
            )
        if not completion or not completion.choices:
            raise RuntimeError("Pas de réponse du LLM")
        msg = completion.choices[0].message
        # Si un appel de fonction est demandé par le LLM
        if hasattr(msg, 'function_call') and msg.function_call:
            fname = msg.function_call.name
            args = json.loads(msg.function_call.arguments)
            # Appel de la fonction correspondante
            if fname == "collect_data":
                result = self.chercheur.collect_data(args["source_type"], args["query"])
            elif fname == "analyze_data":
                result = self.analyste.analyze_data(args.get("data", []))
            elif fname == "similarity_search":
                result = self.vectordb.similarity_search(args["query"], top_k=args.get("top_k", 3))
            elif fname == "fetch_ai_news":
                result = self.news_agent.fetch_ai_news()
            else:
                result = {}
            # Ajouter le retour de fonction dans les messages
            messages = [system_msg, user_msg,
                        {"role": "assistant", "content": None, "function_call": msg.function_call},
                        {"role": "function", "name": fname, "content": json.dumps(result)}]
            # 2e appel LLM : synthèse des résultats
            final = openai.chat.completions.create(  # type: ignore
                model=self.redacteur.model,
                messages=messages,  # type: ignore
                temperature=0.2
            )
            response = final.choices[0].message.content or ""
        else:
            # Pas de function_call, retour direct du LLM
            response = msg.content or ""
        # Stocker la réponse
        self.conversation_history[-1]['response'] = response
        # Persister l'interaction dans la BDD SQL
        self.sql_db.save_interaction(query, response)
        return response
    
    def _generate_data_rich_response(self, query: str, results: Dict[str, Any], plan: TaskPlan) -> str:
        """✨ Nina génère un rapport synthétique via AgentRedacteur."""
        # Fusionner les insights au niveau supérieur
        insights = results.get("insights", {})
        merged = {}
        merged.update(insights)

        # RAG : recherche de passages similaires
        passages = self.vectordb.similarity_search(query, top_k=3)
        if passages:
            merged["passages_similaires"] = passages
        else:
            # Fallback actualités si pas de passages récents
            news_items = self.news_agent.fetch_ai_news()
            merged["news"] = news_items

        # Génération du rapport final via AgentRedacteur (en appelant le LLM local si configuré)
        report = self.redacteur.generate_report(merged, history=self.conversation_history, reasoning=plan.reasoning, profile=self.user_profile)
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