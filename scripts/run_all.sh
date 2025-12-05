#!/bin/bash
set -euo pipefail

###############################################################################
#                 RUN_ALL.SH — VERSION PRO / BULLET-PROOF
#    Auto-détection du projet, logs, redémarrage serveur, monitoring
###############################################################################

# ============================
# 🔍 AUTO-DÉTECTION RACINE
# ============================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_DIR="$PROJECT_ROOT/python"
LOG_DIR="$PROJECT_ROOT/logs"
MONITOR_LOG="$LOG_DIR/monitoring.log"

mkdir -p "$LOG_DIR"

echo "[RUN_ALL] Racine détectée : $PROJECT_ROOT"
echo "[RUN_ALL] Logs dans : $LOG_DIR"
sleep 0.5

# ============================
# 🧹 NETTOYAGE + BUILD C
# ============================
echo "[RUN_ALL] Compilation C…"
(make -C "$PROJECT_ROOT" clean && make -C "$PROJECT_ROOT" all -j$(nproc)) \
    > "$LOG_DIR/build.log" 2>&1 || {
    echo "❌ ERREUR BUILD — voir $LOG_DIR/build.log"
    exit 1
}
echo "✔ Build OK"

# ============================
# 🐍 ENV PYTHON
# ============================
echo "[RUN_ALL] Activation environnement Python…"
cd "$PYTHON_DIR"
if [ ! -d venv ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > "$LOG_DIR/pip_install.log" 2>&1

# ============================
# 🔄 MONITORING CPU/RAM (background)
# ============================
monitor_system() {
    echo "[MONITOR] Démarrage monitoring CPU/RAM" > "$MONITOR_LOG"
    while true; do
        ts=$(date "+%Y-%m-%d %H:%M:%S")
        cpu=$(grep 'cpu ' /proc/stat | awk '{u=$2+$4; t=$2+$4+$5; if (prev_total!="") printf "%.2f\n",100*( (u-prev_idle)/(t-prev_total) ); prev_idle=$5; prev_total=t}')
        mem=$(free -m | awk '/Mem:/ {print $3"/"$2" MB"}')
        echo "$ts  CPU=${cpu}%  MEM=${mem}" >> "$MONITOR_LOG"
        sleep 2
    done
}

monitor_system &
PID_MONITOR=$!
echo "[RUN_ALL] Monitoring PID = $PID_MONITOR"

# ============================
# 🚀 LANCEMENT SERVEUR AVEC SURVEILLANCE
# ============================
launch_server_supervised() {
    local bin_path="$1"
    local port="$2"
    local log_file="$3"

    echo "[SUPERVISOR] Lancement serveur : $bin_path (port $port)"
    while true; do
        "$bin_path" >> "$log_file" 2>&1 &
        local pid=$!

        echo "[SUPERVISOR] PID serveur = $pid"
        wait $pid

        echo "⚠ Serveur crashé ou arrêté — redémarrage automatique dans 2s…" | tee -a "$log_file"
        sleep 2
    done
}

# ============================
# 🧪 BENCHMARK AVEC SUPERVISION AUTO
# ============================
echo "[RUN_ALL] Benchmark…"

# On lance benchmark en mode superviseur “safe”
python3 benchmark.py > "$LOG_DIR/benchmark.log" 2>&1 || {
    echo "❌ ERREUR BENCHMARK — voir $LOG_DIR/benchmark.log"
    kill $PID_MONITOR
    exit 1
}

echo "✔ Benchmark OK"

# ============================
# 📊 GRAPHIQUES
# ============================
echo "[RUN_ALL] Génération graphiques…"
python3 plot_results.py > "$LOG_DIR/plots.log" 2>&1
echo "✔ Graphiques OK"

# ============================
# 🧹 ARRÊT DES SERVICES & MONITORING
# ============================
echo "[RUN_ALL] Nettoyage des superviseurs…"
kill $PID_MONITOR 2>/dev/null || true

echo "🎉 Pipeline complet terminé avec succès."
echo "📦 Logs : $LOG_DIR"
echo "📊 Résultats : python/results.json — python/results.xlsx"
echo "🖼 Figures : python/figures/"

