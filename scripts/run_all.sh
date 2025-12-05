#!/bin/bash
set -euo pipefail

echo "[RUN_ALL] Pipeline complet (build + bench + plots)"

PROJECT_DIR="$(pwd)"
PYTHON_DIR="$PROJECT_DIR/python"

echo "[RUN_ALL] Compilation C..."
cd "$PROJECT_DIR"
make clean
make all

echo "[RUN_ALL] Environnement Python..."
cd "$PYTHON_DIR"
if [ ! -d venv ]; then
  python3 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate
pip install -r requirements.txt

echo "[RUN_ALL] Benchmark..."
python3 benchmark.py

echo "[RUN_ALL] Graphiques..."
python3 plot_results.py

echo "[RUN_ALL] Terminé. Résultats: python/results.*, python/figures/"
