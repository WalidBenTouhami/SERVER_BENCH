#!/bin/bash
set -euo pipefail

# ================================
#  VIEW_RESULTS.SH
#  Affiche automatiquement:
#    - results.json (formaté)
#    - results.xlsx (tabulaire)
# ================================

# Couleurs
GREEN="\033[1;32m"
BLUE="\033[1;34m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

echo -e "${BLUE}[VIEW_RESULTS] Script d'affichage des résultats${RESET}"

# Détection du dossier projet
PROJECT_ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
PYTHON_DIR="$PROJECT_ROOT/python"
cd "$PROJECT_ROOT"

echo -e "${GREEN}[OK] Racine du projet : $PROJECT_ROOT${RESET}"

JSON_FILE="$PYTHON_DIR/results.json"
XLSX_FILE="$PYTHON_DIR/results.xlsx"

# ============================
# Vérification des fichiers
# ============================
if [[ ! -f "$JSON_FILE" ]]; then
    echo -e "${RED}[ERREUR] results.json introuvable.${RESET}"
    exit 1
fi

if [[ ! -f "$XLSX_FILE" ]]; then
    echo -e "${RED}[ERREUR] results.xlsx introuvable.${RESET}"
    exit 1
fi

# ============================
# Activation de l'environnement Python
# ============================
echo -e "${BLUE}[PYTHON] Chargement de l'environnement...${RESET}"

if [[ -d "$PYTHON_DIR/venv" ]]; then
    source "$PYTHON_DIR/venv/bin/activate"
else
    echo -e "${YELLOW}[WARN] venv manquant → création automatique...${RESET}"
    python3 -m venv "$PYTHON_DIR/venv"
    source "$PYTHON_DIR/venv/bin/activate"
    pip install -r "$PYTHON_DIR/requirements.txt"
fi

echo -e "${GREEN}[OK] Python prêt.${RESET}"

# ============================
# 1) AFFICHAGE results.json
# ============================
echo -e "\n${BLUE}===== 📄 RESULTS.JSON (FORMATÉ) =====${RESET}"

# installation jq si non présent
if ! command -v jq >/dev/null 2>&1; then
    echo -e "${YELLOW}[INFO] jq non installé → installation...${RESET}"
    sudo apt update -y && sudo apt install jq -y
fi

jq . "$JSON_FILE" | head -n 50
echo -e "${YELLOW}... (affichage limité à 50 lignes) ...${RESET}"

# ============================
# 2) AFFICHAGE results.xlsx
# ============================
echo -e "\n${BLUE}===== 📊 RESULTS.XLSX (APERÇU TABULAIRE) =====${RESET}"

python3 - << 'EOF'
import pandas as pd
import json, sys
from pathlib import Path

xlsx = Path("python/results.xlsx")
df = pd.read_excel(xlsx)

print("\nColonnes détectées :")
print(df.columns.tolist())

print("\nPremières lignes :")
print(df.head(10).to_string(index=False))

# Vérification colonnes obligatoires
required = {"server","clients","success","fail","mean","median","p95","p99","max_latency","cpu_mean","mem_mean","throughput_rps"}
missing = required - set(df.columns)

if missing:
    print("\n[ALERTE] Colonnes manquantes :", missing)
else:
    print("\n[OK] Toutes les colonnes essentielles sont présentes.")
EOF

echo -e "\n${GREEN}[VIEW_RESULTS] Affichage terminé avec succès.${RESET}"

