# Team Ratings Scraper for EvanMiya

This scraper fetches the Team Ratings table from `https://evanmiya.com/?team_ratings`, extracts the columns you requested, and saves the data to CSV and SQLite. It also zips the CSV so you can upload to Tableau easily.

Prerequisites
- Python 3.9+
- Install dependencies (preferably in a virtualenv):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Usage
- Run once and exit:

```powershell
python scrape_team_ratings.py --once
# skip creating zip if you want
python scrape_team_ratings.py --once --no-zip
```

- Run as a background scheduler (scrapes every 60 minutes by default):

```powershell
python scrape_team_ratings.py --daemon --minutes 60
# skip creating zip on each run
python scrape_team_ratings.py --daemon --minutes 60 --no-zip
```

Outputs
- `team_ratings.csv`: appended CSV with `scrape_time_utc` column
- `team_ratings.csv.zip`: zipped CSV (ready to upload to Tableau)
- `team_ratings.db`: SQLite DB with table `team_ratings`
- `scrape_team_ratings.log`: log file

Scheduling options
- Windows Task Scheduler: create a task to run the `--once` command on your preferred interval.
- GitHub Actions: see `.github/workflows/scrape.yml` for an example workflow that runs nightly.

Notes
- The site uses JavaScript (Shiny + reactable), so the scraper uses Playwright to render and extract the table (in CI this works out-of-the-box; on Windows you may need Python 3.11 or MSVC Build Tools).
- If the site exposes a CSV download endpoint in future, the script will attempt to detect and use it.
- CI workflow (`.github/workflows/scrape.yml`) runs nightly and uploads artifacts: CSV, DB, and zipped CSV for easy download.

Optional: Publish to Tableau automatically (advanced)
- If you want fully automated publishing to Tableau Server/Online, we can add an optional step to convert `team_ratings.csv` to a `.hyper` extract and publish via REST. This requires adding `tableauhyperapi` and `tableauserverclient` to `requirements.txt`, and configuring env vars (`TABLEAU_SERVER`, `TABLEAU_SITE_ID`, `TABLEAU_USERNAME`, `TABLEAU_PASSWORD`, `TABLEAU_PROJECT_NAME`, `TABLEAU_DATASOURCE_NAME`). Let me know and I’ll wire this in.

If you'd like I can:
- Add automatic team name normalization and a canonical mapping file.
- Add CSV header deduplication (single header row instead of repeated headers when appending).
- Add a small web UI or a data export endpoint.
