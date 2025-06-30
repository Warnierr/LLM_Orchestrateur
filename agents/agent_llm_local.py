import requests
import json
import os
from typing import List, Dict, Any

# Configuration Ollama par défaut
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "mistral:7b-instruct"
LOCAL_MODEL_PATH = "models/mistral-7b-instruct-v0.2.Q4_K_M/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

class AgentLLMLocal:
    """Agent LLM local basé sur Ollama avec fallback vers modèle local."""
    
    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = OLLAMA_BASE_URL):
        """Initialise l'agent avec Ollama ou fallback local."""
        self.model = model
        self.base_url = base_url
        self.use_ollama = False
        self.memory = None  # Initialisé à la demande
        self.use_vllm = False
        self.llm_client = None
        
        self.fallback_responses = {
            "nom": "Je suis Nina, votre assistante IA locale. Je fonctionne actuellement en mode fallback car Ollama n'est pas disponible.",
            "salut": "Bonjour ! Je suis Nina. Comment puis-je vous aider aujourd'hui ?",
            "actualités": "Je peux rechercher les dernières actualités IA pour vous. Voulez-vous que je procède ?",
            "default": "Je suis Nina, votre assistante IA. Ollama n'étant pas disponible, je fonctionne en mode simplifié. Installez Ollama depuis ollama.com pour une expérience complète."
        }
        
        # Vérifier que Ollama est accessible
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            self.use_ollama = True
            print(f"[AgentLLMLocal] ✅ Ollama connecté sur {self.base_url}")
        except Exception as e:
            print(f"[AgentLLMLocal] ⚠️ Ollama non accessible: {e}")
            print(f"[AgentLLMLocal] Mode fallback activé")
            if os.path.exists(LOCAL_MODEL_PATH):
                print(f"[AgentLLMLocal] Modèle local trouvé: {LOCAL_MODEL_PATH}")
            else:
                print(f"[AgentLLMLocal] ⚠️ Modèle local non trouvé: {LOCAL_MODEL_PATH}")
        # Tentative d'intégration de vLLM pour le modèle local
        try:
            from vllm import LLM
            self.llm_client = LLM(model=LOCAL_MODEL_PATH)
            self.use_vllm = True
            print(f"[AgentLLMLocal] vLLM chargé avec le modèle local: {LOCAL_MODEL_PATH}")
        except Exception as e:
            print(f"[AgentLLMLocal] vLLM non disponible ou erreur de chargement du modèle: {e}")
        
        # Fonctions exposées au modèle pour Function Calling
        self.functions = [
            {
                "name": "collect_data",
                "description": "Collecte des données depuis une source externe",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_type": {"type": "string"},
                        "query": {"type": "string"}
                    },
                    "required": ["source_type", "query"]
                }
            },
            {
                "name": "search_wikipedia",
                "description": "Recherche des informations sur Wikipedia en français",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "similarity_search",
                "description": "Recherche de passages similaires dans la mémoire vectorielle",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "top_k": {"type": "integer"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "analyze_data",
                "description": "Analyse des données collectées pour extraire des insights",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["data"]
                }
            },
            {
                "name": "fetch_ai_news",
                "description": "Récupère les dernières actualités IA",
                "parameters": {"type": "object", "properties": {}, "required": []}
            },
            {
                "name": "plan_tasks",
                "description": "Planifie des tâches selon une liste de descriptions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tasks": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["tasks"]
                }
            },
            {
                "name": "generate_report",
                "description": "Génère un rapport synthétique à partir des insights",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "insights": {"type": "object"}
                    },
                    "required": ["insights"]
                }
            }
        ]

    def _get_memory(self):
        """Initialise la mémoire à la demande."""
        if self.memory is None:
            try:
                from agents.agent_memory import AgentMemory
                self.memory = AgentMemory()
            except Exception as e:
                print(f"[AgentLLMLocal] ⚠️ Impossible d'initialiser la mémoire: {e}")
                self.memory = None
        return self.memory

    def chat_with_memory(self, messages: List[Dict[str, str]]) -> str:
        """Chat avec prise en compte de la mémoire."""
        if not messages:
            return "Bonjour ! Je suis Nina. Comment puis-je vous aider ?"
        
        user_input = messages[-1].get("content", "")
        
        # Récupérer le contexte de mémoire
        memory = self._get_memory()
        context = ""
        if memory:
            context = memory.get_context_for_response(user_input)
        
        # Enrichir le prompt avec le contexte
        if context and messages:
            system_msg = messages[0] if messages[0].get("role") == "system" else None
            if system_msg:
                system_msg["content"] += f"\n\nContexte de mémoire:\n{context}"
            else:
                messages.insert(0, {"role": "system", "content": f"Contexte de mémoire:\n{context}"})
        
        # Générer la réponse
        response = self.chat(messages)
        
        # Sauvegarder la conversation
        if memory:
            memory.add_conversation(user_input, response)
        
        return response

    def generate_with_memory(self, prompt: str) -> str:
        """Génère une réponse avec prise en compte de la mémoire."""
        system_msg = {"role": "system", "content": "Vous êtes Nina, une assistante IA locale. Répondez en français, de manière concise et précise."}
        user_msg = {"role": "user", "content": prompt}
        return self.chat_with_memory([system_msg, user_msg])

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Effectue un échange chat avec vLLM, Ollama ou fallback."""
        # Prioritise vLLM si disponible
        if self.use_vllm and self.llm_client is not None:
            return self._vllm_chat(messages)
        # Puis Ollama
        if self.use_ollama:
            try:
                prompt = self._build_prompt_from_messages(messages)
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.2, "top_p": 0.9}
                    },
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
            except Exception as e:
                print(f"[AgentLLMLocal] Erreur chat Ollama: {e}")
        # Fallback final
        return self._fallback_chat(messages)

    def _fallback_chat(self, messages: List[Dict[str, str]]) -> str:
        """Mode fallback pour le chat."""
        if not messages:
            return self.fallback_responses["default"]
        
        last_message = messages[-1].get("content", "").lower()
        
        if any(word in last_message for word in ["nom", "qui", "tu es", "vous êtes"]):
            return self.fallback_responses["nom"]
        elif any(word in last_message for word in ["bonjour", "salut", "hello"]):
            return self.fallback_responses["salut"]
        elif any(word in last_message for word in ["actualité", "news", "nouvelles"]):
            return self.fallback_responses["actualités"]
        else:
            return f"{self.fallback_responses['default']} Votre question: '{last_message}'"

    def _vllm_chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat via vLLM en local."""
        try:
            prompt = self._build_prompt_from_messages(messages)
            # Génération vLLM
            outputs = self.llm_client.generate(prompt)  # type: ignore
            # Récupérer le premier token stream si possible
            outputs_iter = iter(outputs)
            first = next(outputs_iter)
            return first.outputs[0].text
        except Exception as e:
            print(f"[AgentLLMLocal] Erreur vLLM: {e}")
            return self._fallback_chat(messages)

    def generate(self, prompt: str) -> str:
        """Génère une réponse à partir d'un prompt simple."""
        if not self.use_ollama:
            return self._fallback_generate(prompt)
            
        system_msg = {"role": "system", "content": "Vous êtes Nina, une assistante IA locale. Répondez en français, de manière concise et précise."}
        user_msg = {"role": "user", "content": prompt}
        return self.chat([system_msg, user_msg])

    def _fallback_generate(self, prompt: str) -> str:
        """Mode fallback pour generate."""
        return self._fallback_chat([{"role": "user", "content": prompt}])

    def _build_prompt_from_messages(self, messages: List[Dict[str, str]]) -> str:
        """Construit un prompt à partir des messages de chat."""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"<|system|>\n{content}\n")
            elif role == "user":
                prompt_parts.append(f"<|user|>\n{content}\n")
            elif role == "assistant":
                prompt_parts.append(f"<|assistant|>\n{content}\n")
            elif role == "tool":
                prompt_parts.append(f"<|tool_result|>\n{content}\n")
        
        prompt_parts.append("<|assistant|>\n")
        return "".join(prompt_parts)

    def _execute_function(self, name: str, args: Dict[str, Any]) -> Any:
        """Appelle dynamiquement les fonctions de l'orchestrateur."""
        try:
            from agents.agent_chercheur_v3 import AgentChercheurV3  # type: ignore
            from agents.agent_analyste import AgentAnalyste  # type: ignore
            from agents.agent_news import AgentNews  # type: ignore
            from tools.vector_db import VectorDB  # type: ignore
            from agents.agent_planificateur import AgentPlanificateur  # type: ignore
            from agents.agent_redacteur import AgentRedacteur  # type: ignore
            
            if name == "collect_data":
                source = args.get("source_type") or ""
                query = args.get("query") or ""
                return AgentChercheurV3().collect_data(source, query)
            elif name == "search_wikipedia":
                query = args.get("query") or ""
                return self._search_wikipedia(query)
            elif name == "similarity_search":
                q = args.get("query") or ""
                top_k = args.get("top_k", 3)
                return VectorDB().similarity_search(q, top_k=top_k)
            elif name == "analyze_data":
                return AgentAnalyste().analyze_data(args.get("data") or [])
            elif name == "fetch_ai_news":
                return AgentNews().fetch_ai_news()
            elif name == "plan_tasks":
                tasks = args.get("tasks") or []
                AgentPlanificateur().plan_tasks(tasks)
                return {"status": "done"}
            elif name == "generate_report":
                insights = args.get("insights") or {}
                return AgentRedacteur().generate_report(insights)
            else:
                return {"error": f"Fonction inconnue: {name}"}
                
        except Exception as e:
            return {"error": f"Erreur lors de l'exécution de {name}: {e}"}

    def _search_wikipedia(self, query: str) -> List[str]:
        """Recherche directe sur Wikipedia via l'API officielle."""
        try:
            import requests
            
            # API de recherche Wikipedia française
            search_url = "https://fr.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": 3
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            search_data = response.json()
            
            results = []
            search_results = search_data.get("query", {}).get("search", [])
            
            for page in search_results[:3]:
                title = page.get("title")
                snippet = page.get("snippet", "")
                
                if title:
                    # Récupérer le contenu complet de la page
                    content_url = "https://fr.wikipedia.org/w/api.php"
                    content_params = {
                        "action": "query",
                        "format": "json",
                        "titles": title,
                        "prop": "extracts",
                        "exintro": True,
                        "explaintext": True,
                        "exsectionformat": "plain"
                    }
                    
                    try:
                        content_resp = requests.get(content_url, params=content_params, timeout=10)
                        if content_resp.status_code == 200:
                            content_data = content_resp.json()
                            pages = content_data.get("query", {}).get("pages", {})
                            
                            for page_id, page_data in pages.items():
                                extract = page_data.get("extract", "")
                                if extract:
                                    result = f"Wikipedia - {title}\n{extract[:500]}..."
                                    results.append(result)
                                    break
                    except:
                        # Fallback avec les données de recherche
                        result = f"Wikipedia - {title}"
                        if snippet:
                            # Nettoyer le snippet HTML
                            import re
                            clean_snippet = re.sub(r'<[^>]+>', '', snippet)
                            result += f"\n{clean_snippet[:300]}..."
                        results.append(result)
            
            return results
            
        except Exception as e:
            print(f"[AgentLLMLocal] Erreur Wikipedia: {e}")
            return [f"Erreur lors de la recherche Wikipedia pour '{query}': {e}"]

    def chat_with_functions(self, messages: List[Dict[str, str]]) -> str:
        """Chat avec support des appels de fonctions (simulation)."""
        # Pour l'instant, on simule le function calling
        # Dans une version future, on pourrait parser la réponse du modèle
        # pour détecter des appels de fonctions
        
        # Ajouter le contexte des fonctions disponibles
        functions_context = "Fonctions disponibles:\n"
        for func in self.functions:
            functions_context += f"- {func['name']}: {func['description']}\n"
        
        enhanced_messages = messages.copy()
        if enhanced_messages and enhanced_messages[0].get("role") == "system":
            enhanced_messages[0]["content"] += f"\n\n{functions_context}"
        else:
            enhanced_messages.insert(0, {"role": "system", "content": functions_context})
        
        return self.chat(enhanced_messages) 