# 🚀 Serveur TCP & HTTP — Mono-thread / Multi-thread (C/POSIX)
### Projet Ingénieur — Serveur Hautes Performances + Queue FIFO Générique + Benchmarks Automatisés

Ce projet implémente plusieurs serveurs réseau en **C/POSIX**, comparant les architectures :
- **TCP mono-thread** (`serveur_mono`)
- **TCP multi-thread** (`serveur_multi`)
- **HTTP mono-thread** (`serveur_mono_http`)
- **HTTP multi-thread avec pool de threads** (`serveur_multi_http`)

Il inclut :
- une **file FIFO générique thread-safe** (queue.c)
- des **tests unitaires C**
- un **client de stress** Python capable de monter à plusieurs centaines de connexions
- un système de **benchmarks automatisés**
- un **dashboard HTML interactif** (Plotly)
- des **scripts DevOps** : build, test, bench, monitoring
- un **système de reconstruction automatique du projet** (`rebuild_project.py`)

---

# 📂 Arborescence du projet

server_project/
├── src/
│ ├── serveur_mono.c
│ ├── serveur_multi.c
│ ├── serveur_mono_http.c
│ ├── serveur_multi_http.c
│ ├── queue.c / queue.h
│ ├── http.c / http.h
│
├── tests/
│ └── test_queue.c
│
├── python/
│ ├── client_stress.py
│ ├── benchmark.py
│ ├── export_html.py
│ ├── dashboard.html (généré)
│
├── scripts/
│ ├── run_all.sh
│ ├── monitor.sh
│
├── docs/
│ ├── rapport.tex
│ ├── rapport.pdf (généré)
│
├── Makefile
├── rebuild_project.py
├── create_http_files.py
├── results.json / results.xlsx (générés)
└── README.md

markdown
Copier le code

---

# 🧩 Fonctionnalités principales

## 1. ⭐ Serveur TCP Mono-thread
- Un seul thread gère toutes les connexions.
- Architecture séquentielle simple.

## 2. 🔥 Serveur TCP Multi-thread
- Pool fixe de threads.
- File d’attente FIFO générique thread-safe.
- Scalabilité testée jusqu’à 300 clients concurrents.

## 3. 🌐 Serveurs HTTP
### Mono-thread
- Réponses HTML & JSON.
- Parseur HTTP robuste (`parse_http_request`).

### Multi-thread
- Thread pool (8 workers par défaut).
- HTTP 1.1 minimal sans frameworks.
- Routes :
  - `/` → page HTML
  - `/hello` → JSON
  - Autres → 404

## 4. 📊 Benchmarks & Monitoring (Python)
- Latence moyenne / médiane / p95 / p99
- Débit (requests per second)
- Taux d’erreurs
- Utilisation CPU & RAM du serveur
- Export vers :
  - `results.json`
  - `results.xlsx`
  - Dashboard HTML : `python/dashboard.html`

---

# 🧪 Tests unitaires C

Lancement :

```bash
make test
Testé :

intégrité de la queue FIFO

comportement multi-producteurs / multi-consommateurs

🛠️ Compilation
Compilation complète :

bash
Copier le code
make clean
make -j$(nproc)
Exécution rapide :

bash
Copier le code
make run_mono
make run_multi
make run_mono_http
make run_multi_http
Arrêt des serveurs :

bash
Copier le code
make kill_servers
📦 Reconstruction complète automatique
bash
Copier le code
python3 rebuild_project.py
Ce script :

régénère les fichiers HTTP

nettoie le projet

recompile

lance les tests

vérifie l’intégrité du projet

🚀 Pipeline complet (build + bench + plots)
bash
Copier le code
./scripts/run_all.sh
Étapes :

compilation C

installation env Python

exécution du benchmark

export JSON/XLSX

génération du panel HTML

📈 Dashboard interactif
Génération :

bash
Copier le code
python3 python/export_html.py
Ouverture :

bash
Copier le code
xdg-open python/dashboard.html
Contenu :

courbes latence vs clients

courbes throughput

CPU/RAM sampling

comparatif mono vs multi

🧠 Architecture technique & Conception
Queue FIFO Générique
basée sur tableau circulaire

verrouillage via mutex + condition variables

supporte tout type (void *)

utilisée par le serveur multi HTTP

Pool de threads
modèle "worker permanent"

réduction drastique du coût d’allocation de threads

bien plus performant sur forte charge

Analyse des performances
Multi-thread HTTP > Mono-thread TCP

Multi TCP > Mono TCP (comme prévu)

🔒 Sécurité et robustesse
serveurs isolés via fork? ou threads → sécurisé

sanitizers disponibles :

bash
Copier le code
make debug
reconstruction auto en cas d’erreur

monitoring CPU/RAM intégré

scripts résilients (run_all.sh bulletproof)

📝 Rapport académique
Disponible dans :

bash
Copier le code
docs/rapport.tex
docs/rapport.pdf
Inclut :

contexte

analyse d’architecture

résultats graphiques

interprétation

conclusion professionnelle

🤝 Auteur
Walid Ben Touhami
Projet Système & Réseaux — Ingénieur Informatique
Serveurs C hautes performances / Benchmarking / DevOps

📄 Licence
MIT — libre d’usage académique et professionnel.
