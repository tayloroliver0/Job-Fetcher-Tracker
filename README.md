# Job Fetcher and Application Tracker

A command-line tool that pulls remote job listings from Remotive and Remote OK, lets you search and filter them, and tracks your applications in a local SQLite database.

[Watch the demo](https://youtu.be/uDvNYVL4EAU) (recorded for v1, which used Remotive only)

## Features

- Fetches job listings from two public APIs, Remotive and Remote OK
- If one source is down, the other source's jobs are still saved. The tool tells you which source failed and offers a retry
- Creates the jobs table on the first fetch and adds only new listings on later fetches, so there are no duplicates
- Filters listings by keyword and category, and exports a filtered shortlist to CSV
- Tracks applications: add a job, update its status, and attach notes. Updating a job that isn't in your tracker shows an error instead of failing silently

## Getting started

```bash
git clone https://github.com/tayloroliver0/Job-Fetcher-Tracker.git
cd Job-Fetcher-Tracker
pip install -r requirements.txt
python project.py
```

The menu offers three options:

1. **Fetch new listings** pulls the latest jobs from both sources.
2. **Browse jobs** filters listings and optionally exports them to CSV.
3. **Application tracker** adds a job to your tracker, updates its status, or attaches a note.

## Running the tests

```bash
pytest
```

## How it works

| File | Purpose |
| --- | --- |
| `project.py` | The main program: a command-line menu, a `Pipeline` class that manages the SQLite tables, and a `Job` class |
| `test_project.py` | Tests for `export_shortlist`, `clean_description`, `fetch_jobs`, and the network failure paths |
| `requirements.txt` | Python dependencies |

**Fetching.** `fetch_jobs` and `fetch_remoteok_jobs` each call one API and raise an exception if the request fails. `normfetch_jobs` converts both sources into the same dictionary shape, catches each source's failure separately, and returns the jobs plus a list of failures. The menu stores whatever came back, then prints each failure and asks whether to retry. `clean_description` strips the HTML from each description, and `store_jobs` inserts only the jobs that aren't already in the table.

**Browsing.** The chosen filters build a SQL query against the jobs table. Each result becomes a `Job` object that prints cleanly in the terminal, and `export_shortlist` writes the filtered jobs to a CSV file.

**Tracking.** The `Pipeline` methods `add_application`, `adj_status` and `add_note` write to a separate applications table. Adding a job that is already tracked, or one that doesn't exist, gives a different clear error for each case. Updating or annotating a job that isn't tracked yet reports an error instead of doing nothing.

**Testing.** The tests use temporary file paths and test data, so they never write to your real files. They replace `requests.get` and the fetch functions with fakes, so no test makes a real network request. The failure tests check that a network error escapes `fetch_jobs` and that one failing source doesn't lose the other source's jobs. `Pipeline` takes the database path as a parameter, which lets tests run against a temporary database.

## Design decisions

**SQLite instead of a flat file.** I needed data that persists and can be queried and updated row by row. A flat file would have meant reading everything and writing custom filtering logic for each operation, while SQLite provides all of that built in.

**Two tables instead of one.** I considered putting application status and notes as columns on the jobs table. I separated them because every job you haven't applied to would carry placeholder values in columns that don't apply to it.

**Functions take data as parameters instead of fetching it.** `clean_description` originally called `fetch_jobs()` internally. While writing its test I realized that would trigger a real network request every time, so I passed the data in instead. I later did the same for `store_jobs`, and `Pipeline` takes its database path as a parameter for the same reason: tests can supply their own inputs.

**Errors travel to the layer that can act on them.** The fetch functions raise on failure and never print or prompt. `normfetch_jobs` collects each source's failure as data, and the menu is the only place that talks to the user. This is what lets the menu offer a retry without losing the jobs from the source that worked.

**What I cut from v1.** I planned a `Scorer` class to rate job fit and a status history that logged every change. I dropped the history because letting the user overwrite a status was enough, and I dropped scoring because v1 didn't need it.

## Known limitations

- **Jobs are deduplicated by ID alone.** The two sources number their jobs independently, so a collision would silently skip a job. Their ID ranges don't overlap today, but nothing guarantees it.
- **Remote OK jobs have no category or job type.** The API only provides a list of tags, so filtering by category returns Remotive jobs only.
- **Remote OK salaries are shown as the raw range.** The API doesn't say whether a range is hourly or yearly, so I don't guess.
- **A retry re-fetches both sources.** This is harmless because duplicates are skipped, but it makes one extra request to a source that already worked.

## Roadmap

- Expand test coverage to the remaining `Pipeline` methods
- Retry only the source that failed
- Add an AI job-fit scorer using the Anthropic API

## Data sources

Job listings come from [Remotive](https://remotive.com) and [Remote OK](https://remoteok.com).

## Author

Oliver Taylor: [github.com/tayloroliver0](https://github.com/tayloroliver0)
