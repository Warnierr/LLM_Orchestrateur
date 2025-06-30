# agent_redacteur.py

try:
    import openai  # type: ignore

    _OPENAI = True
except ImportError:
    _OPENAI = False

import os
import json
from typing import Dict, Any

class AgentRedacteur:
    def __init__(self):
        # Configure openai endpoint for LocalAI/Ollama if dispo
        if _OPENAI:
            openai.api_key = os.getenv("OPENAI_API_KEY", "demo")
            openai.base_url = os.getenv("OPENAI_API_BASE", "http://localhost:8080/v1")
            self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def generate_report(self, context_data: Dict[str, Any], reasoning: str, profile: Dict[str, Any]):
        """Génère un rapport synthétique en utilisant le contexte complet."""
        
        query = context_data.get('query', '')
        search_results = context_data.get('search_results', {})
        summary = context_data.get('conversation_summary', 'Aucun résumé fourni.')
        
        # Préparation du prompt enrichi
        prompt = f"""Tu es Nina, une assistante IA. Ta mission est de fournir une réponse complète et pertinente à la requête de l'utilisateur.

Pour cela, tu disposes de plusieurs sources d'information :
1.  **La requête actuelle de l'utilisateur.**
2.  **Les résultats d'une recherche web.**
3.  **Un résumé de l'historique récent de la conversation.**

Analyse toutes ces informations pour formuler la meilleure réponse possible. Le résumé te donne le contexte global de la discussion.

---
### CONTEXTE ###

**Requête Actuelle :**
{query}

**Résultats de la Recherche Web :**
{json.dumps(search_results, indent=2, ensure_ascii=False)}

**Résumé de la Conversation :**
{summary}

---
### TA RÉPONSE SYNTHÉTISÉE ###
"""

        # Appel au LLM local pour la synthèse finale
        try:
            from agents.agent_llm_local import AgentLLMLocal
            local_llm = AgentLLMLocal()
            if local_llm.use_ollama:
                return local_llm.generate(prompt)
            else:
                return "Le service de synthèse est actuellement indisponible."
        except Exception as e:
            print(f"[AgentRedacteur] Erreur lors de la synthèse finale : {e}")
            return "Désolé, une erreur est survenue lors de la génération de la réponse."

    def format_report(self, insights):
        # Implémenter la logique pour formater le rapport
        print("Formatage du rapport...")
        report = "Rapport d'Analyse:\n"
        for key, value in insights.items():
            report += f"- {key}: {value}\n"
        return report 