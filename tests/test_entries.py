"""Tests des entrées : création, validation, propriétés et symboles."""

from datetime import date, datetime, time

import pytest

from bujo.entries import Entry, Event, Note, Task
from bujo.enums import Signifier, TaskStatus
from bujo.exceptions import EmptyNameError, InvalidDateError, ValidationError

DAY = date(2026, 11, 14)


def test_new_task_has_default_values() -> None:
    """Une tâche neuve est à faire, sans signifiant ni origine."""
    task = Task("Réviser", "Chapitre 3", DAY)
    assert task.name == "Réviser"
    assert task.description == "Chapitre 3"
    assert task.log_date == DAY
    assert task.status is TaskStatus.TODO
    assert task.signifier is None
    assert task.migrated_from is None
    assert isinstance(task.created_at, datetime)


def test_log_date_defaults_to_today() -> None:
    """Sans date, une entrée appartient au log du jour."""
    assert Note("Idée", "").log_date == date.today()


def test_each_entry_has_a_unique_id() -> None:
    """Deux entrées de même nom ont des identifiants différents."""
    assert Task("Courses", "", DAY).id != Task("Courses", "", DAY).id


def test_name_is_stripped() -> None:
    """Les espaces autour du nom sont retirés."""
    assert Task("  Courses  ", "", DAY).name == "Courses"


@pytest.mark.parametrize("bad_name", ["", "   ", None, 42])
def test_invalid_name_is_rejected(bad_name: object) -> None:
    """Un nom vide ou qui n'est pas un texte est refusé."""
    with pytest.raises(EmptyNameError):
        Task(bad_name, "", DAY)


def test_name_setter_validates() -> None:
    """Renommer une entrée applique la même validation."""
    task = Task("Courses", "", DAY)
    task.name = "Marché"
    assert task.name == "Marché"
    with pytest.raises(EmptyNameError):
        task.name = "  "


def test_description_setter() -> None:
    """La description peut être modifiée, mais doit rester un texte."""
    note = Note("Idée", "", DAY)
    note.description = "Une appli de BuJo"
    assert note.description == "Une appli de BuJo"
    with pytest.raises(ValidationError):
        note.description = 123


def test_description_must_be_text() -> None:
    """Une description qui n'est pas un texte est refusée."""
    with pytest.raises(ValidationError):
        Task("Courses", None, DAY)


@pytest.mark.parametrize(
    "bad_date", ["2026-11-14", datetime(2026, 11, 14, 9, 30), 14]
)
def test_invalid_log_date_is_rejected(bad_date: object) -> None:
    """Seuls les objets date (sans heure) sont acceptés."""
    with pytest.raises(InvalidDateError):
        Task("Courses", "", bad_date)


def test_signifier_can_be_set_and_removed() -> None:
    """On peut ajouter puis retirer un signifiant."""
    task = Task("Courses", "", DAY, Signifier.PRIORITY)
    assert task.signifier is Signifier.PRIORITY
    task.signifier = None
    assert task.signifier is None


def test_invalid_signifier_is_rejected() -> None:
    """Un signifiant doit être un membre de l'énumération Signifier."""
    with pytest.raises(ValidationError):
        Task("Courses", "", DAY, "*")


def test_symbols_depend_on_entry_type() -> None:
    """Chaque type d'entrée a son propre symbole (polymorphisme)."""
    assert Task("Courses", "", DAY).symbol == "•"
    assert Event("Cours", "", DAY).symbol == "○"
    assert Note("Idée", "", DAY).symbol == "–"


def test_entry_is_abstract() -> None:
    """On ne peut pas créer une Entry directement."""
    with pytest.raises(TypeError):
        Entry("Courses", "")


def test_repr_shows_class_and_name() -> None:
    """La représentation contient la classe et le nom de l'entrée."""
    text = repr(Task("Courses", "", DAY))
    assert text.startswith("Task(")
    assert "'Courses'" in text


def test_event_with_time() -> None:
    """Un événement a une date et éventuellement une heure."""
    event = Event("Cours", "Salle B12", DAY, time(14, 0))
    assert event.event_date == DAY
    assert event.log_date == DAY
    assert event.event_time == time(14, 0)


def test_event_without_time() -> None:
    """L'heure d'un événement est facultative."""
    assert Event("Anniversaire", "", DAY).event_time is None


def test_event_requires_a_date() -> None:
    """Un événement sans date est refusé."""
    with pytest.raises(InvalidDateError):
        Event("Cours", "", None)


def test_event_rejects_invalid_time() -> None:
    """Une heure qui n'est pas un objet time est refusée."""
    with pytest.raises(InvalidDateError):
        Event("Cours", "", DAY, "14h")
