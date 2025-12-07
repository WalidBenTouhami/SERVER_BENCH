#!/usr/bin/env bash
set -euo pipefail

echo "──────────────────────────────────────────────"
echo "🛑 Arrêt des serveurs C"
echo "──────────────────────────────────────────────"

pkill serveur_mono       2>/dev/null || true
pkill serveur_multi      2>/dev/null || true
pkill serveur_mono_http  2>/dev/null || true
pkill serveur_multi_http 2>/dev/null || true

echo "✔ Tous les serveurs ont été arrêtés (si présents)."

