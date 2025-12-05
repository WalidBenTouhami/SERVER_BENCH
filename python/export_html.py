#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.io as pio

BASE_DIR = Path(__file__).resolve().parent

RESULTS_JSON = BASE_DIR / "results.json"
OUTPUT_HTML = BASE_DIR / "dashboard.html"


def load_results():
    if not RESULTS_JSON.exists():
        raise FileNotFoundError(f"❌ Fichier introuvable : {RESULTS_JSON}")

    data = json.loads(RESULTS_JSON.read_text())
    return pd.DataFrame(data)


def generate_dashboard(df: pd.DataFrame):
    html_parts = []

    # ======== TITRE ========
    html_parts.append("""
    <h1 style="font-family:Arial; text-align:center;">Dashboard Benchmark</h1>
    <hr>
    """)

    # ======== TABLEAU ========
    html_parts.append("<h2>Tableau des résultats</h2>")
    html_parts.append(df.to_html(index=False, classes="table table-striped"))

    # ======== PLOT : Débit ========
    fig1 = px.line(df, x="clients", y="throughput_rps", color="server",
                   title="Débit (req/s) selon la charge")
    fig1_html = pio.to_html(fig1, include_plotlyjs="cdn", full_html=False)
    html_parts.append("<h2>Débit</h2>" + fig1_html)

    # ======== PLOT : Latence P99 ========
    fig2 = px.line(df, x="clients", y="p99", color="server",
                   title="Latence P99 (ms)")
    fig2_html = pio.to_html(fig2, include_plotlyjs="cdn", full_html=False)
    html_parts.append("<h2>Latence P99</h2>" + fig2_html)

    # ======== PLOT : CPU ========
    fig3 = px.line(df, x="clients", y="cpu_mean", color="server",
                   title="CPU moyen (%)")
    fig3_html = pio.to_html(fig3, include_plotlyjs="cdn", full_html=False)
    html_parts.append("<h2>CPU moyen</h2>" + fig3_html)

    # Générer la page HTML complète
    OUTPUT_HTML.write_text("\n".join(html_parts), encoding="utf-8")
    print(f"\n✔ Dashboard généré : {OUTPUT_HTML}\n")


def main():
    df = load_results()
    generate_dashboard(df)


if __name__ == "__main__":
    main()

