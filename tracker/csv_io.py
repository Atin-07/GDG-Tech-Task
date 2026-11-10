"""CSV input and CSV/JSON output."""
import csv
import json
import sys
from dataclasses import asdict

from tracker.config import NAME_COLUMNS
from tracker.models import Student


def read_students(path, column):
    try:
        f = open(path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        sys.exit(f"Cannot open CSV: {exc}")
    with f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            sys.exit("CSV is empty.")
        fields = {h.strip(): h for h in reader.fieldnames}
        if column not in fields:
            sys.exit(f"CSV is missing the '{column}' column. Found: {list(fields)}")
        name_col = next((fields[h] for h in fields if h.lower() in NAME_COLUMNS), None)
        students = []
        for i, rec in enumerate(reader, start=2):  # row 1 is the header
            url = (rec.get(fields[column]) or "").strip()
            name = (rec.get(name_col) or "").strip() if name_col else ""
            students.append(Student(i, name, url))
    return students


def export_results(results, path):
    """Write results to .json or .csv depending on the file extension."""
    data = [asdict(r) for r in results]
    with open(path, "w", newline="", encoding="utf-8") as f:
        if path.lower().endswith(".json"):
            json.dump(data, f, indent=2)
        else:
            writer = csv.DictWriter(f, fieldnames=list(data[0]) if data else ["row"])
            writer.writeheader()
            writer.writerows(data)


def read_required_badges(path):
    """One badge title per line. Blank lines and lines starting with # are ignored."""
    try:
        with open(path, encoding="utf-8-sig") as f:
            titles = [ln.strip() for ln in f if ln.strip() and not ln.lstrip().startswith("#")]
    except OSError as exc:
        sys.exit(f"Cannot open required-badges file: {exc}")
    if not titles:
        sys.exit(f"Required-badges file is empty: {path}")
    return tuple(titles)
