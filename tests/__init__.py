"""Asynchronous Python client for the Open Data Platform API of Namur."""

from pathlib import Path


def load_fixtures(filename: str) -> str:
    """Load a fixture."""
    path = Path(__file__).parent / "fixtures" / filename
    return path.read_text()
