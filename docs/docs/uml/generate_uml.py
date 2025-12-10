#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent

uml_files = [
    "uml_seq_mono.puml",
    "uml_seq_multi.puml",
    "uml_seq_http_mono.puml",
    "uml_seq_http_multi.puml"
]

print("\n🔧 Génération automatique des UML .SVG …\n")

for f in uml_files:
    puml_path = BASE / f
    svg_path  = BASE / f.replace(".puml", ".svg")

    if not puml_path.exists():
        print(f"❌ Fichier manquant : {puml_path}")
        continue

    cmd = ["plantuml", "-tsvg", str(puml_path)]
    print(f"▶ plantuml {f} → {svg_path.name}")
    subprocess.run(cmd, check=True)

print("\n✅ UML générés avec succès !")
print("Fichiers SVG disponibles dans :", BASE)