#!/usr/bin/env bash
# Optimized server shutdown script with validation and feedback
set -euo pipefail

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

echo "──────────────────────────────────────────────"
echo "🛑 Arrêt des serveurs C"
echo "──────────────────────────────────────────────"

# Array of server process names
SERVERS=("serveur_mono" "serveur_multi" "serveur_mono_http" "serveur_multi_http")
KILLED_COUNT=0

for server in "${SERVERS[@]}"; do
    if PIDS=$(pgrep -x "$server" 2>/dev/null); then
        COUNT=$(echo "$PIDS" | wc -l)
        log_info "Arrêt de $COUNT instance(s) de $server (PIDs: $(echo $PIDS | tr '\n' ' '))"
        echo "$PIDS" | xargs -r kill -SIGINT 2>/dev/null || true
        
        # Wait briefly and verify termination
        sleep 0.5
        if pgrep -x "$server" >/dev/null 2>&1; then
            log_warn "$server ne s'est pas arrêté gracieusement, utilisation de SIGKILL"
            pgrep -x "$server" | xargs -r kill -SIGKILL 2>/dev/null || true
        fi
        
        KILLED_COUNT=$((KILLED_COUNT + COUNT))
    fi
done

if [ $KILLED_COUNT -eq 0 ]; then
    log_warn "Aucun serveur en cours d'exécution trouvé"
else
    log_info "✓ $KILLED_COUNT processus serveur(s) arrêté(s) avec succès"
fi

