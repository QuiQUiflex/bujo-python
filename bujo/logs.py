"""Pages du journal : Daily Logs et Monthly Logs."""

from abc import ABC, abstractmethod
from datetime import date

from bujo.entries import Entry, Task
from bujo.exceptions import EntryNotFoundError


class Log(ABC):
    """Classe abstraite pour les pages de journal (Daily, Monthly)."""

    def __init__(self) -> None:
        """Initialise une page vide."""
        self._entries: list[Entry] = []

    def add(self, entry: Entry) -> None:
        """Ajoute une entrée à la page."""
        self._entries.append(entry)

    def remove(self, entry: Entry) -> None:
        """Supprime une entrée de la page."""
        self._entries.remove(entry)

    def get(self, entry_id: str) -> Entry:
        """Récupère une entrée par son ID.

        Lève EntryNotFoundError si absente.
        """
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        raise EntryNotFoundError(f"Entrée {entry_id} non trouvée")

    @property
    def entries(self) -> list[Entry]:
        """Toutes les entrées de la page."""
        return self._entries.copy()

    @property
    def tasks(self) -> list[Task]:
        """Toutes les tâches de la page."""
        return [e for e in self._entries if isinstance(e, Task)]

    @property
    def pending_tasks(self) -> list[Task]:
        """Tâches à faire (état TODO)."""
        return [t for t in self.tasks if t.is_pending()]

    @property
    @abstractmethod
    def title(self) -> str:
        """Titre de la page."""

    @property
    @abstractmethod
    def accepts(self) -> type:
        """Type d'entrée accepté par cette page."""


class DailyLog(Log):
    """Page pour un jour : Daily Log."""

    def __init__(self, day: date) -> None:
        """Crée un Daily Log pour le jour passé en paramètre."""
        super().__init__()
        self.day = day

    @property
    def title(self) -> str:
        """Titre formaté : 'Daily Log du JJ/MM/AAAA'."""
        return f"Daily Log du {self.day.strftime('%d/%m/%Y')}"

    @property
    def accepts(self) -> type:
        """Accepte toutes les entrées."""
        return object


class MonthlyLog(Log):
    """Page pour un mois : Monthly Log."""

    def __init__(self, year: int, month: int) -> None:
        """Crée un Monthly Log pour l'année et le mois passés."""
        super().__init__()
        self.year = year
        self.month = month

    @property
    def title(self) -> str:
        """Titre formaté : 'Monthly Log MM/AAAA'."""
        return f"Monthly Log {self.month:02d}/{self.year}"

    @property
    def accepts(self) -> type:
        """Accepte les tâches planifiées (SCHEDULED)."""
        return Task
