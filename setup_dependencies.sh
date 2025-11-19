#!/bin/bash
# Dependency installation script for Ninja Dash
# Installs all required dependencies for building and running the game

echo "============================================"
echo "Ninja Dash - Dependency Setup"
echo "============================================"
echo ""
echo "This script will install all required dependencies:"
echo "  - pygame (game engine)"
echo "  - pyinstaller (executable builder)"
echo "  - pytest (testing framework)"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH!"
        echo ""
        echo "Please install Python 3.8+ from https://www.python.org/"
        echo "Or use your system's package manager:"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "  Fedora: sudo dnf install python3 python3-pip"
        echo "  macOS: brew install python3"
        echo ""
        exit 1
    fi
    PYTHON_CMD=python
    PIP_CMD=pip
else
    PYTHON_CMD=python3
    PIP_CMD=pip3
fi

echo "[OK] Python found:"
$PYTHON_CMD --version
echo ""

# Check for pip
if ! command -v $PIP_CMD &> /dev/null; then
    echo "ERROR: pip is not installed or not in PATH!"
    echo "Please install pip for your Python version."
    echo ""
    exit 1
fi

echo "[OK] pip found"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
echo ""
$PIP_CMD install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies!"
    echo "Please check the error messages above."
    echo ""
    exit 1
fi

echo ""
echo "============================================"
echo "Dependencies installed successfully!"
echo "============================================"
echo ""
echo "You can now:"
echo "  1. Run the game: $PYTHON_CMD main.py"
echo "  2. Build executables: ./build_scripts/build_all.sh"
echo ""
echo "============================================"
echo ""
