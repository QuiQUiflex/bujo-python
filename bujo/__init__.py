"""Bibliothèque bujo : tenir un Bullet Journal en Python."""

import logging

__version__ = "0.1.0"

# Une bibliothèque ne doit rien afficher tant que l'application ne l'a
# pas demandé : le NullHandler absorbe les messages de log par défaut.
# Les fichiers de logs s'activent avec bujo.logging_config.setup_logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())
