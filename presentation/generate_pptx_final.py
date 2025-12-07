from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
import os

OUTPUT_DIR = "presentation"
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(OUTPUT_DIR, "presentation_finale_serveur.pptx")

prs = Presentation()
TITLE_FONT = Pt(38)
TEXT_FONT = Pt(22)

# -----------------------------------------------------
# Helper : ajout slide titre
# -----------------------------------------------------
def add_title_slide(title, subtitle=""):
    slide_layout = prs.slide_layouts[0]  # Title slide
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title
    slide.placeholders[1].text = subtitle


# -----------------------------------------------------
# Helper : slide texte simple
# -----------------------------------------------------
def add_bullet_slide(title, bullets):
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title

    body = slide.placeholders[1].text_frame
    for b in bullets:
        body.add_paragraph().text = b


# -----------------------------------------------------
# SLIDE 1 — Title
# -----------------------------------------------------
add_title_slide(
    "Serveur Haute Performance – TCP & HTTP",
    "Projet Ingénieur – Implémentation complète Multi-thread / Benchmarks"
)

# -----------------------------------------------------
# SLIDE 2 — Plan
# -----------------------------------------------------
add_bullet_slide("Plan de la présentation", [
    "1. Architecture globale du projet",
    "2. Serveur TCP mono-thread – Yassine",
    "3. Serveur HTTP mono-thread – Islem",
    "4. Serveur Multi-thread haute performance – Walid",
    "5. Serveur HTTP Multi-thread – Ghada",
    "6. Benchmarks & Dashboard Python",
    "7. Répartition finale des tâches du groupe"
])

# -----------------------------------------------------
# SLIDES POUR CHAQUE MEMBRE
# -----------------------------------------------------
# Yassine
add_bullet_slide("TCP Mono-thread (Yassine)", [
    "Boucle accept → recv → send",
    "Modèle séquentiel simple",
    "Limites : blocage, faible scalabilité",
    "Utilisé comme baseline pour le benchmark"
])

# Islem
add_bullet_slide("HTTP Mono-thread (Islem)", [
    "Parseur HTTP minimaliste",
    "Routes : / et /hello",
    "Réponses HTML et JSON",
    "Démo du fonctionnement mono-thread"
])

# Walid
add_bullet_slide("Serveur Multi-thread (Walid)", [
    "Thread Pool fixe",
    "Queue FIFO générique thread-safe",
    "Workers permanents",
    "Optimisation haute charge (100–300 clients)"
])

# Ghada
add_bullet_slide("HTTP Multi-thread (Ghada)", [
    "Routage HTTP avancé",
    "JSON / HTML / 404",
    "Amélioration du parsing",
    "Scalabilité et gestion concurrente"
])

# -----------------------------------------------------
# SLIDE UML
# -----------------------------------------------------
add_bullet_slide("Diagramme UML – Architecture serveur", [
    "Classes : Server, Worker, Queue, Client",
    "Relations : Worker → Queue → Server",
    "File FIFO générique comme cœur du système"
])

# -----------------------------------------------------
# SLIDE BENCHMARK
# -----------------------------------------------------
add_bullet_slide("Benchmarks Python – Résultats", [
    "Latence moyenne, médiane, p95, p99",
    "Débit (RPS)",
    "CPU & RAM via psutil",
    "Export JSON / XLSX / Dashboard HTML"
])

# -----------------------------------------------------
# SLIDE RÉPARTITION DU GROUPE
# -----------------------------------------------------
add_bullet_slide("Répartition des tâches", [
    "1️⃣ Walid – Serveur Multi-thread & optimisation",
    "2️⃣ Yassine – Serveur TCP Mono-thread",
    "3️⃣ Islem – HTTP Mono-thread",
    "4️⃣ Ghada – HTTP Multi-thread & routage"
])

# -----------------------------------------------------
# ENREGISTREMENT
# -----------------------------------------------------
prs.save(OUTPUT_FILE)
print(f"✔ PPTX généré : {OUTPUT_FILE}")

