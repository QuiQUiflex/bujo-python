"""Affichage du journal avec les symboles du rapid logging.

Ce module ne modifie jamais le journal : il transforme seulement les
entrées et les pages en texte, prêt à être affiché dans un terminal.
"""

import calendar
from collections.abc import Iterable

from bujo.entries import Entry, Event, Task
from bujo.enums import Signifier, TaskStatus
from bujo.logs import Log, MonthlyLog

# Caractère Unicode qui barre le caractère placé juste avant lui.
_STRIKE = "\u0336"

# Initiales des jours, du lundi (0) au dimanche (6).
_WEEKDAY_INITIALS = ["L", "M", "M", "J", "V", "S", "D"]

# Clé des symboles, affichée par render_key.
_KEY: list[tuple[str, str]] = [
    ("•", "tâche à faire"),
    ("×", "tâche terminée"),
    (">", "tâche migrée"),
    ("<", "tâche planifiée"),
    ("•", "tâche abandonnée (nom barré)"),
    ("○", "événement"),
    ("–", "note"),
    (Signifier.PRIORITY.value, "priorité"),
    (Signifier.IDEA.value, "idée"),
]


def strike(text: str) -> str:
    """Barre un texte en ajoutant le caractère U+0336 après chaque lettre.

    Args:
        text: Le texte à barrer.

    Returns:
        Le texte barré.
    """
    return "".join(char + _STRIKE for char in text)


def format_entry(entry: Entry) -> str:
    """Met en forme une entrée sur une seule ligne.

    La ligne contient le signifiant (ou un espace), le symbole, l'heure
    pour un événement, le nom, puis la description entre parenthèses.
    Le nom d'une tâche abandonnée est barré.

    Args:
        entry: L'entrée à afficher.

    Returns:
        La ligne de texte, par exemple « * • Réviser (Chapitre 3) ».
    """
    signifier = entry.signifier.value if entry.signifier else " "
    name = entry.name
    if isinstance(entry, Task) and entry.status is TaskStatus.CANCELLED:
        name = strike(name)
    if isinstance(entry, Event) and entry.event_time is not None:
        name = f"{entry.event_time.strftime('%H:%M')} {name}"
    line = f"{signifier} {entry.symbol} {name}"
    if entry.description:
        line += f" ({entry.description})"
    return line


def render_log(log: Log) -> str:
    """Affiche une page du journal : son titre puis ses entrées.

    Args:
        log: La page à afficher (Daily Log ou Monthly Log).

    Returns:
        Le texte de la page, sur plusieurs lignes.
    """
    lines = [log.title, "=" * len(log.title)]
    if log.entries:
        lines.extend(format_entry(entry) for entry in log.entries)
    else:
        lines.append("(page vide)")
    return "\n".join(lines)


def render_tasks(tasks: Iterable[Task]) -> str:
    """Affiche une liste de tâches, chacune précédée de sa date.

    Args:
        tasks: Les tâches à afficher.

    Returns:
        Une ligne par tâche, ou « (aucune tâche) » si la liste est vide.
    """
    lines = [
        f"{task.log_date:%d/%m} {format_entry(task)}" for task in tasks
    ]
    if not lines:
        return "(aucune tâche)"
    return "\n".join(lines)


def render_month(log: MonthlyLog) -> str:
    """Affiche un Monthly Log : le calendrier du mois puis ses tâches.

    Comme sur papier, chaque jour du mois occupe une ligne avec
    l'initiale du jour de la semaine (L, M, M, J, V, S, D).

    Args:
        log: Le Monthly Log à afficher.

    Returns:
        Le texte du mois, sur plusieurs lignes.
    """
    lines = [log.title, "=" * len(log.title)]
    days_in_month = calendar.monthrange(log.year, log.month)[1]
    for day in range(1, days_in_month + 1):
        weekday = calendar.weekday(log.year, log.month, day)
        lines.append(f"{day:2d} {_WEEKDAY_INITIALS[weekday]}")
    lines.append("")
    lines.append("Tâches du mois")
    if log.entries:
        lines.extend(format_entry(entry) for entry in log.entries)
    else:
        lines.append("(aucune tâche ce mois-ci)")
    return "\n".join(lines)


def render_key() -> str:
    """Affiche la clé des symboles utilisés dans le journal.

    Returns:
        La légende, un symbole par ligne.
    """
    title = "Clé des symboles"
    lines = [title, "=" * len(title)]
    lines.extend(f"{symbol}  {meaning}" for symbol, meaning in _KEY)
    return "\n".join(lines)