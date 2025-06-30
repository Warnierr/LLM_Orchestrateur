# 🤖 Nina - Assistant IA Intelligent & Autonome

Nina est un assistant IA avancé qui utilise une architecture multi-agents pour fournir des réponses intelligentes et contextuelles. Elle combine recherche web, analyse de données, mémoire vectorielle et génération de contenu.

## ✨ Fonctionnalités

- **🧠 Intelligence Multi-Agents** : Orchestration intelligente de 6 agents spécialisés
- **🔍 Recherche Web Avancée** : Collecte automatique depuis DuckDuckGo, Wikipedia, APIs
- **📊 Analyse de Données** : Extraction d'insights et apprentissage continu
- **🗄️ Mémoire Vectorielle** : RAG avec base vectorielle Qdrant
- **📰 Actualités IA** : Récupération automatique des dernières news
- **🎯 Planification** : Structuration et organisation de tâches
- **💬 LLM Local** : Support Ollama/LocalAI pour l'inférence locale

## 🚀 Installation

1. **Cloner le projet**
```bash
git clone https://github.com/votre-repo/nina_project.git
cd nina_project
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration LLM Local (optionnel)**
```bash
# Installer Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Télécharger un modèle
ollama pull mistral:7b
```

## 🎮 Utilisation

### Interface CLI Interactive
```bash
python nina.py
```

### Mode Direct LLM
```bash
python app/cli.py --direct
```

### Requête Unique
```bash
python nina.py --query "Quelles sont les dernières actualités en IA ?"
```

### Tests et Diagnostic
```bash
python nina.py --test
```

## 📁 Structure du Projet

```
nina_project/
├── agents/                 # Agents spécialisés
│   ├── agent_nina.py      # Agent principal (orchestrateur)
│   ├── agent_chercheur*.py # Agents de recherche (v1, v2, v3)
│   ├── agent_llm_local.py # Interface LLM local
│   └── ...
├── app/                   # Interfaces utilisateur
│   ├── cli.py            # Interface ligne de commande
│   ├── orchestrator.py   # Pipeline d'orchestration
│   └── interface.py      # Interface enrichie
├── tools/                # Outils utilitaires
│   └── vector_db.py      # Base de données vectorielle
├── tests/                # Tests unitaires
├── examples/             # Scripts de démonstration
├── docs/                 # Documentation
├── models/               # Modèles LLM locaux
└── configs/              # Fichiers de configuration
```

## 🧪 Exemples et Démonstrations

Le dossier `examples/` contient plusieurs scripts de démonstration :

- `demo.py` : Démonstration complète des capacités
- `demo_llm.py` : Test du LLM local
- `demo_intelligence.py` : Benchmarks d'intelligence
- `auto_test_nina.py` : Tests automatisés

```bash
python examples/demo.py
```

## ⚙️ Configuration

### Variables d'Environnement

```bash
# LLM Local (Ollama/LocalAI)
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_API_KEY=ollama

# APIs Externes (optionnel)
NEWSAPI_KEY=votre_cle_newsapi
SERPAPI_KEY=votre_cle_serpapi
```

### Fichier de Configuration

Éditez `configs/crew_config.yaml` pour personnaliser :
- Préférences utilisateur
- Configuration des agents
- Paramètres du LLM local

## 🧪 Tests

```bash
# Tous les tests
python -m pytest tests/ -v

# Tests spécifiques
python -m pytest tests/test_agent_nina.py -v

# Avec couverture
python -m pytest tests/ --cov=nina_project
```

## 🔧 Développement

### Ajout d'un Nouvel Agent

1. Créer `agents/agent_nouveau.py`
2. Implémenter les méthodes requises
3. Intégrer dans `agent_nina.py`
4. Ajouter les tests correspondants

### Architecture Multi-Agents

Nina utilise une architecture modulaire où chaque agent a une responsabilité spécifique :

- **AgentNina** : Orchestrateur principal, analyse les requêtes
- **AgentChercheur** : Collecte de données web (3 versions disponibles)
- **AgentAnalyste** : Extraction d'insights et analyse
- **AgentRedacteur** : Génération de rapports et synthèses
- **AgentNews** : Récupération d'actualités
- **AgentPlanificateur** : Organisation et planification

## 📈 Roadmap

- [ ] Interface web Streamlit
- [ ] Support multimodal (images, audio)
- [ ] Intégration APIs supplémentaires
- [ ] Optimisation des performances
- [ ] Déploiement cloud

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir `docs/` pour plus de détails sur l'architecture.

## 📄 Licence

MIT License - voir le fichier LICENSE pour plus de détails.

---

**Nina v0.2.0** - Assistant IA Intelligent & Autonome 🤖 