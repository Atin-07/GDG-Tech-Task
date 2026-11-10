# Learn With Communities Tracker

A CLI tool that reads a CSV of Google Skills public profile URLs, counts each student's completed skill badges, and reports who has finished the campaign, who is in progress and various other options!

Built for the GDGoC NFSU Gandhinagar core team selection (Tech lead task).

## Project structure
```
skills-tracker/
├── main.py                 # entry point (thin wrapper around tracker.cli)
├── requirements.txt
├── pytest.ini
├── data/
│   ├── GDG_Tech_Lead_Task_Sample.csv # fake sample rows only; real data is git-ignored
│   └── required_badges.txt # the 10 campaign badge titles (edit if the curriculum changes)
├── output/                 # exported results go here (git-ignored)
├── tracker/
│   ├── config.py           # constants, regexes, default Settings
│   ├── models.py           # Student, Result, status codes
│   ├── errors.py           # FetchError
│   ├── validators.py       # profile URL validation
│   ├── rate_limiter.py     # global rate limiter shared by all threads
│   ├── fetcher.py          # HTTP GET with retries + exponential backoff
│   ├── parser.py           # HTML -> (name, unique badge count)
│   ├── checker.py          # one student -> one Result (status logic)
│   ├── runner.py           # thread pool, keeps input order
│   ├── csv_io.py           # read CSV, export CSV/JSON
│   ├── report.py           # rich summary table
│   └── cli.py              # argparse + wiring
└── tests/                  # one test file per module, fake HTTP, no network
```
Data flows one way: `cli -> csv_io -> runner -> checker -> (validators, fetcher -> rate_limiter, parser) -> report`.

## How it works
1. Reads the CSV (column `Google Skills Profile URL`; an optional `Name` column is used for display).
2. Validates each URL (must be a `skills.google` public profile URL).
3. Fetches the profile page. The page is server-rendered, so no browser automation is needed.
4. Checks which of the **10 required campaign badges** (`data/required_badges.txt`) appear as earned on the profile. Badges outside the list do not count. Use `--any-badge` to count any badge instead.
5. Prints a progress bar and a colour-coded table, and optionally exports CSV/JSON.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
```bash
python main.py data/students_sample.csv
python main.py students.csv --target 10 --workers 3 --delay 1.0 --out output/results.csv
python main.py students.csv --out output/results.json
python main.py students.csv --only complete --out output/finishers.csv
```

| Option | Default | Meaning |
|---|---|---|
| `--column` | `Google Skills Profile URL` | URL column header |
| `--target` | number of required badges | Badges needed for COMPLETE |
| `--required-file` | `data/required_badges.txt` | One required badge title per line |
| `--any-badge` | off | Count any badge, ignore the required list |
| `--only` | none | `complete`, `incomplete` or `errors`: show/export just that group |
| `--workers` | 3 | Concurrent workers |
| `--delay` | 1.0 | Minimum seconds between request starts (shared by all workers) |
| `--jitter` | 0.5 | Extra random 0..N seconds added to each gap |
| `--retries` | 3 | Retries on timeout / 429 / 5xx |
| `--timeout` | 15 | Per-request timeout (s) |
| `--out` | none | Export to `.csv` or `.json` |

An example on the sample CSV provided:
<img width="959" height="563" alt="image" src="https://github.com/user-attachments/assets/2c78b342-debc-4581-9468-aadf2d60f194" />



## CSV format
```csv
Name,Google Skills Profile URL
Sample Complete,https://www.skills.google/public_profiles/be556f7b-ab4b-4be7-82fb-9be45202ddd7
```
The student list is fully customizable: pass any CSV path. Only the URL column is required.

## Rate limiting
A single global limiter (`rate_limiter.py`) spaces out request *start times* across all worker threads (`--delay` plus random jitter), so raising `--workers` can never exceed the configured request rate. Workers only overlap network latency.

## Error handling
One bad row never stops the run. Each row ends with exactly one status:

| Status | Meaning |
|---|---|
| `COMPLETE` | badges >= target |
| `IN_PROGRESS` | 1 to target-1 badges |
| `NO_BADGES` | profile visible, zero badges |
| `PRIVATE_OR_UNAVAILABLE` | page loaded but no profile content is visible |
| `NOT_FOUND` | HTTP 404 |
| `INVALID_URL` | empty or not a Google Skills profile URL |
| `RATE_LIMITED` / `SERVER_ERROR` | 429 / 5xx persisted after all retries |
| `NETWORK_ERROR` | timeouts or connection failures after all retries |
| `PARSE_ERROR` | unexpected response or parser failure |
| `DUPLICATE` | same profile URL as an earlier row; fetched only once |

Retries use exponential backoff with jitter and respect `Retry-After` on 429.

## Tests
```bash
python -m pytest -q
```
26 tests covering required-badge matching, duplicates, filters, validation, parsing, every status path, retry/backoff, the rate limiter, and CSV/JSON I/O, using a fake HTTP session.

## Design decisions
- `requests` + `BeautifulSoup`: lighter and faster than a headless browser.
- Unique badge IDs prevent double counting.
- Fetching, parsing and status logic are separate modules, so each can be tested and changed independently.
- Threads (not async): the work is I/O-bound and small, and the global limiter keeps the request rate fixed anyway.

## Limitations
- Badge titles are matched by name. If Google renames a course, update `data/required_badges.txt`.
- The private-profile check is heuristic until verified against real private profiles.
