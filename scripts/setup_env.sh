#!/usr/bin/env bash
set -euo pipefail
venv_dir=".venv"
if ! command -v python >/dev/null 2>&1; then
  echo "Python not found on PATH. Install Python 3.10+ and retry." >&2
  exit 1
fi

python -m venv "$venv_dir"
echo "Activating virtualenv and installing requirements..."
source "$venv_dir/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Setup complete. Activate with: source $venv_dir/bin/activate"
