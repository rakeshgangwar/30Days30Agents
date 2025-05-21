#!/bin/bash
# Setup script for Digi-Persona

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    # Install uv using pip
    pip install uv
fi

# Create a virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

echo "Setup complete! You can now run the application with:"
echo "source .venv/bin/activate && python scripts/run_app.py"
