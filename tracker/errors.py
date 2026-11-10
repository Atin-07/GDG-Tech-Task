"""Custom exceptions."""


class FetchError(Exception):
    """Raised by the fetcher when a page cannot be retrieved. Carries a status code for the report."""

    def __init__(self, status, detail):
        super().__init__(detail)
        self.status = status
        self.detail = detail
