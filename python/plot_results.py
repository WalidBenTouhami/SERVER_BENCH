#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import os

OUTPUT = "figures"
os.makedirs(OUTPUT, exist_ok=True)

COLOR_MONO = "#E67E22"
COLOR_MULTI = "#2980B9"

def load_results():
    df = pd.read_excel("results.xlsx")
    mono = df[df.server == "mono"]
    multi = df[df.server == "multi"]
    return mono, multi

def graph_throughput(mono, multi):
    plt.figure(figsize=(8, 5))
    plt.plot(mono.clients, mono.throughput_rps, marker="o", color=COLOR_MONO, label="Mono-thread")
    plt.plot(multi.clients, multi.throughput_rps, marker="o", color=COLOR_MULTI, label="Multi-thread")
    plt.xlabel("Clients")
    plt.ylabel("Débit (req/s)")
    plt.title("Débit VS nombre de clients")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/1-throughput.png", dpi=160)
    plt.close()

def graph_latency_p99(mono, multi):
    plt.figure(figsize=(8, 5))
    plt.plot(mono.clients, mono.p99, marker="o", color=COLOR_MONO, label="Mono-thread")
    plt.plot(multi.clients, multi.p99, marker="o", color=COLOR_MULTI, label="Multi-thread")
    plt.xlabel("Clients")
    plt.ylabel("Latence P99 (ms)")
    plt.title("Latence P99 VS nombre de clients")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/2-latency_p99.png", dpi=160)
    plt.close()

def graph_cpu(mono, multi):
    plt.figure(figsize=(8, 5))
    plt.plot(mono.clients, mono.cpu_mean, marker="o", color=COLOR_MONO, label="Mono-thread")
    plt.plot(multi.clients, multi.cpu_mean, marker="o", color=COLOR_MULTI, label="Multi-thread")
    plt.xlabel("Clients")
    plt.ylabel("CPU moyen (%)")
    plt.title("CPU moyen")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/3-cpu.png", dpi=160)
    plt.close()

def graph_memory(mono, multi):
    plt.figure(figsize=(8, 5))
    plt.plot(mono.clients, mono.mem_mean, marker="o", color=COLOR_MONO, label="Mono-thread")
    plt.plot(multi.clients, multi.mem_mean, marker="o", color=COLOR_MULTI, label="Multi-thread")
    plt.xlabel("Clients")
    plt.ylabel("Mémoire (MB)")
    plt.title("Mémoire RSS")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/4-memory.png", dpi=160)
    plt.close()

def graph_speedup(mono, multi):
    plt.figure(figsize=(8, 5))
    speedup = multi.throughput_rps.values / mono.throughput_rps.values
    plt.plot(mono.clients, speedup, marker="o", color="#16A085")
    plt.axhline(1.0, color="gray", linestyle="--")
    plt.xlabel("Clients")
    plt.ylabel("Speedup (multi/mono)")
    plt.title("Speedup multi-thread")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/5-speedup.png", dpi=160)
    plt.close()

def graph_saturation(mono, multi):
    plt.figure(figsize=(8, 5))
    plt.plot(mono.clients, mono.cpu_mean, marker="o", linestyle="--", color=COLOR_MONO, label="Mono-thread")
    plt.plot(multi.clients, multi.cpu_mean, marker="o", linestyle="--", color=COLOR_MULTI, label="Multi-thread")
    plt.xlabel("Clients")
    plt.ylabel("CPU (%)")
    plt.title("Saturation CPU")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/6-saturation.png", dpi=160)
    plt.close()

def main():
    mono, multi = load_results()
    graph_throughput(mono, multi)
    graph_latency_p99(mono, multi)
    graph_cpu(mono, multi)
    graph_memory(mono, multi)
    graph_speedup(mono, multi)
    graph_saturation(mono, multi)
    print("[PLOT] Graphiques générés dans figures/")

if __name__ == "__main__":
    main()
