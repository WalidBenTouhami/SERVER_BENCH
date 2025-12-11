#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Génère une cheat-sheet PDF du pipeline DevOps et des commandes essentielles.
Utilise reportlab.
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path


def main():
    ROOT = Path(__file__).resolve().parent.parent
    OUTDIR = ROOT / "docs"
    OUTDIR.mkdir(exist_ok=True)

    pdf_path = OUTDIR / "cheatsheet.pdf"

    styles = getSampleStyleSheet()
    title = styles["Title"]
    text = styles["BodyText"]

    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    content = []

    # ================================
    # TITRE PRINCIPAL
    # ================================
    content.append(Paragraph("Cheat-Sheet — Serveurs TCP/HTTP & Pipeline DevOps", title))
    content.append(Spacer(1, 20))

    # ================================
    # PIPELINE D’EXÉCUTION
    # ================================
    content.append(Paragraph("<b>Pipeline d’exécution</b>", title))
    content.append(Spacer(1, 12))

    pipeline = """
    1. Activer l’environnement Python :
       source venv/bin/activate

    2. Générer les fichiers HTTP :
       python3 create_http_files.py

    3. Compilation optimisée :
       make clean
       make -j$(nproc)

    4. Démarrage de tous les serveurs :
       ./scripts/start_all.sh
    """

    content.append(Paragraph(pipeline.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;"), text))
    content.append(Spacer(1, 20))

    # ================================
    # COMMANDES CLÉS
    # ================================
    content.append(Paragraph("<b>Commandes clés</b>", title))
    content.append(Spacer(1, 12))

    commands = """
    make clean               — nettoyage complet
    make -j$(nproc)          — compilation rapide
    make debug               — compilation avec sanitizers
    make test                — tests automatiques
    make kill_servers        — arrêt propre des serveurs
    """

    content.append(Paragraph(commands.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;"), text))
    content.append(Spacer(1, 20))

    # ================================
    # DEBUG / QUALITÉ
    # ================================
    content.append(Paragraph("<b>Debug & Analyse</b>", title))
    content.append(Spacer(1, 12))

    debug = """
    Valgrind (memory) :
       valgrind --leak-check=full ./bin/serveur_multi

    Valgrind (threads) :
       valgrind --tool=helgrind ./bin/serveur_multi

    Sanitizers GCC :
       make debug
    """

    content.append(Paragraph(debug.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;"), text))
    content.append(Spacer(1, 20))

    # ================================
    # BENCHMARKS
    # ================================
    content.append(Paragraph("<b>Benchmarks & Stress Tests</b>", title))
    content.append(Spacer(1, 12))

    bench = """
    Stress TCP mono-thread :
       python3 python/client_stress_tcp.py --port 5050 --clients 200

    Stress TCP multi-thread :
       python3 python/client_stress_tcp.py --port 5051 --clients 200

    Stress HTTP (mono/multi) :
       python3 python/client_stress_http.py --port 8080 --clients 200
       python3 python/client_stress_http.py --port 8081 --clients 200

    Benchmarks extrêmes :
       make benchmark_extreme
    """

    content.append(Paragraph(bench.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;"), text))
    content.append(Spacer(1, 20))

    # ================================
    # CI/CD
    # ================================
    content.append(Paragraph("<b>CI/CD – GitHub Actions</b>", title))
    content.append(Spacer(1, 12))

    cicd = """
    • build.yml        : build + tests + valgrind
    • cppcheck.yml     : analyse statique
    • codeql.yml       : sécurité
    • benchmarks.yml   : bench + badge throughput
    • deploy_docs.yml  : GitHub Pages
    """

    content.append(Paragraph(cicd.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;"), text))

    # ================================
    # EXPORT
    # ================================
    doc.build(content)
    print(f"✔ Cheat-sheet générée : {pdf_path}")


if __name__ == "__main__":
    main()

