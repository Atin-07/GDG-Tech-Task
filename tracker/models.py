"""Data containers and status codes."""
from dataclasses import dataclass

COMPLETE = "COMPLETE"
IN_PROGRESS = "IN_PROGRESS"
NO_BADGES = "NO_BADGES"
PRIVATE = "PRIVATE_OR_UNAVAILABLE"
NOT_FOUND = "NOT_FOUND"
INVALID_URL = "INVALID_URL"
RATE_LIMITED = "RATE_LIMITED"
SERVER_ERROR = "SERVER_ERROR"
NETWORK_ERROR = "NETWORK_ERROR"
PARSE_ERROR = "PARSE_ERROR"
DUPLICATE = "DUPLICATE"

ERROR_STATUSES = (INVALID_URL, NOT_FOUND, RATE_LIMITED, SERVER_ERROR, NETWORK_ERROR, PARSE_ERROR)

# --only filter groups
FILTERS = {
    "complete": (COMPLETE,),
    "incomplete": (IN_PROGRESS, NO_BADGES),
    "errors": ERROR_STATUSES + (PRIVATE,),
}


@dataclass
class Student:
    row: int        # CSV row number (header = row 1)
    name: str
    url: str


@dataclass
class Result:
    row: int
    name: str
    url: str
    badges: int
    status: str
    detail: str = ""
