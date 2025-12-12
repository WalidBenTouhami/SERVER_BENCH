#!/usr/bin/env bash
# Optimized test runner with timeout and detailed reporting
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs"

readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

mkdir -p "$LOG_DIR"

echo "──────────────────────────────────────────────"
echo "🧪 Exécution des tests unitaires C"
echo "──────────────────────────────────────────────"

cd "$PROJECT_ROOT"

# Check if Makefile has test target
if ! grep -q "^test:" Makefile 2>/dev/null; then
    log_error "Target 'test' introuvable dans le Makefile"
    exit 1
fi

# Run tests with timeout and capture output
TEST_LOG="${LOG_DIR}/test_run_$(date +%Y%m%d_%H%M%S).log"
log_info "Exécution des tests (timeout: 5min)…"
log_info "Logs sauvegardés dans: $TEST_LOG"

START_TIME=$(date +%s)

if timeout 300 make test 2>&1 | tee "$TEST_LOG"; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo ""
    echo "──────────────────────────────────────────────"
    log_info "✓ Tests réussis en ${DURATION}s"
    echo "──────────────────────────────────────────────"
    
    # Summary from test output
    if grep -q "PASS" "$TEST_LOG"; then
        PASS_COUNT=$(grep -c "PASS" "$TEST_LOG" || echo "0")
        log_info "Tests passés: $PASS_COUNT"
    fi
    
    exit 0
else
    EXIT_CODE=$?
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo ""
    echo "──────────────────────────────────────────────"
    
    if [ $EXIT_CODE -eq 124 ]; then
        log_error "✗ Tests interrompus après timeout (5min)"
    else
        log_error "✗ Tests échoués après ${DURATION}s (code: $EXIT_CODE)"
    fi
    
    echo "──────────────────────────────────────────────"
    log_info "Consulte le log complet: $TEST_LOG"
    
    # Show last 20 lines of error
    if [ -f "$TEST_LOG" ]; then
        echo ""
        log_warn "Dernières lignes du log:"
        tail -n 20 "$TEST_LOG"
    fi
    
    exit $EXIT_CODE
fi

