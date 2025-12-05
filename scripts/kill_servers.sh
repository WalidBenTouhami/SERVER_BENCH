#!/bin/bash
echo "[KILL] Fermeture des serveurs…"

pkill -f serveur_mono     2>/dev/null
pkill -f serveur_multi    2>/dev/null
pkill -f serveur_mono_http 2>/dev/null
pkill -f serveur_multi_http 2>/dev/null

sleep 0.5

# Vérifie si des ports sont encore occupés
for PORT in 5050 5051 8080 8081; do
    if sudo lsof -i :$PORT > /dev/null 2>&1; then
        echo "[WARN] Port $PORT encore utilisé !"
        PID=$(sudo lsof -t -i :$PORT)
        echo "       → kill -9 $PID"
        sudo kill -9 $PID
    fi
done

echo "[OK] Tous les serveurs sont arrêtés et ports libérés."

