#!/bin/bash
# =============================================================
# TECHIN 510 Week 7 - One-Command Setup
# =============================================================
# Usage: bash setup.sh
# =============================================================

set -e

echo ""
echo "========================================"
echo "  TECHIN 510 Week 7 Setup"
echo "  Integrating AI and LLM Features"
echo "========================================"
echo ""

# Check Python version
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python is not installed. Please install Python 3.11+."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "[1/5] Found Python $PYTHON_VERSION"

# Create virtual environment
echo "[2/5] Creating virtual environment..."
$PYTHON_CMD -m venv .venv

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Install dependencies
echo "[4/5] Installing dependencies..."
pip install -r requirements.txt --quiet

# Check for .env file
echo "[5/5] Checking environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "  IMPORTANT: We created a .env file from .env.example."
    echo "  You MUST edit .env and add your Anthropic API key."
    echo "  Get your key at: https://console.anthropic.com/settings/keys"
    echo ""
else
    echo "  .env file already exists."
fi

echo ""
echo "========================================"
echo "  Setup complete!"
echo "========================================"
echo ""
echo "  Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "  2. Activate the virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "     source .venv/Scripts/activate"
else
    echo "     source .venv/bin/activate"
fi
echo "  3. Run the app:"
echo "     streamlit run app.py"
echo ""
