#!/usr/bin/env bash
# ============================================================================
#  RUN INTERACTIF – Serveurs TCP/HTTP + Benchmarks + UML + DevOps
#  Projet : server_project
#  Auteur : Walid Ben Touhami
#  Version : EXTREME DEVOPS
# ============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VENV_DIR="$ROOT_DIR/venv"
VENV_PY="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
CYAN="\033[1;36m"
RESET="\033[0m"

HTTP_MONO_PORT=8080
HTTP_MULTI_PORT=8081
TCP_MONO_PORT=5050
TCP_MULTI_PORT=5051

# ----------------------------------------------------------------------------
# Utilitaires
# ----------------------------------------------------------------------------

pause() {
    read -rp "Appuie sur Entrée pour continuer..." _
}

info() {
    echo -e "${CYAN}[INFO]${RESET} $*"
}

ok() {
    echo -e "${GREEN}[OK]${RESET} $*"
}

warn() {
    echo -e "${YELLOW}[WARN]${RESET} $*"
}

err() {
    echo -e "${RED}[ERROR]${RESET} $*"
}

# Arrêt propre des serveurs à la sortie
cleanup() {
    echo -e "${RED}→ Arrêt des serveurs (make kill_servers)...${RESET}"
    make kill_servers >/dev/null 2>&1 || true
}
trap cleanup EXIT

# ----------------------------------------------------------------------------
# Vérifications préalables
# ----------------------------------------------------------------------------

check_makefile() {
    if [ ! -f "$ROOT_DIR/Makefile" ]; then
        err "Makefile introuvable. Es-tu bien dans server_project ?"
        exit 1
    fi
}

check_venv() {
    if [ ! -x "$VENV_PY" ]; then
        warn "Environnement virtuel Python inexistant : $VENV_DIR"
        read -rp "Créer le venv et installer les dépendances Python ? [o/N] " ans
        ans="${ans:-n}"
        if [[ "$ans" =~ ^[oOyY]$ ]]; then
            info "Création du venv..."
            python3 -m venv "$VENV_DIR"
            ok "venv créé."

            info "Installation des dépendances Python principales..."
            "$VENV_PIP" install --upgrade pip >/dev/null
            if [ -f "$ROOT_DIR/python/requirements.txt" ]; then
                "$VENV_PIP" install -r "$ROOT_DIR/python/requirements.txt"
            fi
            # dépendances courantes du projet
            "$VENV_PIP" install psutil pandas matplotlib plotly kaleido \
                reportlab python-pptx cairosvg websockets watchdog >/dev/null || true
            ok "Dépendances Python installées (ou partiellement, selon disponibilité)."
        else
            warn "Certaines commandes Python (benchmarks, UML HTML, PPTX, PDF...) peuvent échouer."
        fi
    fi
}

# ----------------------------------------------------------------------------
# Étapes du pipeline
# ----------------------------------------------------------------------------

step_venv() {
    check_venv
    ok "venv prêt."
}

step_generate_http_files() {
    if [ -f "$ROOT_DIR/create_http_files.py" ]; then
        info "Génération/actualisation des fichiers HTTP (create_http_files.py)..."
        "$VENV_PY" "$ROOT_DIR/create_http_files.py"
        ok "Fichiers HTTP générés."
    else
        warn "create_http_files.py introuvable – étape ignorée."
    fi
}

step_build() {
    info "Nettoyage + compilation optimisée (make -j)..."
    make clean
    make -j"$(nproc)"
    ok "Build C terminé."
}

step_uml() {
    if [ -f "$ROOT_DIR/docs/uml/generate_uml.py" ]; then
        info "Génération UML (PUML + SVG) + mise à jour du README..."
        "$VENV_PY" "$ROOT_DIR/docs/uml/generate_uml.py" || python3 "$ROOT_DIR/docs/uml/generate_uml.py"
        if [ -f "$ROOT_DIR/docs/uml/update_readme_uml.py" ]; then
            "$VENV_PY" "$ROOT_DIR/docs/uml/update_readme_uml.py" || python3 "$ROOT_DIR/docs/uml/update_readme_uml.py"
        fi
        ok "UML générés et README mis à jour."
    else
        warn "docs/uml/generate_uml.py introuvable – UML non régénérés."
    fi
}

step_presentation() {
    if [ -f "$ROOT_DIR/presentation/generate_pptx_final.py" ]; then
        info "Génération de la présentation PowerPoint..."
        ( cd "$ROOT_DIR/presentation" && "$VENV_PY" ./generate_pptx_final.py || python3 ./generate_pptx_final.py )
        ok "PPTX généré."
    else
        warn "presentation/generate_pptx_final.py introuvable – PPTX non régénéré."
    fi

    if [ -f "$ROOT_DIR/presentation/generate_pdf_script_extreme.py" ]; then
        info "Génération des PDF de script / slides (EXTREME)..."
        ( cd "$ROOT_DIR/presentation" && "$VENV_PY" ./generate_pdf_script_extreme.py --pdf || python3 ./generate_pdf_script_extreme.py --pdf )
        ok "PDF générés."
    elif [ -f "$ROOT_DIR/presentation/generate_pdf_script.py" ]; then
        info "Génération du script PDF simple..."
        ( cd "$ROOT_DIR/presentation" && "$VENV_PY" ./generate_pdf_script.py || python3 ./generate_pdf_script.py )
        ok "PDF script généré."
    else
        warn "Aucun script PDF trouvé dans presentation/ – étape ignorée."
    fi
}

step_start_servers() {
    if [ -f "$ROOT_DIR/scripts/start_all.sh" ]; then
        info "Démarrage de tous les serveurs via scripts/start_all.sh..."
        chmod +x "$ROOT_DIR/scripts/start_all.sh"
        "$ROOT_DIR/scripts/start_all.sh"
        ok "Serveurs démarrés (TCP & HTTP)."
    else
        info "start_all.sh introuvable – démarrage manuel des serveurs via make run_*..."
        make run_mono
        make run_multi
        make run_mono_http
        make run_multi_http
        ok "Serveurs TCP/HTTP lancés."
    fi
}

step_smoke_http_routes() {
    info "Smoke test des routes HTTP..."
    for route in "/" "/hello" "/time" "/stats"; do
        echo -e "${CYAN}→ GET http://127.0.0.1:${HTTP_MONO_PORT}${route}${RESET}"
        curl -s "http://127.0.0.1:${HTTP_MONO_PORT}${route}" || true
        echo
        echo -e "${CYAN}→ GET http://127.0.0.1:${HTTP_MULTI_PORT}${route}${RESET}"
        curl -s "http://127.0.0.1:${HTTP_MULTI_PORT}${route}" || true
        echo -e "\n---\n"
    done
    ok "Smoke tests HTTP terminés (monothread + multithread)."
}

step_stress_tcp() {
    info "Stress tests TCP (mono + multi) via Makefile..."
    make stress_tcp_mono || warn "stress_tcp_mono a échoué ou la cible n'existe pas."
    make stress_tcp_multi || warn "stress_tcp_multi a échoué ou la cible n'existe pas."
    ok "Stress TCP terminé (si cibles disponibles)."
}

step_stress_http() {
    info "Stress tests HTTP (mono + multi) via Makefile..."
    make stress_http_mono || warn "stress_http_mono a échoué ou la cible n'existe pas."
    make stress_http_multi || warn "stress_http_multi a échoué ou la cible n'existe pas."
    ok "Stress HTTP terminé (si cibles disponibles)."
}

step_benchmark_extreme() {
    info "Benchmarks EXTREME..."
    make benchmark_extreme || {
        warn "Cible benchmark_extreme indisponible – tentative directe de python/benchmark_extreme.py"
        if [ -f "$ROOT_DIR/python/benchmark_extreme.py" ]; then
            "$VENV_PY" "$ROOT_DIR/python/benchmark_extreme.py" || python3 "$ROOT_DIR/python/benchmark_extreme.py"
        else
            warn "python/benchmark_extreme.py introuvable."
        fi
    }
    ok "Benchmarks EXTREME terminés (si script/cible présents)."
}

step_cheatsheet() {
    if [ -f "$ROOT_DIR/scripts/generate_cheatsheet.py" ]; then
        info "Génération de la cheat-sheet PDF..."
        "$VENV_PY" "$ROOT_DIR/scripts/generate_cheatsheet.py" || python3 "$ROOT_DIR/scripts/generate_cheatsheet.py"
        ok "Cheat-sheet générée."
    else
        warn "scripts/generate_cheatsheet.py introuvable – pas de cheat-sheet générée."
    fi
}

step_status() {
    echo -e "${CYAN}=== STATUT PROCESSUS SERVEURS (approx.) ===${RESET}"
    ps aux | grep -E "serveur_mono|serveur_multi|serveur_mono_http|serveur_multi_http" | grep -v grep || echo "Aucun serveur détecté."
    echo
    echo -e "${CYAN}=== PORTS ÉCOUTE (5050,5051,8080,8081) ===${RESET}"
    ss -ltnp 2>/dev/null | grep -E ":(5050|5051|8080|8081)" || echo "Aucun port cible en écoute."
    echo
}

# ----------------------------------------------------------------------------
# Pipeline FULL RUN (du début à la fin)
# ----------------------------------------------------------------------------

pipeline_full() {
    echo -e "${CYAN}=== PIPELINE COMPLET : FULL RUN ===${RESET}"
    check_makefile
    check_venv
    step_generate_http_files
    step_build
    step_uml
    step_presentation
    step_start_servers
    step_smoke_http_routes
    step_stress_tcp
    step_stress_http
    step_benchmark_extreme
    step_cheatsheet
    ok "FULL RUN terminé."
}

# ----------------------------------------------------------------------------
# Menu interactif
# ----------------------------------------------------------------------------

menu() {
    clear
    echo -e "${GREEN}======================================================${RESET}"
    echo -e "${GREEN}   RUN INTERACTIF – Serveurs TCP/HTTP & Benchmarks    ${RESET}"
    echo -e "${GREEN}======================================================${RESET}"
    echo
    echo "Racine projet : $ROOT_DIR"
    echo
    echo "1) FULL RUN – Tout exécuter (build + UML + PPTX + serveurs + stress + benchmarks)"
    echo "2) Build seul (clean + make -j)"
    echo "3) Générer UML + mise à jour README"
    echo "4) Générer présentation (PPTX + PDF)"
    echo "5) Démarrer tous les serveurs"
    echo "6) Smoke test des routes HTTP"
    echo "7) Stress tests TCP + HTTP"
    echo "8) Benchmarks EXTREME uniquement"
    echo "9) Statut des serveurs / ports"
    echo "k) Kill serveurs (make kill_servers)"
    echo "q) Quitter"
    echo
}

main_loop() {
    check_makefile

    while true; do
        menu
        read -rp "Choix ? [1-9/k/q] : " choice
        case "$choice" in
            1)
                pipeline_full
                pause
                ;;
            2)
                check_venv
                step_build
                pause
                ;;
            3)
                check_venv
                step_uml
                pause
                ;;
            4)
                check_venv
                step_presentation
                pause
                ;;
            5)
                step_start_servers
                pause
                ;;
            6)
                step_smoke_http_routes
                pause
                ;;
            7)
                check_venv
                step_stress_tcp
                step_stress_http
                pause
                ;;
            8)
                check_venv
                step_benchmark_extreme
                pause
                ;;
            9)
                step_status
                pause
                ;;
            k|K)
                cleanup
                pause
                ;;
            q|Q)
                echo "Sortie."
                break
                ;;
            *)
                echo "Choix invalide."
                pause
                ;;
        esac
    done
}

main_loop

