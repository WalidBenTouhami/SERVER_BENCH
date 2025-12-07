#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PY_DIR="${PROJECT_ROOT}/python"
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/auto_run.log"

mkdir -p "$LOG_DIR"

timestamp() { date +"%Y-%m-%d %H:%M:%S"; }
log() { echo "[$(timestamp)] $*" | tee -a "$LOG_FILE"; }

echo "──────────────────────────────────────────────" | tee -a "$LOG_FILE"
echo "🚀 Pipeline complet (build + bench + plots)"     | tee -a "$LOG_FILE"
echo "Racine : ${PROJECT_ROOT}"                         | tee -a "$LOG_FILE"
echo "──────────────────────────────────────────────" | tee -a "$LOG_FILE"

# venv global
if [[ -d "${PROJECT_ROOT}/venv" ]]; then
    log "🐍 Activation du venv global…"
    # shellcheck disable=SC1091
    source "${PROJECT_ROOT}/venv/bin/activate"
else
    log "❌ venv introuvable. Lance ./setup.sh en premier."
    exit 1
fi

log "🧱 Compilation C…"
(
    cd "$PROJECT_ROOT"
    make clean
    make -j
)

log "🔥 Exécution du benchmark Python…"
(
    cd "$PY_DIR"
    python3 benchmark.py
    python3 plot_results.py
    python3 export_html.py
)

log "✔ Pipeline terminé. Résultats dans python/results.* et python/figures/."

