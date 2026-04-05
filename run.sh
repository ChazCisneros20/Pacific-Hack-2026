#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -q -r requirements.txt
    echo "Done."
fi

# Activate and run
source .venv/bin/activate
cd src
python app.py
