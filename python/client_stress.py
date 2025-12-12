#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized TCP stress test client with better error handling and connection pooling.
"""

import socket
import struct
import time
import statistics
import sys
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


def envoyer_requete(host: str, port: int, number: int) -> float:
    """Send single request and measure latency in milliseconds.
    
    Returns:
        float: Latency in ms, or -1.0 on error
    """
    start = time.perf_counter()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Optimize socket options
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 0)
            s.settimeout(5.0)
            
            s.connect((host, port))
            
            # Send request
            data = struct.pack("!i", number)
            s.sendall(data)
            
            # Receive response with proper buffer handling
            result_raw = _recv_exact(s, 4)
            ts_raw = _recv_exact(s, 8)
            
            if not result_raw or not ts_raw:
                return -1.0
            
            # Validate response
            _ = struct.unpack("!i", result_raw)[0]
            _ = struct.unpack("!q", ts_raw)[0]
            
    except socket.timeout:
        return -1.0
    except ConnectionRefusedError:
        return -1.0
    except Exception:
        return -1.0
    
    end = time.perf_counter()
    return (end - start) * 1000.0


def _recv_exact(sock: socket.socket, size: int) -> Optional[bytes]:
    """Receive exact number of bytes or return None."""
    data = b''
    while len(data) < size:
        try:
            chunk = sock.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        except socket.timeout:
            return None
    return data


def lancer_stress_test(host: str, port: int, clients: int, number: int = 42) -> Dict[str, Any]:
    """Launch stress test with multiple concurrent clients.
    
    Args:
        host: Server hostname
        port: Server port
        clients: Number of concurrent clients
        number: Test number to send
        
    Returns:
        Dictionary with test results and statistics
    """
    latences: List[float] = []
    errors: List[str] = []
    
    # Use optimal number of workers (not more than needed)
    max_workers = min(clients, 500)  # Limit to prevent resource exhaustion
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(envoyer_requete, host, port, number)
                   for _ in range(clients)]
        
        for f in as_completed(futures):
            try:
                lat = f.result()
                if lat >= 0:
                    latences.append(lat)
                else:
                    errors.append("timeout_or_error")
            except Exception as e:
                errors.append(str(e))

    success_count = len(latences)
    fail_count = clients - success_count

    if not latences:
        return {
            "clients": clients,
            "success": 0,
            "fail": fail_count,
            "mean": None,
            "median": None,
            "p95": None,
            "p99": None,
            "max": None,
            "min": None,
            "latences": [],
        }

    latences_sorted = sorted(latences)
    n = len(latences_sorted)

    def percentile(p: float) -> float:
        """Calculate percentile value."""
        if n == 0:
            return 0.0
        k = int(p * (n - 1))
        return latences_sorted[k]

    return {
        "clients": clients,
        "success": success_count,
        "fail": fail_count,
        "mean": statistics.mean(latences),
        "median": statistics.median(latences),
        "p95": percentile(0.95),
        "p99": percentile(0.99),
        "max": max(latences),
        "min": min(latences),
        "latences": latences,
    }


def main() -> None:
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Client de stress TCP optimisé",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s --port 5050 --clients 100
  %(prog)s --host 192.168.1.10 --port 5050 --clients 500
        """
    )
    parser.add_argument("--host", default="127.0.0.1", help="Adresse du serveur")
    parser.add_argument("--port", type=int, required=True, help="Port du serveur")
    parser.add_argument("--clients", type=int, default=50, help="Nombre de clients concurrents")
    parser.add_argument("--number", type=int, default=42, help="Nombre à envoyer au serveur")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")
    args = parser.parse_args()

    print(f"[CLIENT] Test de stress TCP")
    print(f"  Cible: {args.host}:{args.port}")
    print(f"  Clients: {args.clients}")
    print(f"  Nombre: {args.number}")
    print()
    
    start = time.time()
    res = lancer_stress_test(args.host, args.port, args.clients, args.number)
    elapsed = time.time() - start
    
    # Print results
    print("Résultats:")
    print(f"  ✓ Succès: {res['success']}/{res['clients']} ({res['success']/res['clients']*100:.1f}%)")
    print(f"  ✗ Échecs: {res['fail']}")
    
    if res['mean'] is not None:
        print(f"\nLatences (ms):")
        print(f"  Moyenne: {res['mean']:.2f}")
        print(f"  Médiane: {res['median']:.2f}")
        print(f"  Min: {res['min']:.2f}")
        print(f"  Max: {res['max']:.2f}")
        print(f"  P95: {res['p95']:.2f}")
        print(f"  P99: {res['p99']:.2f}")
        
        throughput = res['success'] / elapsed if elapsed > 0 else 0
        print(f"\nPerformance:")
        print(f"  Temps total: {elapsed:.2f}s")
        print(f"  Débit: {throughput:.1f} req/s")
    
    if args.verbose:
        print(f"\nDonnées brutes:")
        print(res)
    
    # Exit with error if too many failures
    if res['fail'] > res['clients'] * 0.5:
        print("\n⚠ Plus de 50% d'échecs détectés", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrompu par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)

