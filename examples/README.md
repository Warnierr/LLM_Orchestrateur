# Exemples Nina

Ce dossier contient des scripts de démonstration et de test pour Nina.

## Scripts disponibles

### `demo.py`
Démonstration interactive complète des capacités de Nina :
- Collecte et analyse web
- Récupération d'actualités
- Analyse et recommandations
- Planification de tâches

```bash
python examples/demo.py
```

### `demo_llm.py`
Test basique du LLM local avec questions simples :
- Questions de culture générale
- Test de la génération de réponses

```bash
python examples/demo_llm.py
```

### `demo_intelligence.py`
Benchmarks d'intelligence pour évaluer les capacités du LLM :
- Tests de logique
- Questions de sciences
- Compréhension de texte

```bash
python examples/demo_intelligence.py
```

### `auto_test_nina.py`
Test automatisé de l'orchestrateur Nina :
- Vérification du pipeline complet
- Mesure des performances
- Rapport d'exécution

```bash
python examples/auto_test_nina.py
```

## Utilisation

Ces scripts sont conçus pour être exécutés depuis la racine du projet :

```bash
cd nina_project
python examples/[script_name].py
```

Assurez-vous d'avoir installé les dépendances :

```bash
pip install -r requirements.txt
``` 