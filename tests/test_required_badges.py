from tests.helpers import URL, FakeResp, FakeSession, page_titled
from tracker import models as m
from tracker.checker import check_profile
from tracker.config import Settings
from tracker.parser import match_required
from tracker.rate_limiter import RateLimiter

REQ = tuple(f"Course {i}" for i in range(10))
SET = Settings(target=10, retries=1, required_badges=REQ)
LIM = RateLimiter(0, 0)


def run(html):
    return check_profile(FakeSession(FakeResp(200, html)), LIM, m.Student(2, "", URL), SET)


def test_all_required_is_complete():
    r = run(page_titled(REQ))
    assert (r.status, r.badges, r.detail) == (m.COMPLETE, 10, "")


def test_extra_badges_do_not_count():
    r = run(page_titled(REQ[:4], extra=("Some Other Badge",) * 6))
    assert r.badges == 4 and r.status == m.IN_PROGRESS  # 10 badges on page, only 4 are campaign badges
    assert "missing 6" in r.detail and "Course 9" in r.detail


def test_description_mention_is_not_an_earned_badge():
    r = run(page_titled(REQ[:3], description_mentions=("Course 9",)))
    assert r.badges == 3


def test_no_campaign_badges():
    assert run(page_titled([], extra=("Other",))).status == m.NO_BADGES


def test_dash_and_case_insensitive_match():
    matched, missing = match_required("Store ... Cloud \u2013 Console Earned Nov 3", ["store ... cloud - console"])
    assert matched and not missing
