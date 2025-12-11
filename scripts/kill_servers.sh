#!/usr/bin/env bash
set -euo pipefail

echo "──────────────────────────────────────────────"
echo "🛑 Arrêt des serveurs C"
echo "──────────────────────────────────────────────"

pgrep serveur_mono       | xargs -r kill -SIGINT 2>/dev/null || true
pgrep serveur_multi      | xargs -r kill -SIGINT 2>/dev/null || true
pgrep serveur_mono_http  | xargs -r kill -SIGINT 2>/dev/null || true
pgrep serveur_multi_http | xargs -r kill -SIGINT 2>/dev/null || true

echo "✔ Tous les serveurs ont été arrêtés (si présents)."

