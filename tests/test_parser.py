from tests.helpers import page
from tracker.parser import parse_profile


def test_counts_unique_badges_and_reads_name():
    name, count, _ = parse_profile(page(10))
    assert (name, count) == ("Test User", 10)


def test_no_badges():
    assert parse_profile(page(0))[1] == 0
