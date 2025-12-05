---

# ✅ **README.md**

---

# 🖥️ **Serveur TCP Mono-thread vs Multi-thread en C (Projet Systèmes d’Exploitation Avancés)**

**Auteur : Walid Ben Touhami**
**Technologies : C11 · POSIX Threads · Python3 · Linux Ubuntu 24.04 · GitHub CI/CD**

---

## 📌 **Résumé du projet**

Ce projet met en œuvre et compare **deux architectures complètes de serveurs TCP** en C :

* ✔ **serveur_mono** → modèle séquentiel, mono-thread
* ✔ **serveur_multi** → modèle concurrent basé sur :

  * un **thread acceptor**
  * un **pool fixe de 8 workers**
  * une **queue FIFO thread-safe** (mutex + condition variables)

Chaque requête simule un **traitement intensif** :
→ 100 000 calculs `sqrt()` + délai aléatoire 10–100 ms.
Cela permet d'obtenir une comparaison **réaliste** mono vs multi-thread.

Le projet inclut également :

* un **client de stress Python**
* un **benchmark complet** (latence, throughput, CPU, RAM)
* des **graphiques d’analyse**
* une **CI/CD GitHub Actions**
* un **générateur automatique de slides PowerPoint**
* un **rapport LaTeX** pour soutenance

Ce projet constitue un cas d’étude complet en **programmation système, threading, performance et architecture logicielle**.

---

## 📂 **Structure du projet**

```
server_project/
│
├── src/
│   ├── serveur_mono.c
│   ├── serveur_multi.c
│   ├── queue.c
│   └── queue.h
│
├── tests/
│   └── test_queue.c         # tests unitaires FIFO
│
├── benchmark/
│   ├── client.py            # client de stress
│   ├── benchmark.py         # benchmark global
│   └── plot_results.py      # graphiques
│
├── docs/
│   ├── rapport.tex
│   └── diagrammes UML (optionnel)
│
├── generate_ppt.py          # génération automatique PPTX
├── Makefile                 # build Pro (debug, test, sanitizer, run…)
├── INSTALL.md               # installation & exécution
└── README.md                # ce fichier
```

---

# 🚀 **Compilation & exécution**

## 🔧 **Compilation standard**

```
make
```

## 🧹 Nettoyage

```
make clean
```

## 🐛 Mode debug (ASan + UBSan)

```
make debug
```

---

# ▶️ **Exécution des serveurs**

## Mono-thread

```
make run_mono
```

Disponible sur **port 5050**.

## Multi-thread

```
make run_multi
```

Disponible sur **port 5051**.

## Arrêt des serveurs

```
make kill_servers
```

---

# 🧪 **Tests unitaires**

```
make test
```

Teste entièrement la **file FIFO thread-safe** (mutex + cond + shutdown).

Sortie typique :

```
[TEST] consumer received 1000 items
[TEST] test_queue terminé.
```

---

# 📊 **Benchmark complet (Python)**

Le benchmark exécute :

* 10, 50, 100, 200, 300 clients simultanés
* Mesure :

  * latence moyenne
  * P95, P99
  * throughput (req/s)
  * CPU total & par cœur (psutil)
  * consommation mémoire (RSS)
* Export :

  * JSON
  * Excel
* Génère 6 graphiques :

  * débit vs charge
  * latence P99 vs clients
  * heatmap CPU
  * consommation mémoire
  * speedup multi-thread
  * saturation des workers

### Exécution :

```
python3 benchmark/benchmark.py
```

---

# 📑 **Rapport LaTeX (soutenance)**

Le dossier `docs/` contient :

* un rapport `.tex` complet (plan 5–7 pages)
* sections "architecture", "analyse des résultats", "limites", "perspectives"
* espaces réservés pour les graphiques produits par le benchmark

Compilation :

```
cd docs
pdflatex rapport.tex
```

---

# 🎞️ **Présentation PowerPoint (générée automatiquement)**

Le script Python génère un **PPTX académique 16:9 complet** :

```
python3 generate_ppt.py
```

Sortie :

```
presentation_server_project.pptx
```

---

# 🧠 **Architecture conceptuelle**

### **Mono-thread**

```
while (1) {
    client = accept();
    traiter(client);
}
```

→ Simple mais saturé dès ~10 connexions.

### **Multi-thread**

```
acceptor → queue → workers (×8)
```

→ Scalabilité, réduction du temps de réponse, meilleure utilisation CPU.

---

# 📈 **Résultats attendus**

* Le multi-thread devient **4× à 7× plus rapide**
* Le mono-thread sature rapidement
* Le speedup augmente proportionnellement au nombre de workers
* Le contexte fixe du pool évite l’overhead de création de threads

---

# 🔮 **Perspectives d’évolution**

* Passage à **epoll** + threads hybrides
* Version **multi-processus** avec `fork()` + mémoire partagée
* Implémentation **lock-free MPMC**
* Intégration Docker & Kubernetes
* Monitoring Prometheus + Grafana

---

# 📜 Licence

Projet académique — diffusion et réutilisation autorisées dans un cadre pédagogique.

---



