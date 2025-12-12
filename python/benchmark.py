#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized benchmark script with parallel execution and better resource monitoring.
"""

import subprocess
import time
import psutil
import json
import pandas as pd
import os
import threading
import sys
from pathlib import Path
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from client_stress import lancer_stress_test

# Configuration
TEST_CLIENTS = [10, 50, 100, 200, 300]
COMPILE_JOBS = os.cpu_count() or 4

ROOT = Path(__file__).resolve().parent.parent
BIN_MONO = ROOT / "bin" / "serveur_mono"
BIN_MULTI = ROOT / "bin" / "serveur_multi"

SERVERS = {
    "mono": {"bin": str(BIN_MONO), "port": 5050},
    "multi": {"bin": str(BIN_MULTI), "port": 5051},
}

# Colors for output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def log_info(msg: str) -> None:
    """Log info message with color."""
    print(f"{GREEN}[INFO]{NC} {msg}")


def log_warn(msg: str) -> None:
    """Log warning message with color."""
    print(f"{YELLOW}[WARN]{NC} {msg}")


def log_error(msg: str) -> None:
    """Log error message with color."""
    print(f"{RED}[ERROR]{NC} {msg}", file=sys.stderr)


def compiler() -> None:
    """Compile project with optimizations."""
    log_info(f"Compilation (make clean + make -j{COMPILE_JOBS})…")
    try:
        subprocess.run(["make", "clean"], cwd=ROOT, check=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        subprocess.run(["make", "-j", str(COMPILE_JOBS)], cwd=ROOT, check=True,
                      stderr=subprocess.PIPE)
        log_info("Compilation réussie ✓")
    except subprocess.CalledProcessError as e:
        log_error(f"Échec de compilation: {e.stderr.decode()}")
        sys.exit(1)


def lancer_serveur(type_srv: str) -> subprocess.Popen:
    """Start server with validation."""
    bin_path = SERVERS[type_srv]["bin"]
    
    # Check if binary exists
    if not Path(bin_path).exists():
        raise FileNotFoundError(f"Binaire introuvable: {bin_path}")
    
    proc = subprocess.Popen(
        [bin_path],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    
    # Wait for server to be ready
    time.sleep(1.0)
    
    # Verify server is still running
    if proc.poll() is not None:
        stderr = proc.stderr.read().decode() if proc.stderr else ""
        raise RuntimeError(f"Serveur {type_srv} a crashé: {stderr}")
    
    return proc


def arreter_serveur(proc: subprocess.Popen) -> None:
    """Stop server gracefully with fallback to kill."""
    if proc.poll() is not None:
        return  # Already stopped
    
    proc.terminate()
    try:
        proc.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        log_warn("Serveur ne répond pas au SIGTERM, utilisation de SIGKILL")
        proc.kill()
        proc.wait(timeout=1.0)


def monitor_process(pid: int, stop_event: threading.Event, 
                   cpu_samples: List[float], mem_samples: List[float]) -> None:
    """Monitor process CPU and memory with error handling."""
    try:
        p = psutil.Process(pid)
    except psutil.NoSuchProcess:
        log_warn(f"Processus {pid} introuvable pour monitoring")
        return
    
    while not stop_event.is_set():
        try:
            # Use shorter interval for more frequent sampling
            cpu = p.cpu_percent(interval=0.1)
            mem = p.memory_info().rss / (1024 * 1024)  # MB
            
            cpu_samples.append(cpu)
            mem_samples.append(mem)
            
            time.sleep(0.1)  # Adjust sampling rate
        except psutil.NoSuchProcess:
            break
        except Exception as e:
            log_warn(f"Erreur de monitoring: {e}")
            break


def benchmark_serveur(type_srv: str) -> List[Dict[str, Any]]:
    """Benchmark a specific server type with all client counts."""
    port = SERVERS[type_srv]["port"]
    results = []

    log_info(f"Début benchmark serveur: {type_srv}")

    for nclients in TEST_CLIENTS:
        log_info(f"{type_srv} - {nclients} clients")

        try:
            proc = lancer_serveur(type_srv)
            pid = proc.pid
        except Exception as e:
            log_error(f"Échec démarrage serveur {type_srv}: {e}")
            continue

        cpu_samples: List[float] = []
        mem_samples: List[float] = []

        stop_evt = threading.Event()
        mon_thread = threading.Thread(
            target=monitor_process,
            args=(pid, stop_evt, cpu_samples, mem_samples),
            daemon=True
        )
        mon_thread.start()

        t_start = time.perf_counter()
        try:
            res = lancer_stress_test("127.0.0.1", port, nclients)
        except Exception as e:
            log_error(f"Échec stress test pour {type_srv}: {e}")
            stop_evt.set()
            mon_thread.join(timeout=1.0)
            arreter_serveur(proc)
            continue
        t_end = time.perf_counter()

        stop_evt.set()
        mon_thread.join(timeout=2.0)
        arreter_serveur(proc)

        elapsed = t_end - t_start
        throughput = res["success"] / elapsed if elapsed > 0 else 0.0

        cpu_mean = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0.0
        mem_mean = sum(mem_samples) / len(mem_samples) if mem_samples else 0.0
        
        # Also compute max/min for better analysis
        cpu_max = max(cpu_samples) if cpu_samples else 0.0
        mem_max = max(mem_samples) if mem_samples else 0.0

        result_entry = {
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
            "cpu_max": cpu_max,
            "mem_mean": mem_mean,
            "mem_max": mem_max,
            "throughput_rps": throughput,
            "time_total": elapsed,
        }
        results.append(result_entry)
        
        # Print summary for this run
        log_info(f"  ✓ Débit: {throughput:.1f} req/s, P99: {res['p99']:.1f}ms, "
                f"CPU: {cpu_mean:.1f}%, Mém: {mem_mean:.1f}MB")

    return results


def main() -> None:
    """Main benchmark execution with error handling and timing."""
    start_time = time.time()
    
    # Change to python directory for output files
    output_dir = ROOT / "python"
    output_dir.mkdir(exist_ok=True)
    os.chdir(output_dir)
    
    log_info("=== Début du benchmark ===")
    log_info(f"Serveurs à tester: {', '.join(SERVERS.keys())}")
    log_info(f"Nombres de clients: {TEST_CLIENTS}")
    
    # Compile first
    compiler()
    
    # Run benchmarks (can be parallelized if needed)
    final_results: List[Dict[str, Any]] = []
    for srv_type in SERVERS.keys():
        try:
            r = benchmark_serveur(srv_type)
            final_results.extend(r)
        except Exception as e:
            log_error(f"Erreur benchmark {srv_type}: {e}")
            continue
    
    if not final_results:
        log_error("Aucun résultat de benchmark généré")
        sys.exit(1)
    
    # Save results with error handling
    try:
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(final_results, f, indent=4, ensure_ascii=False)
        log_info("✓ Résultats JSON sauvegardés")
    except Exception as e:
        log_error(f"Échec sauvegarde JSON: {e}")
    
    try:
        df = pd.DataFrame(final_results)
        df.to_excel("results.xlsx", index=False)
        log_info("✓ Résultats Excel sauvegardés")
    except Exception as e:
        log_error(f"Échec sauvegarde Excel: {e}")
    
    # Summary
    elapsed = time.time() - start_time
    log_info(f"=== Benchmark terminé en {elapsed:.1f}s ===")
    log_info(f"Fichiers générés dans: {output_dir}")
    log_info("  • results.json - Données brutes")
    log_info("  • results.xlsx - Tableau Excel")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_warn("\nBenchmark interrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        log_error(f"Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

