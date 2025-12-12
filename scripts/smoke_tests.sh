#!/usr/bin/env bash
# ============================================================
# SMOKE TESTS TCP & HTTP — Mono & Multi-thread
# Version : NINJA PRO – 100% fiable en CI GitHub Actions
# ============================================================

set -euo pipefail
IFS=$'\n\t'

# ───── Couleurs ─────
GREEN="\033[1;32m"
RED="\033[1;31m"
BLUE="\033[1;34m"
YELLOW="\033[1;33m"
RESET="\033[0m"

# ───── Configuration ─────
TCP_MONO_PORT=5050
TCP_MULTI_PORT=5051
HTTP_MONO_PORT=8080
HTTP_MULTI_PORT=8081

BIN_DIR="./bin"
CLIENT_SCRIPT="python3 python/client_stress_tcp.py"

# ───── Fonctions utilitaires ─────
log()   { echo -e "${BLUE}[SMOKE] $*${RESET}"; }
ok()    { echo -e "${GREEN}OK $*${RESET}"; }
fail()  { echo -e "${RED}FAIL $*${RESET}"; exit 1; }
warn()  { echo -e "${YELLOW}WARN $*${RESET}"; }

# ───── Nettoyage propre à la sortie ─────
cleanup() {
    local pids=("$@")
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
    done
}
PIDS=()
trap 'cleanup "${PIDS[@]}"' EXIT

# ───── Attente intelligente qu’un port soit ouvert ─────
wait_for_port() {
    local port=$1
    local timeout=10
    local elapsed=0
    while ! nc -z 127.0.0.1 "$port" 2>/dev/null; do
        ((elapsed++))
        if [ $elapsed -ge $timeout ]; then
            fail "Timeout attente port $port"
        fi
        sleep 0.5
    done
}

# ───── Test unitaire réutilisable ─────
run_test() {
    local name=$1
    local cmd=$2
    log "Test → $name"
    if eval "$cmd"; then
        ok "$name"
    else
        fail "$name"
    fi
}

# ============================================================
echo -e "${BLUE}=== SMOKE TESTS : TCP & HTTP (Mono + Multi) ===${RESET}"

# 1. TCP Mono-thread
log "Démarrage serveur TCP mono-thread (port $TCP_MONO_PORT)…"
"$BIN_DIR/serveur_mono" > /dev/null 2>&1 &
PIDS+=($!)
wait_for_port $TCP_MONO_PORT
run_test "TCP Mono-thread" "$CLIENT_SCRIPT --port $TCP_MONO_PORT --clients 5 --ramp 1"

# 2. TCP Multi-thread
log "Démarrage serveur TCP multi-thread (port $TCP_MULTI_PORT…"
"$BIN_DIR/serveur_multi" > /dev/null 2>&1 &
PIDS+=($!)
wait_for_port $TCP_MULTI_PORT
run_test "TCP Multi-thread" "$CLIENT_SCRIPT --port $TCP_MULTI_PORT --clients 5 --ramp 1"

# 3. HTTP Mono-thread
log "Démarrage serveur HTTP mono-thread (port $HTTP_MONO_PORT)…"
"$BIN_DIR/serveur_mono_http" > /dev/null 2>&1 &
PIDS+=($!)
wait_for_port $HTTP_MONO_PORT
run_test "HTTP Mono-thread /hello" "curl -f -s http://127.0.0.1:$HTTP_MONO_PORT/hello | grep -q "msg""
run_test "HTTP Mono-thread /stats" "curl -f -s http://127.0.0.1:$HTTP_MONO_PORT/stats | grep -q "total_requests""

# 4. HTTP Multi-thread
log "Démarrage serveur HTTP multi-thread (port $HTTP_MULTI_PORT)…"
"$BIN_DIR/serveur_multi_http" > /dev/null 2>&1 &
PIDS+=($!)
wait_for_port $HTTP_MULTI_PORT
run_test "HTTP Multi-thread /hello" "curl -f -s http://127.0.0.1:$HTTP_MULTI_PORT/hello | grep -q "msg""
run_test "HTTP Multi-thread /stats" "curl -f -s http://127.0.0.1:$HTTP_MULTI_PORT/stats | grep -q "total_requests""

# ───── Fin ─────
echo
echo -e "${GREEN}TOUS LES SMOKE TESTS SONT PASSÉS AVEC SUCCÈS !${RESET}"
echo -e "${GREEN}Prêt pour la production et la soutenance 20/20${RESET}"
exit 0
