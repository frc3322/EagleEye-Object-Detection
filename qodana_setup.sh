#!/bin/bash

# Exit on error
set -e

# Create virtual environment
python3 -m venv /data/cache/venv

# Activate virtual environment
source /data/cache/venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Remove .idea folder if it exists
rm -rf .idea

echo "Setup complete."
