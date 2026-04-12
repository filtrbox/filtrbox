#!/bin/bash

# =====================================================
# FILTRBOX - Script d'installation client
# A executer sur le Pi du client via SSH
# =====================================================

echo "======================================"
echo "  FILTRBOX - Installation client"
echo "======================================"
echo ""

# Demander les informations
read -p "ID unique du client (ex: pi-dupont) : " DEVICE_ID
read -p "Nom affiché (ex: Piscine Dupont)    : " DEVICE_NAME
read -p "Mot de passe client                 : " CLIENT_PASS
read -p "Prénom client (pour login)          : " CLIENT_USER

# Générer une clé API unique
API_KEY=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 32)

echo ""
echo "======================================"
echo "  Configuration en cours..."
echo "======================================"

# Cloner le dépôt Pi
if [ ! -d ~/ProgPI/FILTRBOX_2 ]; then
    mkdir -p ~/ProgPI
    cd ~/ProgPI
    git clone https://github.com/filtrbox/filtrbox-pi.git FILTRBOX_2
fi

cd ~/ProgPI/FILTRBOX_2

# Configurer les paramètres cloud
sed -i "s/DEVICE_ID    = .*/DEVICE_ID    = \"$DEVICE_ID\"/" web_server.py
sed -i "s/DEVICE_NAME  = .*/DEVICE_NAME  = \"$DEVICE_NAME\"/" web_server.py
sed -i "s/API_KEY      = .*/API_KEY      = \"$API_KEY\"/" web_server.py

# Installer les dépendances
pip3 install flask flask-cors RPi.GPIO --break-system-packages

# Installer le service
sudo cp filtrbox.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable filtrbox
sudo systemctl start filtrbox

echo ""
echo "======================================"
echo "  Création du compte client sur VPS..."
echo "======================================"

# Créer le compte client sur le VPS
curl -s -X POST https://filtrbox.fr/api/admin/user/add \
    -H "Content-Type: application/json" \
    -d "{\"user\":\"admin\",\"password\":\"$(cat ~/filtrbox/.admin_pass 2>/dev/null || echo 'filtrbox2026')\",\"username\":\"$CLIENT_USER\",\"password_new\":\"$CLIENT_PASS\",\"devices\":[\"$DEVICE_ID\"]}"

echo ""
echo "======================================"
echo "✅ Installation terminée !"
echo "======================================"
echo ""
echo "  Client : $CLIENT_USER"
echo "  Piscine : $DEVICE_NAME"
echo "  Accès  : https://filtrbox.fr/client"
echo "  Login  : $CLIENT_USER"
echo "  Pass   : $CLIENT_PASS"
echo "  API Key: $API_KEY"
echo ""
echo "  Vérification dans 10 secondes..."
sleep 10

STATUS=$(curl -s "https://filtrbox.fr/api/admin/devices?user=admin&password=$(cat ~/filtrbox/.admin_pass 2>/dev/null || echo 'filtrbox2026')" | python3 -c "import sys,json; d=json.load(sys.stdin); dev=d.get('$DEVICE_ID',{}); print('EN LIGNE' if dev.get('online') else 'HORS LIGNE')" 2>/dev/null)

echo "  Statut Pi : $STATUS"
echo ""
