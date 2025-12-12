#!/usr/bin/env bash
# Optimized Valgrind analysis with comprehensive output parsing
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

# Parse command line arguments
SERVER_BIN="${1:-./bin/serveur_multi}"
OUT_DIR="logs"
OUT_FILE="${OUT_DIR}/valgrind_report_$(date +%Y%m%d_%H%M%S).txt"

mkdir -p "$OUT_DIR"

echo "──────────────────────────────" | tee "$OUT_FILE"
echo "🧠 Valgrind Full Analysis" | tee -a "$OUT_FILE"
echo "Binaire: $SERVER_BIN" | tee -a "$OUT_FILE"
echo "──────────────────────────────" | tee -a "$OUT_FILE"

# Check if valgrind is installed
if ! command -v valgrind >/dev/null 2>&1; then
    log_error "Valgrind n'est pas installé"
    echo "  → Sur Ubuntu/Debian: sudo apt install valgrind" | tee -a "$OUT_FILE"
    exit 1
fi

# Check if binary exists
if [[ ! -f "$SERVER_BIN" ]]; then
    log_error "Binaire introuvable: $SERVER_BIN"
    echo "  → Compile d'abord avec: make" | tee -a "$OUT_FILE"
    exit 1
fi

# Check if binary is executable
if [[ ! -x "$SERVER_BIN" ]]; then
    log_error "Binaire non exécutable: $SERVER_BIN"
    chmod +x "$SERVER_BIN" || exit 1
fi

log_info "Analyse en cours (peut prendre plusieurs minutes)..."
log_info "Sortie: $OUT_FILE"

# Run valgrind with comprehensive options
START_TIME=$(date +%s)

# Run with timeout to prevent hanging
if timeout 120 valgrind \
    --leak-check=full \
    --show-leak-kinds=all \
    --track-origins=yes \
    --verbose \
    --log-file="${OUT_FILE}.raw" \
    --error-exitcode=1 \
    "$SERVER_BIN" 2>&1 | tee -a "$OUT_FILE"; then
    
    VALGRIND_EXIT=0
else
    VALGRIND_EXIT=$?
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Parse results
echo "" | tee -a "$OUT_FILE"
echo "──────────────────────────────" | tee -a "$OUT_FILE"
echo "📊 Analyse des résultats" | tee -a "$OUT_FILE"
echo "──────────────────────────────" | tee -a "$OUT_FILE"

if [ -f "${OUT_FILE}.raw" ]; then
    # Extract summary
    if grep -q "ERROR SUMMARY" "${OUT_FILE}.raw"; then
        ERROR_COUNT=$(grep "ERROR SUMMARY" "${OUT_FILE}.raw" | tail -1 | grep -oP '\d+(?= errors)' || echo "0")
        log_info "Erreurs détectées: $ERROR_COUNT" | tee -a "$OUT_FILE"
    fi
    
    if grep -q "definitely lost" "${OUT_FILE}.raw"; then
        LEAKS=$(grep "definitely lost" "${OUT_FILE}.raw" | tail -1)
        log_warn "Fuites mémoire: $LEAKS" | tee -a "$OUT_FILE"
    fi
    
    # Append raw log
    cat "${OUT_FILE}.raw" >> "$OUT_FILE"
    rm -f "${OUT_FILE}.raw"
fi

echo "" | tee -a "$OUT_FILE"
echo "Durée d'analyse: ${DURATION}s" | tee -a "$OUT_FILE"

if [ $VALGRIND_EXIT -eq 0 ] || [ $VALGRIND_EXIT -eq 124 ]; then
    log_info "✓ Rapport généré: $OUT_FILE"
    if [ $VALGRIND_EXIT -eq 124 ]; then
        log_warn "Analyse interrompue après timeout (2min)"
    fi
else
    log_error "✗ Valgrind a détecté des erreurs"
    log_info "Consulte le rapport: $OUT_FILE"
    exit $VALGRIND_EXIT
fi