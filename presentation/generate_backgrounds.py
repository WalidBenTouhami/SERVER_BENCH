from PIL import Image, ImageDraw
import os

OUTPUT_DIR = "presentation/backgrounds"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def gen_background(color, name):
    img = Image.new("RGB", (1920, 1080), color)
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Serveur Haute Performance", fill=(255,255,255))
    img.save(os.path.join(OUTPUT_DIR, name))

gen_background((10, 30, 60), "background_blue_engineer.png")
gen_background((20, 20, 20), "background_dark_tech.png")
gen_background((230, 230, 230), "background_white_clean.png")

print("✔ Backgrounds générés dans presentation/backgrounds/")

