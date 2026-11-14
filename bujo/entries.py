"""Modèle des entrées du journal : tâches, événements et notes.

Les trois types d'entrées héritent de la classe abstraite ``Entry``,
qui regroupe ce qu'elles ont en commun (identifiant, nom, description,
dates, signifiant). Chaque classe fille définit son propre symbole :
c'est un exemple de polymorphisme.
"""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import date, datetime, time

from bujo.enums import Signifier, TaskStatus
from bujo.exceptions import InvalidDateError, InvalidTransitionError
from bujo.validation import (
    validate_date,
    validate_description,
    validate_name,
    validate_signifier,
    validate_time,
)

logger = logging.getLogger(__name__)

# Règles du cycle de vie : seule une tâche « à faire » peut changer
# d'état. Les quatre autres états sont définitifs (décision de
# conception expliquée dans docs/conception.md).
_ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.TODO: {
        TaskStatus.DONE,
        TaskStatus.MIGRATED,
        TaskStatus.SCHEDULED,
        TaskStatus.CANCELLED,
    },
    TaskStatus.DONE: set(),
    TaskStatus.MIGRATED: set(),
    TaskStatus.SCHEDULED: set(),
    TaskStatus.CANCELLED: set(),
}

# Symbole affiché pour chaque état. Une tâche abandonnée garde sa
# puce : c'est son nom qui est barré à l'affichage (bujo.display).
_TASK_SYMBOLS: dict[TaskStatus, str] = {
    TaskStatus.TODO: "•",
    TaskStatus.DONE: "×",
    TaskStatus.MIGRATED: ">",
    TaskStatus.SCHEDULED: "<",
    TaskStatus.CANCELLED: "•",
}


class Entry(ABC):
    """Classe de base abstraite de toutes les entrées du journal.

    On ne crée jamais une ``Entry`` directement, mais une ``Task``, un
    ``Event`` ou une ``Note``. Les attributs sont privés (préfixe
    ``_``) et lus à travers des propriétés : c'est l'encapsulation.
    """

    def __init__(
        self,
        name: str,
        description: str,
        log_date: date | None = None,
        signifier: Signifier | None = None,
    ) -> None:
        """Crée une entrée.

        Args:
            name: Nom de l'entrée, qui ne doit pas être vide.
            description: Description de l'entrée (peut être vide).
            log_date: Date du log de l'entrée ; aujourd'hui par défaut.
            signifier: Signifiant optionnel (priorité ou idée).

        Raises:
            EmptyNameError: Si le nom est vide.
            ValidationError: Si la description ou le signifiant est
                invalide.
            InvalidDateError: Si ``log_date`` n'est pas une date.
        """
        if log_date is None:
            log_date = date.today()
        self._id: str = uuid.uuid4().hex
        self._name: str = validate_name(name)
        self._description: str = validate_description(description)
        self._created_at: datetime = datetime.now()
        self._log_date: date = validate_date(log_date)
        self._signifier: Signifier | None = validate_signifier(signifier)

    @property
    def id(self) -> str:
        """Identifiant unique de l'entrée (lecture seule)."""
        return self._id

    @property
    def name(self) -> str:
        """Nom de l'entrée."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Renomme l'entrée (le nouveau nom ne doit pas être vide)."""
        self._name = validate_name(value)

    @property
    def description(self) -> str:
        """La description de l'entrée."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Modifie la description : elle doit rester un texte."""
        self._description = validate_description(value)

    @property
    def created_at(self) -> datetime:
        """Date et heure de création (lecture seule)."""
        return self._created_at

    @property
    def log_date(self) -> date:
        """Date du log auquel l'entrée appartient (lecture seule)."""
        return self._log_date

    @property
    def signifier(self) -> Signifier | None:
        """Signifiant de l'entrée, ou ``None``."""
        return self._signifier

    @signifier.setter
    def signifier(self, value: Signifier | None) -> None:
        """Modifie le signifiant (``None`` pour le retirer)."""
        self._signifier = validate_signifier(value)

    @property
    @abstractmethod
    def symbol(self) -> str:
        """Symbole du rapid logging qui représente l'entrée."""

    def __repr__(self) -> str:
        """Renvoie une représentation lisible, utile pour déboguer."""
        return (
            f"{type(self).__name__}(id={self._id[:8]!r}, "
            f"name={self._name!r}, log_date={self._log_date})"
        )


class Task(Entry):
    """Tâche : une chose à faire, avec un état qui évolue.

    Une tâche est créée à l'état ``TODO`` et ne change d'état qu'à
    travers ses méthodes (``complete``, ``cancel``, ``migrate``,
    ``schedule``), qui vérifient les règles de transition.
    """

    def __init__(
        self,
        name: str,
        description: str,
        log_date: date | None = None,
        signifier: Signifier | None = None,
        migrated_from: str | None = None,
    ) -> None:
        """Crée une tâche à l'état ``TODO``.

        Args:
            name: Nom de la tâche, qui ne doit pas être vide.
            description: Description de la tâche (peut être vide).
            log_date: Date du log de la tâche ; aujourd'hui par défaut.
            signifier: Signifiant optionnel (priorité ou idée).
            migrated_from: Identifiant de la tâche d'origine, si cette
                tâche a été créée par une migration ou une
                planification.
        """
        super().__init__(name, description, log_date, signifier)
        self._status: TaskStatus = TaskStatus.TODO
        self._migrated_from: str | None = migrated_from

    @property
    def status(self) -> TaskStatus:
        """État actuel de la tâche (modifiable par les méthodes)."""
        return self._status

    @property
    def migrated_from(self) -> str | None:
        """Identifiant de la tâche d'origine, ou ``None``."""
        return self._migrated_from

    @property
    def symbol(self) -> str:
        """Symbole de la tâche, qui dépend de son état."""
        return _TASK_SYMBOLS[self._status]

    def is_pending(self) -> bool:
        """Indique si la tâche est encore à faire."""
        return self._status is TaskStatus.TODO

    def complete(self) -> None:
        """Marque la tâche comme terminée.

        Raises:
            InvalidTransitionError: Si la tâche n'est pas à faire.
        """
        self._change_status(TaskStatus.DONE)

    def cancel(self) -> None:
        """Abandonne la tâche, devenue sans objet.

        Raises:
            InvalidTransitionError: Si la tâche n'est pas à faire.
        """
        self._change_status(TaskStatus.CANCELLED)

    def migrate(self, target_date: date) -> Task:
        """Reporte la tâche vers un jour postérieur.

        Comme sur papier, la tâche d'origine reste dans son log avec
        l'état « migrée », pour garder l'historique. Une nouvelle
        tâche (avec un nouvel identifiant) est créée pour la date
        cible : c'est au journal de la ranger dans le bon log.

        Args:
            target_date: Date vers laquelle reporter la tâche.

        Returns:
            La nouvelle tâche, reliée à l'originale par
            ``migrated_from``.

        Raises:
            InvalidTransitionError: Si la tâche n'est pas à faire.
            InvalidDateError: Si la date cible n'est pas postérieure à
                la date du log de la tâche.
        """
        # On vérifie tout AVANT de modifier l'état : en cas d'erreur,
        # la tâche reste intacte.
        self._check_transition(TaskStatus.MIGRATED)
        target_date = validate_date(target_date)
        if target_date <= self._log_date:
            logger.error(
                "Migration de %r vers le %s impossible", self, target_date
            )
            raise InvalidDateError(
                "La date de migration doit être postérieure au "
                f"{self._log_date}."
            )
        self._change_status(TaskStatus.MIGRATED)
        return self._copy_to(target_date)

    def schedule(self, target_date: date) -> Task:
        """Planifie la tâche dans un mois futur.

        Fonctionne comme ``migrate``, mais la date cible doit se
        trouver dans un mois postérieur au mois de la tâche.

        Args:
            target_date: Date (dans un mois futur) visée par la tâche.

        Returns:
            La nouvelle tâche, reliée à l'originale par
            ``migrated_from``.

        Raises:
            InvalidTransitionError: Si la tâche n'est pas à faire.
            InvalidDateError: Si la date cible n'est pas dans un mois
                postérieur.
        """
        self._check_transition(TaskStatus.SCHEDULED)
        target_date = validate_date(target_date)
        current_month = (self._log_date.year, self._log_date.month)
        if (target_date.year, target_date.month) <= current_month:
            logger.error(
                "Planification de %r en %s impossible", self, target_date
            )
            raise InvalidDateError(
                "La planification doit viser un mois postérieur."
            )
        self._change_status(TaskStatus.SCHEDULED)
        return self._copy_to(target_date)

    def _check_transition(self, new_status: TaskStatus) -> None:
        """Lève une erreur si le passage vers ``new_status`` est interdit."""
        if new_status not in _ALLOWED_TRANSITIONS[self._status]:
            logger.error(
                "Transition interdite pour %r : %s -> %s",
                self,
                self._status.value,
                new_status.value,
            )
            raise InvalidTransitionError(
                f"Impossible de passer la tâche '{self._name}' de l'état "
                f"« {self._status.value} » à l'état « {new_status.value} »."
            )

    def _change_status(self, new_status: TaskStatus) -> None:
        """Change l'état de la tâche après avoir vérifié la règle."""
        self._check_transition(new_status)
        old_status = self._status
        self._status = new_status
        logger.info(
            "Tâche %r : %s -> %s",
            self._name,
            old_status.value,
            new_status.value,
        )

    def _copy_to(self, target_date: date) -> Task:
        """Crée la copie à faire utilisée par la migration."""
        return Task(
            self._name,
            self._description,
            log_date=target_date,
            signifier=self._signifier,
            migrated_from=self._id,
        )


class Event(Entry):
    """Événement : quelque chose qui a lieu à une date donnée.

    La date de l'événement est aussi la date du log où il est rangé.
    """

    def __init__(
        self,
        name: str,
        description: str,
        event_date: date,
        event_time: time | None = None,
        signifier: Signifier | None = None,
    ) -> None:
        """Crée un événement.

        Args:
            name: Nom de l'événement, qui ne doit pas être vide.
            description: Description de l'événement (peut être vide).
            event_date: Date de l'événement (obligatoire).
            event_time: Heure de l'événement (facultative).
            signifier: Signifiant optionnel (priorité ou idée).

        Raises:
            InvalidDateError: Si la date ou l'heure est invalide.
        """
        super().__init__(
            name, description, validate_date(event_date), signifier
        )
        self._event_time: time | None = validate_time(event_time)

    @property
    def event_date(self) -> date:
        """Date de l'événement (identique à la date du log)."""
        return self._log_date

    @property
    def event_time(self) -> time | None:
        """Heure de l'événement, ou ``None`` si elle n'est pas précisée."""
        return self._event_time

    @property
    def symbol(self) -> str:
        """Symbole d'un événement : le cercle « ○ »."""
        return "○"


class Note(Entry):
    """Note : une information à retenir, sans état ni échéance."""

    @property
    def symbol(self) -> str:
        """Symbole d'une note : le tiret « – »."""
        return "–"
