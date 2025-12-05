# Guide d'installation

## 1. Prérequis (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install -y build-essential python3 python3-pip python3-venv make git
sudo apt install -y python3-psutil python3-pandas python3-matplotlib plotly=="5.24.1" kaleido
```

## 2. Générer le projet (si ce n'est pas déjà fait)

Après avoir copié `rebuild_project.py` :

```bash
python3 rebuild_project.py
cd server_project
```

## 3. Compilation des serveurs C

```bash
make clean
make all
```

Mode debug avec sanitizers :

```bash
make debug
```

## 4. Environnement Python

```bash
cd python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. Lancer un benchmark complet

Depuis la racine du projet :

```bash
cd ..
./scripts/run_all.sh
```

Les résultats sont dans `python/results.json`, `python/results.xlsx`
et les figures dans `python/figures/`.

## 6. Tests

```bash
./scripts/run_tests.sh
```

## 7. Nettoyage

```bash
./scripts/clean_project.sh
```
