"""Tests de la classe Journal."""

from datetime import date

import pytest

from bujo.enums import Signifier, TaskStatus
from bujo.exceptions import EntryNotFoundError
from bujo.journal import Journal

DAY = date(2026, 11, 14)
NEXT_DAY = date(2026, 11, 15)


# ----------------------------------------------------------------------
# Ajout d'entrées
# ----------------------------------------------------------------------


def test_add_task_defaults_to_today(journal: Journal) -> None:
    """Sans jour précisé, la tâche va dans le Daily Log d'aujourd'hui."""
    task = journal.add_task("Tâche", "Desc")
    assert task.name == "Tâche"
    assert task.description == "Desc"
    assert task.log_date == date.today()
    assert task in journal.daily_log().entries


def test_add_task_on_specific_day(journal: Journal) -> None:
    """La tâche va dans le Daily Log du jour demandé."""
    task = journal.add_task("Tâche", day=DAY)
    assert task.log_date == DAY
    assert task in journal.daily_log(DAY).entries


def test_add_task_with_signifier(journal: Journal) -> None:
    """Le signifiant est transmis à la tâche."""
    task = journal.add_task("Tâche", day=DAY, signifier=Signifier.PRIORITY)
    assert task.signifier is Signifier.PRIORITY


def test_add_monthly_task(journal: Journal) -> None:
    """La tâche va dans le Monthly Log, datée du 1er du mois."""
    task = journal.add_monthly_task("Tâche", year=2026, month=12)
    assert task.log_date == date(2026, 12, 1)
    assert task in journal.monthly_log(2026, 12).entries


def test_add_event(journal: Journal) -> None:
    """L'événement va dans le Daily Log de son jour."""
    event = journal.add_event("Réunion", DAY)
    assert event.name == "Réunion"
    assert event.event_date == DAY
    assert event in journal.daily_log(DAY).entries


def test_add_note(journal: Journal) -> None:
    """La note va dans le Daily Log de sa date."""
    note = journal.add_note("Idée", "C'est intéressant")
    assert note.name == "Idée"
    assert note.description == "C'est intéressant"
    assert note in journal.daily_log(note.log_date).entries


# ----------------------------------------------------------------------
# Consultation
# ----------------------------------------------------------------------


def test_get_entry(journal: Journal) -> None:
    """On retrouve une entrée grâce à son identifiant."""
    task = journal.add_task("Tâche", day=DAY)
    assert journal.get_entry(task.id) is task


def test_get_task(journal: Journal) -> None:
    """On retrouve une tâche grâce à son identifiant."""
    task = journal.add_task("Tâche", day=DAY)
    assert journal.get_task(task.id) is task


def test_get_task_on_a_note_fails(journal: Journal) -> None:
    """get_task refuse une entrée qui n'est pas une tâche."""
    note = journal.add_note("Idée")
    with pytest.raises(EntryNotFoundError):
        journal.get_task(note.id)


def test_get_nonexistent_entry(journal: Journal) -> None:
    """Un identifiant inconnu lève EntryNotFoundError."""
    with pytest.raises(EntryNotFoundError):
        journal.get_entry("identifiant-inconnu")


def test_daily_logs_are_sorted(journal: Journal) -> None:
    """Les Daily Logs sont triés par date."""
    journal.add_task("Plus tard", day=NEXT_DAY)
    journal.add_task("Plus tôt", day=DAY)
    assert [log.day for log in journal.daily_logs] == [DAY, NEXT_DAY]


def test_monthly_logs_are_sorted(journal: Journal) -> None:
    """Les Monthly Logs sont triés par mois."""
    journal.add_monthly_task("Plus tard", year=2027, month=1)
    journal.add_monthly_task("Plus tôt", year=2026, month=12)
    keys = [(log.year, log.month) for log in journal.monthly_logs]
    assert keys == [(2026, 12), (2027, 1)]


def test_pending_tasks(journal: Journal) -> None:
    """Seules les tâches à faire sont renvoyées."""
    task1 = journal.add_task("Tâche 1", day=NEXT_DAY)
    task2 = journal.add_task("Tâche 2", day=DAY)
    journal.complete_task(task1.id)
    assert journal.pending_tasks == [task2]


def test_pending_tasks_are_sorted_by_date(journal: Journal) -> None:
    """Les tâches à faire sont triées par date."""
    later = journal.add_task("Tâche 1", day=date(2026, 11, 20))
    sooner = journal.add_task("Tâche 2", day=NEXT_DAY)
    assert journal.pending_tasks == [sooner, later]


def test_events_on(journal: Journal) -> None:
    """events_on ne renvoie que les événements du jour."""
    event1 = journal.add_event("Réunion", DAY)
    event2 = journal.add_event("Rappel", DAY)
    journal.add_task("Pas un événement", day=DAY)
    events = journal.events_on(DAY)
    assert len(events) == 2
    assert event1 in events
    assert event2 in events


def test_events_on_empty_day(journal: Journal) -> None:
    """Un jour sans page renvoie une liste vide."""
    assert journal.events_on(DAY) == []


# ----------------------------------------------------------------------
# Recherche
# ----------------------------------------------------------------------


def test_find_by_name(journal: Journal) -> None:
    """La recherche renvoie les entrées dont le nom correspond."""
    journal.add_task("Réviser Python", day=DAY)
    journal.add_task("Faire un exercice", day=DAY)
    results = journal.find_by_name("Réviser")
    assert [entry.name for entry in results] == ["Réviser Python"]


def test_find_by_name_ignores_case_and_accents(journal: Journal) -> None:
    """« REVISER » trouve « Réviser Python »."""
    journal.add_task("Réviser Python", day=DAY)
    assert len(journal.find_by_name("REVISER")) == 1


def test_find_by_name_ignores_spaces(journal: Journal) -> None:
    """Les espaces ne comptent pas dans la recherche."""
    journal.add_task("Réviser Python", day=DAY)
    assert len(journal.find_by_name("réviserpython")) == 1
    assert len(journal.find_by_name("  python  ")) == 1


def test_find_by_name_without_result(journal: Journal) -> None:
    """Une recherche sans correspondance renvoie une liste vide."""
    journal.add_task("Réviser Python", day=DAY)
    assert journal.find_by_name("cuisine") == []


# ----------------------------------------------------------------------
# Modification
# ----------------------------------------------------------------------


def test_complete_task(journal: Journal) -> None:
    """Terminer une tâche change son état."""
    task = journal.add_task("Tâche", day=DAY)
    journal.complete_task(task.id)
    assert task.status is TaskStatus.DONE


def test_cancel_task(journal: Journal) -> None:
    """Abandonner une tâche change son état."""
    task = journal.add_task("Tâche", day=DAY)
    journal.cancel_task(task.id)
    assert task.status is TaskStatus.CANCELLED


def test_delete_entry(journal: Journal) -> None:
    """Une entrée supprimée disparaît du journal et de sa page."""
    task = journal.add_task("Tâche", day=DAY)
    journal.delete_entry(task.id)
    assert task not in journal.daily_log(DAY).entries
    with pytest.raises(EntryNotFoundError):
        journal.get_entry(task.id)


def test_delete_nonexistent_entry(journal: Journal) -> None:
    """Supprimer une entrée inconnue lève EntryNotFoundError."""
    with pytest.raises(EntryNotFoundError):
        journal.delete_entry("identifiant-inconnu")


def test_set_signifier(journal: Journal) -> None:
    """On peut ajouter un signifiant à une entrée existante."""
    task = journal.add_task("Tâche", day=DAY)
    journal.set_signifier(task.id, Signifier.PRIORITY)
    assert task.signifier is Signifier.PRIORITY


# ----------------------------------------------------------------------
# Migration et planification
# ----------------------------------------------------------------------


def test_migrate_task(journal: Journal) -> None:
    """L'originale reste en place, une seule copie est créée."""
    task = journal.add_task("Tâche", day=DAY)
    copy = journal.migrate_task(task.id, NEXT_DAY)
    assert task.status is TaskStatus.MIGRATED
    assert task in journal.daily_log(DAY).entries
    assert journal.daily_log(NEXT_DAY).entries == [copy]
    assert journal.pending_tasks == [copy]
    assert copy.migrated_from == task.id


def test_migrate_day(journal: Journal) -> None:
    """Seules les tâches à faire sont migrées."""
    task1 = journal.add_task("Tâche 1", day=DAY)
    task2 = journal.add_task("Tâche 2", day=DAY)
    journal.complete_task(task1.id)
    copies = journal.migrate_day(DAY, NEXT_DAY)
    assert task1.status is TaskStatus.DONE
    assert task2.status is TaskStatus.MIGRATED
    assert len(copies) == 1
    assert copies[0].log_date == NEXT_DAY


def test_migrate_day_without_log(journal: Journal) -> None:
    """Migrer un jour sans page ne fait rien."""
    assert journal.migrate_day(DAY, NEXT_DAY) == []


def test_migrate_month(journal: Journal) -> None:
    """Les tâches à faire passent au Monthly Log du mois suivant."""
    done = journal.add_monthly_task("Faite", year=2026, month=11)
    todo = journal.add_monthly_task("À faire", year=2026, month=11)
    journal.complete_task(done.id)
    copies = journal.migrate_month(2026, 11)
    assert todo.status is TaskStatus.MIGRATED
    assert done.status is TaskStatus.DONE
    assert journal.monthly_log(2026, 12).entries == copies
    assert copies[0].log_date == date(2026, 12, 1)


def test_migrate_month_december_goes_to_january(journal: Journal) -> None:
    """Décembre migre vers janvier de l'année suivante."""
    journal.add_monthly_task("Tâche", year=2026, month=12)
    copies = journal.migrate_month(2026, 12)
    assert copies[0].log_date == date(2027, 1, 1)


def test_migrate_month_without_log(journal: Journal) -> None:
    """Migrer un mois sans page ne fait rien."""
    assert journal.migrate_month(2026, 11) == []


def test_schedule_task(journal: Journal) -> None:
    """La copie planifiée va dans le Monthly Log du mois visé."""
    task = journal.add_task("Tâche", day=DAY)
    copy = journal.schedule_task(task.id, date(2026, 12, 5))
    assert task.status is TaskStatus.SCHEDULED
    assert copy in journal.monthly_log(2026, 12).entries
