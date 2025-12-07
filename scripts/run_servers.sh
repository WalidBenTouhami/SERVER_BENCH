#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BIN_DIR="${PROJECT_ROOT}/bin"
LOG_DIR="${PROJECT_ROOT}/logs"

mkdir -p "$LOG_DIR"

echo "──────────────────────────────────────────────"
echo "🚀 Lancement manuel des serveurs C"
echo "──────────────────────────────────────────────"

# Mono TCP
echo "▶ serveur_mono (TCP 5050)…"
"${BIN_DIR}/serveur_mono"  > "${LOG_DIR}/serveur_mono.log"  2>&1 &

# Multi TCP
echo "▶ serveur_multi (TCP 5051)…"
"${BIN_DIR}/serveur_multi" > "${LOG_DIR}/serveur_multi.log" 2>&1 &

echo "ℹ Utiliser make kill_servers ou ./scripts/kill_servers.sh pour arrêter."

