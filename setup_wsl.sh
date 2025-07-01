#!/bin/bash
echo "🚀 Démarrage de l'installation des dépendances pour Nina sur WSL..."

# Mise à jour des paquets
sudo apt-get update && sudo apt-get upgrade -y

# Installation de Python et des outils de base
sudo apt-get install -y python3-pip python3-venv git

# Clonage du projet (si non déjà présent)
if [ ! -d "nina_project" ]; then
    echo "Clonage du dépôt nina_project..."
    git clone https://github.com/Warnierr/LLM_Orchestrateur.git nina_project
fi
cd nina_project

# Création et activation de l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
fi
source venv/bin/activate

# Installation de PyTorch avec le support CUDA
# Assurez-vous que votre version de CUDA est compatible
echo "Installation de PyTorch pour CUDA..."
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Installation de VLLM
echo "Installation de VLLM..."
pip3 install vllm

# Installation des autres dépendances Python
echo "Installation des autres dépendances depuis requirements.txt..."
pip3 install -r requirements.txt

echo -e "\n✅ Installation terminée !"
echo "Pour activer l'environnement, lancez : cd nina_project && source venv/bin/activate"
echo "Ensuite, vous devrez télécharger le modèle Mixtral dans un dossier et mettre à jour le chemin dans agents/agent_llm_local.py" 