#!/bin/bash

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH for future sessions
    if [[ -f "$HOME/.zshrc" ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    else
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    fi
    
    # Add to current PATH
    export PATH="$HOME/.local/bin:$PATH"
fi

# Source uv environment
source "$HOME/.local/bin/env"

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Install requirements
echo "Installing requirements..."
uv pip install -r requirements.txt

# Instead of activating the venv, just inform the user
echo "Setup complete!"
echo "To start using the environment, run:"
echo "    source .venv/bin/activate"