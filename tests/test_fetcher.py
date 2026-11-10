import pytest
import requests

from tests.helpers import URL, FakeResp, FakeSession
from tracker import models as m
from tracker.errors import FetchError
from tracker.fetcher import fetch
from tracker.rate_limiter import RateLimiter

LIM = RateLimiter(0, 0)


def test_retry_then_success():
    s = FakeSession(FakeResp(429, headers={"Retry-After": "1"}), FakeResp(503), FakeResp(200, "ok"))
    assert fetch(s, URL, LIM, 2, 5).status_code == 200 and s.calls == 3


@pytest.mark.parametrize("responses,expected", [
    ([FakeResp(429)] * 3, m.RATE_LIMITED),
    ([FakeResp(500)] * 3, m.SERVER_ERROR),
    ([requests.Timeout()] * 3, m.NETWORK_ERROR),
])
def test_retries_exhausted(responses, expected):
    with pytest.raises(FetchError) as e:
        fetch(FakeSession(*responses), URL, LIM, 2, 5)
    assert e.value.status == expected


def test_404_is_returned_not_retried():
    s = FakeSession(FakeResp(404))
    assert fetch(s, URL, LIM, 2, 5).status_code == 404 and s.calls == 1
