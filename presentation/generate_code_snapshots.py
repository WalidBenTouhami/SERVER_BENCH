#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_code_snapshots.py
--------------------------

Génère automatiquement des captures PNG du code source
avec coloration syntaxique (style Dracula ou fallback Monokai).

Fichiers pris en charge :
  - src/http.c
  - src/http.h
  - src/queue.c
  - src/queue.h
  - src/serveur_mono.c
  - src/serveur_mono_http.c
  - src/serveur_multi.c
  - src/serveur_multi_http.c
  - python/client_stress.py

Les PNG sont générés dans : presentation/code_snapshots/
"""

from pathlib import Path

from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import CLexer, CppLexer, PythonLexer
from pygments.styles import get_style_by_name, STYLE_MAP


ROOT = Path(__file__).resolve().parents[1]  # server_project/
SRC_DIR = ROOT / "src"
PY_DIR = ROOT / "python"
SNAP_DIR = ROOT / "presentation" / "code_snapshots"


def get_style_name() -> str:
    """
    Essaie de charger 'dracula', sinon fallback vers 'monokai'.
    (Dracula n'est pas toujours disponible dans l'install Pygments de base.)
    """
    try:
        get_style_by_name("dracula")
        return "dracula"
    except Exception:
        # fallback robuste
        if "monokai" in STYLE_MAP:
            return "monokai"
        return "native"


def make_formatter():
    style_name = get_style_name()
    print(f"[INFO] Style Pygments utilisé pour le code : {style_name}")
    return ImageFormatter(
        style=style_name,
        font_name="DejaVu Sans Mono",
        font_size=16,
        line_numbers=True,
        line_pad=2,
        image_pad=10,
    )


def generate_one(code_path: Path, out_name: str, lexer) -> None:
    SNAP_DIR.mkdir(parents=True, exist_ok=True)

    if not code_path.exists():
        print(f"[WARN] Fichier introuvable, snapshot ignoré : {code_path}")
        return

    with code_path.open("r", encoding="utf-8") as f:
        code = f.read()

    formatter = make_formatter()
    png_path = SNAP_DIR / out_name

    print(f"[GEN] {code_path} -> {png_path}")
    data = highlight(code, lexer, formatter)
    with png_path.open("wb") as out:
        out.write(data)


def generate_all_snapshots() -> None:
    """
    Génère tous les snapshots de code nécessaires pour la présentation.
    """
    print("=== GÉNÉRATION DES CAPTURES DE CODE (PNG) ===")

    # C / Header
    generate_one(SRC_DIR / "http.c", "code_http_c.png", CLexer())
    generate_one(SRC_DIR / "http.h", "code_http_h.png", CLexer())
    generate_one(SRC_DIR / "queue.c", "code_queue_c.png", CLexer())
    generate_one(SRC_DIR / "queue.h", "code_queue_h.png", CLexer())

    generate_one(SRC_DIR / "serveur_mono.c", "code_serveur_mono_c.png", CLexer())
    generate_one(
        SRC_DIR / "serveur_mono_http.c",
        "code_serveur_mono_http_c.png",
        CLexer(),
    )
    generate_one(
        SRC_DIR / "serveur_multi.c",
        "code_serveur_multi_c.png",
        CLexer(),
    )
    generate_one(
        SRC_DIR / "serveur_multi_http.c",
        "code_serveur_multi_http_c.png",
        CLexer(),
    )

    # Python
    generate_one(
        PY_DIR / "client_stress.py",
        "code_client_stress_py.png",
        PythonLexer(),
    )

    print("✔ Captures de code générées dans presentation/code_snapshots/")


if __name__ == "__main__":
    generate_all_snapshots()

