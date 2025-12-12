#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized results plotting with better performance and caching.
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for better performance
import matplotlib.pyplot as plt
import json
import sys
from pathlib import Path
from typing import Tuple

# Configuration
ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "figures"
OUTPUT.mkdir(exist_ok=True)

# Set matplotlib style for better looking plots
plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'


def log_info(msg: str) -> None:
    """Log info message."""
    print(f"{GREEN}[INFO]{NC} {msg}")


def log_error(msg: str) -> None:
    """Log error message."""
    print(f"{RED}[ERROR]{NC} {msg}", file=sys.stderr)


def load_results() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load results with fallback to JSON if Excel fails."""
    xlsx_path = ROOT / "results.xlsx"
    json_path = ROOT / "results.json"
    
    # Try Excel first
    if xlsx_path.exists():
        try:
            df = pd.read_excel(xlsx_path)
            log_info(f"Résultats chargés depuis {xlsx_path.name}")
        except Exception as e:
            log_error(f"Échec lecture Excel: {e}, essai JSON...")
            df = None
    else:
        df = None
    
    # Fallback to JSON
    if df is None:
        if not json_path.exists():
            raise FileNotFoundError(f"Aucun fichier de résultats trouvé dans {ROOT}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        log_info(f"Résultats chargés depuis {json_path.name}")
    
    # Split by server type
    mono = df[df['server'] == "mono"]
    multi = df[df['server'] == "multi"]
    
    if mono.empty or multi.empty:
        log_error("Données manquantes pour mono ou multi")
        raise ValueError("Données incomplètes")
    
    return mono, multi


def save_figure(name: str) -> None:
    """Save figure in multiple formats with optimization."""
    png_path = OUTPUT / f"{name}.png"
    svg_path = OUTPUT / f"{name}.svg"
    
    plt.tight_layout()
    
    # Save PNG with optimized DPI
    plt.savefig(png_path, dpi=150, bbox_inches='tight')
    
    # Save SVG for vector graphics
    plt.savefig(svg_path, bbox_inches='tight')
    
    plt.close()
    
    log_info(f"✓ Graphique sauvegardé: {name} (PNG + SVG)")


def graph_throughput(mono, multi):
    plt.figure(figsize=(8, 5))
    plt.plot(mono.clients, mono.throughput_rps, marker="o", label="Mono-thread")
    plt.plot(multi.clients, multi.throughput_rps, marker="o", label="Multi-thread")
    plt.xlabel("Clients")
    plt.ylabel("Débit (req/s)")
    plt.title("Débit VS nombre de clients")
    plt.legend()
    save_figure("1-throughput")


def graph_latency_p99(mono, multi):
    plt.figure(figsize=(8, 5))
    plt.plot(mono.clients, mono.p99, marker="o", label="Mono-thread")
    plt.plot(multi.clients, multi.p99, marker="o", label="Multi-thread")
    plt.xlabel("Clients")
    plt.ylabel("Latence P99 (ms)")
    plt.title("Latence P99 VS nombre de clients")
    plt.legend()
    save_figure("2-latency_p99")


def graph_cpu(mono, multi):
    plt.figure(figsize=(8, 5))
    plt.plot(mono.clients, mono.cpu_mean, marker="o", label="Mono-thread")
    plt.plot(multi.clients, multi.cpu_mean, marker="o", label="Multi-thread")
    plt.xlabel("Clients")
    plt.ylabel("CPU moyen (%)")
    plt.title("CPU moyen")
    plt.legend()
    save_figure("3-cpu")


def graph_memory(mono, multi):
    plt.figure(figsize=(8, 5))
    plt.plot(mono.clients, mono.mem_mean, marker="o", label="Mono-thread")
    plt.plot(multi.clients, multi.mem_mean, marker="o", label="Multi-thread")
    plt.xlabel("Clients")
    plt.ylabel("Mémoire (MB)")
    plt.title("Mémoire RSS")
    plt.legend()
    save_figure("4-memory")


def graph_speedup(mono, multi):
    plt.figure(figsize=(8, 5))
    speedup = multi.throughput_rps.values / mono.throughput_rps.values
    plt.plot(mono.clients, speedup, marker="o")
    plt.axhline(1.0)
    plt.xlabel("Clients")
    plt.ylabel("Speedup (multi/mono)")
    plt.title("Speedup multi-thread")
    save_figure("5-speedup")


def graph_saturation(mono, multi):
    plt.figure(figsize=(8, 5))
    plt.plot(mono.clients, mono.cpu_mean, marker="o", linestyle="--", label="Mono-thread")
    plt.plot(multi.clients, multi.cpu_mean, marker="o", linestyle="--", label="Multi-thread")
    plt.xlabel("Clients")
    plt.ylabel("CPU (%)")
    plt.title("Saturation CPU")
    plt.legend()
    save_figure("6-saturation")


def main() -> None:
    """Generate all plots with error handling."""
    import time
    
    log_info("=== Génération des graphiques ===")
    start = time.time()
    
    try:
        mono, multi = load_results()
        log_info(f"Données chargées: {len(mono)} points mono, {len(multi)} points multi")
    except Exception as e:
        log_error(f"Échec du chargement des résultats: {e}")
        sys.exit(1)
    
    # Generate all plots with individual error handling
    plots = [
        ("Débit", graph_throughput),
        ("Latence P99", graph_latency_p99),
        ("CPU", graph_cpu),
        ("Mémoire", graph_memory),
        ("Speedup", graph_speedup),
        ("Saturation", graph_saturation),
    ]
    
    success_count = 0
    for name, func in plots:
        try:
            func(mono, multi)
            success_count += 1
        except Exception as e:
            log_error(f"Échec génération graphique {name}: {e}")
    
    elapsed = time.time() - start
    
    log_info(f"=== Génération terminée en {elapsed:.1f}s ===")
    log_info(f"Graphiques générés: {success_count}/{len(plots)}")
    log_info(f"Répertoire de sortie: {OUTPUT}")
    
    if success_count < len(plots):
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_error("\nInterrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        log_error(f"Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

