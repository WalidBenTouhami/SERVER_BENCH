#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===============================================================
   generate_pdf_script.py – VERSION ULTRA PRO / EXTREME DEVOPS
===============================================================

Fonctionnalités :

1️⃣ Génération d’un PDF textuel (script / résumé) via reportlab  
2️⃣ Export automatique du PowerPoint → PDF via LibreOffice headless  
3️⃣ Choix automatique : 
      - si le PPTX existe → conversion PowerPoint -> PDF
      - sinon → création du PDF textuel fallback

4️⃣ Messages détaillés, erreurs gérées, idempotence.

Dépendances :
    pip install reportlab
    sudo apt install libreoffice (ou libreoffice-core)
"""

import subprocess
import shutil
from pathlib import Path

# -------------------------------------------------------------------
# Chemins
# -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent       # /server_project
PRESENTATION_DIR = ROOT / "presentation/presentation"
PPTX = PRESENTATION_DIR / "presentation_finale_serveur.pptx"
SCRIPT_PDF = PRESENTATION_DIR / "script_presentation.pdf"
TEXT_PDF = PRESENTATION_DIR / "script_textuel.pdf"

# -------------------------------------------------------------------
# 1️⃣ Fonction : Génération PDF textuel (fallback ou complément)
# -------------------------------------------------------------------
def generate_textual_pdf():
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        print("❌ Module reportlab manquant. Installe-le : pip install reportlab")
        return False

    print("📝 Génération PDF TEXTUEL (reportlab)…")

    doc = SimpleDocTemplate(str(TEXT_PDF), pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    SECTIONS = [
        ("Introduction",
         "Présentation du projet Serveur Haute Performance (TCP/HTTP, C/POSIX, Python)."),
        ("Architecture globale",
         "Modules, file FIFO, thread pool, routage HTTP, séquences mono/multi-thread."),
        ("Serveur TCP Mono-thread",
         "Boucle accept → recv → traitement → send."),
        ("Serveur HTTP Mono-thread",
         "Parsing HTTP, routage statique, réponses HTML/JSON."),
        ("Serveur Multi-thread",
         "Workers, file FIFO bornée, contention réduite, arrêt propre."),
        ("Serveur HTTP Multi-thread",
         "Gestion concurrente HTTP 1.1, statistiques globales."),
        ("Benchmarks Python",
         "Latence, throughput, CPU, RAM, dashboard Plotly."),
        ("Conclusion",
         "Améliorations possibles : HTTPS, keep-alive, load-balancing."),
    ]

    for title, body in SECTIONS:
        content.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
        content.append(Spacer(1, 14))
        content.append(Paragraph(body, styles["BodyText"]))
        content.append(Spacer(1, 20))

    doc.build(content)
    print(f"✔ PDF textuel généré : {TEXT_PDF}")
    return True


# -------------------------------------------------------------------
# 2️⃣ Fonction : Conversion PowerPoint → PDF via LibreOffice
# -------------------------------------------------------------------
def convert_pptx_to_pdf():
    if not PPTX.exists():
        print("❌ Fichier PPTX introuvable :")
        print(f"   {PPTX}")
        print("   → Exécute d'abord generate_pptx_final.py.")
        return False

    # Vérifier la disponibilité de LibreOffice
    libreoffice = shutil.which("libreoffice") or shutil.which("soffice")
    if not libreoffice:
        print("⚠️ LibreOffice introuvable → PDF textuel seulement.")
        return False

    print("📄 Conversion du PowerPoint → PDF via LibreOffice headless…")

    cmd = [
        libreoffice,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(PRESENTATION_DIR),
        str(PPTX),
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"✔ PDF PPTX généré : {SCRIPT_PDF}")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Erreur LibreOffice :", e)
        return False


# -------------------------------------------------------------------
# 3️⃣ Exécution générale
# -------------------------------------------------------------------
def main():
    print("=== EXPORT PDF – MODE AUTO ===")

    # 1. Essayer d'abord d’exporter le PPTX en PDF
    if convert_pptx_to_pdf():
        print("🌟 Export PPTX→PDF réussi.")
        return

    # 2. Sinon fallback → PDF textuel
    print("➡️  Mode fallback : génération d’un PDF textuel…")
    if generate_textual_pdf():
        print("✔ Fallback PDF généré.")
    else:
        print("❌ Échec total : aucun PDF généré.")


if __name__ == "__main__":
    main()

