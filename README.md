# 🚀 Serveur TCP & HTTP Hautes Performances — C/POSIX

## ⚡ Extreme Edition — Multi-threading • Queue FIFO • Benchmarks • UML • Mermaid • CI/CD

---

<p align="center">
  <img src="https://img.shields.io/badge/C89-POSIX-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/MultiThreading-pthreads-purple?style=flat-square"/>
  <img src="https://img.shields.io/badge/HTTP-1.1-orange?style=flat-square"/>
  <img src="https://img.shields.io/badge/Benchmark-Python3-yellow?style=flat-square"/>
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square"/>
</p>

---

# 🔧 Badges GitHub Actions CI/CD

| Workflow                                 | Badge                                                                                                                                         |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Build & Test (GCC + Make + Valgrind)** | ![Build](https://img.shields.io/github/actions/workflow/status/WalidBenTouhami/server_project/build.yml?branch=main\&style=flat-square)       |
| **Static Analysis (Cppcheck)**           | ![Cppcheck](https://img.shields.io/github/actions/workflow/status/WalidBenTouhami/server_project/cppcheck.yml?branch=main\&style=flat-square) |
| **CodeQL Security Scan**                 | ![CodeQL](https://img.shields.io/github/actions/workflow/status/WalidBenTouhami/server_project/codeql.yml?branch=main\&style=flat-square)     |
| **Python Benchmarks CI**                 | ![Python](https://img.shields.io/github/actions/workflow/status/WalidBenTouhami/server_project/benchmarks.yml?branch=main\&style=flat-square) |

---

# 📚 Table des matières automatique

* [🎥 GIF Démonstrations](#-gif-démonstrations)
* [📦 Projet — Version FR/EN](#-projet--version-fren)
* [🧠 Diagrams Mermaid intégrés](#-diagrams-mermaid-intégrés)
* [📊 Benchmarks](#-benchmarks)
* [🛠 Installation](#-installation)
* [⚙ Exécution](#-exécution)
* [🧪 Tests & Validation](#-tests--validation)
* [📡 API HTTP](#-api-http)
* [📂 Architecture du projet](#-architecture-du-projet)
* [🚀 Pipeline DevOps complet](#-pipeline-devops-complet)
* [👤 Auteurs](#-auteurs)
* [📜 Licence](#-licence)

---

# 🎥 GIF Démonstrations



### Multi-thread server execution

![server-multi](docs/gif/server_multi.gif)

### Benchmark execution

![bench](docs/gif/benchmark.gif)

---

# 📦 **Projet — Version FR/EN**

## 🇫🇷 Version Française

Ce projet implémente **4 serveurs haute performance** basés sur :

* Sockets POSIX bas niveau
* Multi-threading (pthreads)
* Queue FIFO thread-safe
* HTTP parser minimaliste
* Benchmarks avancés Python
* Automatisation complète (Makefile, scripts, DevOps)

| Serveur            | Protocole | Architecture        |
| ------------------ | --------- | ------------------- |
| serveur_mono       | TCP       | mono-thread         |
| serveur_multi      | TCP       | multi-thread + FIFO |
| serveur_mono_http  | HTTP 1.1  | mono-thread         |
| serveur_multi_http | HTTP 1.1  | multi-thread + FIFO |

---

## 🇬🇧 English Summary

This project provides **4 high-performance network servers** using:

* POSIX low-level sockets
* Multi-threaded worker pool
* Thread-safe FIFO queue
* Minimal HTTP 1.1 router
* Python benchmark suite
* Full DevOps automation

---

# 🧠 Diagrams Mermaid intégrés

---

## 1) **Architecture Globale**

```mermaid
flowchart LR
    classDef client fill:#0af,color:#fff;
    classDef accept fill:#09f,color:#fff;
    classDef queue fill:#f90,color:#000;
    classDef worker fill:#6c0,color:#fff;
    classDef treat fill:#c0c,color:#fff;
    classDef resp fill:#555,color:#fff;

    A["Clients"]:::client --> B["accept()"]:::accept
    B --> C["Queue FIFO<br/>(mutex + condvar)"]:::queue
    C --> D["Worker 1"]:::worker
    C --> E["Worker 2"]:::worker
    C --> F["Worker N"]:::worker
    D --> G["Traitement"]:::treat
    E --> G
    F --> G
    G --> H["send()"]:::resp
```

---

## 2) **Queue FIFO Thread-Safe**

```mermaid
classDiagram
    class queue_t {
        queue_node_t* head
        queue_node_t* tail
        pthread_mutex_t mutex
        pthread_cond_t not_empty
        pthread_cond_t not_full
        size_t size
        size_t size_max
        +push(void*)
        +void* pop()
        +destroy()
    }

    class queue_node_t {
        void* data
        queue_node_t* next
    }

    queue_t --> queue_node_t
```

---

## 3) **Modèle de Threads — Dispatcher & Workers**

```mermaid
sequenceDiagram
    participant Client
    participant Dispatcher
    participant Queue
    participant Worker

    Client->>Dispatcher: accept()
    Dispatcher->>Queue: push(fd)
    Queue->>Worker: pop(fd)
    Worker->>Worker: traitement_lourd()
    Worker->>Client: send()
```

---

# 📊 Benchmarks

Les figures sont auto-générées :

![Throughput](python/figures/1-throughput.png)
![Latency](python/figures/2-latency_p99.png)
![CPU](python/figures/3-cpu.png)
![Memory](python/figures/4-memory.png)

---

# 🛠 Installation

```bash
sudo apt install build-essential python3 python3-venv python3-pip
git clone https://github.com/WalidBenTouhami/server_project.git
cd server_project
make -j$(nproc)
```

---

# ⚙ Exécution

```bash
make run_mono
make run_multi
make run_mono_http
make run_multi_http
```

---

# 🧪 Tests & Validation

```bash
make test
valgrind --leak-check=full ./bin/serveur_multi
valgrind --tool=helgrind ./bin/serveur_multi
make debug
```

---

# 📡 API HTTP

| Route    | Description       |
| -------- | ----------------- |
| `/`      | Accueil           |
| `/hello` | JSON response     |
| `/time`  | Timestamp         |
| `/stats` | Worker statistics |

Exemple :

```json
{
  "msg": "Hello from HTTP server",
  "requests": 128,
  "worker": 3
}
```

---

# 📂 Architecture du projet

```
src/
├── http.c / http.h
├── queue.c / queue.h
├── serveur_mono.c
├── serveur_multi.c
├── serveur_mono_http.c
└── serveur_multi_http.c
```

---

# 🚀 Pipeline DevOps complet

Pipeline exécuté via :

```bash
./scripts/run_interactive.sh
```

Ce pipeline réalise :

* Vérification & génération HTTP
* Build C (optimisations O3 + LTO)
* Génération UML (PlantUML → SVG + injection README)
* Génération PPTX + PDF
* Démarrage automatique des serveurs
* Tests HTTP (curl)
* Stress-tests TCP/HTTP
* Benchmarks extrêmes JSON/CSV/PNG/HTML
* Monitoring CPU/mémoire
* Kill propre multi-threads
* Exécution CI/CD GitHub Actions

---

# 👤 Auteurs

| Auteur                 | Rôle                                | Expertise                |
| ---------------------- | ----------------------------------- | ------------------------ |
| **Walid Ben Touhami**  | DevOps, Multi-threading, Benchmarks | High-performance systems |
| **Yassin Ben Aoun**    | HTTP parser                         | Protocol engineering     |
| **Ghada Sakouhi**      | FIFO Queue, UML                     | Software architecture    |
| **Islem Ben Chaabene** | TCP mono-thread                     | POSIX networking         |

---

# 📜 Licence

```
MIT License — Academic Use Only
```

---


