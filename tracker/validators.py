"""URL validation."""
from urllib.parse import urlparse

from tracker.config import ALLOWED_HOSTS, PROFILE_PATH


def validate_url(url):
    """True if url looks like a Google Skills public profile URL."""
    try:
        p = urlparse((url or "").strip())
    except ValueError:
        return False
    return (
        p.scheme in ("http", "https")
        and p.netloc.lower() in ALLOWED_HOSTS
        and bool(PROFILE_PATH.match(p.path))
    )


def normalize_url(url):
    """key for duplicate detection, or None if the URL is not a valid profile URL."""
    if not validate_url(url):
        return None
    p = urlparse(url.strip())
    return p.path.rstrip("/").lower()  # the profile id alone identifies the profile
