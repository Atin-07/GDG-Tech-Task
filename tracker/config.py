"""Constants and default settings. Nothing in here does any work."""
import re
from dataclasses import dataclass
from pathlib import Path

URL_COLUMN = "Google Skills Profile URL"
NAME_COLUMNS = ("name", "student name", "full name")

ALLOWED_HOSTS = {
    "skills.google", "www.skills.google",
    "cloudskillsboost.google", "www.cloudskillsboost.google",
}
PROFILE_PATH = re.compile(r"^/public_profiles/[0-9a-fA-F-]{36}/?$")
BADGE_HREF = re.compile(r"/public_profiles/[0-9a-fA-F-]{36}/badges/(\d+)")

DEFAULT_REQUIRED_FILE = Path(__file__).resolve().parent.parent / "data" / "required_badges.txt"

USER_AGENT = "GDGoC-NFSU-LearnWithCommunities-Tracker/1.0 (student project)"


@dataclass
class Settings:
    """Runtime options."""
    target: int = 10        # badges needed for COMPLETE
    workers: int = 3        # concurrent worker threads
    delay: float = 1.0      # min seconds between request starts (all workers combined)
    jitter: float = 0.5     # extra random 0..jitter seconds per gap
    retries: int = 3        # retries on timeout / 429 / 5xx
    timeout: float = 15.0   # per-request timeout (seconds)
    required_badges: tuple = ()  # badge titles that count; empty = count any badge
