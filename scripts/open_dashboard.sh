#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PY_DIR="${PROJECT_ROOT}/python"
DASHBOARD="${PY_DIR}/dashboard.html"
RESULTS_JSON="${PY_DIR}/results.json"
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/dashboard_open.log"

mkdir -p "$LOG_DIR"

timestamp() { date +"%Y-%m-%d %H:%M:%S"; }
log() { echo "[$(timestamp)] $*" | tee -a "$LOG_FILE"; }

echo "──────────────────────────────────────"
echo "🖥 Ouverture Dashboard"
echo "──────────────────────────────────────"

# venv global
if [[ -d "${PROJECT_ROOT}/venv" ]]; then
    log "🐍 Activation du venv global…"
    # shellcheck disable=SC1091
    source "${PROJECT_ROOT}/venv/bin/activate"
else
    log "❌ venv introuvable. Lance ./setup.sh."
    exit 1
fi

if [[ ! -f "$RESULTS_JSON" ]]; then
    log "❌ python/results.json introuvable. Lance d'abord ./scripts/run_all.sh."
    exit 1
fi

if [[ ! -f "$DASHBOARD" ]]; then
    log "ℹ Dashboard absent — génération via export_html.py"
    (cd "$PY_DIR" && python3 export_html.py)
fi

log "🖥 Ouverture : $DASHBOARD"
xdg-open "$DASHBOARD" >/dev/null 2>&1 || \
    log "⚠ Impossible d'ouvrir automatiquement. Fichier : $DASHBOARD"

