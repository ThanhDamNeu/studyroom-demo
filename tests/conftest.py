from datetime import datetime, timedelta

import pytest

from studyroom import create_app

# Fixed clock: tests never depend on today's date (no flaky tests).
NOW = datetime(2026, 11, 20, 8, 0)


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db"),
                       "CLOCK": lambda: NOW})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def at():
    """at(9) -> 2026-11-21 09:00, the day after NOW."""
    day = NOW.date() + timedelta(days=1)
    return lambda hour, minute=0: datetime(day.year, day.month, day.day, hour, minute)
