Voici une **mise en page nettement améliorée du README.md**, beaucoup plus professionnelle, structurée, élégante, lisible, adaptée à GitHub et conforme aux standards des projets open-source modernes.

Cette version utilise :

* une hiérarchie visuelle optimisée
* des tableaux
* des blocs clairement segmentés
* des sections avec titres normalisés
* des listes compactes mais riches
* des encadrés de commandes stylés
* une arborescence lisible
* des emojis utilisés intelligemment et non en excès

---

# ✅ **README.md — Version Premium Optimisée**

````markdown
# 🚀 Serveur TCP & HTTP — Mono-thread / Multi-thread (C/POSIX)
### Projet Ingénieur : Serveur Hautes Performances + Queue FIFO Générique + Benchmarks Automatisés

Ce projet implémente plusieurs serveurs réseau en **C/POSIX**, permettant de comparer les architectures :

| Type de serveur | Protocole | Architecture | Fichier |
|-----------------|-----------|--------------|---------|
| Mono-thread     | TCP       | Séquentielle | `serveur_mono` |
| Multi-thread    | TCP       | Thread pool  | `serveur_multi` |
| Mono-thread     | HTTP      | Séquentielle | `serveur_mono_http` |
| Multi-thread    | HTTP      | Thread pool + Queue | `serveur_multi_http` |

---

# 📦 Fonctionnalités principales

## ⭐ 1. Serveur TCP Mono-thread
- Gestion séquentielle.
- Idéal pour comparer avec la version multi-thread.
- Très simple pour étudier le fonctionnement basique d’un serveur.

---

## 🔥 2. Serveur TCP Multi-thread
- Pool fixe de threads.
- File FIFO **générique** et **thread-safe**.
- Performances testées jusqu’à **300 clients concurrents**.
- Architecture proche des serveurs professionnels.

---

## 🌐 3. Serveurs HTTP (C → HTTP 1.1 minimal)
### **Mono-thread**
- Réponses HTML/JSON simples.
- Parseur HTTP robuste : `parse_http_request`.

### **Multi-thread**
- Thread pool (8 workers par défaut).
- Routes disponibles :
  - `/` → Page HTML
  - `/hello` → JSON
  - Autres → 404 NOT FOUND
- Performances supérieures sous charge.

---

## 📊 4. Benchmarks & Monitoring (Python)
Les scripts Python permettent :

- Mesures de **latence** : moyenne, médiane, p95, p99.
- Mesure du **débit (requests/sec)**.
- Monitoring **CPU** & **RAM** du serveur.
- Export automatique vers :
  - `results.json`
  - `results.xlsx`
  - Dashboard HTML interactif (`dashboard.html`)
- Stress test scalable (10 → 300 clients).

---

# 📂 Arborescence du projet

```text
server_project/
├── src/
│   ├── serveur_mono.c
│   ├── serveur_multi.c
│   ├── serveur_mono_http.c
│   ├── serveur_multi_http.c
│   ├── queue.c / queue.h
│   ├── http.c / http.h
│
├── tests/
│   └── test_queue.c
│
├── python/
│   ├── client_stress.py
│   ├── benchmark.py
│   ├── export_html.py
│   ├── dashboard.html (généré)
│
├── scripts/
│   ├── run_all.sh
│   ├── monitor.sh
│
├── docs/
│   ├── rapport.tex
│   ├── rapport.pdf (généré)
│
├── Makefile
├── rebuild_project.py
├── create_http_files.py
├── results.json / results.xlsx (générés)
└── README.md
````

---

# 🧪 Tests unitaires C

### Exécution

```bash
make test
```

### Tests réalisés

* Validité de la FIFO (queue générique).
* Synchronisation multi-producteurs / multi-consommateurs.

---

# 🛠️ Compilation & Exécution

## 💻 Compilation complète

```bash
make clean
make -j$(nproc)
```

## ▶️ Exécution des serveurs

```bash
make run_mono
make run_multi
make run_mono_http
make run_multi_http
```

## 🛑 Arrêt de tous les serveurs

```bash
make kill_servers
```

---

# 🔧 Reconstruction automatique du projet

Script intelligent :

```bash
python3 rebuild_project.py
```

Rôle :

* régénération des fichiers HTTP,
* nettoyage complet,
* re-compilation,
* exécution des tests,
* vérification d’intégrité.

---

# 🚀 Pipeline complet : Build + Benchmarks + Graphiques

Lancement :

```bash
./scripts/run_all.sh
```

Automatisation :

1. Compilation C
2. Vérification env Python
3. Benchmarks TCP/HTTP
4. Export JSON/XLSX
5. Génération dashboard Plotly

---

# 📈 Dashboard HTML interactif

### Génération :

```bash
python3 python/export_html.py
```

### Ouverture :

```bash
xdg-open python/dashboard.html
```

Contenu du dashboard :

* courbes de latence (mean, median, p95, p99)
* throughput en rps
* consommation CPU/RAM
* comparatif mono-thread vs multi-thread

---

# 🧠 Architecture logicielle

## 🟦 Queue FIFO Générique (Thread-safe)

* tableau circulaire
* mutex + conditions
* supporte tout type : `void*`
* utilisée par `serveur_multi_http`

## 🟧 Pool de threads

* workers permanents
* évite le coût d’allocation de threads
* architecture industrielle

## 📊 Analyse des performances

| Architecture           | Performances                          |
| ---------------------- | ------------------------------------- |
| HTTP Multi > HTTP Mono | ✔ Scalabilité bien supérieure         |
| TCP Multi  > TCP Mono  | ✔ Latence réduite et throughput élevé |

---

# 🔒 Sécurité & Robustesse

* Sanitizers intégrés :

```bash
make debug
```

* Monitoring CPU/RAM intégré.
* Scripts durcis (`run_all.sh` → bullet-proof).
* Reconstruction automatique en cas d’erreur.

---

# 📝 Rapport académique (LaTeX)

Disponible dans :

```
docs/rapport.tex
docs/rapport.pdf
```

Contient :

* Contexte et objectifs
* Modélisation & architecture
* Résultats expérimentaux
* Graphiques et analyse
* Conclusion professionnelle

---

# 👤 Auteur

**Walid Ben Touhami**
**Yassin Ben Aoun**
**Ghada Sakouhi**
**Islem Ben Chaabene**


Ingénieurs Informatique — Systèmes & Réseaux
Serveurs C Haute Performance • Benchmarking • DevOps • Architecture Logicielle

---

# 📄 Licence

Ce projet est distribué sous licence **MIT**, permettant un usage libre académique et professionnel.

```

---

