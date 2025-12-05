#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Benchmark TCP mono-thread vs multi-thread
Optimisé — Auto-détection du projet — Robuste — Monitoring CPU/RAM
"""

import subprocess
import time
import psutil
import json
import pandas as pd
import os
import threading
from client_stress import lancer_stress_test


# ============================================================
# AUTO-DÉTECTION DU PROJET
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BIN_DIR = os.path.join(PROJECT_ROOT, "bin")
FIG_DIR = os.path.join(PROJECT_ROOT, "python", "figures")

# Listes des serveurs
SERVERS = {
    "mono": {
        "bin": os.path.join(BIN_DIR, "serveur_mono"),
        "port": 5050
    },
    "multi": {
        "bin": os.path.join(BIN_DIR, "serveur_multi"),
        "port": 5051
    },
}

TEST_CLIENTS = [10, 50, 100, 200, 300]


# ============================================================
# COMPILATION
# ============================================================

def compiler():
    """Compile le projet C via Makefile."""
    print("[BENCH] Compilation…")
    subprocess.run(["make", "clean"], cwd=PROJECT_ROOT, check=True)
    subprocess.run(["make", "all"], cwd=PROJECT_ROOT, check=True)


# ============================================================
# LANCEMENT SERVEUR
# ============================================================

def lancer_serveur(type_srv: str) -> subprocess.Popen:
    """Lance un serveur mono ou multi via binaire absolu."""
    bin_path = SERVERS[type_srv]["bin"]

    if not os.path.isfile(bin_path):
        raise FileNotFoundError(f"❌ Binaire introuvable : {bin_path}")

    print(f"[BENCH] Lancement {type_srv} : {bin_path}")

    proc = subprocess.Popen(
        [bin_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=PROJECT_ROOT
    )

    time.sleep(1.0)
    return proc


def arreter_serveur(proc: subprocess.Popen):
    """Arrêt propre d’un serveur."""
    proc.terminate()
    try:
        proc.wait(timeout=2.0)
    except subprocess.TimeoutExpired:
        proc.kill()


# ============================================================
# MONITORING CPU / RAM
# ============================================================

def monitor_process(pid: int, stop_event: threading.Event, cpu_samples, mem_samples):
    """Mesure CPU/RAM du process serveur pendant le benchmark."""
    try:
        p = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return

    while not stop_event.is_set():
        try:
            cpu = p.cpu_percent(interval=0.2)
            mem = p.memory_info().rss / (1024 * 1024)
            cpu_samples.append(cpu)
            mem_samples.append(mem)
        except psutil.NoSuchProcess:
            break


# ============================================================
# BENCHMARK SERVEUR
# ============================================================

def benchmark_serveur(type_srv: str):
    port = SERVERS[type_srv]["port"]
    results = []

    for nclients in TEST_CLIENTS:
        print(f"\n[BENCH] → {type_srv.upper()} — {nclients} clients")

        proc = lancer_serveur(type_srv)
        pid = proc.pid

        # Monitoring CPU / RAM
        cpu_samples, mem_samples = [], []
        stop_evt = threading.Event()
        mon_thread = threading.Thread(
            target=monitor_process,
            args=(pid, stop_evt, cpu_samples, mem_samples)
        )
        mon_thread.start()

        t_start = time.perf_counter()
        res = lancer_stress_test("127.0.0.1", port, nclients)
        t_end = time.perf_counter()

        # Arrêt du serveur + monitoring
        stop_evt.set()
        mon_thread.join()
        arreter_serveur(proc)

        elapsed = t_end - t_start
        throughput = res["success"] / elapsed if elapsed > 0 else 0.0

        cpu_mean = sum(cpu_samples) / len(cpu_samples) if cpu_samples else None
        mem_mean = sum(mem_samples) / len(mem_samples) if mem_samples else None

        results.append({
            "server": type_srv,
            "clients": nclients,
            "success": res["success"],
            "fail": res["fail"],
            "mean": res["mean"],
            "median": res["median"],
            "p95": res["p95"],
            "p99": res["p99"],
            "max_latency": res["max"],
            "cpu_mean": cpu_mean,
            "mem_mean": mem_mean,
            "throughput_rps": throughput,
            "time_total": elapsed,
        })

        print(f"[OK] {type_srv} — {nclients} clients — "
              f"Débit {throughput:.1f} req/s — CPU {cpu_mean:.1f}% — RAM {mem_mean:.1f} MB")

    return results


# ============================================================
# MAIN
# ============================================================

def main():
    compiler()

    final_results = []
    for srv_type in SERVERS.keys():
        final_results.extend(benchmark_serveur(srv_type))

    # Export résultats
    json_path = os.path.join(PROJECT_ROOT, "python", "results.json")
    xlsx_path = os.path.join(PROJECT_ROOT, "python", "results.xlsx")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4, ensure_ascii=False)

    df = pd.DataFrame(final_results)
    df.to_excel(xlsx_path, index=False)

    print(f"\n[BENCH] Résultats écrits dans :\n→ {json_path}\n→ {xlsx_path}")


if __name__ == "__main__":
    main()

