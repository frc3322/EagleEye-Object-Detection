#!/bin/bash

# Exit on error
set -e

apt install pyenv

# Ensure pyenv is available
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"

# Install and set Python version
pyenv install -s 3.13.0
pyenv global 3.13.0

# Create virtual environment
python3 -m venv /data/cache/venv

# Activate virtual environment
source /data/cache/venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Remove .idea folder if it exists
rm -rf .idea

echo "Setup complete."
