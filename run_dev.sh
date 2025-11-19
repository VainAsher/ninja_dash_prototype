#!/bin/bash
# Quick development runner - runs game from source without building
# Uses environment configuration system

# Change to project root
cd "$(dirname "$0")"

echo "============================================"
echo "Ninja Dash - Development Mode"
echo "============================================"
echo ""
echo "Running from source (no build required)"
echo "Press Ctrl+C to stop"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed!"
        exit 1
    fi
    PYTHON_CMD=python
else
    PYTHON_CMD=python3
fi

# Check for pygame
$PYTHON_CMD -c "import pygame" &> /dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: pygame is not installed!"
    echo ""
    read -p "Install dependencies? (y/n): " INSTALL
    if [[ "$INSTALL" =~ ^[Yy]$ ]]; then
        pip3 install -r requirements.txt || pip install -r requirements.txt
    else
        echo "ERROR: Dependencies required to run game"
        exit 1
    fi
fi

# Run the game (defaults to TEST environment)
$PYTHON_CMD main.py --env=test
