#!/bin/bash
set -euo pipefail

echo "[CLEAN] Nettoyage complet du projet"

PROJECT_DIR="$(pwd)"

rm -f "$PROJECT_DIR/serveur_mono" "$PROJECT_DIR/serveur_multi" "$PROJECT_DIR/test_queue"
rm -f "$PROJECT_DIR"/src/*.o "$PROJECT_DIR"/tests/*.o

rm -rf "$PROJECT_DIR/python/venv"
rm -f "$PROJECT_DIR/python/results.json" "$PROJECT_DIR/python/results.xlsx"
rm -rf "$PROJECT_DIR/python/figures"

rm -rf "$PROJECT_DIR/logs"

echo "[CLEAN] OK"
