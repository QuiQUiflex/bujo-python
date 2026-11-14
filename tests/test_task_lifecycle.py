"""Tests du cycle de vie des tâches : états, migration, planification."""

from datetime import date

import pytest

from bujo.entries import Task
from bujo.enums import Signifier, TaskStatus
from bujo.exceptions import InvalidDateError, InvalidTransitionError

DAY = date(2026, 11, 14)
NEXT_DAY = date(2026, 11, 15)
NEXT_MONTH = date(2026, 12, 3)


def make_task() -> Task:
    """Crée une tâche à faire, datée du 14/11/2026."""
    return Task("Réviser", "Chapitre 3", DAY, Signifier.PRIORITY)


def test_complete() -> None:
    """Terminer une tâche change son état et son symbole."""
    task = make_task()
    task.complete()
    assert task.status is TaskStatus.DONE
    assert task.symbol == "×"
    assert not task.is_pending()


def test_cancel() -> None:
    """Abandonner une tâche change son état, pas sa puce."""
    task = make_task()
    task.cancel()
    assert task.status is TaskStatus.CANCELLED
    assert task.symbol == "•"


def test_migrate_creates_a_linked_copy() -> None:
    """La migration marque l'originale et crée une copie à faire."""
    task = make_task()
    copy = task.migrate(NEXT_DAY)
    assert task.status is TaskStatus.MIGRATED
    assert task.symbol == ">"
    assert copy.status is TaskStatus.TODO
    assert copy.log_date == NEXT_DAY
    assert copy.id != task.id
    assert copy.migrated_from == task.id
    assert copy.name == task.name
    assert copy.description == task.description
    assert copy.signifier is task.signifier


@pytest.mark.parametrize("target", [DAY, date(2026, 11, 1)])
def test_migrate_to_past_or_same_day_fails(target: date) -> None:
    """On ne peut migrer que vers un jour postérieur."""
    task = make_task()
    with pytest.raises(InvalidDateError):
        task.migrate(target)
    assert task.status is TaskStatus.TODO


def test_migrate_with_invalid_date_fails() -> None:
    """La date cible doit être un objet date."""
    task = make_task()
    with pytest.raises(InvalidDateError):
        task.migrate("demain")
    assert task.status is TaskStatus.TODO


def test_schedule_to_a_future_month() -> None:
    """Planifier une tâche crée une copie dans le mois visé."""
    task = make_task()
    copy = task.schedule(NEXT_MONTH)
    assert task.status is TaskStatus.SCHEDULED
    assert task.symbol == "<"
    assert copy.log_date == NEXT_MONTH
    assert copy.migrated_from == task.id


@pytest.mark.parametrize("target", [date(2026, 11, 30), date(2026, 10, 5)])
def test_schedule_requires_a_later_month(target: date) -> None:
    """La planification doit viser un mois postérieur."""
    task = make_task()
    with pytest.raises(InvalidDateError):
        task.schedule(target)
    assert task.status is TaskStatus.TODO


def put_in_state(task: Task, status: TaskStatus) -> None:
    """Amène une tâche à faire dans l'état final demandé."""
    if status is TaskStatus.DONE:
        task.complete()
    elif status is TaskStatus.CANCELLED:
        task.cancel()
    elif status is TaskStatus.MIGRATED:
        task.migrate(NEXT_DAY)
    else:
        task.schedule(NEXT_MONTH)


ACTIONS = {
    "complete": lambda task: task.complete(),
    "cancel": lambda task: task.cancel(),
    "migrate": lambda task: task.migrate(date(2026, 11, 20)),
    "schedule": lambda task: task.schedule(date(2027, 1, 5)),
}

FINAL_STATES = [
    TaskStatus.DONE,
    TaskStatus.CANCELLED,
    TaskStatus.MIGRATED,
    TaskStatus.SCHEDULED,
]


@pytest.mark.parametrize("status", FINAL_STATES)
@pytest.mark.parametrize("action", list(ACTIONS))
def test_final_states_are_definitive(
    status: TaskStatus, action: str
) -> None:
    """Aucune action n'est possible sur une tâche dans un état final.

    Par exemple : terminer une tâche abandonnée, ou migrer une tâche
    déjà terminée. L'état de la tâche ne doit pas changer.
    """
    task = make_task()
    put_in_state(task, status)
    with pytest.raises(InvalidTransitionError):
        ACTIONS[action](task)
    assert task.status is status
