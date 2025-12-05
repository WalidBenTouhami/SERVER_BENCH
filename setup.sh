#!/usr/bin/env bash
set -e

echo "🌱 Création du venv Python…"
rm -rf venv
python3 -m venv venv
source venv/bin/activate

echo "📦 Installation dépendances Python…"
pip install --upgrade pip
pip install psutil pandas matplotlib

echo "🛠 Regénération fichiers HTTP…"
python3 create_http_files.py

echo "🔧 Compilation du projet…"
make clean
make -j$(nproc)

echo "🧪 Tests unitaires…"
make test

echo "🎉 Setup terminé avec succès."

