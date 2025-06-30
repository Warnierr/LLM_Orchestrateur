# Roadmap du projet Nina

## Statut actuel

- 📦 Phases 1 à 5 complétées :
  - Fondations, CLI vLLM, mémoire vectorielle, orchestrateur multi-agents, intégration de vLLM (>=0.8.5) avec Function Calling de base.

## Prochaines étapes

1. 🗂️ Hiérarchisation de la mémoire (MemoryManager à trois couches)
   - Mémoire de travail (fenêtre glissante des 10–20 derniers messages)
   - Mémoire sémantique (vectorielle / RAG)
   - Mémoire condensée (résumés périodiques via agent Summarizer + table SQL `summaries`)
2. 🛠️ Mémoire personnalisée (SQL + Qdrant)
   - `tools/sql_db.py` (SQLAlchemy) + `tools/vector_db.py` (Qdrant)
   - Configuration `DATABASE_URL` (SQLite pour POC, PostgreSQL en production)
3. 🤖 Fiabilisation de Nina LLM
   - Chaîne de raisonnement détaillée (chain-of-thought)
   - Gestion robuste des appels de fonctions (fallback local/cloud)
4. 🔍 Amélioration des embeddings & re-ranking
   - Remplacer l'embedder maison par un modèle HF (`SentenceTransformers`, DPR…)
   - Cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) pour filtrage des passages
5. ♻️ Auto-critique & apprentissage continu
   - Boucle d'évaluation post-réponse, feedback utilisateur, ajustement de prompts
   - Réentrainement incrémental selon retours
6. 📊 Knowledge Graph d'entités
   - Extraction NER (SpaCy, HF) et relations
   - Stockage Neo4j / RDF + requêtes factuelles (ex. "Quels projets AI ai-je mentionnés ?")
7. 🎼 Multi-modalité
   - Intégration STT (Whisper) et TTS (Coqui, pyttsx3…)
   - Support audio & images
8. ⚙️ Orchestrateur avancé
   - Expérimenter CrewAI vs LangChain pour workflows dynamiques
   - Uniformiser appels de fonctions, tracing & monitoring
9. 🔒 Sécurité & actions système
   - Agent Shell contrôlé (sandbox)
   - Gouvernance des permissions
10. 📈 Scalabilité & production
    - Qdrant en Docker / FAISS sur disque pour indices persistants
    - Déployer PostgreSQL ou Redis pour la partie SQL
    - CI/CD, tests d'intégration, monitoring (logs, métriques)
    - Containerisation (Docker + Kubernetes), packaging pip
11. 🎤 Modules audio (STT Whisper, TTS)
12. 🌐 Interface web & observabilité (Streamlit, logging structuré)
13. ✅ Tests & CI/CD (couverture tests, GitHub Actions)
14. 📦 Déploiement & packaging (Docker, pip)
15. 📚 Documentation & push Git (README, docs/, guides)
16. 🔎 Résultats du test d'intelligence générale

## Étape suivante immédiate

- Implémenter l'étape 5 : compléter `agents/agent_llm_local.py` et `app/cli.py` pour que Nina LLM utilise pleinement l'Orchestrateur via Function Calling. 