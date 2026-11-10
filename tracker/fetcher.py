"""HTTP layer: rate-limited GET with retries and exponential backoff."""
import random
import time

import requests

from tracker.config import USER_AGENT
from tracker.errors import FetchError
from tracker.models import NETWORK_ERROR, RATE_LIMITED, SERVER_ERROR


def build_session():
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    return session


def fetch(session, url, limiter, retries, timeout, backoff=2.0):
    """Return a Response (200, 404, or any non-retryable code). Raises FetchError when retries run out."""
    for attempt in range(retries + 1):
        limiter.wait()
        last = attempt == retries
        try:
            resp = session.get(url, timeout=timeout)
        except (requests.Timeout, requests.ConnectionError) as exc:
            if last:
                raise FetchError(NETWORK_ERROR, f"{type(exc).__name__} after {retries + 1} attempts")
            time.sleep(backoff ** attempt + random.uniform(0, 0.5))
            continue
        except requests.RequestException as exc:
            raise FetchError(NETWORK_ERROR, str(exc))

        if resp.status_code == 429 or resp.status_code >= 500:
            if last:
                kind = RATE_LIMITED if resp.status_code == 429 else SERVER_ERROR
                raise FetchError(kind, f"HTTP {resp.status_code} after {retries + 1} attempts")
            retry_after = resp.headers.get("Retry-After", "")
            wait = float(retry_after) if retry_after.isdigit() else backoff ** (attempt + 1)
            time.sleep(wait + random.uniform(0, 0.5))
            continue
        return resp
    raise FetchError(NETWORK_ERROR, "unreachable")  # pragma: no cover
