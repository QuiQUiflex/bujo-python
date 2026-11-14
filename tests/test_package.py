"""Tests de l'API publique du paquet bujo."""

import bujo


def test_version() -> None:
    """La version correspond à la fin du niveau 2."""
    assert bujo.__version__ == "0.2.0"


def test_public_api_is_importable() -> None:
    """Chaque nom annoncé dans __all__ existe dans le paquet."""
    for name in bujo.__all__:
        assert hasattr(bujo, name)