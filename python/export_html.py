#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
export_html.py — Dashboard avancé pour les benchmarks serveur

Fonctionnalités :
  - Lecture des résultats depuis results.json
  - Tableau synthétique des mesures
  - Analyse IA avancée (texte) des performances mono vs multi
  - Comparateur interactif mono vs multi (slider sur le nombre de clients)
  - Affichage des graphiques PNG existants (python/figures/*.png)
  - Mode sombre / clair avec toggle et mémorisation dans localStorage
  - Export automatique d’un rapport PDF (dashboard.pdf) basé sur les résultats

Dépendances Python :
  - json, pathlib, pandas
  - reportlab (optionnel pour le PDF — sinon le script continue sans PDF)
"""

import json
from pathlib import Path

import pandas as pd

# =========================
#  CONSTANTES / CHEMINS
# =========================

ROOT = Path(__file__).resolve().parent          # /home/xpert/server_project/python
PROJECT_ROOT = ROOT.parent                      # /home/xpert/server_project
RESULTS_JSON = ROOT / "results.json"
FIG_DIR = ROOT / "figures"
OUTPUT_HTML = ROOT / "dashboard.html"
OUTPUT_PDF = ROOT / "dashboard.pdf"


# =========================
#  LECTURE DES RÉSULTATS
# =========================

def load_results():
    """Charge les résultats depuis results.json et retourne (data_list, df)."""
    if not RESULTS_JSON.exists():
        raise FileNotFoundError(f"Fichier introuvable : {RESULTS_JSON}")

    with RESULTS_JSON.open("r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    return data, df


def build_table_html(data):
    """Construit le tableau HTML des résultats détaillés."""
    if not data:
        return "<p>Aucune donnée disponible.</p>"

    cols = list(data[0].keys())
    thead = "".join(f"<th>{c}</th>" for c in cols)
    rows = []
    for row in data:
        tr = "".join(f"<td>{row.get(c, '')}</td>" for c in cols)
        rows.append(f"<tr>{tr}</tr>")

    tbody = "\n".join(rows)

    return f"""
    <table class="perf-table">
        <thead><tr>{thead}</tr></thead>
        <tbody>{tbody}</tbody>
    </table>
    """


# =========================
#  ANALYSE IA AVANCÉE
# =========================

def _nearest_row(df, server, clients_target):
    """Retourne la ligne dont le nombre de clients est le plus proche de clients_target."""
    sub = df[df["server"] == server]
    if sub.empty:
        return None
    # Index de la ligne avec distance minimale
    idx = (sub["clients"] - clients_target).abs().idxmin()
    return sub.loc[idx]


def build_analysis_paragraphs(df):
    """
    Génère des paragraphes d'analyse "IA" à partir des statistiques.
    Retourne une liste de paragraphes (texte brut).
    """
    if df.empty:
        return ["Aucune donnée de benchmark disponible pour l'analyse."]

    servers = sorted(df["server"].unique())
    if not {"mono", "multi"}.issubset(set(servers)):
        return [
            "Les résultats ne contiennent pas simultanément les serveurs "
            "« mono » et « multi ». La comparaison complète n'est pas possible."
        ]

    mono = df[df["server"] == "mono"].copy()
    multi = df[df["server"] == "multi"].copy()

    # Nettoyage minimal : on ignore les NaN pour les moyennes
    def safe_mean(series):
        s = series.dropna()
        return float(s.mean()) if len(s) > 0 else None

    mono_th_mean = safe_mean(mono["throughput_rps"])
    multi_th_mean = safe_mean(multi["throughput_rps"])
    mono_p99_mean = safe_mean(mono["p99"])
    multi_p99_mean = safe_mean(multi["p99"])
    mono_cpu_mean = safe_mean(mono.get("cpu_mean", pd.Series(dtype=float)))
    multi_cpu_mean = safe_mean(multi.get("cpu_mean", pd.Series(dtype=float)))
    mono_mem_mean = safe_mean(mono.get("mem_mean", pd.Series(dtype=float)))
    multi_mem_mean = safe_mean(multi.get("mem_mean", pd.Series(dtype=float)))

    max_clients = int(df["clients"].max())
    mono_high = _nearest_row(df, "mono", max_clients)
    multi_high = _nearest_row(df, "multi", max_clients)

    # Speedup moyen
    if mono_th_mean and mono_th_mean > 0:
        speedup_mean = multi_th_mean / mono_th_mean if multi_th_mean else 0.0
    else:
        speedup_mean = 0.0

    paragraphs = []

    # Paragraphe 1 : vue globale
    paragraphs.append(
        "Globalement, les mesures de benchmark montrent que le serveur multi-thread "
        f"offre un débit moyen d’environ {multi_th_mean:.1f} requêtes par seconde, "
        f"contre {mono_th_mean:.1f} req/s pour le serveur mono-thread. "
        f"Sur l’ensemble des configurations testées, cela correspond à un gain moyen "
        f"de performance d’environ {speedup_mean:.2f}× en faveur de l’architecture multi-thread."
    )

    # Paragraphe 2 : latence
    if mono_p99_mean is not None and multi_p99_mean is not None:
        paragraphs.append(
            "En termes de latence, la mesure P99 (latence subie par les 1 % de requêtes les plus lentes) "
            f"reste plus favorable au serveur multi-thread, avec une P99 moyenne de {multi_p99_mean:.1f} ms "
            f"contre {mono_p99_mean:.1f} ms pour le mono-thread. "
            "Cela indique que le multi-thread absorbe mieux les pics de charge et réduit les phénomènes "
            "de saturation lorsque le nombre de clients simultanés augmente."
        )

    # Paragraphe 3 : comportement en forte charge
    if mono_high is not None and multi_high is not None:
        paragraphs.append(
            f"À la charge la plus élevée (≈ {max_clients} clients), on observe un débit "
            f"de {multi_high['throughput_rps']:.1f} req/s pour le serveur multi-thread "
            f"contre {mono_high['throughput_rps']:.1f} req/s pour le mono-thread. "
            f"La latence P99 atteint {mono_high['p99']:.1f} ms côté mono, "
            f"alors qu’elle est de {multi_high['p99']:.1f} ms côté multi, "
            "ce qui confirme que le mono-thread atteint rapidement un plateau de performance "
            "tandis que le multi-thread continue à exploiter les cœurs CPU disponibles."
        )

    # Paragraphe 4 : CPU et mémoire
    if mono_cpu_mean is not None and multi_cpu_mean is not None:
        paragraphs.append(
            "L’analyse de l’utilisation CPU montre que les deux architectures finissent par saturer "
            "les cœurs disponibles, mais le serveur multi-thread parvient à transformer cette "
            f"consommation CPU en débit utile plus élevé (CPU moyen ≈ {multi_cpu_mean:.1f} % "
            f"contre {mono_cpu_mean:.1f} % pour le mono-thread). "
            "La consommation mémoire reste globalement maîtrisée pour les deux serveurs, "
            "avec une légère surconsommation attendue côté multi-thread liée à la gestion des threads "
            "et de la file FIFO."
        )

    # Paragraphe 5 : recommandations
    paragraphs.append(
        "En pratique, l’architecture multi-thread avec file FIFO bornée constitue le meilleur choix "
        "pour un environnement de production soumis à des pics de charge importants, à condition de "
        "maîtriser la complexité de synchronisation et l’arrêt propre des threads. "
        "Le serveur mono-thread conserve néanmoins un intérêt pédagogique fort et peut être adapté "
        "à des scénarios simples ou à faible charge, où la lisibilité du code prime sur la performance brute."
    )

    return paragraphs


def build_analysis_html(paragraphs):
    """Convertit la liste de paragraphes en bloc HTML."""
    html_parts = ['<h2>🧠 Analyse avancée des performances</h2>']
    for p in paragraphs:
        html_parts.append(f"<p>{p}</p>")
    return "\n".join(html_parts)


# =========================
#  EXPORT PDF (optionnel)
# =========================

def export_pdf_report(df, paragraphs):
    """
    Génère un PDF « dashboard.pdf » dans le dossier python/.
    Utilise reportlab si disponible, sinon ignore silencieusement.
    """
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        print("⚠ reportlab non installé : export PDF ignoré.")
        return

    styles = getSampleStyleSheet()
    style_title = styles["Title"]
    style_h2 = styles["Heading2"]
    style_body = styles["BodyText"]

    doc = SimpleDocTemplate(str(OUTPUT_PDF), pagesize=A4)
    elems = []

    # Titre
    elems.append(Paragraph("Dashboard de performances – Serveur TCP/HTTP", style_title))
    elems.append(Spacer(1, 12))

    # Résumé statistique minimal
    if not df.empty:
        servers = ", ".join(sorted(df["server"].unique()))
        clients_min = int(df["clients"].min())
        clients_max = int(df["clients"].max())
        elems.append(Paragraph(
            f"Types de serveurs présents : {servers}. "
            f"Plage de charge testée : de {clients_min} à {clients_max} clients simultanés.",
            style_body
        ))
        elems.append(Spacer(1, 12))

    # Analyse (paragraphes IA)
    elems.append(Paragraph("Analyse avancée", style_h2))
    for p in paragraphs:
        elems.append(Paragraph(p, style_body))
        elems.append(Spacer(1, 8))

    # Figures principales si disponibles
    if FIG_DIR.exists():
        for name in ["1-throughput.png", "2-latency_p99.png",
                     "3-cpu.png", "4-memory.png", "5-speedup.png"]:
            fig_path = FIG_DIR / name
            if fig_path.exists():
                elems.append(Spacer(1, 12))
                elems.append(Paragraph(name.replace(".png", ""), style_h2))
                try:
                    # Largeur raisonnable ; la hauteur est ajustée automatiquement
                    elems.append(Image(str(fig_path), width=400, preserveAspectRatio=True, mask="auto"))
                except Exception:
                    # Si l'image pose problème, on l'ignore
                    pass

    doc.build(elems)
    print(f"✔ Rapport PDF généré : {OUTPUT_PDF}")


# =========================
#  CONSTRUCTION HTML
# =========================

def build_html(data, df, analysis_html):
    """Construit le HTML complet (dashboard) sous forme de chaîne."""
    # Table détaillée
    table_html = build_table_html(data)

    # Stats pour résumé simple
    summary_html = ""
    if not df.empty:
        summary = (
            df.groupby("server")[["throughput_rps", "p99", "cpu_mean", "mem_mean"]]
            .mean(numeric_only=True)
            .rename(columns={
                "throughput_rps": "Débit moyen (req/s)",
                "p99": "Latence P99 moyenne (ms)",
                "cpu_mean": "CPU moyen (%)",
                "mem_mean": "Mémoire moyenne (MB)",
            })
        )
        summary_html = summary.to_html(
            classes="summary-table",
            float_format=lambda x: f"{x:.2f}",
            border=0
        )

    # Données pour le comparateur interactif
    data_json = json.dumps(data, ensure_ascii=False)
    min_clients = int(df["clients"].min()) if not df.empty else 0
    max_clients = int(df["clients"].max()) if not df.empty else 0

    parts = []

    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="fr">')
    parts.append("<head>")
    parts.append('  <meta charset="utf-8">')
    parts.append("  <title>Dashboard – Serveur Haute Performance</title>")
    parts.append("  <style>")
    # Thème (variables CSS)
    parts.append("  :root {")
    parts.append("    --bg-color: #fafafa;")
    parts.append("    --text-color: #111111;")
    parts.append("    --card-bg: #ffffff;")
    parts.append("    --accent: #0d47a1;")
    parts.append("    --accent-soft: #e3f2fd;")
    parts.append("    --border-color: #cccccc;")
    parts.append("  }")
    parts.append("  body[data-theme=\"dark\"] {")
    parts.append("    --bg-color: #0b1020;")
    parts.append("    --text-color: #f5f5f5;")
    parts.append("    --card-bg: #161b2e;")
    parts.append("    --accent: #90caf9;")
    parts.append("    --accent-soft: #1e2746;")
    parts.append("    --border-color: #394264;")
    parts.append("  }")
    parts.append("  body {")
    parts.append("    font-family: Arial, sans-serif;")
    parts.append("    margin: 2rem;")
    parts.append("    background: var(--bg-color);")
    parts.append("    color: var(--text-color);")
    parts.append("  }")
    parts.append("  h1 { color: var(--accent); }")
    parts.append("  h2 { color: var(--accent); }")
    parts.append("  .card {")
    parts.append("    background: var(--card-bg);")
    parts.append("    border-radius: 8px;")
    parts.append("    box-shadow: 0 2px 6px rgba(0,0,0,0.08);")
    parts.append("    padding: 1.5rem;")
    parts.append("    margin-bottom: 1.5rem;")
    parts.append("    border: 1px solid var(--border-color);")
    parts.append("  }")
    parts.append("  .perf-table, .summary-table, .compare-table {")
    parts.append("    border-collapse: collapse;")
    parts.append("    width: 100%;")
    parts.append("    margin-top: 1rem;")
    parts.append("    font-size: 0.9rem;")
    parts.append("  }")
    parts.append("  .perf-table th, .summary-table th, .compare-table th {")
    parts.append("    background: var(--accent-soft);")
    parts.append("    padding: 8px;")
    parts.append("    border: 1px solid var(--border-color);")
    parts.append("    text-align: center;")
    parts.append("  }")
    parts.append("  .perf-table td, .summary-table td, .compare-table td {")
    parts.append("    padding: 6px;")
    parts.append("    border: 1px solid var(--border-color);")
    parts.append("    text-align: center;")
    parts.append("  }")
    parts.append("  img {")
    parts.append("    max-width: 650px;")
    parts.append("    border: 1px solid var(--border-color);")
    parts.append("    background: var(--card-bg);")
    parts.append("    padding: 4px;")
    parts.append("    margin: 8px;")
    parts.append("  }")
    parts.append("  .toolbar {")
    parts.append("    display: flex;")
    parts.append("    justify-content: space-between;")
    parts.append("    align-items: center;")
    parts.append("    margin-bottom: 1rem;")
    parts.append("  }")
    parts.append("  .btn {")
    parts.append("    border-radius: 4px;")
    parts.append("    border: 1px solid var(--border-color);")
    parts.append("    background: var(--accent-soft);")
    parts.append("    color: var(--accent);")
    parts.append("    padding: 0.4rem 0.8rem;")
    parts.append("    cursor: pointer;")
    parts.append("    font-size: 0.9rem;")
    parts.append("  }")
    parts.append("  .btn:hover {")
    parts.append("    filter: brightness(1.05);")
    parts.append("  }")
    parts.append("  .slider-row {")
    parts.append("    display: flex;")
    parts.append("    align-items: center;")
    parts.append("    gap: 1rem;")
    parts.append("    margin-top: 0.5rem;")
    parts.append("  }")
    parts.append("  .slider-row input[type=\"range\"] {")
    parts.append("    flex: 1;")
    parts.append("  }")
    parts.append("  </style>")
    parts.append("</head>")
    parts.append('<body data-theme="light">')

    # Barre outils (titre + boutons)
    parts.append('<div class="toolbar">')
    parts.append('  <h1>Dashboard – Serveur Haute Performance</h1>')
    parts.append('  <div>')
    parts.append('    <button id="themeToggle" class="btn">Basculer mode sombre</button>')
    parts.append("  </div>")
    parts.append("</div>")

    # Résumé
    parts.append('<div class="card">')
    parts.append("<h2>Résumé statistique</h2>")
    if summary_html:
        parts.append(summary_html)
    else:
        parts.append("<p>Aucun résumé disponible (pas de données).</p>")
    parts.append("</div>")

    # Analyse IA
    parts.append('<div class="card">')
    parts.append(analysis_html)
    parts.append("</div>")

    # Comparateur interactif
    parts.append('<div class="card">')
    parts.append("<h2>⚖ Comparateur interactif Mono vs Multi</h2>")
    if min_clients < max_clients:
        parts.append("<p>"
                     "Choisis un nombre de clients pour comparer les métriques "
                     "entre le serveur mono-thread et le multi-thread. "
                     "Le point de mesure le plus proche sera utilisé pour chaque serveur."
                     "</p>")
        parts.append('<div class="slider-row">')
        parts.append(f'  <label for="clientSlider">Nombre de clients :</label>')
        parts.append(
            f'  <input type="range" id="clientSlider" '
            f'min="{min_clients}" max="{max_clients}" step="1" value="{min_clients}">'
        )
        parts.append('  <span id="clientValue"></span>')
        parts.append("</div>")
        parts.append('<div id="compareOutput" style="margin-top:1rem;"></div>')
    else:
        parts.append("<p>Données insuffisantes pour activer le comparateur interactif.</p>")
    parts.append("</div>")

    # Graphiques existants
    parts.append('<div class="card">')
    parts.append("<h2>📈 Graphiques de performance</h2>")
    if FIG_DIR.exists():
        pngs = sorted(FIG_DIR.glob("*.png"))
        if pngs:
            for fig in pngs:
                parts.append(f'<div><img src="figures/{fig.name}" alt="{fig.name}"></div>')
        else:
            parts.append("<p>Aucun fichier PNG trouvé dans python/figures/.</p>")
    else:
        parts.append("<p>Le dossier python/figures/ n'existe pas encore. "
                     "Lance d’abord plot_results.py ou le pipeline complet.</p>")
    parts.append("</div>")

    # Script JS
    parts.append("<script>")
    parts.append(f"const DATA = {data_json};")
    parts.append(f"const MIN_CLIENTS = {min_clients};")
    parts.append(f"const MAX_CLIENTS = {max_clients};")

    parts.append("""
function getNearestRow(clients, server) {
  const filtered = DATA.filter(r => r.server === server);
  if (filtered.length === 0) return null;
  let best = filtered[0];
  let bestDiff = Math.abs(filtered[0].clients - clients);
  for (let i = 1; i < filtered.length; i++) {
    const d = Math.abs(filtered[i].clients - clients);
    if (d < bestDiff) {
      bestDiff = d;
      best = filtered[i];
    }
  }
  return best;
}

function updateCompare() {
  const slider = document.getElementById("clientSlider");
  const valueSpan = document.getElementById("clientValue");
  const out = document.getElementById("compareOutput");
  if (!slider || !out || !valueSpan) return;

  const clients = parseInt(slider.value);
  valueSpan.textContent = clients;

  const mono = getNearestRow(clients, "mono");
  const multi = getNearestRow(clients, "multi");

  if (!mono || !multi) {
    out.innerHTML = "<p>Données insuffisantes pour cette configuration.</p>";
    return;
  }

  const thMono = mono.throughput_rps || 0.0;
  const thMulti = multi.throughput_rps || 0.0;
  const p99Mono = mono.p99 || 0.0;
  const p99Multi = multi.p99 || 0.0;
  const cpuMono = (mono.cpu_mean === null || mono.cpu_mean === undefined) ? 0.0 : mono.cpu_mean;
  const cpuMulti = (multi.cpu_mean === null || multi.cpu_mean === undefined) ? 0.0 : multi.cpu_mean;
  const memMono = (mono.mem_mean === null || mono.mem_mean === undefined) ? 0.0 : mono.mem_mean;
  const memMulti = (multi.mem_mean === null || multi.mem_mean === undefined) ? 0.0 : multi.mem_mean;

  const speedup = thMono > 0 ? (thMulti / thMono) : 0.0;

  out.innerHTML =
    '<table class="compare-table">' +
      '<thead><tr>' +
        '<th>Métrique</th>' +
        '<th>Mono-thread</th>' +
        '<th>Multi-thread</th>' +
      '</tr></thead>' +
      '<tbody>' +
        '<tr><td>Clients (point le plus proche)</td>' +
          '<td>' + mono.clients + '</td>' +
          '<td>' + multi.clients + '</td></tr>' +
        '<tr><td>Débit (req/s)</td>' +
          '<td>' + thMono.toFixed(1) + '</td>' +
          '<td>' + thMulti.toFixed(1) + '</td></tr>' +
        '<tr><td>Latence P99 (ms)</td>' +
          '<td>' + p99Mono.toFixed(1) + '</td>' +
          '<td>' + p99Multi.toFixed(1) + '</td></tr>' +
        '<tr><td>CPU moyen (%)</td>' +
          '<td>' + cpuMono.toFixed(1) + '</td>' +
          '<td>' + cpuMulti.toFixed(1) + '</td></tr>' +
        '<tr><td>Mémoire moyenne (MB)</td>' +
          '<td>' + memMono.toFixed(1) + '</td>' +
          '<td>' + memMulti.toFixed(1) + '</td></tr>' +
        '<tr><td>Speedup multi / mono (débit)</td>' +
          '<td colspan="2">' + speedup.toFixed(2) + '×</td></tr>' +
      '</tbody>' +
    '</table>';
}

function initTheme() {
  const saved = window.localStorage.getItem("dashboardTheme");
  const body = document.body;
  if (saved === "dark") {
    body.setAttribute("data-theme", "dark");
  } else {
    body.setAttribute("data-theme", "light");
  }
}

function toggleTheme() {
  const body = document.body;
  const current = body.getAttribute("data-theme") || "light";
  const next = (current === "light") ? "dark" : "light";
  body.setAttribute("data-theme", next);
  window.localStorage.setItem("dashboardTheme", next);
}

document.addEventListener("DOMContentLoaded", function () {
  initTheme();
  const slider = document.getElementById("clientSlider");
  if (slider) {
    slider.addEventListener("input", updateCompare);
    updateCompare();
  }
  const btn = document.getElementById("themeToggle");
  if (btn) {
    btn.addEventListener("click", toggleTheme);
  }
});
""")

    parts.append("</script>")
    parts.append("</body>")
    parts.append("</html>")

    return "\n".join(parts)


# =========================
#  MAIN
# =========================

def main():
    data, df = load_results()
    paragraphs = build_analysis_paragraphs(df)
    analysis_html = build_analysis_html(paragraphs)

    html = build_html(data, df, analysis_html)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"✔ Dashboard HTML généré : {OUTPUT_HTML}")

    # Export PDF du dashboard (rapport synthétique)
    export_pdf_report(df, paragraphs)


if __name__ == "__main__":
    main()

