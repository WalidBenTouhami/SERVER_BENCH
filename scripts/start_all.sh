#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "──────────────────────────────────────────────"
echo "🚀 Lancement pipeline complet — $(date)"
echo "Racine du projet : ${PROJECT_ROOT}"
echo "──────────────────────────────────────────────"

"${PROJECT_ROOT}/scripts/run_all.sh"

echo "📊 Pour visualiser les résultats :"
echo "   ➜ ./scripts/open_dashboard.sh"
echo "   ➜ ./scripts/view_results.sh"

