#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    raise SystemExit(
        "❌ Le module Pillow (PIL) est manquant.\n"
        "   Installe-le dans le venv : pip install pillow"
    )

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "presentation" / "backgrounds"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def gen_background(color, name: str) -> None:
    img = Image.new("RGB", (1920, 1080), color)
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Serveur Haute Performance", fill=(255, 255, 255))
    out_path = OUTPUT_DIR / name
    img.save(out_path)
    print(f"✔ Background généré : {out_path}")


def main() -> None:
    gen_background((10, 30, 60), "background_blue_engineer.png")
    gen_background((20, 20, 20), "background_dark_tech.png")
    gen_background((230, 230, 230), "background_white_clean.png")
    print(f"✔ Tous les backgrounds ont été générés dans {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

