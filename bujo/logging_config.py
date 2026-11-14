"""Configuration des fichiers de logs techniques du projet.

Les modules de bujo écrivent leurs messages avec ``logging``. Par
défaut, ces messages ne vont nulle part. La fonction ``setup_logging``
les envoie dans deux fichiers, comme le demande le sujet.
"""

import logging
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEBUG_FILE = "debug.log"
ERROR_FILE = "errors.log"


def setup_logging(log_dir: str | Path = "logs") -> logging.Logger:
    """Envoie les messages du paquet bujo dans deux fichiers.

    ``debug.log`` reçoit tous les messages (niveau DEBUG et plus) et
    ``errors.log`` ne reçoit que les erreurs (ERROR et CRITICAL).
    Appeler la fonction plusieurs fois ne crée pas de doublons : les
    anciens fichiers de logs sont d'abord détachés.

    Args:
        log_dir: Dossier des fichiers de logs, créé s'il n'existe pas.

    Returns:
        Le logger du paquet ``bujo``.
    """
    directory = Path(log_dir)
    directory.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("bujo")
    logger.setLevel(logging.DEBUG)

    # On retire les fichiers déjà branchés, pour éviter les doublons.
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
            handler.close()

    formatter = logging.Formatter(LOG_FORMAT)
    files = ((DEBUG_FILE, logging.DEBUG), (ERROR_FILE, logging.ERROR))
    for filename, level in files:
        handler = logging.FileHandler(directory / filename, encoding="utf-8")
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger