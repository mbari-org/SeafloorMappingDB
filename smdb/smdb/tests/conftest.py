"""Pytest fixtures for smdb tests."""
import pytest
from django.core.management import call_command


@pytest.fixture
def missions_notes_5(db):
    """Load missions_notes_5.json fixture (5 missions with nav_track for map display)."""
    call_command("loaddata", "missions_notes_5.json")
