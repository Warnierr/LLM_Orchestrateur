import os
from typing import List, Dict, Any

# Ce chemin devra être adapté à l'endroit où vous stockez vos modèles dans WSL
VLLM_MODEL_PATH = "/mnt/c/Users/User/Desktop/Projets/Orchestrateur LLM/nina_project/models/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf"

try:
    from vllm import LLM, SamplingParams
    VLLM_AVAILABLE = True
except ImportError:
    VLLM_AVAILABLE = False

class AgentLLMLocal:
    def __init__(self, model: str = VLLM_MODEL_PATH):
        self.model_path = model
        self.llm_client = None
        
        if VLLM_AVAILABLE:
            if os.path.exists(self.model_path):
                print("[AgentLLMLocal] ✅ Initialisation du moteur VLLM...")
                self.sampling_params = SamplingParams(temperature=0.2, top_p=0.95, max_tokens=512)
                self.llm_client = LLM(model=self.model_path)
                print("[AgentLLMLocal] Moteur VLLM initialisé avec succès.")
            else:
                print(f"[AgentLLMLocal] ⚠️ ERREUR : Le fichier du modèle est introuvable à l'emplacement : {self.model_path}")
                print("Veuillez télécharger le modèle et/ou corriger le chemin dans agent_llm_local.py")
        else:
            print("[AgentLLMLocal] ⚠️ ERREUR : La librairie VLLM n'est pas installée. Veuillez lancer le script setup_wsl.sh")

    def generate(self, prompt: str) -> str:
        if self.llm_client:
            try:
                outputs = self.llm_client.generate(prompt, self.sampling_params)
                if outputs:
                    return outputs[0].outputs[0].text
                return "Aucune réponse générée par VLLM."
            except Exception as e:
                print(f"[AgentLLMLocal] Erreur lors de la génération VLLM : {e}")
                return "Une erreur est survenue lors de l'appel au moteur VLLM."
        
        return "Le moteur VLLM n'est pas initialisé correctement." 