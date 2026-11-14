# bujo : une bibliothèque Python de Bullet Journal

Projet du cours de Python (cycle ingénieur, 1re année).

`bujo` permet de tenir un Bullet Journal en Python : tâches, événements
et notes, rangés dans des Daily Logs et des Monthly Logs, avec la
migration des tâches non terminées et l'affichage avec les symboles du
rapid logging.

## Équipe

- Ethan
- Riyane
- Antoine

## Installation

Prérequis : Anaconda (ou Miniconda) et Git.

```bash
git clone git@github.com:QuiQUiflex/bujo-python.git
cd bujo-python
conda create -n bujo python=3.12 -y
conda activate bujo
pip install -r requirements.txt
```

## Utilisation

```python
from datetime import date, timedelta

from bujo import Journal, Signifier
from bujo.display import render_log

journal = Journal()
journal.add_task("Réviser Python", "Chapitre POO", signifier=Signifier.PRIORITY)
journal.add_note("Idée", "Une appli de BuJo en ligne de commande")
journal.migrate_day(date.today(), date.today() + timedelta(days=1))
print(render_log(journal.daily_log()))
```

Démonstration complète :

```bash
python demo.py
```

Ce script affiche un journal dans le terminal et remplit les fichiers
`logs/debug.log` (tous les messages) et `logs/errors.log` (erreurs).

## Fonctionnalités

Niveau 1 :

- ajouter, terminer, supprimer et afficher des tâches ;
- cycle de vie complet d'une tâche : à faire, terminée, migrée,
  planifiée, abandonnée ;
- trois types d'entrées : tâches, événements (date et heure), notes ;
- identifiant unique pour chaque entrée.

Niveau 2 :

- organisation en Daily Logs et Monthly Logs ;
- migration d'un jour vers un autre et d'un mois vers le suivant ;
- signifiants (priorité, idée) ;
- affichage avec les symboles du rapid logging.

## Tests et qualité

```bash
pytest --cov=bujo --cov-report=term-missing   # tests et couverture
flake8 .                                      # respect de PEP 8
pydocstyle .                                  # présence des docstrings
```

Ces trois vérifications sont aussi lancées automatiquement par GitHub
Actions à chaque push (`.github/workflows/ci.yml`).

## Documentation

```bash
sphinx-build -b html docs docs/_build/html
```

Ouvrir ensuite `docs/_build/html/index.html` dans un navigateur. La
conception (diagrammes de classes et d'états) est décrite dans
[docs/conception.md](docs/conception.md).

## Structure du projet

```text
bujo-python/
├── bujo/                  # code de la bibliothèque
│   ├── __init__.py        # API publique du paquet
│   ├── enums.py           # états des tâches, signifiants
│   ├── exceptions.py      # exceptions personnalisées
│   ├── validation.py      # validation des saisies
│   ├── entries.py         # Entry, Task, Event, Note
│   ├── logs.py            # Log, DailyLog, MonthlyLog
│   ├── journal.py         # Journal (point d'entrée principal)
│   ├── display.py         # affichage avec les symboles
│   └── logging_config.py  # fichiers de logs techniques
├── tests/                 # tests unitaires (pytest)
├── docs/                  # documentation Sphinx et conception
├── logs/                  # fichiers de logs produits par la démo
├── demo.py                # script de démonstration
└── requirements.txt       # dépendances
```

## Organisation du travail

Chaque fonctionnalité est développée sur une branche dédiée, puis
fusionnée dans `main` par une Pull Request relue par un autre membre
de l'équipe. Les versions stables sont marquées par des tags
(`v0.2.0` : niveaux 1 et 2).