"""Énumérations du Bullet Journal : états des tâches et signifiants."""

from enum import Enum


class TaskStatus(Enum):
    """État d'une tâche dans son cycle de vie.

    Une tâche commence toujours à l'état ``TODO``. Les quatre autres
    états sont définitifs (voir la classe ``Task``).
    """

    TODO = "à faire"
    DONE = "terminée"
    MIGRATED = "migrée"
    SCHEDULED = "planifiée"
    CANCELLED = "abandonnée"


class Signifier(Enum):
    """Signifiant ajouté devant une entrée pour la mettre en valeur.

    La valeur de chaque membre est le symbole affiché.
    """

    PRIORITY = "*"
    IDEA = "!"
