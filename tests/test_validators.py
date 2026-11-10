from tests.helpers import URL
from tracker.validators import validate_url


def test_valid_url():
    assert validate_url(URL)


def test_rejects_other_hosts_bad_paths_and_empty():
    assert not validate_url("https://example.com/x")
    assert not validate_url("https://www.skills.google/public_profiles/abc")
    assert not validate_url("")
    assert not validate_url(None)
