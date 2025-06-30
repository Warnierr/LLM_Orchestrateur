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
5. 📚 Intégration Agent Wikipedia via LangChain
   - Utiliser `WikipediaAPIWrapper` ou `WikipediaQueryRun` de LangChain pour interroger l'API Wikipedia
   - Créer `agents/agent_wikipedia.py` avec la classe `AgentWikipedia`
   - Ajouter `agent_wikipedia` dans `configs/crew_config.yaml` et exposer via Function Calling dans `AgentNina`
6. 🤖 Ajout Agent Grok (Salesforce)
   - Créer `agents/agent_grok.py` avec un endpoint REST et clé API
   - Exposer `AgentGrok` dans `configs/crew_config.yaml` sous `agents:`
   - Ajouter la fonction `grok_query` dans `AgentNina.think_and_respond` pour les déclencheurs "grok", "Grok AI"
7. ♻️ Auto-critique & apprentissage continu
   - Boucle d'évaluation post-réponse, feedback utilisateur, ajustement de prompts
   - Réentrainement incrémental selon retours
8. 📊 Knowledge Graph d'entités
   - Extraction NER (SpaCy, HF) et relations
   - Stockage Neo4j / RDF + requêtes factuelles (ex. "Quels projets AI ai-je mentionnés ?")
9. 🎼 Multi-modalité
   - Intégration STT (Whisper) et TTS (Coqui, pyttsx3…)
   - Support audio & images
10. ⚙️ Orchestrateur avancé
    - Expérimenter CrewAI vs LangChain pour workflows dynamiques
    - Uniformiser appels de fonctions, tracing & monitoring
11. 🔒 Sécurité & actions système
    - Agent Shell contrôlé (sandbox)
    - Gouvernance des permissions
12. 📈 Scalabilité & production
    - Qdrant en Docker / FAISS sur disque pour indices persistants
    - Déployer PostgreSQL ou Redis pour la partie SQL
    - CI/CD, tests d'intégration, monitoring (logs, métriques)
    - Containerisation (Docker + Kubernetes), packaging pip
13. 🎤 Modules audio (STT Whisper, TTS)
14. 🌐 Interface web & observabilité (Streamlit, logging structuré)
15. ✅ Tests & CI/CD (couverture tests, GitHub Actions)
16. 📦 Déploiement & packaging (Docker, pip)
17. 📚 Documentation & push Git (README, docs/, guides)
18. 🔎 Résultats du test d'intelligence générale

## Améliorations futures du raisonnement LLM

10. **Intégration de LLMs de pointe** : Tester et intégrer des modèles plus performants supportés par la configuration matérielle actuelle.
    - **Option A (Qualité Maximale)** : `Mistral-Mixtral-8x7B-Instruct` pour une capacité de raisonnement et de synthèse supérieure.
    - **Option B (Réactivité Maximale)** : `Meta-Llama-3-8B-Instruct` pour un équilibre parfait entre performance et vitesse.
11. **Chaîne de Pensée (Chain-of-Thought)** : Modifier le prompt pour demander au LLM d'expliciter son raisonnement étape par étape avant de donner la réponse finale, afin d'améliorer la qualité et la fiabilité des réponses complexes.
12. **Apprentissage par l'exemple (Few-shot Prompting)** : Pour les tâches de raisonnement, inclure dans le prompt un ou deux exemples de questions/réponses correctes pour "montrer" au LLM le format et la logique attendus.
13. **Montée en gamme du modèle (Futur)** : Pour des capacités de raisonnement au-delà des standards actuels, envisager de passer à de futurs modèles nécessitant une infrastructure de type serveur.

## Étape suivante immédiate

- Implémenter l'étape 5 : compléter `agents/agent_llm_local.py` et `app/cli.py` pour que Nina LLM utilise pleinement l'Orchestrateur via Function Calling. 