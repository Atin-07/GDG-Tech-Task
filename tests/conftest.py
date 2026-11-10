import pytest

from tracker import fetcher


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Retries/backoff must not slow the tests down."""
    monkeypatch.setattr(fetcher.time, "sleep", lambda s: None)
