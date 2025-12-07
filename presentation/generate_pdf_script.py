#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    raise SystemExit(
        "❌ Le module reportlab est manquant.\n"
        "   Installe-le dans le venv : pip install reportlab"
    )

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "presentation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PDF_PATH = OUTPUT_DIR / "script_presentation.pdf"


def main() -> None:
    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    sections = [
        ("Introduction",
         "Présentation du projet Serveur Haute Performance (TCP/HTTP, C/POSIX, Python)."),
        ("Architecture globale",
         "Diagramme UML, modules, file FIFO, thread pool, routage HTTP."),
        ("Serveur TCP Mono-thread – Yassine",
         "Boucle accept → recv → traitement → send, limites en scalabilité."),
        ("Serveur HTTP Mono-thread – Islem",
         "Parsing HTTP, routes de base, réponses HTML/JSON."),
        ("Serveur Multi-thread – Walid",
         "Workers permanents, file FIFO bornée, optimisation haute charge."),
        ("Serveur HTTP Multi-thread – Ghada",
         "Routage HTTP concurrent, gestion de plusieurs clients simultanés."),
        ("Benchmarks Python",
         "Latence, débit, CPU/RAM, scripts de génération de graphiques et dashboard."),
        ("Conclusion",
         "Synthèse des résultats et perspectives d’extension (HTTPS, load-balancing, etc.)."),
    ]

    for title, body in sections:
        content.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
        content.append(Spacer(1, 12))
        content.append(Paragraph(body, styles["BodyText"]))
        content.append(Spacer(1, 20))

    doc.build(content)
    print(f"✔ PDF généré : {PDF_PATH}")


if __name__ == "__main__":
    main()

