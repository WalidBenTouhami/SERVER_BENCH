#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "──────────────────────────────────────────────"
echo "🧹 Nettoyage projet (C + logs + figures)"
echo "──────────────────────────────────────────────"

cd "$PROJECT_ROOT"

make clean || true
rm -rf python/figures/*.png python/figures/*.svg || true
rm -f python/results.json python/results.xlsx || true

echo "✔ Nettoyage terminé."

