# 🤖 Guide d'Utilisation de Nina v0.2.0

## 🌟 Démarrage Rapide

### Installation
```bash
pip install -e .
```

### Premier test
```bash
python nina.py --test
```

### Lancement de l'interface
```bash
python nina.py
```

## 💬 Interface CLI

### Commandes disponibles
- **Questions naturelles** : Tapez directement votre question
- `/help` : Affiche l'aide
- `/stats` : Statistiques de la session
- `/reset` : Nouvelle session
- `/exit` : Quitter

### Exemples de questions
- "Quelles sont les dernières actualités en IA ?"
- "Analyse-moi les tendances du machine learning"
- "Crée un plan d'apprentissage pour le deep learning"
- "Recherche des informations sur les transformers"

## 🎛️ Options CLI

### Test et diagnostic
```bash
python nina.py --test        # Test complet
python nina.py --version     # Informations système
```

### Questions directes
```bash
python nina.py --query "Votre question ici"
```

### Interface web (en développement)
```bash
python nina.py --web
```

## 🎬 Démonstration

### Lancer la démo interactive
```bash
python demo.py
```

Cette démonstration vous montre :
- Collecte et analyse web
- Récupération d'actualités
- Analyse et recommandations
- Planification de tâches

## ⚙️ Configuration

### Variables d'environnement (.env)
```bash
# LLM Configuration
OPENAI_API_BASE=http://localhost:8080/v1
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=mistral-7b

# Services externes
NEWSAPI_KEY=your_newsapi_key

# Configuration Nina
LOG_LEVEL=INFO
NINA_DATA_DIR=./data
MAX_SEARCH_RESULTS=10
```

### Configuration LLM Local

#### Avec LocalAI
```bash
# Installation LocalAI
curl https://localai.io/install.sh | sh

# Lancement
local-ai --models-path ./models
```

#### Avec Ollama
```bash
# Installation Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Téléchargement d'un modèle
ollama pull mistral:7b

# Lancement du serveur
ollama serve
```

## 🧠 Agents de Nina

### Agent Chercheur
- **Fonction** : Collecte de données web
- **Sources** : DuckDuckGo, APIs
- **Formats** : HTML, JSON, texte

### Agent Analyste
- **Fonction** : Analyse des données collectées
- **Méthodes** : Extraction d'insights, statistiques
- **Sortie** : Rapports structurés

### Agent News
- **Fonction** : Actualités spécialisées IA
- **Sources** : NewsAPI.org, DuckDuckGo
- **Fallback** : Scraping automatique

### Agent Planificateur
- **Fonction** : Gestion de tâches et objectifs
- **Capacités** : Priorisation, échéances
- **Intégration** : Calendrier, notifications

### Agent Rédacteur
- **Fonction** : Génération de rapports
- **Formats** : Markdown, texte structuré
- **LLM** : Support LocalAI/Ollama/OpenAI

### Agent Apprentissage
- **Fonction** : Amélioration continue
- **Méthodes** : Mémoire vectorielle, recommandations
- **Persistance** : Base Qdrant

## 🔍 Fonctionnalités Avancées

### Recherche Sémantique (RAG)
- Base vectorielle Qdrant in-memory
- Embeddings déterministes
- Recherche par similarité
- Mémoire temporelle

### Système de Mémoire
- **Mémoire courte** : Session en cours
- **Mémoire longue** : Base vectorielle persistante
- **Apprentissage** : Amélioration des recommandations

### Collecte Web Intelligente
- User-Agent personnalisé
- Gestion des timeouts
- Fallback automatique
- Rate limiting respectueux

## 🐛 Dépannage

### Problèmes courants

#### Import Error
```bash
# Réinstaller le package
pip uninstall nina_project
pip install -e .
```

#### Tests qui échouent
```bash
# Vérifier les dépendances
pip install -r requirements.txt

# Lancer les tests individuellement
python -m pytest tests/test_orchestrator.py -v
```

#### Erreur de connexion LLM
- Vérifiez que LocalAI/Ollama fonctionne
- Configurez `OPENAI_API_BASE` correctement
- Testez avec `curl http://localhost:8080/v1/models`

#### Pas de résultats web
- Vérifiez votre connexion internet
- DuckDuckGo peut parfois bloquer les bots
- Ajoutez des délais entre les requêtes

### Logs et Debug
```bash
# Mode debug
DEBUG=true python nina.py

# Logs détaillés
LOG_LEVEL=DEBUG python nina.py
```

## 📈 Métriques et Monitoring

### Statistiques de session
- Utilisez `/stats` dans l'interface CLI
- Historique des questions/réponses
- Temps de traitement
- Agents utilisés

### Performance
- Temps de réponse typique : 3-8 secondes
- Collecte web : 1-3 secondes
- Analyse : 0.5-1 seconde
- Génération rapport : 1-2 secondes

## 🔮 Prochaines Fonctionnalités

### Phase 2 (En développement)
- Agent Nina principal autonome
- Système de décision intelligent
- Mémoire utilisateur personnalisée
- Reasoning chain explicite

### Phase 3 (Planifié)
- Interface web Streamlit
- API REST complète
- Intégrations externes (Slack, Discord)
- Base de données relationnelle

### Phase 4 (Vision)
- Application mobile
- Extension navigateur
- Plugins et connecteurs
- Mode vocal

## 💡 Conseils d'Utilisation

### Questions efficaces
- Soyez spécifique : "Analyse les tendances IA en 2024" plutôt que "Parle-moi d'IA"
- Mentionnez le contexte : "Pour un débutant en ML" ou "Niveau avancé"
- Demandez des formats précis : "Fais un plan étape par étape"

### Optimisation des performances
- Laissez Nina apprendre : plus vous l'utilisez, meilleures sont ses recommandations
- Utilisez `/reset` pour des nouveaux sujets non liés
- Configurez un LLM local pour de meilleures réponses

### Utilisation professionnelle
- Configurez vos propres APIs (NewsAPI, etc.)
- Personnalisez les prompts dans `configs/`
- Intégrez dans vos CI/CD pour l'automatisation

## 🤝 Support et Contribution

### Support
- Documentation : Ce guide
- Issues : GitHub Issues
- Tests : `python nina.py --test`

### Contribution
- Code : Pull requests bienvenues
- Documentation : Améliorations suggérées
- Tests : Nouveaux cas de test
- Idées : Discussions GitHub

---

**Nina v0.2.0** - Assistant IA Intelligent & Autonome  
*Développé avec ❤️ pour la communauté IA francophone* 