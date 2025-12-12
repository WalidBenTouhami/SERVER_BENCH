#!/usr/bin/env bash
# Optimized full pipeline script with parallel execution and comprehensive logging
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PY_DIR="${PROJECT_ROOT}/python"
LOG_DIR="${PROJECT_ROOT}/logs"
LOG_FILE="${LOG_DIR}/auto_run.log"

# Colors
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Logging functions with timestamps
timestamp() { date +"%Y-%m-%d %H:%M:%S"; }
log() { 
    local msg="[$(timestamp)] $*"
    echo -e "$msg" | tee -a "$LOG_FILE"
}
log_step() { log "${BLUE}▶${NC} $*"; }
log_success() { log "${GREEN}✓${NC} $*"; }
log_error() { log "${RED}✗${NC} $*" >&2; }
log_warn() { log "${YELLOW}⚠${NC} $*"; }

# Error handling
trap 'log_error "Pipeline interrompu à la ligne $LINENO"; exit 1' ERR

# Start time tracking
START_TIME=$(date +%s)

echo "──────────────────────────────────────────────" | tee -a "$LOG_FILE"
echo "🚀 Pipeline complet (build + bench + plots)"     | tee -a "$LOG_FILE"
echo "Racine : ${PROJECT_ROOT}"                         | tee -a "$LOG_FILE"
echo "CPU cores: $(nproc)"                              | tee -a "$LOG_FILE"
echo "──────────────────────────────────────────────" | tee -a "$LOG_FILE"

# venv global activation with validation
log_step "Vérification environnement Python…"
if [[ -d "${PROJECT_ROOT}/venv" ]]; then
    log_success "Venv trouvé, activation…"
    # shellcheck disable=SC1091
    source "${PROJECT_ROOT}/venv/bin/activate" || {
        log_error "Échec d'activation du venv"
        exit 1
    }
    
    # Verify Python version
    PYTHON_VERSION=$(python3 --version 2>&1)
    log_success "Python activé: $PYTHON_VERSION"
else
    log_error "venv introuvable. Exécute ./setup.sh en premier."
    exit 1
fi

# Check required Python packages
log_step "Vérification dépendances Python…"
for pkg in pandas matplotlib psutil; do
    if ! python3 -c "import $pkg" 2>/dev/null; then
        log_warn "Package manquant: $pkg (tentative d'installation)"
        pip install --quiet "$pkg" || log_warn "Installation de $pkg a échoué"
    fi
done

# C compilation with optimizations
log_step "🧱 Compilation C (optimisée avec -j$(nproc))…"
COMPILE_START=$(date +%s)
(
    cd "$PROJECT_ROOT"
    make clean 2>&1 | tee -a "$LOG_FILE"
    make -j"$(nproc)" 2>&1 | tee -a "$LOG_FILE" || {
        log_error "Échec de compilation"
        exit 1
    }
)
COMPILE_END=$(date +%s)
COMPILE_TIME=$((COMPILE_END - COMPILE_START))
log_success "Compilation terminée en ${COMPILE_TIME}s"

# Python benchmark execution with error handling
log_step "🔥 Exécution du benchmark Python…"
BENCH_START=$(date +%s)
(
    cd "$PY_DIR"
    
    # Run benchmark with timeout protection
    timeout 600 python3 benchmark.py 2>&1 | tee -a "$LOG_FILE" || {
        log_error "Benchmark a échoué ou timeout (10min)"
        exit 1
    }
    log_success "Benchmark terminé"
    
    # Generate plots in parallel if possible
    log_step "Génération des graphiques…"
    python3 plot_results.py 2>&1 | tee -a "$LOG_FILE" &
    PLOT_PID=$!
    
    log_step "Génération du dashboard HTML…"
    python3 export_html.py 2>&1 | tee -a "$LOG_FILE" &
    EXPORT_PID=$!
    
    # Wait for both processes
    wait $PLOT_PID || log_warn "plot_results.py a rencontré une erreur"
    wait $EXPORT_PID || log_warn "export_html.py a rencontré une erreur"
    
    log_success "Visualisations générées"
)
BENCH_END=$(date +%s)
BENCH_TIME=$((BENCH_END - BENCH_START))
log_success "Benchmark et visualisations terminés en ${BENCH_TIME}s"

# Summary
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

echo "" | tee -a "$LOG_FILE"
echo "──────────────────────────────────────────────" | tee -a "$LOG_FILE"
log_success "✓ Pipeline terminé avec succès!"
echo "──────────────────────────────────────────────" | tee -a "$LOG_FILE"
echo "Temps total: ${TOTAL_TIME}s (Compilation: ${COMPILE_TIME}s, Benchmark: ${BENCH_TIME}s)" | tee -a "$LOG_FILE"
echo "Résultats disponibles:" | tee -a "$LOG_FILE"
echo "  • Données: python/results.json et python/results.xlsx" | tee -a "$LOG_FILE"
echo "  • Graphiques: python/figures/" | tee -a "$LOG_FILE"
echo "  • Dashboard: python/dashboard.html" | tee -a "$LOG_FILE"
echo "  • Logs: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

