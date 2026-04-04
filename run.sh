#!/usr/bin/env bash
set -euo pipefail

# Activate virtual environment and run the app
source .venv/bin/activate
cd src
python app.py