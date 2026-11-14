"""Tests du paquet bujo lui-même."""

import bujo


def test_version_is_defined() -> None:
    """Le paquet expose un numéro de version."""
    assert isinstance(bujo.__version__, str)
