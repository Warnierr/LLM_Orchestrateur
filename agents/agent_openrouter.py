import os
import requests
import json
import hashlib
from typing import Optional, Dict, Any, List

class AgentOpenRouter:
    """Agent universel pour interroger n'importe quel LLM via l'API OpenRouter."""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    CACHE_FILE = "data/openrouter_cache.json"

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialise l'agent avec la clé API OpenRouter et charge le cache.
        La clé peut être passée directement ou via la variable d'environnement OPENROUTER_API_KEY.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("La clé API OPENROUTER_API_KEY doit être fournie.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Créer le répertoire de données s'il n'existe pas
        os.makedirs(os.path.dirname(self.CACHE_FILE), exist_ok=True)
        self._load_cache()

    def _load_cache(self):
        """Charge le cache depuis un fichier JSON."""
        try:
            with open(self.CACHE_FILE, 'r') as f:
                self.cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.cache = {}

    def _save_cache(self):
        """Sauvegarde le cache dans un fichier JSON."""
        with open(self.CACHE_FILE, 'w') as f:
            json.dump(self.cache, f, indent=4)

    def _get_cache_key(self, model_name: str, messages: List[Dict[str, str]], temperature: float) -> str:
        """Crée une clé de hachage unique pour une requête donnée."""
        request_string = f"{model_name}{json.dumps(messages)}{temperature}"
        return hashlib.sha256(request_string.encode()).hexdigest()

    def invoke(
        self, 
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        """
        Invoque un modèle LLM via OpenRouter, avec un système de cache.

        Args:
            model_name: Le nom du modèle à utiliser (ex: "xai/grok-3.1", "anthropic/claude-3-sonnet").
            messages: La liste des messages (prompt) au format OpenAI.
            temperature: La température pour la génération.
            max_tokens: Le nombre maximum de jetons à générer.

        Returns:
            La réponse textuelle du modèle.
        """
        # --- Gestion du Cache ---
        cache_key = self._get_cache_key(model_name, messages, temperature)
        if cache_key in self.cache:
            print("--- INFO: Réponse trouvée dans le cache. ---")
            return self.cache[cache_key]
        
        # --- Appel API si non trouvé dans le cache ---
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        
        try:
            api_url = f"{self.BASE_URL}/chat/completions"
            response = requests.post(api_url, json=payload, headers=self.headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if data.get("choices") and data["choices"]:
                message_content = data["choices"][0].get("message", {}).get("content", "")
                if message_content:
                    # Sauvegarder dans le cache avant de retourner
                    self.cache[cache_key] = message_content
                    self._save_cache()
                    return message_content.strip()
            
            return "Réponse du modèle non trouvée ou vide."
            
        except requests.exceptions.HTTPError as http_err:
            error_details = ""
            try:
                error_details = response.json()
            except Exception:
                error_details = response.text
            return f"Erreur HTTP de l'API OpenRouter: {http_err} - {error_details}"
        except Exception as e:
            return f"Erreur lors de la communication avec OpenRouter: {e}" 