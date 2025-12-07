#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "──────────────────────────────────────────────"
echo "🚀 Setup du projet Serveur TCP/HTTP (C + Python)"
echo "Racine : ${PROJECT_ROOT}"
echo "──────────────────────────────────────────────"

# 1) Vérif outils de base
echo "🔍 Vérification outils système..."
for cmd in gcc make python3; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "❌ Commande manquante : $cmd"
        echo "   → Sur Ubuntu : sudo apt install -y build-essential python3 python3-venv python3-pip make git curl netcat"
        exit 1
    fi
done
echo "✔ Outils système OK."

# 2) Création/MAJ du venv global
if [[ ! -d "${PROJECT_ROOT}/venv" ]]; then
    echo "🌱 Création du venv Python global…"
    python3 -m venv "${PROJECT_ROOT}/venv"
fi

echo "🐍 Activation du venv…"
# shellcheck disable=SC1091
source "${PROJECT_ROOT}/venv/bin/activate"

echo "📦 Installation des dépendances Python…"
pip install --upgrade pip
pip install -r "${PROJECT_ROOT}/python/requirements.txt"

# 3) Regénération fichiers HTTP + build + tests
echo "🛠 Reconstruction C (HTTP + TCP)…"
python3 "${PROJECT_ROOT}/rebuild_project.py"

echo "🎉 Setup terminé avec succès."
echo "   ➜ Pour lancer le pipeline complet : ./scripts/start_all.sh"

