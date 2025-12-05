#!/bin/bash
set -euo pipefail

# ===========================
#   Nettoyage des warnings GTK
# ===========================
export NO_AT_BRIDGE=1
export GDK_BACKEND=x11
export MOZ_ENABLE_WAYLAND=0
export LIBGL_ALWAYS_INDIRECT=1

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HTML_FILE="$PROJECT_ROOT/python/dashboard.html"
LOG_FILE="$PROJECT_ROOT/logs/dashboard_open.log"

mkdir -p "$PROJECT_ROOT/logs"

echo "[INFO] Ouverture du dashboard: $HTML_FILE" | tee "$LOG_FILE"

if [ ! -f "$HTML_FILE" ]; then
    echo "[ERREUR] dashboard.html introuvable. Exécute 'python3 export_html.py' d'abord."
    exit 1
fi

# ===========================
#  Fonction d'ouverture
# ===========================
open_html() {
    if command -v xdg-open >/dev/null; then
        xdg-open "$1" >> "$LOG_FILE" 2>&1 && exit 0
    fi
    if command -v firefox >/dev/null; then
        firefox "$1" >> "$LOG_FILE" 2>&1 && exit 0
    fi
    if command -v chromium-browser >/dev/null; then
        chromium-browser "$1" >> "$LOG_FILE" 2>&1 && exit 0
    fi
    if command -v google-chrome >/dev/null; then
        google-chrome "$1" >> "$LOG_FILE" 2>&1 && exit 0
    fi
    echo "[ERREUR] Impossible d'ouvrir un navigateur." | tee -a "$LOG_FILE"
    exit 1
}

open_html "$HTML_FILE"

