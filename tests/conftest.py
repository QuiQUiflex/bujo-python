"""Fixtures partagées pour les tests."""

import pytest

from bujo.journal import Journal


@pytest.fixture
def journal() -> Journal:
    """Crée un journal vide pour chaque test."""
    return Journal()
