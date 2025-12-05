#!/bin/bash
set -euo pipefail

echo "[TEST] Tests unitaires + smoke tests"

PROJECT_DIR="$(pwd)"

echo "[TEST] Compilation (mode debug avec sanitizers)..."
make debug

echo "[TEST] Test unitaire queue (test_queue)..."
make test

echo "[TEST] Smoke test serveur_mono..."
./serveur_mono >/dev/null 2>&1 &
PID_MONO=$!
sleep 1

cd "$PROJECT_DIR/python"
if [ ! -d venv ]; then python3 -m venv venv; fi
# shellcheck disable=SC1091
source venv/bin/activate
pip install -r requirements.txt >/dev/null
python3 client_stress.py --port 5050 --clients 5 || echo "[TEST] client_stress mono: erreur"

kill $PID_MONO 2>/dev/null || true
echo "[TEST] Terminé."
