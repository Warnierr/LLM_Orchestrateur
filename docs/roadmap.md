# Roadmap du Projet Nina

## Vision : Un Agent Autonome Intelligent

L'objectif est de faire de Nina un agent capable de raisonner, d'apprendre et d'agir de manière autonome pour assister l'utilisateur dans des tâches complexes.

---

### Phase 1 : Consolidation de l'Architecture (Terminée)
- **Fondations du projet** : CLI, structure des agents, etc.
- **Intégration d'un LLM local** : `Mistral-7B`.
- **Mémoire initiale** : SQL (historique) et Vectorielle (Qdrant).
- **Orchestrateur de base** : `CrewAI` pour la collaboration d'agents.

---

### Phase 2 : Vers une Intelligence Unifiée (En cours)

L'objectif de cette phase est de centraliser l'accès à l'intelligence et de jeter les bases d'un raisonnement avancé.

**Priorité #1 : Interface LLM Universelle avec OpenRouter**
- **Action** : Remplacer les agents LLM spécifiques (`agent_grok`, `agent_llm_local`) par un `agent_openrouter.py` unique.
- **Bénéfice** : Accès à des dizaines de modèles (Grok, Claude, GPT-4, Llama 3) via une seule API, simplifiant la maintenance et augmentant la flexibilité.

**Priorité #2 : Implémentation du Framework `ReAct` (Reason + Act)**
- **Action** : Refondre l'`Orchestrateur` pour qu'il suive une boucle de raisonnement :
    1.  **Réflexion (Reason)** : Le LLM décompose le problème et choisit un outil (ex: recherche web).
    2.  **Action (Act)** : L'orchestrateur exécute l'outil.
    3.  **Observation** : Le résultat de l'action est analysé.
    4.  La boucle continue jusqu'à la résolution du problème.
- **Bénéfice** : Rend Nina capable de gérer des tâches complexes en plusieurs étapes, de s'auto-corriger et de montrer sa logique.

**Priorité #3 : Amélioration Active de la Mémoire**
- **Action** : Mettre en place la boucle d'apprentissage : `Rappeler -> Agir -> Consolider`.
- **Rappeler** : Avant chaque action, Nina consulte ses mémoires SQL et Vectorielle pour contextualiser la demande.
- **Consolider** : Après chaque tâche complexe, un agent extrait les "faits" importants du résultat et les sauvegarde dans la mémoire SQL et Vectorielle (via la nouvelle table `facts`).
- **Bénéfice** : Nina apprend continuellement de ses interactions et de ses recherches.

---

### Phase 3 : Capacités Avancées et Autonomie

Une fois la Phase 2 terminée, nous nous concentrerons sur l'enrichissement de l'intelligence de Nina.

- **Knowledge Graph d'Entités** :
    - **Action** : Mettre en place une base de données graphe (ex: Neo4j) et un processus pour extraire les entités (personnes, lieux, projets) et leurs relations à partir des faits appris.
    - **Bénéfice** : Permet à Nina de faire des déductions complexes en naviguant les relations entre les concepts qu'elle connaît.

- **Planification Stratégique (Tree of Thoughts - ToT)** :
    - **Action** : Faire évoluer le framework `ReAct` pour explorer plusieurs chemins de résolution en parallèle, évaluer leur potentiel et choisir le meilleur.
    - **Bénéfice** : Capacité à résoudre des problèmes ouverts qui n'ont pas de solution unique évidente.

- **Intégrations d'Outils Étendues** :
    - **Action** : Intégrer de nouveaux outils essentiels comme `agent_wikipedia`, la recherche web (DuckDuckGo), et un agent capable d'exécuter du code dans un `sandbox` sécurisé.
    - **Bénéfice** : Augmente le champ d'action de Nina.

- **Multi-modalité** :
    - **Action** : Intégration de la reconnaissance vocale (STT via Whisper) et de la synthèse vocale (TTS).
    - **Bénéfice** : Permet une interaction plus naturelle avec Nina.

---
*Ce document sera mis à jour au fur et à mesure de l'avancement du projet.* 