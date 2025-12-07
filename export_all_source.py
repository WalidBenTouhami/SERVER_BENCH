#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from pathlib import Path

# ================= CONFIGURATION =================
PROJECT_ROOT = Path.cwd()
OUTPUT_FILE = PROJECT_ROOT / "TOUT_LE_CODE_SOURCE_COMPLET.txt"

# Extensions à inclure (fichiers code / config)
INCLUDE_EXT = {
    ".c", ".h",
    ".py", ".sh",
    ".md", ".tex",
    ".yml", ".yaml",
    ".json", ".toml",
    ".cfg", ".conf",
}

# Fichiers SANS extension qu'on veut inclure (ex : Makefile)
INCLUDE_NO_EXT = {
    "Makefile",
    "CMakeLists.txt",
}

EXCLUDE_DIRS = {
    "venv", "__pycache__", ".git",
    "bin", "build", "logs",
    "figures", "proofs",
    "presentation/backgrounds",
    "results",
}

EXCLUDE_FILES = {
    "results.json",
    "results.xlsx",
    "dashboard.html",
    "presentation_finale_serveur.pptx",
    "script_presentation.pdf",
    ".gitignore",
    OUTPUT_FILE.name,
}


def should_include(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.name in EXCLUDE_FILES:
        return False
    if path.name.startswith("."):
        return False

    # Exclusion par répertoire
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False

    if path.suffix:
        return path.suffix.lower() in INCLUDE_EXT

    # Fichier sans extension : on filtre explicitement
    return path.name in INCLUDE_NO_EXT


def main():
    files = sorted([p for p in PROJECT_ROOT.rglob("*") if should_include(p)])

    with OUTPUT_FILE.open("w", encoding="utf-8") as out:
        out.write("# PROJET COMPLET - TOUT LE CODE SOURCE\n")
        out.write(f"# Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")
        out.write(f"# Nombre de fichiers inclus : {len(files)}\n")
        out.write(f"# Chemin du projet : {PROJECT_ROOT}\n")
        out.write("#" + "=" * 80 + "\n\n")

        for file_path in files:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            out.write(f"### FICHIER : {rel_path}\n")
            out.write("# " + "-" * 60 + "\n")
            try:
                content = file_path.read_text(encoding="utf-8")
                out.write(content)
            except UnicodeDecodeError:
                out.write("# [ERREUR : fichier binaire ou encodage non UTF-8]\n")
            except Exception as e:
                out.write(f"# [ERREUR lors de la lecture : {e}]\n")
            out.write("\n\n")
            out.write("# " + "=" * 80 + "\n\n")

    size_kb = OUTPUT_FILE.stat().st_size // 1024
    print("Succès ! Tout le code source a été exporté dans :")
    print(f"→ {OUTPUT_FILE}")
    print(f"→ Taille approximative : {size_kb} Ko")
    print(f"→ {len(files)} fichiers inclus")


if __name__ == "__main__":
    main()

