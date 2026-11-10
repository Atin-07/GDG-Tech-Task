"""Business logic: turn one student's profile URL into one Result."""
from tracker.errors import FetchError
from tracker.fetcher import fetch
from tracker.models import (COMPLETE, IN_PROGRESS, INVALID_URL, NO_BADGES, NOT_FOUND,
                            PARSE_ERROR, PRIVATE, Result)
from tracker.parser import match_required, parse_profile
from tracker.validators import validate_url


def classify(count, target):
    if count >= target:
        return COMPLETE
    return IN_PROGRESS if count > 0 else NO_BADGES


def check_profile(session, limiter, student, settings):
    """Never raises for expected failures: every outcome becomes a Result with a status."""
    row, name, url = student.row, student.name, student.url
    if not url or not validate_url(url):
        return Result(row, name, url, 0, INVALID_URL, "not a Google Skills public profile URL")
    try:
        resp = fetch(session, url.strip(), limiter, settings.retries, settings.timeout)
    except FetchError as exc:
        return Result(row, name, url, 0, exc.status, exc.detail)

    if resp.status_code == 404:
        return Result(row, name, url, 0, NOT_FOUND, "HTTP 404")
    if resp.status_code != 200:
        return Result(row, name, url, 0, PARSE_ERROR, f"unexpected HTTP {resp.status_code}")

    try:
        page_name, total, text = parse_profile(resp.text)
    except Exception as exc:  # parser must never kill the run
        return Result(row, name, url, 0, PARSE_ERROR, f"{type(exc).__name__}: {exc}")

    display = name or page_name or "(unknown)"
    if total == 0 and (not page_name or "private" in text or "not public" in text):
        return Result(row, display, url, 0, PRIVATE, "no profile content visible")

    if settings.required_badges:  # only the campaign badges count
        matched, missing = match_required(text, settings.required_badges)
        count = len(matched)
        detail = f"missing {len(missing)}: " + "; ".join(missing) if missing else ""
    else:  # fallback: any badge counts
        count, detail = total, ""
    return Result(row, display, url, count, classify(count, settings.target), detail)
