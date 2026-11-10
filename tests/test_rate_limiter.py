from tracker import rate_limiter
from tracker.rate_limiter import RateLimiter


def test_slots_are_spaced(monkeypatch):
    sleeps = []
    monkeypatch.setattr(rate_limiter.time, "sleep", sleeps.append)
    monkeypatch.setattr(rate_limiter.time, "monotonic", lambda: 100.0)
    lim = RateLimiter(1.0, 0)
    for _ in range(3):
        lim.wait()
    assert sleeps == [1.0, 2.0]  # first call goes immediately, next two are queued 1s apart
