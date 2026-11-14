"""Tests de l'affichage (module bujo.display)."""

from datetime import date, time

from bujo.display import (
    format_entry,
    render_key,
    render_log,
    render_month,
    render_tasks,
    strike,
)
from bujo.entries import Event, Note, Task
from bujo.enums import Signifier
from bujo.logs import DailyLog, MonthlyLog

DAY = date(2026, 11, 16)


def test_strike_adds_a_bar_after_each_character() -> None:
    """Chaque caractère est suivi du trait de barrage."""
    assert strike("ab") == "a\u0336b\u0336"


def test_strike_empty_text() -> None:
    """Un texte vide reste vide."""
    assert strike("") == ""


def test_format_todo_task() -> None:
    """Une tâche à faire s'affiche avec une puce."""
    assert format_entry(Task("Réviser", "", DAY)) == "  • Réviser"


def test_format_done_task() -> None:
    """Une tâche terminée s'affiche avec une croix."""
    task = Task("Réviser", "", DAY)
    task.complete()
    assert format_entry(task) == "  × Réviser"


def test_format_cancelled_task_is_struck() -> None:
    """Le nom d'une tâche abandonnée est barré."""
    task = Task("Réviser", "", DAY)
    task.cancel()
    assert format_entry(task) == f"  • {strike('Réviser')}"


def test_format_task_with_signifier_and_description() -> None:
    """Le signifiant est en tête, la description entre parenthèses."""
    task = Task("Réviser", "Chapitre 3", DAY, Signifier.PRIORITY)
    assert format_entry(task) == "* • Réviser (Chapitre 3)"


def test_format_event_with_time() -> None:
    """L'heure d'un événement est affichée avant son nom."""
    event = Event("Cours", "", DAY, time(10, 0))
    assert format_entry(event) == "  ○ 10:00 Cours"


def test_format_event_without_time() -> None:
    """Un événement sans heure n'affiche que son nom."""
    assert format_entry(Event("Cours", "", DAY)) == "  ○ Cours"


def test_format_note_with_idea() -> None:
    """Une note s'affiche avec un tiret."""
    note = Note("Idée", "", DAY, Signifier.IDEA)
    assert format_entry(note) == "! – Idée"


def test_render_log() -> None:
    """Une page affiche son titre, un soulignement et ses entrées."""
    log = DailyLog(DAY)
    log.add(Task("Réviser", "", DAY))
    lines = render_log(log).splitlines()
    assert lines[0] == log.title
    assert lines[1] == "=" * len(log.title)
    assert lines[2] == "  • Réviser"


def test_render_empty_log() -> None:
    """Une page vide l'indique."""
    assert "(page vide)" in render_log(DailyLog(DAY))


def test_render_tasks() -> None:
    """Chaque tâche est précédée de sa date."""
    text = render_tasks([Task("Réviser", "", DAY)])
    assert text == "16/11   • Réviser"


def test_render_no_tasks() -> None:
    """Une liste vide l'indique."""
    assert render_tasks([]) == "(aucune tâche)"


def test_render_month_calendar() -> None:
    """Le calendrier de novembre 2026 commence un dimanche."""
    lines = render_month(MonthlyLog(2026, 11)).splitlines()
    assert lines[2] == " 1 D"
    assert lines[31] == "30 L"
    assert lines[32] == ""
    assert "(aucune tâche ce mois-ci)" in lines


def test_render_month_with_task() -> None:
    """Les tâches du mois sont affichées après le calendrier."""
    log = MonthlyLog(2026, 11)
    log.add(Task("Préparer le rendu", "", date(2026, 11, 1)))
    assert render_month(log).endswith("  • Préparer le rendu")


def test_render_key_contains_all_symbols() -> None:
    """La clé contient tous les symboles du journal."""
    text = render_key()
    for symbol in ["•", "×", ">", "<", "○", "–", "*", "!"]:
        assert symbol in text
