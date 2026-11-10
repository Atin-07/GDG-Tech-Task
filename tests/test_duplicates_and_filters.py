from tracker import runner
from tracker.config import Settings
from tracker.models import COMPLETE, DUPLICATE, INVALID_URL, IN_PROGRESS, NETWORK_ERROR, Result, Student
from tracker.report import filter_results
from tracker.validators import normalize_url
from tests.helpers import PID, URL


def test_normalize_url_ignores_case_slash_query():
    assert normalize_url(URL + "/") == normalize_url(URL + "?x=1") == normalize_url(URL)
    assert normalize_url("https://example.com/x") is None


def test_duplicate_row_is_not_fetched_twice(monkeypatch):
    calls = []

    def fake_check(session, limiter, s, settings):
        calls.append(s.row)
        return Result(s.row, s.name, s.url, 10, COMPLETE)

    monkeypatch.setattr(runner, "check_profile", fake_check)
    students = [Student(2, "A", URL), Student(3, "B", URL + "/"), Student(4, "C", ""), Student(5, "D", "")]
    ticks = []
    out = runner.run_checks(students, Settings(delay=0, jitter=0), on_done=lambda: ticks.append(1))
    assert calls == [2, 4, 5]                      # row 3 never fetched; blank rows are not merged
    assert [r.status for r in out] == [COMPLETE, DUPLICATE, COMPLETE, COMPLETE]
    assert out[1].detail == "same profile as row 2" and out[1].row == 3
    assert len(ticks) == 4                          # progress bar still reaches 4/4


def test_only_filter():
    rs = [Result(2, "a", "u", 10, COMPLETE), Result(3, "b", "u", 4, IN_PROGRESS),
          Result(4, "c", "u", 0, INVALID_URL), Result(5, "d", "u", 0, NETWORK_ERROR)]
    assert [r.row for r in filter_results(rs, "complete")] == [2]
    assert [r.row for r in filter_results(rs, "incomplete")] == [3]
    assert [r.row for r in filter_results(rs, "errors")] == [4, 5]
    assert len(filter_results(rs, None)) == 4
