#!/usr/bin/env bash

# ==============================================================================
# Script: setupPersonalAssistant.sh
# Description: Interactive setup script for cloning PersonalAssistant, configuring SSH,
#              creating Python .venv, installing requirements, and setting up environment.
# README: # PersonalAssistant: AI Personal Assistant powered by LangChain, LangGraph, and Streamlit
# Usage: chmod +x setupPersonalAssistant.sh && ./setupPersonalAssistant.sh
# ==============================================================================

set -e

KEY_FILE="$HOME/.ssh/id_ed25519"
SSH_EMAIL="saptarshibhosale604@gmail.com"
REPO_URL="git@github.com:saptarshibhosale604/PersonalAssistant.git"
REPO_DIR="$HOME/PersonalAssistant"

# Function to prompt user for confirmation before running a command
run_step() {
    local step_desc="$1"
    local step_cmd="$2"

    echo ""
    echo "============================================================"
    echo " STEP: $step_desc"
    echo " COMMAND: $step_cmd"
    echo "============================================================"

    read -rp "Do you want to run this step? [y/N]: " choice
    case "$choice" in
        [Yy]* )
            eval "$step_cmd"
            echo "[✓] Step completed."
            ;;
        * )
            echo "[–] Skipped."
            ;;
    esac
}

echo "Starting PersonalAssistant setup..."

# Step 1: SSH Key Check / Generation
if [ -f "$KEY_FILE" ]; then
    echo "[!] SSH key already exists at $KEY_FILE"
else
    run_step \
        "Generate SSH ED25519 key pair" \
        "ssh-keygen -t ed25519 -C '$SSH_EMAIL' -f '$KEY_FILE'"
fi

# Step 2: Display Public Key
run_step \
    "Display Public SSH Key" \
    "cat '${KEY_FILE}.pub'"

# Step 3: Clone Repository
run_step \
    "Clone PersonalAssistant repository" \
    "git clone '$REPO_URL' '$REPO_DIR'"

# Ensure repository directory exists before proceeding
if [ -d "$REPO_DIR" ]; then
    cd "$REPO_DIR"
else
    echo "Directory $REPO_DIR does not exist. Skipping inner setup."
    exit 1
fi

# Step 4: Create 1-line README.md if missing
if [ ! -f "README.md" ]; then
    run_step \
        "Create 1-line README.md" \
        "echo '# PersonalAssistant: AI Personal Assistant powered by LangChain, LangGraph, and Streamlit' > README.md"
fi

# Step 5: Create requirements.txt if missing & display content
if [ ! -f "requirements.txt" ]; then
    run_step \
        "Create default requirements.txt" \
        "cat << 'EOF' > requirements.txt
langchain
langchain-community
langchain-openai
langgraph
streamlit
python-dotenv
pydantic
requests
EOF"
fi

run_step \
    "Display requirements.txt contents" \
    "cat requirements.txt"

# Step 6: Create Python Virtual Environment
run_step \
    "Create Python virtual environment (.venv)" \
    "python3 -m venv .venv"

# Step 7: Upgrade pip and install requirements
run_step \
    "Install dependencies from requirements.txt into .venv" \
    ".venv/bin/python -m pip install --upgrade pip && .venv/bin/pip install -r requirements.txt"

# Step 8: Environment Variables Setup
if [ ! -f ".env" ]; then
    run_step \
        "Create template .env file" \
        "cat << 'EOF' > .env
OPENAI_API_KEY=your_openai_api_key_here
PORT=8501
EOF"
fi

echo ""
echo "============================================================"
echo " PersonalAssistant environment setup complete!"
echo " To start working, run: cd ~/PersonalAssistant && source .venv/bin/activate"
echo "============================================================"
