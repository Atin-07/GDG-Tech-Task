"""Concurrency: run check_profile for every student on a thread pool."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from tracker.checker import check_profile
from tracker.fetcher import build_session
from tracker.models import DUPLICATE, PARSE_ERROR, Result
from tracker.rate_limiter import RateLimiter
from tracker.validators import normalize_url


def run_checks(students, settings, on_done=None):
    """Return results in the same order as `students`. `on_done()` is called after each finished row.
    A profile URL that appears more than once is fetched only once; later rows get status DUPLICATE."""
    session = build_session()
    limiter = RateLimiter(settings.delay, settings.jitter)

    first_row = {}   # profile key -> row of its first occurrence
    to_fetch = []    # students that need a real check
    for s in students:
        key = normalize_url(s.url)
        if key is None or key not in first_row:  # invalid URLs are checked individually (no network)
            if key is not None:
                first_row[key] = s.row
            to_fetch.append(s)

    done = {}        # row -> Result
    with ThreadPoolExecutor(max_workers=max(1, settings.workers)) as pool:
        futures = [(s, pool.submit(check_profile, session, limiter, s, settings)) for s in to_fetch]
        for s, fut in futures:
            try:
                done[s.row] = fut.result()
            except Exception as exc:
                done[s.row] = Result(s.row, s.name, s.url, 0, PARSE_ERROR, f"unexpected: {exc}")
            if on_done:
                on_done()

    results = []
    for s in students:
        if s.row in done:
            results.append(done[s.row])
        else:  # duplicate row: reuse the first occurrence's result, flagged
            original = done[first_row[normalize_url(s.url)]]
            results.append(replace(original, row=s.row, name=s.name or original.name, status=DUPLICATE,
                                   detail=f"same profile as row {original.row}"))
            if on_done:
                on_done()
    return results
