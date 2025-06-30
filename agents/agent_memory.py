"""
Agent de mémoire pour Nina - Gestion de la mémoire conversationnelle et des connaissances
Implémente les meilleures pratiques de 2024-2025 pour les systèmes de mémoire d'agents IA
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from tools.vector_db import VectorDB

class AgentMemory:
    """Agent de mémoire avancé pour Nina avec hiérarchie et compression intelligente."""
    
    def __init__(self, memory_file: str = "data/nina_memory.json"):
        """Initialise l'agent de mémoire avec architecture hiérarchique."""
        self.memory_file = memory_file
        self.vector_db = VectorDB()
        
        # Mémoire hiérarchique à plusieurs niveaux
        self.conversation_history = []  # Mémoire épisodique complète
        self.user_preferences = {}      # Préférences utilisateur
        self.learned_facts = {}         # Faits appris par sujet
        self.memory_graph = {}          # Relations entre entités (inspiré Mem0g)
        self.compressed_memories = []   # Mémoires compressées pour efficacité
        
        # Métadonnées de mémoire avancées
        self.memory_importance_scores = {}  # Scores d'importance par mémoire
        self.access_patterns = {}           # Fréquence d'accès aux mémoires
        self.temporal_decay_factors = {}    # Facteurs de décroissance temporelle
        
        # Configuration du système de scoring
        self.relevance_weight = 0.6
        self.recency_weight = 0.25
        self.importance_weight = 0.15
        self.max_working_memory_size = 5000  # tokens
        
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)
        
        # Charger la mémoire existante
        self.load_memory()
        
        print(f"[AgentMemory] Mémoire hiérarchique initialisée : {len(self.conversation_history)} conversations")

    def add_conversation(self, user_input: str, nina_response: str, context: Optional[Dict[str, Any]] = None):
        """Ajoute une conversation avec scoring et compression intelligente."""
        if context is None:
            context = {}
            
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "nina": nina_response,
            "context": context,
            "importance_score": self._calculate_importance(user_input, nina_response),
            "entities": self._extract_entities(user_input + " " + nina_response),
            "topics": self._extract_topics(user_input + " " + nina_response)
        }
        
        # Générer un ID unique pour cette conversation
        conv_id = self._generate_conversation_id(conversation)
        conversation["id"] = conv_id
        
        self.conversation_history.append(conversation)
        
        # Mettre à jour le graphe de mémoire avec les entités
        self._update_memory_graph(conversation)
        
        # Stocker dans la base vectorielle avec métadonnées enrichies
        self.vector_db.add_documents(
            [f"User: {user_input}\nNina: {nina_response}"],
            [{
                "type": "conversation", 
                "timestamp": conversation["timestamp"],
                "importance": conversation["importance_score"],
                "entities": conversation["entities"],
                "topics": conversation["topics"],
                "conv_id": conv_id
            }]
        )
        
        # Compression intelligente si nécessaire
        self._intelligent_compression()
        
        # Sauvegarder
        self.save_memory()
        
        print(f"[AgentMemory] Conversation ajoutée (importance: {conversation['importance_score']:.2f})")

    def _calculate_importance(self, user_input: str, nina_response: str) -> float:
        """Calcule un score d'importance basé sur plusieurs facteurs."""
        importance = 0.5  # Score de base
        
        # Facteurs d'augmentation d'importance
        high_importance_keywords = [
            "préférence", "n'aime pas", "déteste", "adore", "important", 
            "nom", "âge", "travail", "famille", "objectif", "problème",
            "erreur", "bug", "solution", "urgent", "critique"
        ]
        
        text = (user_input + " " + nina_response).lower()
        
        # Boost pour mots-clés importants
        for keyword in high_importance_keywords:
            if keyword in text:
                importance += 0.1
        
        # Boost pour questions personnelles
        if any(word in user_input.lower() for word in ["je", "mon", "ma", "mes"]):
            importance += 0.2
        
        # Boost pour informations factuelles
        if any(word in nina_response.lower() for word in ["définition", "explication", "signifie"]):
            importance += 0.15
        
        # Longueur de la conversation (plus long = potentiellement plus important)
        if len(text.split()) > 50:
            importance += 0.1
        
        return min(importance, 1.0)  # Cap à 1.0

    def _extract_entities(self, text: str) -> List[str]:
        """Extraction simple d'entités (noms, lieux, concepts)."""
        # Implémentation basique - pourrait être améliorée avec NER
        words = text.split()
        entities = []
        
        # Détecter les mots capitalisés (potentiels noms propres)
        for word in words:
            clean_word = word.strip(".,!?;:")
            if clean_word and clean_word[0].isupper() and len(clean_word) > 2:
                if clean_word not in ["Nina", "User", "Je", "Tu", "Il", "Elle"]:
                    entities.append(clean_word)
        
        return list(set(entities))

    def _extract_topics(self, text: str) -> List[str]:
        """Extraction simple de sujets/thèmes."""
        topic_keywords = {
            "programmation": ["python", "code", "programmation", "développement", "bug", "fonction"],
            "alimentation": ["manger", "nourriture", "cuisine", "restaurant", "recette", "plat"],
            "travail": ["travail", "bureau", "collègue", "projet", "réunion", "entreprise"],
            "personnel": ["famille", "ami", "maison", "vacances", "loisir", "hobby"],
            "technologie": ["ordinateur", "internet", "ia", "intelligence", "artificielle", "tech"],
            "santé": ["santé", "médecin", "maladie", "sport", "exercice", "bien-être"]
        }
        
        text_lower = text.lower()
        detected_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics

    def _update_memory_graph(self, conversation: Dict[str, Any]):
        """Met à jour le graphe de mémoire avec les nouvelles entités et relations."""
        entities = conversation["entities"]
        topics = conversation["topics"]
        
        # Créer des nœuds pour les entités
        for entity in entities:
            if entity not in self.memory_graph:
                self.memory_graph[entity] = {
                    "type": "entity",
                    "connections": [],
                    "conversations": [],
                    "topics": []
                }
            
            # Ajouter la conversation à l'entité
            self.memory_graph[entity]["conversations"].append(conversation["id"])
            
            # Ajouter les sujets associés
            for topic in topics:
                if topic not in self.memory_graph[entity]["topics"]:
                    self.memory_graph[entity]["topics"].append(topic)
        
        # Créer des connexions entre entités qui apparaissent ensemble
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                if entity2 not in self.memory_graph[entity1]["connections"]:
                    self.memory_graph[entity1]["connections"].append(entity2)
                if entity1 not in self.memory_graph[entity2]["connections"]:
                    self.memory_graph[entity2]["connections"].append(entity1)

    def _intelligent_compression(self):
        """Compression intelligente des mémoires anciennes moins importantes."""
        if len(self.conversation_history) < 100:
            return  # Pas besoin de compression pour de petites quantités
        
        # Identifier les conversations à compresser (anciennes et peu importantes)
        cutoff_date = datetime.now() - timedelta(days=30)
        candidates_for_compression = []
        
        for conv in self.conversation_history:
            conv_date = datetime.fromisoformat(conv["timestamp"])
            if conv_date < cutoff_date and conv["importance_score"] < 0.7:
                candidates_for_compression.append(conv)
        
        # Compresser les candidats
        for conv in candidates_for_compression:
            if conv not in self.compressed_memories:
                compressed = {
                    "id": conv["id"],
                    "timestamp": conv["timestamp"],
                    "summary": self._compress_conversation(conv),
                    "entities": conv["entities"],
                    "topics": conv["topics"],
                    "importance": conv["importance_score"]
                }
                self.compressed_memories.append(compressed)
                
                # Retirer de l'historique complet
                if conv in self.conversation_history:
                    self.conversation_history.remove(conv)

    def _compress_conversation(self, conversation: Dict[str, Any]) -> str:
        """Compresse une conversation en un résumé concis."""
        user_msg = conversation["user"]
        nina_msg = conversation["nina"]
        
        # Compression simple - garder l'essentiel
        if len(user_msg) > 50:
            user_summary = user_msg[:47] + "..."
        else:
            user_summary = user_msg
            
        if len(nina_msg) > 50:
            nina_summary = nina_msg[:47] + "..."
        else:
            nina_summary = nina_msg
        
        return f"User: {user_summary} | Nina: {nina_summary}"

    def get_context_for_response(self, user_input: str, max_tokens: Optional[int] = None) -> str:
        """Génère un contexte optimisé pour la réponse basé sur la mémoire hiérarchique."""
        if max_tokens is None:
            max_tokens = self.max_working_memory_size
        
        context_parts = []
        current_tokens = 0
        
        # 1. Recherche sémantique dans les conversations
        similar_conversations = self.search_conversations(user_input, 3)
        if similar_conversations:
            context_parts.append("Conversations similaires:")
            for conv in similar_conversations:
                text = conv['text'][:150] + "..." if len(conv['text']) > 150 else conv['text']
                context_parts.append(f"- {text}")
                current_tokens += len(text.split()) * 1.3  # Estimation tokens
        
        # 2. Entités et relations du graphe de mémoire
        entities_in_query = self._extract_entities(user_input)
        if entities_in_query:
            context_parts.append("Entités connues:")
            for entity in entities_in_query:
                if entity in self.memory_graph:
                    entity_info = self.memory_graph[entity]
                    connections = ", ".join(entity_info["connections"][:3])
                    topics = ", ".join(entity_info["topics"][:3])
                    if connections:
                        context_parts.append(f"- {entity}: lié à {connections}")
                    if topics:
                        context_parts.append(f"- {entity}: sujets {topics}")
                    current_tokens += 20  # Estimation
        
        # 3. Préférences utilisateur pertinentes
        if self.user_preferences and current_tokens < max_tokens * 0.8:
            context_parts.append("Préférences utilisateur:")
            for key, pref in list(self.user_preferences.items())[:3]:
                context_parts.append(f"- {key}: {pref['value']}")
                current_tokens += 10
        
        # 4. Conversations récentes (si espace disponible)
        if current_tokens < max_tokens * 0.6:
            recent = self.get_recent_conversations(2)
            if recent:
                context_parts.append("Contexte récent:")
                for conv in recent:
                    summary = f"User: {conv['user'][:30]}... Nina: {conv['nina'][:30]}..."
                    context_parts.append(f"- {summary}")
                    current_tokens += 15
        
        return "\n".join(context_parts) if context_parts else ""

    def search_conversations(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Recherche améliorée avec scoring multiple."""
        try:
            # Recherche vectorielle de base
            results = self.vector_db.similarity_search(query, top_k=limit * 2)
            conversations = []
            
            for result in results:
                if result.get('meta', {}).get('type') == 'conversation':
                    # Calcul du score composite
                    relevance_score = result.get('score', 0.5)
                    
                    # Score de récence
                    timestamp = result.get('meta', {}).get('timestamp')
                    recency_score = self._calculate_recency_score(timestamp)
                    
                    # Score d'importance
                    importance_score = result.get('meta', {}).get('importance', 0.5)
                    
                    # Score composite
                    composite_score = (
                        self.relevance_weight * relevance_score +
                        self.recency_weight * recency_score +
                        self.importance_weight * importance_score
                    )
                    
                    conversations.append({
                        'text': result['text'],
                        'timestamp': timestamp,
                        'composite_score': composite_score,
                        'entities': result.get('meta', {}).get('entities', []),
                        'topics': result.get('meta', {}).get('topics', [])
                    })
            
            # Trier par score composite et retourner les meilleurs
            conversations.sort(key=lambda x: x['composite_score'], reverse=True)
            return conversations[:limit]
            
        except Exception as e:
            print(f"[AgentMemory] Erreur recherche conversations: {e}")
            return []

    def _calculate_recency_score(self, timestamp: str) -> float:
        """Calcule un score de récence avec décroissance temporelle."""
        if not timestamp:
            return 0.0
        
        try:
            conv_time = datetime.fromisoformat(timestamp)
            time_diff = datetime.now() - conv_time
            
            # Décroissance exponentielle : score élevé pour récent, faible pour ancien
            days_old = time_diff.total_seconds() / (24 * 3600)
            recency_score = 1.0 / (1.0 + 0.1 * days_old)
            
            return recency_score
        except:
            return 0.0

    def _generate_conversation_id(self, conversation: Dict[str, Any]) -> str:
        """Génère un ID unique pour une conversation."""
        content = conversation["user"] + conversation["nina"] + conversation["timestamp"]
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def get_memory_stats(self) -> Dict[str, int]:
        """Retourne les statistiques de mémoire améliorées."""
        return {
            "conversations": len(self.conversation_history),
            "compressed_memories": len(self.compressed_memories),
            "preferences": len(self.user_preferences),
            "learned_facts": sum(len(facts) for facts in self.learned_facts.values()),
            "topics": len(self.learned_facts),
            "entities_in_graph": len(self.memory_graph),
            "total_connections": sum(len(entity["connections"]) for entity in self.memory_graph.values())
        }

    def get_recent_conversations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Récupère les conversations récentes."""
        return self.conversation_history[-limit:] if self.conversation_history else []

    def learn_user_preference(self, key: str, value: str):
        """Apprend une préférence utilisateur."""
        self.user_preferences[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self.save_memory()
        print(f"[AgentMemory] Préférence apprise: {key} = {value}")

    def get_user_preference(self, key: str) -> Optional[str]:
        """Récupère une préférence utilisateur."""
        pref = self.user_preferences.get(key)
        return pref["value"] if pref else None

    def learn_fact(self, topic: str, fact: str):
        """Apprend un fait sur un sujet."""
        if topic not in self.learned_facts:
            self.learned_facts[topic] = []
        
        fact_entry = {
            "fact": fact,
            "timestamp": datetime.now().isoformat()
        }
        
        self.learned_facts[topic].append(fact_entry)
        
        # Stocker dans la base vectorielle
        self.vector_db.add_documents(
            [f"Sujet: {topic}\nFait: {fact}"],
            [{"type": "learned_fact", "topic": topic, "timestamp": fact_entry["timestamp"]}]
        )
        
        self.save_memory()
        print(f"[AgentMemory] Fait appris sur '{topic}': {fact}")

    def get_facts_about(self, topic: str) -> List[str]:
        """Récupère les faits connus sur un sujet."""
        facts = self.learned_facts.get(topic, [])
        return [fact["fact"] for fact in facts]

    def save_memory(self):
        """Sauvegarde la mémoire sur disque."""
        try:
            memory_data = {
                "conversation_history": self.conversation_history,
                "user_preferences": self.user_preferences,
                "learned_facts": self.learned_facts,
                "memory_graph": self.memory_graph,
                "compressed_memories": self.compressed_memories,
                "memory_importance_scores": self.memory_importance_scores,
                "access_patterns": self.access_patterns,
                "temporal_decay_factors": self.temporal_decay_factors,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            # Logging des statistiques de mémoire
            try:
                os.makedirs('logs', exist_ok=True)
                stats = self.get_memory_stats()
                log_entry = {'timestamp': datetime.now().isoformat(), **stats}
                with open('logs/memory_stats.jsonl', 'a', encoding='utf-8') as logf:
                    json.dump(log_entry, logf, ensure_ascii=False)
                    logf.write('\n')
            except Exception as log_e:
                print(f"[AgentMemory] Erreur logging mémoire: {log_e}")
        except Exception as e:
            print(f"[AgentMemory] Erreur sauvegarde: {e}")

    def load_memory(self):
        """Charge la mémoire depuis le disque."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                
                self.conversation_history = memory_data.get("conversation_history", [])
                self.user_preferences = memory_data.get("user_preferences", {})
                self.learned_facts = memory_data.get("learned_facts", {})
                self.memory_graph = memory_data.get("memory_graph", {})
                self.compressed_memories = memory_data.get("compressed_memories", [])
                self.memory_importance_scores = memory_data.get("memory_importance_scores", {})
                self.access_patterns = memory_data.get("access_patterns", {})
                self.temporal_decay_factors = memory_data.get("temporal_decay_factors", {})
                
                print(f"[AgentMemory] Mémoire chargée depuis {self.memory_file}")
            else:
                print(f"[AgentMemory] Nouveau fichier de mémoire créé")
                
        except Exception as e:
            print(f"[AgentMemory] Erreur chargement mémoire: {e}")

    def clear_memory(self):
        """Efface toute la mémoire."""
        self.conversation_history = []
        self.user_preferences = {}
        self.learned_facts = {}
        self.memory_graph = {}
        self.compressed_memories = []
        self.memory_importance_scores = {}
        self.access_patterns = {}
        self.temporal_decay_factors = {}
        self.save_memory()
        print("[AgentMemory] Mémoire effacée") 