"""Journal : point d'entrée principal pour gérer le Bullet Journal."""

import unicodedata
from datetime import date, time
from typing import Optional

from bujo.entries import Entry, Event, Note, Task
from bujo.enums import Signifier
from bujo.exceptions import EntryNotFoundError
from bujo.logs import DailyLog, Log, MonthlyLog


def _normalize(text: str) -> str:
    """Prépare un texte pour la recherche.

    Le texte est mis en minuscules, ses accents et ses espaces sont
    retirés : « Réviser Python » devient « reviserpython ».

    Args:
        text: Le texte à préparer.

    Returns:
        Le texte normalisé.
    """
    decomposed = unicodedata.normalize("NFD", text)
    without_accents = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return "".join(without_accents.casefold().split())


class Journal:
    """Gestionnaire principal du Bullet Journal.

    Le journal range chaque entrée dans un Daily Log ou un Monthly Log.
    Le dictionnaire ``_locations`` retient la page de chaque entrée,
    pour la retrouver directement à partir de son identifiant.
    """

    def __init__(self) -> None:
        """Initialise un journal vide."""
        self._daily_logs: dict[date, DailyLog] = {}
        self._monthly_logs: dict[tuple[int, int], MonthlyLog] = {}
        self._locations: dict[str, Log] = {}

    # ------------------------------------------------------------------
    # Méthodes internes
    # ------------------------------------------------------------------

    def _store(self, log: Log, entry: Entry) -> None:
        """Range une entrée dans une page et retient où elle se trouve."""
        log.add(entry)
        self._locations[entry.id] = log

    def _find_log(self, entry_id: str) -> Log:
        """Renvoie la page qui contient l'entrée.

        Args:
            entry_id: L'identifiant de l'entrée.

        Returns:
            La page (Daily Log ou Monthly Log) de l'entrée.

        Raises:
            EntryNotFoundError: Si aucune entrée n'a cet identifiant.
        """
        try:
            return self._locations[entry_id]
        except KeyError:
            raise EntryNotFoundError(
                f"Aucune entrée avec l'identifiant {entry_id!r}."
            ) from None

    # ------------------------------------------------------------------
    # Pages du journal
    # ------------------------------------------------------------------

    def daily_log(self, day: Optional[date] = None) -> DailyLog:
        """Renvoie le Daily Log d'un jour, en le créant si besoin.

        Args:
            day: Le jour voulu (aujourd'hui par défaut).

        Returns:
            Le Daily Log de ce jour.
        """
        if day is None:
            day = date.today()
        if day not in self._daily_logs:
            self._daily_logs[day] = DailyLog(day)
        return self._daily_logs[day]

    def monthly_log(
        self, year: Optional[int] = None, month: Optional[int] = None
    ) -> MonthlyLog:
        """Renvoie le Monthly Log d'un mois, en le créant si besoin.

        Args:
            year: L'année voulue (l'année en cours par défaut).
            month: Le mois voulu (le mois en cours par défaut).

        Returns:
            Le Monthly Log de ce mois.
        """
        today = date.today()
        key = (year or today.year, month or today.month)
        if key not in self._monthly_logs:
            self._monthly_logs[key] = MonthlyLog(*key)
        return self._monthly_logs[key]

    @property
    def daily_logs(self) -> list[DailyLog]:
        """Les Daily Logs, du plus ancien au plus récent."""
        return sorted(self._daily_logs.values(), key=lambda log: log.day)

    @property
    def monthly_logs(self) -> list[MonthlyLog]:
        """Les Monthly Logs, du plus ancien au plus récent."""
        return sorted(
            self._monthly_logs.values(),
            key=lambda log: (log.year, log.month),
        )

    # ------------------------------------------------------------------
    # Ajout d'entrées
    # ------------------------------------------------------------------

    def add_task(
        self,
        name: str,
        description: str = "",
        day: Optional[date] = None,
        signifier: Optional[Signifier] = None,
    ) -> Task:
        """Ajoute une tâche au Daily Log d'un jour.

        Args:
            name: Le nom de la tâche.
            description: Sa description (facultative).
            day: Le jour de la tâche (aujourd'hui par défaut).
            signifier: Un signifiant facultatif (priorité, idée).

        Returns:
            La tâche créée.
        """
        log = self.daily_log(day)
        task = Task(name, description, log.day, signifier)
        self._store(log, task)
        return task

    def add_monthly_task(
        self,
        name: str,
        description: str = "",
        year: Optional[int] = None,
        month: Optional[int] = None,
        signifier: Optional[Signifier] = None,
    ) -> Task:
        """Ajoute une tâche au Monthly Log d'un mois.

        La tâche est datée du premier jour du mois.

        Args:
            name: Le nom de la tâche.
            description: Sa description (facultative).
            year: L'année (l'année en cours par défaut).
            month: Le mois (le mois en cours par défaut).
            signifier: Un signifiant facultatif (priorité, idée).

        Returns:
            La tâche créée.
        """
        log = self.monthly_log(year, month)
        first_day = date(log.year, log.month, 1)
        task = Task(name, description, first_day, signifier)
        self._store(log, task)
        return task

    def add_event(
        self,
        name: str,
        day: date,
        event_time: Optional[time] = None,
        description: str = "",
    ) -> Event:
        """Ajoute un événement au Daily Log de son jour.

        Args:
            name: Le nom de l'événement.
            day: Le jour de l'événement.
            event_time: L'heure de l'événement (facultative).
            description: Sa description (facultative).

        Returns:
            L'événement créé.
        """
        event = Event(
            name, description, event_date=day, event_time=event_time
        )
        self._store(self.daily_log(day), event)
        return event

    def add_note(self, name: str, description: str = "") -> Note:
        """Ajoute une note au Daily Log d'aujourd'hui.

        Args:
            name: Le titre de la note.
            description: Son contenu (facultatif).

        Returns:
            La note créée.
        """
        note = Note(name, description)
        self._store(self.daily_log(note.log_date), note)
        return note

    # ------------------------------------------------------------------
    # Consultation
    # ------------------------------------------------------------------

    def get_entry(self, entry_id: str) -> Entry:
        """Renvoie une entrée à partir de son identifiant.

        Raises:
            EntryNotFoundError: Si aucune entrée n'a cet identifiant.
        """
        return self._find_log(entry_id).get(entry_id)

    def get_task(self, entry_id: str) -> Task:
        """Renvoie une tâche à partir de son identifiant.

        Raises:
            EntryNotFoundError: Si l'entrée n'existe pas ou si ce n'est
                pas une tâche.
        """
        entry = self.get_entry(entry_id)
        if not isinstance(entry, Task):
            raise EntryNotFoundError(
                f"L'entrée {entry_id!r} n'est pas une tâche."
            )
        return entry

    @property
    def entries(self) -> list[Entry]:
        """Toutes les entrées du journal, page par page."""
        result: list[Entry] = []
        for log in [*self.daily_logs, *self.monthly_logs]:
            result.extend(log.entries)
        return result

    @property
    def pending_tasks(self) -> list[Task]:
        """Les tâches à faire, triées par date."""
        tasks = [
            entry
            for entry in self.entries
            if isinstance(entry, Task) and entry.is_pending()
        ]
        return sorted(tasks, key=lambda task: task.log_date)

    def find_by_name(self, query: str) -> list[Entry]:
        """Cherche les entrées dont le nom contient un texte.

        La recherche ignore la casse, les accents et les espaces.

        Args:
            query: Le texte recherché.

        Returns:
            Les entrées trouvées.
        """
        wanted = _normalize(query)
        return [
            entry for entry in self.entries
            if wanted in _normalize(entry.name)
        ]

    def events_on(self, day: date) -> list[Event]:
        """Renvoie les événements d'un jour (liste vide si aucun)."""
        log = self._daily_logs.get(day)
        if log is None:
            return []
        return [entry for entry in log.entries if isinstance(entry, Event)]

    # ------------------------------------------------------------------
    # Modification
    # ------------------------------------------------------------------

    def complete_task(self, entry_id: str) -> None:
        """Marque une tâche comme terminée."""
        self.get_task(entry_id).complete()

    def cancel_task(self, entry_id: str) -> None:
        """Marque une tâche comme abandonnée."""
        self.get_task(entry_id).cancel()

    def delete_entry(self, entry_id: str) -> None:
        """Supprime définitivement une entrée du journal.

        Raises:
            EntryNotFoundError: Si aucune entrée n'a cet identifiant.
        """
        log = self._find_log(entry_id)
        log.remove(log.get(entry_id))
        del self._locations[entry_id]

    def set_signifier(
        self, entry_id: str, signifier: Optional[Signifier]
    ) -> None:
        """Ajoute, change ou retire le signifiant d'une entrée."""
        self.get_entry(entry_id).signifier = signifier

    # ------------------------------------------------------------------
    # Migration et planification
    # ------------------------------------------------------------------

    def migrate_task(self, entry_id: str, target_day: date) -> Task:
        """Migre une tâche vers un autre jour.

        La tâche d'origine reste dans sa page avec le symbole « > ».
        Une copie « à faire » est ajoutée au Daily Log du jour visé.

        Args:
            entry_id: L'identifiant de la tâche.
            target_day: Le jour vers lequel migrer.

        Returns:
            La nouvelle tâche (la copie).
        """
        copy = self.get_task(entry_id).migrate(target_day)
        self._store(self.daily_log(target_day), copy)
        return copy

    def migrate_day(self, source_day: date, target_day: date) -> list[Task]:
        """Migre toutes les tâches à faire d'un jour vers un autre.

        Args:
            source_day: Le jour d'origine.
            target_day: Le jour visé.

        Returns:
            Les nouvelles tâches créées (liste vide si rien à migrer).
        """
        source = self._daily_logs.get(source_day)
        if source is None:
            return []
        return [
            self.migrate_task(task.id, target_day)
            for task in source.pending_tasks
        ]

    def migrate_month(self, year: int, month: int) -> list[Task]:
        """Migre les tâches à faire d'un Monthly Log vers le mois suivant.

        Args:
            year: L'année du Monthly Log d'origine.
            month: Le mois du Monthly Log d'origine.

        Returns:
            Les nouvelles tâches créées (liste vide si rien à migrer).
        """
        source = self._monthly_logs.get((year, month))
        if source is None:
            return []
        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1
        target = self.monthly_log(next_year, next_month)
        first_day = date(next_year, next_month, 1)
        copies = []
        for task in source.pending_tasks:
            copy = task.migrate(first_day)
            self._store(target, copy)
            copies.append(copy)
        return copies

    def schedule_task(self, entry_id: str, target_date: date) -> Task:
        """Planifie une tâche dans un mois futur.

        La tâche d'origine reste dans sa page avec le symbole « < ».
        Une copie est ajoutée au Monthly Log du mois visé.

        Args:
            entry_id: L'identifiant de la tâche.
            target_date: Une date du mois visé.

        Returns:
            La nouvelle tâche (la copie).
        """
        copy = self.get_task(entry_id).schedule(target_date)
        target = self.monthly_log(target_date.year, target_date.month)
        self._store(target, copy)
        return copy
