"""Exceptions personnalisées de la bibliothèque bujo.

Toutes les exceptions héritent de ``BujoError`` : une application peut
ainsi intercepter toutes les erreurs de la bibliothèque avec un seul
``except BujoError``.
"""


class BujoError(Exception):
    """Exception de base de toutes les erreurs de la bibliothèque."""


class EntryNotFoundError(BujoError):
    """Levée quand aucune entrée ne correspond à l'identifiant donné."""


class DuplicateEntryError(BujoError):
    """Levée quand on ajoute une entrée déjà présente dans un log."""


class ValidationError(BujoError):
    """Levée quand une donnée fournie par l'utilisateur est invalide."""


class EmptyNameError(ValidationError):
    """Levée quand le nom d'une entrée est vide."""


class InvalidDateError(ValidationError):
    """Levée quand une date ou une heure est invalide ou incohérente."""


class InvalidTransitionError(BujoError):
    """Levée quand un changement d'état est interdit.

    Exemples : terminer une tâche abandonnée, migrer une note.
    """
