#!/bin/bash
# Script d'installation initiale sur la VM
# À exécuter une seule fois lors de la première configuration

set -e

echo "=== Installation du bot Discord News ==="

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation de Python et pip
sudo apt install -y python3 python3-pip python3-venv git curl

# Création du répertoire
mkdir -p ~/discord-news-bot
cd ~/discord-news-bot

# Clone du repo (à remplacer par ton repo GitHub)
# git clone https://github.com/TON_USERNAME/discord-news-bot.git .

# Création de l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt

# Création du fichier .env (à remplir manuellement)
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Dust API Configuration
DUST_WORKSPACE_ID=
DUST_API_KEY=
DUST_CONVERSATION_ID=
DUST_AGENT_ID=

# Discord Configuration
DISCORD_WEBHOOK_URL=

# Schedule Configuration
DAILY_GENERATION_TIME=07:58
DAILY_FETCH_TIME=08:00
EOF
    echo "⚠️  Fichier .env créé - REMPLIS-LE AVEC TES CREDENTIALS"
fi

# Installation du service systemd
sudo cp scripts/discord-news-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable discord-news-bot

echo "=== Installation terminée ==="
echo "1. Remplis le fichier .env avec tes credentials"
echo "2. Lance le service: sudo systemctl start discord-news-bot"
echo "3. Vérifie le status: sudo systemctl status discord-news-bot"
