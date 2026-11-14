"""Configuration de Sphinx pour la documentation de bujo."""

import os
import sys

# Permet à Sphinx de trouver le paquet bujo (dossier parent de docs/).
sys.path.insert(0, os.path.abspath(".."))

project = "bujo"
author = "Équipe bujo"
copyright = "2026, Équipe bujo"
release = "0.2.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

language = "fr"
exclude_patterns = ["_build"]
html_theme = "alabaster"
autodoc_member_order = "bysource"
