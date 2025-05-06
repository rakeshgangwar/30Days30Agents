#!/bin/bash

# Build script for Gradient Screenshot macOS application

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Check if icon exists, if not generate it
if [ ! -f "icon.icns" ]; then
    echo "Generating app icon..."
    python3 icons/generate_icon.py
    ./icons/create_icns.sh
fi

# Clean up previous builds
rm -rf build dist

# Build the application using PyInstaller
echo "Building macOS application..."
pyinstaller --clean --noconfirm Gradient_Screenshot.spec

# Check if build was successful
if [ -d "dist/Gradient Screenshot.app" ]; then
    echo "\n✅ Build complete! The application is located at:\n$(pwd)/dist/Gradient\ Screenshot.app"
    echo "\nYou can now copy this .app file to your Applications folder or distribute it to others."
    echo "\nTo install to Applications folder, run:\n cp -r \"$(pwd)/dist/Gradient Screenshot.app\" /Applications/"
    
    # Open the dist folder to show the app
    open "$(pwd)/dist/"
else
    echo "\n❌ Build failed. Please check the error messages above."
fi
