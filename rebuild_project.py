#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script officiel de reconstruction du projet.
Ce script :
  ✔ régénère uniquement les fichiers HTTP (http.c/.h + serveurs HTTP)
  ✔ NE modifie PAS le Makefile
  ✔ NE modifie PAS la queue ou les serveurs TCP
  ✔ exécute create_http_files.py
  ✔ lance make clean + make -j
  ✔ exécute les tests unitaires
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

def run(cmd):
    print(f"\n➡️  {cmd}")
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        print(f"❌ Commande échouée : {cmd}")
        sys.exit(ret)

def main():
    print("🔄 Reconstruction du projet TCP + HTTP…")

    # 1) Regénération des fichiers HTTP uniquement
    create_http = ROOT / "create_http_files.py"
    if not create_http.exists():
        print("❌ create_http_files.py introuvable !")
        sys.exit(1)

    run(f"python3 {create_http}")

    # 2) Compilation propre
    run("make clean")
    run("make -j$(nproc)")

    # 3) Tests unitaires (queue.c)
    run("make test")

    print("\n🎉 Projet reconstruit avec succès ! Aucun fichier critique écrasé.\n")

if __name__ == "__main__":
    main()

