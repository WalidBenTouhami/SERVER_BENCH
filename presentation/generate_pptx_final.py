#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

try:
    from pptx import Presentation
except ImportError:
    raise SystemExit(
        "❌ Le module python-pptx est manquant.\n"
        "   Installe-le dans le venv : pip install python-pptx"
    )

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "presentation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "presentation_finale_serveur.pptx"


def add_title_slide(prs: Presentation, title: str, subtitle: str = ""):
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title
    if subtitle:
        slide.placeholders[1].text = subtitle


def add_bullet_slide(prs: Presentation, title: str, bullets):
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title
    body = slide.placeholders[1].text_frame
    body.clear()
    for b in bullets:
        p = body.add_paragraph()
        p.text = b
        p.level = 0


def main() -> None:
    prs = Presentation()

    # Slide 1 — Titre
    add_title_slide(
        prs,
        "Serveur Haute Performance – TCP & HTTP",
        "Projet Ingénieur – Multi-threading, Queue FIFO, Benchmarks Python"
    )

    # Slide 2 — Plan
    add_bullet_slide(prs, "Plan de la présentation", [
        "1. Architecture globale du projet",
        "2. Serveur TCP mono-thread – Yassine",
        "3. Serveur HTTP mono-thread – Islem",
        "4. Serveur TCP Multi-thread – Walid",
        "5. Serveur HTTP Multi-thread – Ghada",
        "6. Benchmarks & Dashboard",
        "7. Répartition des tâches et conclusion",
    ])

    # Yassine
    add_bullet_slide(prs, "TCP Mono-thread (Yassine)", [
        "Boucle accept → recv → traitement → send.",
        "Modèle séquentiel simple et pédagogique.",
        "Faible scalabilité sous forte charge.",
        "Référence de base pour la comparaison de performance.",
    ])

    # Islem
    add_bullet_slide(prs, "HTTP Mono-thread (Islem)", [
        "Serveur HTTP minimaliste basé sur sockets TCP.",
        "Parsing de la ligne de requête (méthode, chemin, query).",
        "Routes simples : / et /hello.",
        "Réponses HTML et JSON, HTTP/1.1.",
    ])

    # Walid
    add_bullet_slide(prs, "TCP Multi-thread (Walid)", [
        "Thread pool fixe de workers.",
        "File FIFO générique thread-safe (queue.c).",
        "Traitement concurrent de nombreuses connexions.",
        "Optimisation de la latence et du débit (req/s).",
    ])

    # Ghada
    add_bullet_slide(prs, "HTTP Multi-thread (Ghada)", [
        "Serveur HTTP concurrent basé sur la queue FIFO.",
        "Routing simple : /, /hello, gestion 404.",
        "Meilleure scalabilité pour de nombreux clients HTTP.",
        "Intégration avec le reste de l’architecture C.",
    ])

    # UML
    add_bullet_slide(prs, "Diagramme UML – Architecture", [
        "Composants principaux : Server, Worker, Queue, Client.",
        "Séparation accept (dispatcher) / traitement (workers).",
        "Queue FIFO comme cœur de la synchronisation.",
    ])

    # Benchmarks
    add_bullet_slide(prs, "Benchmarks Python – Résultats", [
        "Client de stress multi-thread (ThreadPoolExecutor).",
        "Mesures : latence moyenne, médiane, P95, P99.",
        "Débit (requêtes/seconde), CPU et mémoire via psutil.",
        "Export JSON/XLSX + figures PNG/SVG + dashboard HTML.",
    ])

    # Répartition
    add_bullet_slide(prs, "Répartition des tâches", [
        "Walid – Serveur Multi-thread TCP + Benchmarks + DevOps.",
        "Yassine – Serveur TCP Mono-thread.",
        "Islem – Serveur HTTP Mono-thread.",
        "Ghada – Serveur HTTP Multi-thread + routage.",
    ])

    prs.save(str(OUTPUT_FILE))
    print(f"✔ PPTX généré : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

