#!/bin/bash
# Ninja Dash - Run Script for Linux/Mac
# This script creates a virtual environment, installs dependencies, and runs the game

echo "========================================"
echo "     NINJA DASH - Setup and Run"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3 from your package manager"
    exit 1
fi

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
else
    echo "Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing/Updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "========================================"
echo "Starting Ninja Dash..."
echo "========================================"
python main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Game failed to start"
    echo "Check that all files are present"
fi

# Keep terminal open on some systems
read -p "Press Enter to exit..."
