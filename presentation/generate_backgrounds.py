#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génération automatique des backgrounds pour la présentation PowerPoint.
Version PRO – dark mode + light mode + gradients modernes.

Output :
    presentation/backgrounds/bg_light.png
    presentation/backgrounds/bg_dark.png
"""

from PIL import Image, ImageDraw, ImageFilter
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BG_DIR = ROOT / "presentation" / "backgrounds"
BG_DIR.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 1920, 1080


def generate_gradient(color_top, color_bottom, output):
    img = Image.new("RGB", (WIDTH, HEIGHT), color_top)
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    img = img.filter(ImageFilter.GaussianBlur(1.2))
    img.save(output, "PNG")
    print(f"✔ Background généré → {output}")


def main():
    print("\n=== GENERATE BACKGROUNDS ===")

    generate_gradient((240, 240, 240), (200, 210, 220), BG_DIR / "bg_light.png")
    generate_gradient((30, 30, 30), (10, 10, 10), BG_DIR / "bg_dark.png")

    print("✔ Terminé ! Fonds Light/Dark disponibles.\n")


if __name__ == "__main__":
    main()

