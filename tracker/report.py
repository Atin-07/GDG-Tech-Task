"""Terminal output: summary table and totals."""
from rich.table import Table

from tracker.models import COMPLETE, DUPLICATE, ERROR_STATUSES, FILTERS, PRIVATE

STATUS_STYLE = {
    "COMPLETE": "bold green", "IN_PROGRESS": "yellow", "NO_BADGES": "red",
    "PRIVATE_OR_UNAVAILABLE": "magenta", "NOT_FOUND": "red", "INVALID_URL": "red",
    "RATE_LIMITED": "bold red", "SERVER_ERROR": "bold red",
    "NETWORK_ERROR": "bold red", "PARSE_ERROR": "bold red", "DUPLICATE": "cyan",
}


def filter_results(results, only):
    if not only:
        return results
    return [r for r in results if r.status in FILTERS[only]]


def render(results, target, console, shown=None):
    """Table shows `shown` (default: all). The summary line always counts ALL results."""
    table = Table(title="Learn With Communities: Progress", header_style="bold cyan")
    for col in ("#", "Name", "Badges", "Status", "Detail"):
        table.add_column(col)
    for r in (results if shown is None else shown):
        style = STATUS_STYLE.get(r.status, "")
        table.add_row(str(r.row), r.name, f"{r.badges}/{target}", f"[{style}]{r.status}[/]", r.detail)
    console.print(table)

    done = sum(r.status == COMPLETE for r in results)
    errors = sum(r.status in ERROR_STATUSES for r in results)
    private = sum(r.status == PRIVATE for r in results)
    dupes = sum(r.status == DUPLICATE for r in results)
    console.print(f"\n[bold]{done}[/] of {len(results)} completed all {target} badges | "
                  f"[bold]{errors}[/] errors | [bold]{private}[/] private/unavailable | "
                  f"[bold]{dupes}[/] duplicates")
