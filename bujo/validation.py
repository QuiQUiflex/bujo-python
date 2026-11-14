"""Fonctions de validation des données fournies par l'utilisateur.

Elles sont partagées par plusieurs modules. En cas de problème, elles
écrivent un message dans les logs puis lèvent une exception
personnalisée (voir ``bujo.exceptions``).
"""

import logging
from datetime import date, datetime, time

from bujo.enums import Signifier
from bujo.exceptions import EmptyNameError, InvalidDateError, ValidationError

logger = logging.getLogger(__name__)


def validate_name(name: str) -> str:
    """Vérifie qu'un nom n'est pas vide.

    Args:
        name: Le nom à vérifier.

    Returns:
        Le nom, sans les espaces au début et à la fin.

    Raises:
        EmptyNameError: Si le nom est vide ou n'est pas un texte.
    """
    if not isinstance(name, str) or not name.strip():
        logger.error("Nom invalide : %r", name)
        raise EmptyNameError("Le nom ne peut pas être vide.")
    return name.strip()


def validate_description(description: str) -> str:
    """Vérifie qu'une description est bien un texte (éventuellement vide).

    Args:
        description: La description à vérifier.

    Returns:
        La description, inchangée.

    Raises:
        ValidationError: Si la description n'est pas un texte.
    """
    if not isinstance(description, str):
        logger.error("Description invalide : %r", description)
        raise ValidationError("La description doit être un texte.")
    return description


def validate_date(value: date) -> date:
    """Vérifie qu'une valeur est une date (sans heure).

    Les objets ``datetime`` sont refusés volontairement : Python ne
    sait pas comparer un ``datetime`` avec une ``date``, ce qui ferait
    planter la migration des tâches.

    Args:
        value: La valeur à vérifier.

    Returns:
        La date, inchangée.

    Raises:
        InvalidDateError: Si la valeur n'est pas une date.
    """
    if isinstance(value, datetime) or not isinstance(value, date):
        logger.error("Date invalide : %r", value)
        raise InvalidDateError(f"Date invalide : {value!r}.")
    return value


def validate_time(value: time | None) -> time | None:
    """Vérifie qu'une heure est valide (ou absente).

    Args:
        value: L'heure à vérifier, ou ``None``.

    Returns:
        L'heure, inchangée.

    Raises:
        InvalidDateError: Si la valeur n'est ni une heure ni ``None``.
    """
    if value is not None and not isinstance(value, time):
        logger.error("Heure invalide : %r", value)
        raise InvalidDateError(f"Heure invalide : {value!r}.")
    return value


def validate_signifier(value: Signifier | None) -> Signifier | None:
    """Vérifie qu'un signifiant est valide (ou absent).

    Args:
        value: Le signifiant à vérifier, ou ``None``.

    Returns:
        Le signifiant, inchangé.

    Raises:
        ValidationError: Si la valeur n'est ni un ``Signifier`` ni
            ``None``.
    """
    if value is not None and not isinstance(value, Signifier):
        logger.error("Signifiant invalide : %r", value)
        raise ValidationError(f"Signifiant invalide : {value!r}.")
    return value
