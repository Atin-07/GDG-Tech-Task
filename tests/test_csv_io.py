import json

import pytest

from tracker.config import URL_COLUMN
from tracker.csv_io import export_results, read_students
from tracker.models import COMPLETE, Result


def test_reads_students(tmp_path):
    p = tmp_path / "a.csv"
    p.write_text(f"Name,{URL_COLUMN}\nAsha,http://x\n,\n")
    s = read_students(str(p), URL_COLUMN)
    assert [(x.row, x.name, x.url) for x in s] == [(2, "Asha", "http://x"), (3, "", "")]


def test_bad_header_exits(tmp_path):
    p = tmp_path / "a.csv"
    p.write_text("Name,Link\nA,x\n")
    with pytest.raises(SystemExit):
        read_students(str(p), URL_COLUMN)


def test_export_json_and_csv(tmp_path):
    res = [Result(2, "A", "u", 10, COMPLETE)]
    export_results(res, str(tmp_path / "o.json"))
    assert json.loads((tmp_path / "o.json").read_text())[0]["status"] == COMPLETE
    export_results(res, str(tmp_path / "o.csv"))
    assert "COMPLETE" in (tmp_path / "o.csv").read_text()


def test_read_required_badges(tmp_path):
    from tracker.csv_io import read_required_badges
    p = tmp_path / "r.txt"
    p.write_text("# comment\nBadge A\n\n  Badge B  \n")
    assert read_required_badges(str(p)) == ("Badge A", "Badge B")
