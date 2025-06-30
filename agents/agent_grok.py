import os
import requests
from typing import Optional, Dict, Any

class AgentGrok:
    """Agent pour interroger l'API Grok de xAI."""
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialise l'agent avec la clé API de xAI.
        La clé peut être passée directement ou via la variable d'environnement XAI_API_KEY.
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("La clé API XAI_API_KEY doit être fournie.")
        
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def query(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """Envoie le prompt à l'API Grok et retourne la réponse."""
        payload: Dict[str, Any] = {
            "model": "grok-3-latest",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
            data = response.json()
            
            # Extraire le contenu de la réponse de l'assistant
            if data.get("choices") and len(data["choices"]) > 0:
                message = data["choices"][0].get("message")
                if message and message.get("content"):
                    return message["content"].strip()
            
            return "Réponse de Grok non trouvée ou vide."
            
        except requests.exceptions.HTTPError as http_err:
            # Essayer de lire le corps de la réponse d'erreur
            error_details = ""
            try:
                error_details = response.json()
            except Exception:
                error_details = response.text
            return f"Erreur HTTP de l'API Grok: {http_err} - {error_details}"
        except Exception as e:
            return f"Erreur lors de la communication avec l'API Grok: {e}" 