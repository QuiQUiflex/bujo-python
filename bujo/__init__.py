"""bujo : une bibliothèque Python pour tenir un Bullet Journal.

Les classes principales sont importables directement depuis le
paquet, par exemple ``from bujo import Journal, Signifier``.
L'affichage se trouve dans ``bujo.display``.
"""

import logging

from bujo.entries import Entry, Event, Note, Task
from bujo.enums import Signifier, TaskStatus
from bujo.exceptions import (
    BujoError,
    DuplicateEntryError,
    EmptyNameError,
    EntryNotFoundError,
    InvalidDateError,
    InvalidTransitionError,
    ValidationError,
)
from bujo.journal import Journal
from bujo.logging_config import setup_logging
from bujo.logs import DailyLog, Log, MonthlyLog

__version__ = "0.2.0"

__all__ = [
    "BujoError",
    "DailyLog",
    "DuplicateEntryError",
    "EmptyNameError",
    "Entry",
    "EntryNotFoundError",
    "Event",
    "InvalidDateError",
    "InvalidTransitionError",
    "Journal",
    "Log",
    "MonthlyLog",
    "Note",
    "Signifier",
    "Task",
    "TaskStatus",
    "ValidationError",
    "setup_logging",
]

# Bonne pratique pour une bibliothèque : rien n'est affiché tant que
# l'utilisateur n'a pas configuré les logs (avec setup_logging).
logging.getLogger(__name__).addHandler(logging.NullHandler())