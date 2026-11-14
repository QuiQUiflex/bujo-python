"""Tests de la configuration des fichiers de logs."""

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from bujo.logging_config import setup_logging


@pytest.fixture(autouse=True)
def clean_handlers() -> Iterator[None]:
    """Détache les fichiers de logs ajoutés pendant chaque test."""
    yield
    logger = logging.getLogger("bujo")
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
            handler.close()


def test_creates_the_log_directory(tmp_path: Path) -> None:
    """Le dossier des logs est créé s'il n'existe pas."""
    log_dir = tmp_path / "logs"
    setup_logging(log_dir)
    assert log_dir.is_dir()


def test_debug_file_receives_everything(tmp_path: Path) -> None:
    """Le fichier de debug reçoit tous les niveaux de messages."""
    logger = setup_logging(tmp_path)
    logger.debug("message de debug")
    logger.error("message d'erreur")
    content = (tmp_path / "debug.log").read_text(encoding="utf-8")
    assert "message de debug" in content
    assert "message d'erreur" in content


def test_error_file_receives_only_errors(tmp_path: Path) -> None:
    """Le fichier d'erreurs ne reçoit que ERROR et CRITICAL."""
    logger = setup_logging(tmp_path)
    logger.info("message d'information")
    logger.error("message d'erreur")
    logger.critical("message critique")
    content = (tmp_path / "errors.log").read_text(encoding="utf-8")
    assert "message d'information" not in content
    assert "message d'erreur" in content
    assert "message critique" in content


def test_messages_from_submodules_are_saved(tmp_path: Path) -> None:
    """Les messages des modules du paquet arrivent dans les fichiers."""
    setup_logging(tmp_path)
    logging.getLogger("bujo.entries").error("erreur dans entries")
    content = (tmp_path / "errors.log").read_text(encoding="utf-8")
    assert "| ERROR    | bujo.entries | erreur dans entries" in content


def test_no_duplicates_when_called_twice(tmp_path: Path) -> None:
    """Appeler setup_logging deux fois n'écrit pas les messages en double."""
    setup_logging(tmp_path)
    logger = setup_logging(tmp_path)
    logger.error("une seule fois")
    content = (tmp_path / "errors.log").read_text(encoding="utf-8")
    assert content.count("une seule fois") == 1
    file_handlers = [
        handler for handler in logger.handlers
        if isinstance(handler, logging.FileHandler)
    ]
    assert len(file_handlers) == 2