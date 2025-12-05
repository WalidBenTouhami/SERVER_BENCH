#!/bin/bash
set -euo pipefail

echo "[SERVERS] Lancement serveur_mono (5050) et serveur_multi (5051)"

PROJECT_DIR="$(pwd)"
MONO="$PROJECT_DIR/serveur_mono"
MULTI="$PROJECT_DIR/serveur_multi"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"

if [ ! -x "$MONO" ] || [ ! -x "$MULTI" ]; then
  echo "[SERVERS] Binaires manquants. Compile d'abord avec 'make all'."
  exit 1
fi

"$MONO" > "$LOG_DIR/mono.log" 2>&1 &
PID_MONO=$!
"$MULTI" > "$LOG_DIR/multi.log" 2>&1 &
PID_MULTI=$!

echo "[SERVERS] PID mono  = $PID_MONO"
echo "[SERVERS] PID multi = $PID_MULTI"
echo "[SERVERS] Ctrl+C pour arrêter."

trap "echo '[SERVERS] Arrêt'; kill $PID_MONO $PID_MULTI 2>/dev/null || true; exit 0" SIGINT

while true; do sleep 1; done
