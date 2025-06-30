# Roadmap du projet Nina

## Statut actuel

- 📦 Phases 1 à 5 complétées :
  - Fondations, CLI vLLM, mémoire vectorielle, orchestrateur multi-agents, intégration de vLLM (>=0.8.5) avec Function Calling de base.

## Prochaines étapes

1. 🎤 Modules audio (STT Whisper, TTS).
2. 🌐 Interface web Streamlit et observabilité (logging structuré, monitoring).
3. ✅ Tests & CI/CD (couverture tests, GitHub Actions).
4. 📦 Déploiement (Docker, Kubernetes, packaging pip).
5. 🔧 Affiner la brique Function Calling locale :
   - Exposer les fonctions de l'orchestrateur (`collect_data`, `analyze_data`, `similarity_search`, `fetch_ai_news`, `plan_tasks`, `generate_report`).
   - Étendre `AgentLLMLocal.functions` et améliorer `_execute_function`.
   - Adapter le CLI direct (`--direct`) pour déléguer au pipeline via l'Orchestrateur.
6. 📚 Documentation mise à jour (`docs/architecture.md`, `GUIDE_UTILISATION.md`).

## Étape suivante immédiate

- Implémenter l'étape 5 : compléter `agents/agent_llm_local.py` et `app/cli.py` pour que Nina LLM utilise pleinement l'Orchestrateur via Function Calling. 