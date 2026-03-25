#!/bin/bash
# Setup Local Agent for Platinum Tier
# Run this script on your local machine (Windows/Mac/Linux)

set -e

echo "=========================================="
echo "Platinum Local Agent Setup Script"
echo "=========================================="

# Detect OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS="windows"
    PYTHON_CMD="python"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    PYTHON_CMD="python3"
else
    OS="linux"
    PYTHON_CMD="python3"
fi

echo "Detected OS: $OS"

# Get vault path
if [ -z "$1" ]; then
    read -p "Enter vault path (default: ./AI_Employee_Vault): " VAULT_PATH
    VAULT_PATH=${VAULT_PATH:-./AI_Employee_Vault}
else
    VAULT_PATH="$1"
fi

echo "Vault path: $VAULT_PATH"

if [ ! -d "$VAULT_PATH" ]; then
    echo "Error: Vault path does not exist: $VAULT_PATH"
    exit 1
fi

cd "$VAULT_PATH"

echo ""
echo "[Step 1] Check Python Installation"
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "Error: Python not found. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
echo "✓ Python found: $PYTHON_VERSION"

echo ""
echo "[Step 2] Create/Activate Virtual Environment"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

if [ "$OS" = "windows" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✓ Virtual environment activated"

echo ""
echo "[Step 3] Install Dependencies"
pip install --upgrade pip
pip install -r requirements.txt
pip install flask requests

echo "✓ Dependencies installed"

echo ""
echo "[Step 4] Configure Environment Variables"
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    read -p "Enter A2A_SECRET_KEY from cloud agent: " SECRET_KEY

    cat > .env << EOF
# A2A Protocol Secret Key (must match cloud agent)
A2A_SECRET_KEY=$SECRET_KEY

# Gmail API Credentials
GOOGLE_APPLICATION_CREDENTIALS=credentials.json

# Vault Path
VAULT_PATH=$VAULT_PATH

# Log Level
LOG_LEVEL=INFO
EOF
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "[Step 5] Configure Git for Vault Sync"
git config pull.rebase false

echo "✓ Git configured"

echo ""
echo "[Step 6] Update Configuration Files"
read -p "Enter your cloud agent URL (e.g., https://your-domain.com/a2a/v1): " CLOUD_URL

# Update local_a2a_config.json
if [ -f "local_a2a_config.json" ]; then
    # Use Python to update JSON
    $PYTHON_CMD << EOF
import json
with open('local_a2a_config.json', 'r') as f:
    config = json.load(f)
config['a2a']['cloud_agent']['url'] = '$CLOUD_URL'
with open('local_a2a_config.json', 'w') as f:
    json.dump(config, f, indent=2)
print("✓ local_a2a_config.json updated")
EOF
fi

echo ""
echo "[Step 7] Test A2A Protocol"
echo "Running A2A protocol tests..."
$PYTHON_CMD scripts/test_a2a_protocol.py "$VAULT_PATH"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the local agent:"
echo "  $PYTHON_CMD scripts/platinum_local_agent.py $VAULT_PATH"
echo ""
echo "Or use the main entry point:"
echo "  $PYTHON_CMD main.py --tier platinum"
echo ""
echo "Vault Sync:"
echo "  Pull changes: git pull"
echo "  Push changes: git add -A && git commit -m 'Local sync' && git push"
echo ""
echo "Next Steps:"
echo "1. Ensure cloud agent is running"
echo "2. Start local agent"
echo "3. Test end-to-end workflow"
echo ""
