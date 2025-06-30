import requests
import json
import os
from typing import List, Dict, Any

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "mixtral:instruct"

class AgentLLMLocal:
    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model = model
        self.base_url = base_url
        self.use_ollama = self._check_ollama_connection()

    def _check_ollama_connection(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            print(f"[AgentLLMLocal] ✅ Ollama connecté sur {self.base_url}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[AgentLLMLocal] ⚠️ Ollama non accessible: {e}")
            return False

    def generate(self, prompt: str) -> str:
        if not self.use_ollama:
            return "Le service de LLM local n'est pas disponible."
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "top_p": 0.9}
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "Aucune réponse du modèle.")
        except requests.exceptions.RequestException as e:
            print(f"[AgentLLMLocal] Erreur lors de la génération Ollama: {e}")
            return "Une erreur est survenue lors de la communication avec le LLM local." 