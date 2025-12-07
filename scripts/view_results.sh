#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PY_DIR="${PROJECT_ROOT}/python"

echo "──────────────────────────────────────────────"
echo "📊 Inspection rapide des résultats"
echo "──────────────────────────────────────────────"

cd "$PY_DIR"

if [[ ! -f "results.xlsx" ]]; then
    echo "❌ results.xlsx introuvable. Lance ./scripts/run_all.sh."
    exit 1
fi

if [[ -d "${PROJECT_ROOT}/venv" ]]; then
    # shellcheck disable=SC1091
    source "${PROJECT_ROOT}/venv/bin/activate"
fi

python3 - << 'EOF'
import pandas as pd

df = pd.read_excel("results.xlsx")
print("\nColonnes disponibles :")
print(df.columns.tolist())

print("\nAperçu (5 premières lignes) :")
print(df.head())

print("\nRésumé par type de serveur :")
print(df.groupby("server")[["throughput_rps","cpu_mean","mem_mean"]].mean())
EOF

