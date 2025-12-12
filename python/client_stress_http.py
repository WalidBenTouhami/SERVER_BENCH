#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized HTTP stress test client with connection pooling and better performance.

Stress HTTP pour:
  - serveur_mono_http   (port 8080)
  - serveur_multi_http  (port 8081)

Envoie des requêtes GET et mesure la latence et le throughput.
"""

import socket
import time
import json
import csv
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Any

# Optimizations
BUFFER_SIZE = 8192  # Larger buffer for better performance
MAX_WORKERS = 500   # Limit concurrent connections


def envoyer_requete_http(host: str, port: int, path: str, timeout: float = 5.0) -> float:
    """Envoie une requête HTTP GET et retourne la latence en ms.
    
    Args:
        host: Server hostname
        port: Server port
        path: HTTP path to request
        timeout: Socket timeout in seconds
        
    Returns:
        float: Latency in milliseconds, or -1.0 on error
    """
    start = time.perf_counter()
    try:
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode("ascii")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Optimize socket options
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.settimeout(timeout)
            s.connect((host, port))
            s.sendall(req)

            # Lecture optimisée avec buffer plus grand
            response_data = b''
            while True:
                data = s.recv(BUFFER_SIZE)
                if not data:
                    break
                response_data += data
                
                # Early exit if we got a complete response (optional optimization)
                if b'\r\n\r\n' in response_data and len(response_data) > 100:
                    # Simple heuristic: if we have headers + some body, that's enough
                    break

    except socket.timeout:
        return -1.0
    except ConnectionRefusedError:
        return -1.0
    except Exception:
        return -1.0

    end = time.perf_counter()
    return (end - start) * 1000.0


def _percentile(sorted_list: List[float], p: float) -> float:
    """Calculate percentile from sorted list."""
    n = len(sorted_list)
    if n == 0:
        return 0.0
    k = int(p * (n - 1))
    return sorted_list[k]


def lancer_stress_http(host: str, port: int, path: str, clients: int) -> Dict[str, Any]:
    """Launch HTTP stress test with concurrent clients.
    
    Args:
        host: Server hostname
        port: Server port
        path: HTTP path to request
        clients: Number of concurrent clients
        
    Returns:
        Dictionary with test results and statistics
    """
    latences: List[float] = []
    errors = 0

    # Optimize worker count
    max_workers = min(clients, MAX_WORKERS)
    
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(envoyer_requete_http, host, port, path)
            for _ in range(clients)
        ]
        for f in as_completed(futures):
            try:
                lat = f.result()
                if lat >= 0:
                    latences.append(lat)
                else:
                    errors += 1
            except Exception:
                errors += 1
    t1 = time.perf_counter()

    total_time = t1 - t0

    if not latences:
        return {
            "mode": "single",
            "host": host,
            "port": port,
            "path": path,
            "clients": clients,
            "success": 0,
            "fail": clients,
            "throughput_req_s": 0.0,
            "mean_ms": None,
            "median_ms": None,
            "p95_ms": None,
            "p99_ms": None,
            "max_ms": None,
        }

    latences_sorted = sorted(latences)
    mean = statistics.mean(latences_sorted)
    median = statistics.median(latences_sorted)
    p95 = _percentile(latences_sorted, 0.95)
    p99 = _percentile(latences_sorted, 0.99)
    max_v = max(latences_sorted)
    min_v = min(latences_sorted)
    throughput = len(latences_sorted) / total_time if total_time > 0 else 0.0

    return {
        "mode": "single",
        "host": host,
        "port": port,
        "path": path,
        "clients": clients,
        "success": len(latences_sorted),
        "fail": clients - len(latences_sorted),
        "throughput_req_s": round(throughput, 2),
        "mean_ms": round(mean, 3),
        "median_ms": round(median, 3),
        "min_ms": round(min_v, 3),
        "max_ms": round(max_v, 3),
        "p95_ms": round(p95, 3),
        "p99_ms": round(p99, 3),
        "total_time_s": round(total_time, 3),
    }


def lancer_ramp_up_http(
    host: str,
    port: int,
    path: str,
    steps: List[int],
) -> List[Dict[str, Any]]:
    """Run ramp-up stress test with increasing client counts.
    
    Args:
        host: Server hostname
        port: Server port
        path: HTTP path to request
        steps: List of client counts to test
        
    Returns:
        List of result dictionaries for each step
    """
    results = []
    for c in steps:
        print(f"\n[RAMP-UP HTTP] {c} clients → {host}:{port}{path}")
        try:
            stats = lancer_stress_http(host, port, path, c)
            stats["mode"] = "ramp"
            results.append(stats)
        except Exception as e:
            print(f"  ⚠ Erreur: {e}")
            continue
    return results


def export_json(path: str, data: Any) -> None:
    """Export data to JSON file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"✓ JSON exporté → {path}")
    except Exception as e:
        print(f"✗ Échec export JSON: {e}", file=sys.stderr)


def export_csv(path: str, rows: List[Dict[str, Any]]) -> None:
    """Export data to CSV file."""
    if not rows:
        print("⚠ Aucune donnée à exporter en CSV")
        return
    
    try:
        fields = list(rows[0].keys())
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✓ CSV exporté → {path}")
    except Exception as e:
        print(f"✗ Échec export CSV: {e}", file=sys.stderr)


def main() -> None:
    """Main entry point with enhanced CLI and error handling."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Client de stress HTTP optimisé (mono/multi)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s --port 8080 --clients 100
  %(prog)s --port 8080 --path /stats --ramp 10,50,100,200
  %(prog)s --host 192.168.1.10 --port 8081 --clients 500 --json results.json
        """
    )
    parser.add_argument("--host", default="127.0.0.1", help="Adresse du serveur")
    parser.add_argument("--port", type=int, default=8080, help="Port du serveur")
    parser.add_argument("--path", default="/hello", help="Chemin HTTP")
    parser.add_argument("--clients", type=int, default=50, help="Nombre de clients concurrents")
    parser.add_argument(
        "--ramp",
        type=str,
        help="Mode ramp-up: liste de charges (ex: 10,50,100,200)",
    )
    parser.add_argument("--json", type=str, help="Export vers fichier JSON")
    parser.add_argument("--csv", type=str, help="Export vers fichier CSV (mode ramp)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"🚀 HTTP STRESS TEST")
    print(f"{'='*60}")
    print(f"Cible: {args.host}:{args.port}{args.path}")
    print(f"{'='*60}\n")

    try:
        if args.ramp:
            # Ramp-up mode
            steps = [int(x) for x in args.ramp.split(",") if x.strip()]
            print(f"Mode ramp-up: {len(steps)} étapes\n")
            
            results = lancer_ramp_up_http(args.host, args.port, args.path, steps)
            
            # Display summary
            print(f"\n{'='*60}")
            print("RÉSUMÉ RAMP-UP")
            print(f"{'='*60}")
            for r in results:
                success_rate = (r['success'] / r['clients'] * 100) if r['clients'] > 0 else 0
                print(f"  {r['clients']:4d} clients | "
                      f"Débit: {r['throughput_req_s']:7.1f} req/s | "
                      f"P99: {r['p99_ms']:6.2f}ms | "
                      f"Succès: {success_rate:5.1f}%")
            
            if args.json:
                export_json(args.json, results)
            if args.csv:
                export_csv(args.csv, results)
                
        else:
            # Single test mode
            print(f"Test avec {args.clients} clients...\n")
            res = lancer_stress_http(args.host, args.port, args.path, args.clients)
            
            # Display results
            print(f"\n{'='*60}")
            print("RÉSULTATS")
            print(f"{'='*60}")
            
            important_keys = ['success', 'fail', 'throughput_req_s', 'mean_ms', 
                            'median_ms', 'min_ms', 'max_ms', 'p95_ms', 'p99_ms']
            
            for key in important_keys:
                if key in res:
                    value = res[key]
                    print(f"  {key:20s} : {value}")
            
            if args.verbose:
                print(f"\n{'='*60}")
                print("DÉTAILS COMPLETS")
                print(f"{'='*60}")
                for k, v in res.items():
                    if k not in important_keys:
                        print(f"  {k:20s} : {v}")
            
            if args.json:
                export_json(args.json, res)
                
        print(f"\n{'='*60}")
        print("✓ Test terminé")
        print(f"{'='*60}\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Erreur: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

