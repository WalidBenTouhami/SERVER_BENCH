#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script officiel de reconstruction du projet.
- Régénère les fichiers HTTP (http.c/.h + serveurs HTTP)
- Ne touche pas aux serveurs TCP ni à la queue
- Lance : create_http_files.py, make clean, make -j, make test
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print(f"\n➡️  {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Commande échouée (code {e.returncode}) : {' '.join(cmd)}")
        sys.exit(e.returncode)


def main() -> None:
    print("🔄 Reconstruction du projet TCP + HTTP…")

    create_http = ROOT / "create_http_files.py"
    if not create_http.exists():
        print("❌ create_http_files.py introuvable !")
        sys.exit(1)

    # 1) Regénération fichiers HTTP
    run(["python3", str(create_http)], cwd=ROOT)

    # 2) Compilation
    run(["make", "clean"], cwd=ROOT)
    run(["make", "-j"], cwd=ROOT)

    # 3) Tests
    run(["make", "test"], cwd=ROOT)

    print("\n🎉 Projet reconstruit avec succès ! Aucun fichier critique écrasé.\n")


if __name__ == "__main__":
    main()

