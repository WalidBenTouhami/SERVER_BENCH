# Serveur TCP Mono-thread vs Multi-thread en C (Projet complet)

Ce projet compare deux serveurs TCP écrits en C :
- un serveur **mono-thread** (séquentiel) : `serveur_mono`
- un serveur **multi-thread** avec **pool de threads** et **file d'attente bornée** : `serveur_multi`

Le projet comprend :
- du code C (serveurs + queue thread-safe)
- des tests unitaires C (file d'attente)
- un client de stress Python
- un benchmark automatisé (latence, débit, CPU, mémoire)
- des graphiques (matplotlib)
- des scripts shell DevOps (build, tests, benchmark)
- un rapport LaTeX rédigé (structure 5–7 pages, avec emplacements pour graphes)

Voir `INSTALL.md` pour l'installation et `docs/rapport.tex` pour le rapport.
