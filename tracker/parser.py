"""HTML parsing: pull the display name and badge count out of a profile page."""
import re

from bs4 import BeautifulSoup

from tracker.config import BADGE_HREF


def parse_profile(html):
    """Return (display_name, badge_count, page_text_lowercase).
    Badges are counted as UNIQUE badge links, so a repeated link is never double counted."""
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    name = h1.get_text(strip=True) if h1 else ""
    badge_ids = {
        m.group(1)
        for a in soup.find_all("a", href=True)
        if (m := BADGE_HREF.search(a["href"]))
    }
    return name, len(badge_ids), soup.get_text(" ", strip=True).lower()


_DASHES = re.compile(r"[\u2010-\u2015]")


def normalize(text):
    """Lowercase, unify dash characters, collapse whitespace."""
    return re.sub(r"\s+", " ", _DASHES.sub("-", text)).strip().lower()


def match_required(page_text, required):
    """Split the required badge titles into (matched, missing).
    A badge counts only when its title is followed by 'Earned', which is how earned badge cards
    read. This avoids false matches on course descriptions that merely mention a title."""
    text = normalize(page_text)
    matched, missing = [], []
    for title in required:
        found = re.search(re.escape(normalize(title)) + r"\s+earned\b", text)
        (matched if found else missing).append(title)
    return matched, missing
