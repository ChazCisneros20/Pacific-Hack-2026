# Pacific Hack 2026 — Quick Start

This repo contains a minimal hackathon-ready scaffold.

Steps to get started locally:

1. Run the platform-appropriate setup script to create a virtualenv and install dependencies:

   - Windows PowerShell: `scripts/setup_env.ps1`
   - macOS / Linux: `scripts/setup_env.sh`

2. Activate the virtual environment (PowerShell example): `.\.venv\Scripts\Activate.ps1`
3. Run the app or tests (see `scripts` for examples).

Files added by the scaffold:

- [README.md](README.md)
- [.gitignore](.gitignore)
- [requirements.txt](requirements.txt)
- [scripts/setup_env.ps1](scripts/setup_env.ps1)
- [scripts/setup_env.sh](scripts/setup_env.sh)
- [.vscode/extensions.json](.vscode/extensions.json)
- [.vscode/settings.json](.vscode/settings.json)
- [src/__init__.py](src/__init__.py)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)

If you prefer a different language or runtime (Node, Rust, Go), tell me and I will adapt this scaffold.
