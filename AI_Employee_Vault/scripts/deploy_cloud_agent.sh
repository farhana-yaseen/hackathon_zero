#!/bin/bash
# Deploy Platinum Cloud Agent to Oracle Cloud VM
# Run this script on your Oracle Cloud VM

set -e

echo "=========================================="
echo "Platinum Cloud Agent Deployment Script"
echo "=========================================="

# Configuration
VAULT_PATH="/home/ubuntu/AI_Employee_Vault"
PYTHON_VERSION="3.11"
SERVICE_NAME="platinum-cloud-agent"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run as root"
    exit 1
fi

echo ""
echo "[Step 1] System Update"
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo "[Step 2] Install Python and Dependencies"
sudo apt-get install -y python3 python3-pip python3-venv git

echo ""
echo "[Step 3] Clone or Update Vault Repository"
if [ -d "$VAULT_PATH" ]; then
    echo "Vault directory exists, pulling latest changes..."
    cd "$VAULT_PATH"
    git pull
else
    echo "Cloning vault repository..."
    read -p "Enter Git repository URL: " REPO_URL
    git clone "$REPO_URL" "$VAULT_PATH"
    cd "$VAULT_PATH"
fi

echo ""
echo "[Step 4] Create Python Virtual Environment"
python3 -m venv venv
source venv/bin/activate

echo ""
echo "[Step 5] Install Python Dependencies"
pip install --upgrade pip
pip install -r requirements.txt
pip install flask requests

echo ""
echo "[Step 6] Configure Environment Variables"
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# A2A Protocol Secret Key (CHANGE THIS!)
A2A_SECRET_KEY=$(openssl rand -hex 32)

# Gmail API Credentials (if using)
GOOGLE_APPLICATION_CREDENTIALS=credentials.json

# Vault Path
VAULT_PATH=$VAULT_PATH

# Log Level
LOG_LEVEL=INFO
EOF
    echo "✓ .env file created with random A2A secret key"
    echo "⚠️  IMPORTANT: Copy this secret key to your local machine!"
    echo ""
    cat .env | grep A2A_SECRET_KEY
    echo ""
else
    echo "✓ .env file already exists"
fi

echo ""
echo "[Step 7] Configure Git for Vault Sync"
cd "$VAULT_PATH"
git config pull.rebase false
git config user.email "cloud-agent@example.com"
git config user.name "Cloud Agent"

# Setup Git sync cron job
echo "Setting up automatic Git sync..."
CRON_CMD="*/5 * * * * cd $VAULT_PATH && git pull && git add -A && git commit -m 'Cloud agent sync' && git push"
(crontab -l 2>/dev/null | grep -v "Cloud agent sync"; echo "$CRON_CMD") | crontab -

echo "✓ Git sync configured (every 5 minutes)"

echo ""
echo "[Step 8] Configure Systemd Service"
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=Platinum Cloud Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$VAULT_PATH
Environment="PATH=$VAULT_PATH/venv/bin"
EnvironmentFile=$VAULT_PATH/.env
ExecStart=$VAULT_PATH/venv/bin/python3 $VAULT_PATH/scripts/platinum_cloud_agent.py $VAULT_PATH
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Systemd service created"

echo ""
echo "[Step 9] Configure Firewall"
echo "Opening port 8090 for A2A protocol..."
sudo ufw allow 8090/tcp
sudo ufw status

echo ""
echo "[Step 10] Setup HTTPS (Optional - Let's Encrypt)"
read -p "Do you want to setup HTTPS with Let's Encrypt? (y/n): " SETUP_HTTPS

if [ "$SETUP_HTTPS" = "y" ]; then
    read -p "Enter your domain name: " DOMAIN_NAME

    sudo apt-get install -y certbot
    sudo certbot certonly --standalone -d "$DOMAIN_NAME"

    # Update cloud_a2a_config.json with cert paths
    echo "✓ SSL certificates obtained"
    echo "Update cloud_a2a_config.json with:"
    echo "  cert_path: /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"
    echo "  key_path: /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem"
fi

echo ""
echo "[Step 11] Enable and Start Service"
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo ""
echo "[Step 12] Verify Service Status"
sudo systemctl status $SERVICE_NAME --no-pager

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Service Status:"
echo "  Start:   sudo systemctl start $SERVICE_NAME"
echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
echo "  Restart: sudo systemctl restart $SERVICE_NAME"
echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "Vault Sync:"
echo "  Manual sync: cd $VAULT_PATH && git pull && git push"
echo "  Auto sync: Every 5 minutes via cron"
echo ""
echo "Next Steps:"
echo "1. Copy A2A_SECRET_KEY from .env to your local machine"
echo "2. Update cloud_a2a_config.json with your local IP"
echo "3. Start local agent on your machine"
echo "4. Test A2A communication"
echo ""
