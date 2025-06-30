import os
import requests
from typing import Optional, Dict, Any, List

class AgentOpenRouter:
    """Agent universel pour interroger n'importe quel LLM via l'API OpenRouter."""
    
    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialise l'agent avec la clé API OpenRouter.
        La clé peut être passée directement ou via la variable d'environnement OPENROUTER_API_KEY.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("La clé API OPENROUTER_API_KEY doit être fournie.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def invoke(
        self, 
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> str:
        """
        Invoque un modèle LLM via OpenRouter.

        Args:
            model_name: Le nom du modèle à utiliser (ex: "xai/grok-3.1", "anthropic/claude-3-sonnet").
            messages: La liste des messages (prompt) au format OpenAI.
            temperature: La température pour la génération.
            max_tokens: Le nombre maximum de jetons à générer.

        Returns:
            La réponse textuelle du modèle.
        """
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
                message = data["choices"][0].get("message")
                if message and message.get("content"):
                    return message["content"].strip()
            
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