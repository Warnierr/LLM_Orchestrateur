from typing import List, Dict, Any
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_chercheur import AgentChercheur
from agents.agent_analyste import AgentAnalyste, AgentApprentissage
from agents.agent_redacteur import AgentRedacteur
from agents.agent_planificateur import AgentPlanificateur, AgentObjectif
from tools.vector_db import VectorDB
from agents.agent_news import AgentNews
from agents.agent_nina import AgentNina


class Orchestrator:
    """Orchestre la collaboration entre les différents agents de Nina.

    Pipeline par défaut :
        1. Le *chercheur* collecte les données.
        2. L'*analyste* extrait des insights.
        3. L'*apprenant* ingère les données pour améliorer les futures recommandations.
        4. Le *planificateur* décide d'actions éventuelles.
        5. Le *rédacteur* produit une réponse lisible pour l'utilisateur.
    """

    def __init__(self):
        # Agent Nina principal (nouveau!)
        self.nina = AgentNina()
        
        # Agents spécialisés (legacy - gardés pour compatibilité)
        self.chercheur = AgentChercheur()
        self.analyste = AgentAnalyste()
        self.apprenant = AgentApprentissage()
        self.planificateur = AgentPlanificateur()
        self.objectif = AgentObjectif("Amélioration continue")
        self.redacteur = AgentRedacteur()
        self.vectordb = VectorDB()
        self.news_agent = AgentNews()

    # ---------------------------------------------------------------------
    # API publique
    # ---------------------------------------------------------------------
    def orchestrate(self, requete: str) -> str:
        """
        🤖 Nouvelle orchestration intelligente avec Agent Nina !
        
        Nina analyse la requête et décide intelligemment de la stratégie optimale.
        """
        print("[Orchestrator] 🚀 Lancement de Nina v2.0...")
        
        # 🤖 Nina prend le contrôle !
        try:
            response = self.nina.think_and_respond(requete)
            print("[Orchestrator] ✅ Nina a terminé avec succès.")
            return response
            
        except Exception as e:
            print(f"[Orchestrator] ⚠️ Nina a rencontré un problème, fallback vers l'ancien système...")
            print(f"[Orchestrator] Erreur Nina: {e}")
            
            # Fallback vers l'ancien pipeline (pour compatibilité)
            return self._legacy_orchestrate(requete)
    
    def _legacy_orchestrate(self, requete: str) -> str:
        """Pipeline legacy pour compatibilité."""
        print("[Orchestrator] 🔄 Mode compatibilité activé...")

        # Étape 1 – Collecte des données
        raw_data: List[str] = self.chercheur.collect_data("web", requete)
        if not raw_data:
            raw_data = [f"Exemple de résultat pour '{requete}' n°{i}" for i in range(1, 4)]

        # Étape 2 – Analyse
        insights: Dict[str, Any] = self.analyste.analyze_data(raw_data)

        # Étape 3 – Apprentissage continu
        self.apprenant.apprendre(raw_data)
        recommandations = self.apprenant.recommander()
        if recommandations:
            insights["recommandations"] = recommandations

        # Étape 4 – Planification
        self.planificateur.plan_tasks(["Envoyer rapport", "Archiver données"])
        self.objectif.planifier()

        # Étape 5 – RAG
        self.vectordb.add_documents(raw_data)
        passages = self.vectordb.similarity_search(requete, top_k=3)

        def is_fresh(p):
            ts = p.get("meta", {}).get("timestamp") if p else None
            if not ts:
                return False
            try:
                dt = datetime.fromisoformat(ts)
                return dt > datetime.utcnow() - timedelta(hours=24)
            except ValueError:
                return False

        fresh_passages = [p for p in passages if is_fresh(p)]

        if len(fresh_passages) >= 1:
            insights["passages_similaires"] = fresh_passages
        else:
            news_items = self.news_agent.fetch_ai_news()
            if news_items:
                texts = [n["title"] for n in news_items]
                metas = [{"timestamp": n["published"], "url": n["url"], "source": n["source"]} for n in news_items]
                self.vectordb.add_documents(texts, metas)  # type: ignore[arg-type]
                insights["news"] = news_items
            else:
                insights["passages_similaires"] = passages

        # Étape 6 – Rédaction du rapport
        rapport = self.redacteur.generate_report(insights)

        print("[Orchestrator] ✅ Pipeline legacy terminé.")
        return rapport 