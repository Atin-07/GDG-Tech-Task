"""Shared test doubles: fake HTML pages and a fake HTTP session (no real network)."""
PID = "be556f7b-ab4b-4be7-82fb-9be45202ddd7"
URL = f"https://www.skills.google/public_profiles/{PID}"


def page(n, h1="Test User"):
    badges = "".join(f'<a href="/public_profiles/{PID}/badges/{1000 + i}">Badge {i}</a>' for i in range(n))
    dup = f'<a href="/public_profiles/{PID}/badges/1000">dup</a>' if n else ""
    return f"<html><body><h1>{h1}</h1>{badges}{dup}</body></html>"


class FakeResp:
    def __init__(self, status=200, text="", headers=None):
        self.status_code, self.text, self.headers = status, text, headers or {}


class FakeSession:
    def __init__(self, *responses):
        self.responses, self.calls = list(responses), 0

    def get(self, url, timeout=None):
        self.calls += 1
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def page_titled(titles, extra=(), h1="Test User", description_mentions=()):
    """Profile page whose badge cards read 'Title Earned <date>' like the real site."""
    cards = "".join(
        f'<div><a href="/public_profiles/{PID}/badges/{2000 + i}"><img src="x"></a>'
        f'<span>{t}</span> <span>Earned Nov 3, 2026 EST</span></div>'
        for i, t in enumerate(list(titles) + list(extra))
    )
    desc = "".join(f"<p>Earn a skill badge by completing the {t} course. Learn more</p>" for t in description_mentions)
    return f"<html><body><h1>{h1}</h1>{cards}{desc}</body></html>"
