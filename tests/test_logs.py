"""Tests des pages de journal (Daily et Monthly Logs)."""

from datetime import date

from bujo.entries import Note, Task
from bujo.logs import DailyLog, MonthlyLog


def test_daily_log_creation() -> None:
    """Crée un Daily Log et vérifie sa structure."""
    day = date(2026, 11, 14)
    log = DailyLog(day)
    assert log.day == day
    assert log.title == "Daily Log du 14/11/2026"
    assert log.entries == []


def test_daily_log_add_entry() -> None:
    """Ajoute une entrée à un Daily Log."""
    log = DailyLog(date(2026, 11, 14))
    task = Task("Tâche", "", date(2026, 11, 14))
    log.add(task)
    assert task in log.entries
    assert len(log.entries) == 1


def test_daily_log_remove_entry() -> None:
    """Supprime une entrée d'un Daily Log."""
    log = DailyLog(date(2026, 11, 14))
    task = Task("Tâche", "", date(2026, 11, 14))
    log.add(task)
    log.remove(task)
    assert len(log.entries) == 0


def test_daily_log_get_entry() -> None:
    """Récupère une entrée par son ID."""
    log = DailyLog(date(2026, 11, 14))
    task = Task("Tâche", "", date(2026, 11, 14))
    log.add(task)
    retrieved = log.get(task.id)
    assert retrieved == task


def test_monthly_log_creation() -> None:
    """Crée un Monthly Log et vérifie sa structure."""
    log = MonthlyLog(2026, 11)
    assert log.year == 2026
    assert log.month == 11
    assert log.title == "Monthly Log 11/2026"
    assert log.entries == []


def test_log_tasks_property() -> None:
    """Filtre les tâches parmi les entrées."""
    log = DailyLog(date(2026, 11, 14))
    task = Task("Tâche", "", date(2026, 11, 14))
    note = Note("Note", "Contenu")
    log.add(task)
    log.add(note)
    assert len(log.tasks) == 1
    assert task in log.tasks


def test_log_pending_tasks_property() -> None:
    """Filtre les tâches à faire."""
    log = DailyLog(date(2026, 11, 14))
    task1 = Task("Tâche 1", "", date(2026, 11, 14))
    task2 = Task("Tâche 2", "", date(2026, 11, 14))
    log.add(task1)
    log.add(task2)
    task1.complete()
    assert len(log.pending_tasks) == 1
    assert task2 in log.pending_tasks
