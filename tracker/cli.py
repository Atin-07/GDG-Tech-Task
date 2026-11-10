"""Command-line interface: parse arguments and wire the other modules together."""
import argparse
import sys

from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeElapsedColumn

from tracker.config import DEFAULT_REQUIRED_FILE, URL_COLUMN, Settings
from tracker.csv_io import export_results, read_required_badges, read_students
from tracker.models import FILTERS
from tracker.report import filter_results, render
from tracker.runner import run_checks


def build_parser():
    d = Settings()
    ap = argparse.ArgumentParser(description="Track Google Skills badge completion from a CSV of profile URLs.")
    ap.add_argument("csv", help="CSV file containing the profile URL column")
    ap.add_argument("--column", default=URL_COLUMN, help=f"URL column header (default: '{URL_COLUMN}')")
    ap.add_argument("--target", type=int, default=None,
                    help="badges required for completion (default: number of required badges, else 10)")
    ap.add_argument("--required-file", default=str(DEFAULT_REQUIRED_FILE),
                    help="text file with one required badge title per line (default: data/required_badges.txt)")
    ap.add_argument("--any-badge", action="store_true",
                    help="ignore the required list and count any badge")
    ap.add_argument("--only", choices=sorted(FILTERS), help="show/export only this group of results")
    ap.add_argument("--workers", type=int, default=d.workers, help="concurrent workers (default %(default)s)")
    ap.add_argument("--delay", type=float, default=d.delay, help="min seconds between request starts, all workers combined")
    ap.add_argument("--jitter", type=float, default=d.jitter, help="extra random delay 0..jitter seconds")
    ap.add_argument("--retries", type=int, default=d.retries, help="retries for timeouts/429/5xx (default %(default)s)")
    ap.add_argument("--timeout", type=float, default=d.timeout, help="per-request timeout in seconds")
    ap.add_argument("--out", help="export results to this .csv or .json file")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    required = () if args.any_badge else read_required_badges(args.required_file)
    target = args.target or (len(required) if required else Settings().target)
    settings = Settings(target, args.workers, args.delay, args.jitter, args.retries, args.timeout, required)

    console = Console()
    students = read_students(args.csv, args.column)
    if not students:
        sys.exit("No rows found in CSV.")

    with Progress(TextColumn("[bold blue]Checking"), BarColumn(), MofNCompleteColumn(),
                  TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task("", total=len(students))
        results = run_checks(students, settings, on_done=lambda: progress.advance(task))

    shown = filter_results(results, args.only)
    render(results, settings.target, console, shown)
    if args.out:
        export_results(shown, args.out)
        console.print(f"Saved results to [bold]{args.out}[/]")
