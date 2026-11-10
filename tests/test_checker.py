from tests.helpers import URL, FakeResp, FakeSession, page
from tracker import models as m
from tracker.checker import check_profile
from tracker.config import Settings
from tracker.rate_limiter import RateLimiter

SET = Settings(retries=2)
LIM = RateLimiter(0, 0)


def run(session, url=URL):
    return check_profile(session, LIM, m.Student(2, "", url), SET)


def test_complete_in_progress_none():
    assert run(FakeSession(FakeResp(200, page(10)))).status == m.COMPLETE
    assert run(FakeSession(FakeResp(200, page(4)))).status == m.IN_PROGRESS
    assert run(FakeSession(FakeResp(200, page(0)))).status == m.NO_BADGES


def test_private_when_no_content():
    assert run(FakeSession(FakeResp(200, "<html><body>Sign in</body></html>"))).status == m.PRIVATE


def test_not_found_and_invalid():
    assert run(FakeSession(FakeResp(404))).status == m.NOT_FOUND
    assert run(FakeSession(), url="nonsense").status == m.INVALID_URL
    assert run(FakeSession(), url="").status == m.INVALID_URL


def test_fetch_failure_becomes_status():
    assert run(FakeSession(*[FakeResp(429)] * 3)).status == m.RATE_LIMITED

def test_403_is_private():
    r = run(FakeSession(FakeResp(403)))
    assert r.status == m.PRIVATE and "403" in r.detail
