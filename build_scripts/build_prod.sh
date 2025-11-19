#!/bin/bash
# Build script for PRODUCTION environment
# Creates NinjaDash executable for distribution

echo "============================================"
echo "Building Ninja Dash - PRODUCTION Build"
echo "============================================"
echo ""

# Clean previous build
echo "Cleaning previous PRODUCTION build..."
rm -rf build
rm -rf dist/NinjaDash_PROD

# Run PyInstaller with production spec
echo ""
echo "Running PyInstaller..."
pyinstaller build_scripts/ninja_dash_prod.spec --clean --noconfirm

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed!"
    exit 1
fi

echo ""
echo "============================================"
echo "Build completed successfully!"
echo "============================================"
echo "Output: dist/NinjaDash_PROD/"
echo "Executable: dist/NinjaDash_PROD/NinjaDash"
echo "============================================"
echo ""
echo "NOTE: This is the PRODUCTION build for distribution."
echo "Console is hidden and all debug features are disabled."
echo ""
