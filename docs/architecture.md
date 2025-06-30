# Architecture du système Nina

Ci-dessous l'architecture complète et actuelle du projet Nina avec système de mémoire :

```mermaid
graph TD
    U[Utilisateur] --> I[CLI & Interface (app)]
    I --> N[LLM Nina (Mistral via Ollama + Mémoire)]
    N --> O[Orchestrateur (app/orchestrator.py)]
    N <--> M[AgentMemory (agents/agent_memory.py)]
    M <--> F[data/nina_memory.json]
    M <--> V[VectorDB (Qdrant in-memory)]
    
    subgraph "Agents et outils"
      O --> Chercheur[AgentChercheurV3]
      O --> Analyste[AgentAnalyste & AgentApprentissage]
      O --> Plan[AgentPlanificateur & AgentObjectif]
      O --> Redacteur[AgentRedacteur]
      O --> News[AgentNews]
      O --> VDB[VectorDB (Qdrant in-memory)]
      N --> LLMLocal[AgentLLMLocal (avec mémoire)]
    end
```

## Description

- **Utilisateur** : interagit via CLI ou interface web.
- **CLI & Interface** : point d'entrée (app/cli.py, app/interface.py).
- **LLM Nina** : cœur intelligent utilisant Mistral 7B via Ollama, avec système de mémoire intégré.
- **AgentMemory** : gestion de la mémoire conversationnelle, préférences utilisateur et faits appris.
- **Persistance** : sauvegarde dans `data/nina_memory.json` et base vectorielle Qdrant.
- **Orchestrateur** : coordonne les agents spécialisés selon les besoins.
- **Agents spécialisés** : recherche, analyse, planification, rédaction, actualités.

## Flux d'exécution

1. **Requête simple** (salutations) : User → Nina (avec contexte mémoire) → Réponse directe
2. **Requête complexe** : User → Nina → Orchestrateur → Agents → Synthèse → Sauvegarde mémoire
3. **Mémoire** : Chaque interaction enrichit la base de connaissances persistante

## Capacités actuelles

- ✅ **Mémoire conversationnelle** : Se souvient des échanges précédents
- ✅ **Apprentissage continu** : Préférences utilisateur et faits
- ✅ **Contextualisation** : Réponses enrichies par l'historique
- ✅ **Persistance** : Données sauvegardées entre sessions
- ✅ **Recherche sémantique** : Retrouve les conversations similaires
- ✅ **Pipeline multi-agents** : Orchestration intelligente des tâches 