Projet : Serveur TCP Haute Performance (C multi-thread + Python benchmark)

- Développement de serveurs TCP mono-thread et multi-thread en C (POSIX).
- File d'attente FIFO thread-safe bornée (mutex + variables de condition).
- Pool de threads (workers) pour le traitement concurrent des connexions.
- Client de stress Python (ThreadPoolExecutor) jusqu'à 300 connexions.
- Benchmark automatisé : latence moyenne, médiane, P95, P99, débit (req/s), CPU, mémoire.
- Génération de graphiques (matplotlib) et scripts DevOps (build, tests, run_all).
- Rapport LaTeX structuré présentant architecture, résultats et analyse de performance.

Stack : C (POSIX), sockets TCP/IP, pthreads, Python 3, psutil, pandas, matplotlib, Makefile, shell.
