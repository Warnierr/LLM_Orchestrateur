# agent_redacteur.py

try:
    import openai  # type: ignore

    _OPENAI = True
except ImportError:
    _OPENAI = False

import os

class AgentRedacteur:
    def __init__(self):
        # Configure openai endpoint for LocalAI/Ollama if dispo
        if _OPENAI:
            openai.api_key = os.getenv("OPENAI_API_KEY", "demo")
            openai.base_url = os.getenv("OPENAI_API_BASE", "http://localhost:8080/v1")
            self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def generate_report(self, insights, history=None, reasoning=None, profile=None):
        """Génère un rapport synthétique en utilisant le LLM, avec chaîne de raisonnement et historique."""
        # Génération du rapport brut
        print("Génération du rapport brut...")
        report = self.format_report(insights)
        # Préparation du prompt enrichi
        messages = []
        # Message système initial avec raisonnement attendu
        system_content = "Tu es Nina, une assistante qui produit des rapports synthétiques et clairs."
        if reasoning:
            system_content += f" Raisonnement prévu: {reasoning}."
        if profile:
            for k, v in profile.items():
                system_content += f" Préférence {k}: {v}."
        messages.append({"role": "system", "content": system_content})
        # Inclure l'historique si fourni
        if history:
            for entry in history:
                query = entry.get("query", "")
                resp = entry.get("response", "")
                if query:
                    messages.append({"role": "user", "content": query})
                if resp:
                    messages.append({"role": "assistant", "content": resp})
        # Ajouter le rapport brut comme nouvelle demande
        messages.append({"role": "user", "content": report})

        # Si openai dispo, demander au LLM de reformater / résumer
        if _OPENAI:
            try:
                completion = openai.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.2,
                )
                if completion and completion.choices:
                    content = completion.choices[0].message.content or ""
                    return content.strip()
            except Exception as exc:
                print(f"[AgentRedacteur] Erreur appel LLM : {exc}")
                # fallback raw report
                return report

        # Pas de LLM ou échec, renvoyer rapport brut
        return report

    def format_report(self, insights):
        # Implémenter la logique pour formater le rapport
        print("Formatage du rapport...")
        report = "Rapport d'Analyse:\n"
        for key, value in insights.items():
            report += f"- {key}: {value}\n"
        return report 