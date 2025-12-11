#!/usr/bin/env python3
"""
Scrape team ratings from https://evanmiya.com/?team_ratings using Playwright.
Saves results to CSV and SQLite. Can run once or as a scheduled service.
"""
import argparse
import csv
import logging
import os
import sqlite3
import sys
import time
import math
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from typing import Optional

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.sync_api import sync_playwright

# Configuration
URL = os.environ.get("TEAM_RATINGS_URL", "https://evanmiya.com/?team_ratings")
OUT_CSV = os.environ.get("TEAM_RATINGS_CSV", "team_ratings.csv")
OUT_DB = os.environ.get("TEAM_RATINGS_DB", "team_ratings.db")
LOG = os.environ.get("TEAM_RATINGS_LOG", "scrape_team_ratings.log")
ZIP_OUTPUT = os.environ.get("TEAM_RATINGS_ZIP", "team_ratings.csv.zip")
MAX_RETRIES = int(os.environ.get("TEAM_RATINGS_MAX_RETRIES", "4"))
RETRY_BASE_SLEEP = float(os.environ.get("TEAM_RATINGS_RETRY_BASE", "2.0"))

# Team name mapping to match KenPom format
TEAM_NAME_MAPPING = {
    # Remove emojis and normalize to KenPom format
    "Iowa State": "Iowa St.",
    "Michigan State": "Michigan St.",
    "Connecticut": "Connecticut",
    "NC State": "N.C. State",
    "Ohio State": "Ohio St.",
    "Saint Mary's": "Saint Mary's",
    "Miami (Fla.)": "Miami FL",
    "Miami (OH)": "Miami OH",
    "Utah State": "Utah St.",
    "Ole Miss": "Mississippi",
    "San Diego State": "San Diego St.",
    "Florida State": "Florida St.",
    "Kansas State": "Kansas St.",
    "Oklahoma State": "Oklahoma St.",
    "Boise State": "Boise St.",
    "Arizona State": "Arizona St.",
    "Penn State": "Penn St.",
    "McNeese State": "McNeese",
    "Colorado State": "Colorado St.",
    "Mississippi State": "Mississippi St.",
    "Wichita State": "Wichita St.",
    "Illinois State": "Illinois St.",
    "New Mexico State": "New Mexico St.",
    "Fresno State": "Fresno St.",
    "Morgan State": "Morgan St.",
    "Ball State": "Ball St.",
    "Sacramento State": "Sacramento St.",
    "Portland State": "Portland St.",
    "Montana State": "Montana St.",
    "Weber State": "Weber St.",
    "San Jose State": "San Jose St.",
    "Appalachian State": "Appalachian St.",
    "Arkansas State": "Arkansas St.",
    "Georgia State": "Georgia St.",
    "Louisiana State": "LSU",
    "Murray State": "Murray St.",
    "Norfolk State": "Norfolk St.",
    "North Carolina State": "N.C. State",
    "North Dakota State": "North Dakota St.",
    "South Carolina State": "South Carolina St.",
    "South Dakota State": "South Dakota St.",
    "St. John's": "St. John's",
    "St. Mary's": "Saint Mary's",
    # Additional mappings from verification
    "Alabama State": "Alabama St.",
    "Alcorn State": "Alcorn St.",
    "Arkansas-Little Rock": "Little Rock",
    "Arkansas-Pine Bluff": "Arkansas Pine Bluff",
    "Cal State Bakersfield": "Cal St. Bakersfield",
    "Cal State Fullerton": "Cal St. Fullerton",
    "Cal State Northridge": "CSUN",
    "California Baptist": "Cal Baptist",
    "Chicago State": "Chicago St.",
    "Cleveland State": "Cleveland St.",
    "College of Charleston": "Charleston",
    "Coppin State": "Coppin St.",
    "Delaware State": "Delaware St.",
    "Detroit": "Detroit Mercy",
    "East Tennessee State": "East Tennessee St.",
    "Florida International": "FIU",
    "Fort Wayne": "Purdue Fort Wayne",
    "Gardner-Webb": "Gardner Webb",
    "Grambling": "Grambling St.",
    "Idaho State": "Idaho St.",
    "Illinois-Chicago": "Illinois Chicago",
    "Indiana State": "Indiana St.",
    "Jackson State": "Jackson St.",
    "Jacksonville State": "Jacksonville St.",
    "Kennesaw State": "Kennesaw St.",
    "Kent State": "Kent St.",
    "Long Beach State": "Long Beach St.",
    "Long Island": "LIU",
    "Louisiana-Lafayette": "Louisiana",
    "Louisiana-Monroe": "Louisiana Monroe",
    "Loyola Maryland": "Loyola MD",
    "Maryland-Eastern Shore": "Maryland Eastern Shore",
    "Mississippi Valley State": "Mississippi Valley St.",
    "Missouri State": "Missouri St.",
    "Missouri-Kansas City": "Kansas City",
    "Morehead State": "Morehead St.",
    "Nicholls State": "Nicholls",
    "North Texas": "North Texas",
    "Northwestern State": "Northwestern St.",
    "Omaha": "Nebraska Omaha",
    "Oregon State": "Oregon St.",
    "Prairie View": "Prairie View A&M",
    "SIU Edwardsville": "SIUE",
    "Saint Bonaventure": "St. Bonaventure",
    "Saint Francis (PA)": "Saint Francis",
    "Sam Houston State": "Sam Houston St.",
    "South Carolina Upstate": "USC Upstate",
    "Southeast Missouri State": "Southeast Missouri",
    "Southern Mississippi": "Southern Miss",
    "St. Thomas (MN)": "St. Thomas",
    "Tarleton State": "Tarleton St.",
    "Tennessee State": "Tennessee St.",
    "Tennessee-Martin": "Tennessee Martin",
    "Texas A&M-Corpus Christi": "Texas A&M Corpus Chris",
    "Texas State": "Texas St.",
    "Texas-Rio Grande Valley": "UT Rio Grande Valley",
    "Washington State": "Washington St.",
    "Wright State": "Wright St.",
    "Youngstown State": "Youngstown St.",
    "Bethune-Cookman": "Bethune Cookman",
    # Teams that just need emoji removal (keep same name)
    "Baylor": "Baylor",
    "Binghamton": "Binghamton",
    "Boston University": "Boston University",
    "Central Michigan": "Central Michigan",
    "Creighton": "Creighton",
    "Dayton": "Dayton",
    "Delaware": "Delaware",
    "Drake": "Drake",
    "East Carolina": "East Carolina",
    "Eastern Washington": "Eastern Washington",
    "George Mason": "George Mason",
    "Georgetown": "Georgetown",
    "IU Indy": "IU Indy",
    "Kansas": "Kansas",
    "Kentucky": "Kentucky",
    "Longwood": "Longwood",
    "Loyola Marymount": "Loyola Marymount",
    "Minnesota": "Minnesota",
    "Missouri": "Missouri",
    "Niagara": "Niagara",
    "North Carolina": "North Carolina",
    "Pittsburgh": "Pittsburgh",
    "Rhode Island": "Rhode Island",
    "Rider": "Rider",
    "Rutgers": "Rutgers",
    "Siena": "Siena",
    "Temple": "Temple",
    "Texas A&M": "Texas A&M",
    "Texas Tech": "Texas Tech",
    "UCLA": "UCLA",
    "UNLV": "UNLV",
    "USC": "USC",
    "Utah": "Utah",
    "VMI": "VMI",
    "Virginia Tech": "Virginia Tech",
    "Washington": "Washington",
    "Western Illinois": "Western Illinois",
    "Western Michigan": "Western Michigan",
    "Wisconsin": "Wisconsin",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", filename=LOG, filemode="a")
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

# Column names we want to capture (normalize against headers found on the page)
WANTED_COLUMNS = [
    "Relative Ranking",
    "Team",
    "O-Rate",
    "D-Rate",
    "Relative Rating",
    "Opponent Adjust",
    "Pace Adjust",
    "Off Rank",
    "Def Rank",
    "True Tempo",
    "Tempo Rank",
    "Injury Rank",
    "Home Rank",
    "Roster Rank",
    "Kill Shots Per Game",
    "Kill Shots Conceded Per Game",
    "Kill Shots Margin Per Game",
    "Total Kill Shots",
    "Total Kill Shots Conceded",
    "D1 Wins",
    "D1 Losses",
]


def extract_table_from_page(page):
    """Find the reactable table container and extract header+rows."""
    # Wait for the reactable container to render
    selector = "#team_ratings_page-team_ratings"
    logging.info("Waiting for table container %s", selector)
    try:
        page.wait_for_selector(selector, timeout=15000)
    except Exception:
        logging.warning("Container not found quickly, continuing to try to locate table")

    # Try common table selectors inside the container
    table = None
    possible_selectors = [
        f"{selector} table",
        f"{selector} .rt-table",
        f"{selector} div.reactable-table",
        f"{selector} table.reactable",
    ]
    for s in possible_selectors:
        elements = page.query_selector_all(s)
        if elements:
            table = elements[0]
            logging.info("Found table using selector %s", s)
            break

    # If no table element, try to read any text CSV generated by a download element
    if table is None:
        # Look for a download button that might expose CSV via attribute
        dl = page.query_selector("#team_ratings_page-download_team_ratings")
        if dl:
            logging.info("Found download button; attempting to click and capture generated data")
            try:
                with page.expect_download(timeout=5000) as d:
                    dl.click()
                download = d.value
                path = download.path()
                if path:
                    logging.info("Download saved to %s", path)
                    # read CSV into pandas
                    df = pd.read_csv(path)
                    return df
            except Exception as e:
                logging.warning("Download attempt failed: %s", e)

        # As a last resort, try to pull visible text and parse tabular content
        logging.info("No table element found; extracting visible text as fallback")
        text = page.inner_text(selector) if page.query_selector(selector) else page.content()
        # naive parse: split lines and commas
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            raise RuntimeError("Could not find table or textual data on page")
        # try to parse first line as header
        header = [h.strip() for h in lines[0].split("\t")]
        rows = [r.split("\t") for r in lines[1:]]
        df = pd.DataFrame(rows, columns=header)
        return df

    # If we found a table element, extract headers and rows via JS evaluation for robustness
    logging.info("Extracting rows from table DOM")
    script = """
    (table) => {
        function text(el){ return el ? el.innerText.trim() : ''; }
        
        // Reactable uses role attributes, try those first
        let headers = [];
        let headerEls = table.querySelectorAll('[role="columnheader"]');
        if(headerEls && headerEls.length>0){
            headers = Array.from(headerEls).map(h => text(h));
        }
        
        // Fallback strategies if role attribute not found
        if(headers.length === 0){
            headerEls = table.querySelectorAll('thead th, thead td');
            if(headerEls && headerEls.length>0){
                headers = Array.from(headerEls).map(h => text(h));
            }
        }
        
        if(headers.length === 0){
            headerEls = table.querySelectorAll('.rt-th');
            if(headerEls && headerEls.length>0){
                headers = Array.from(headerEls).map(h => text(h));
            }
        }
        
        // Extract rows - reactable uses divs with role="row" and cells with role="cell"
        const rows = [];
        const rowEls = table.querySelectorAll('.rt-tbody [role="row"]');
        if(rowEls && rowEls.length>0){
            for(const r of rowEls){
                const cells = r.querySelectorAll('[role="cell"]');
                if(cells && cells.length > 0){
                    rows.push(Array.from(cells).map(td => text(td)));
                }
            }
        } else {
            // Fallback to standard table structure
            const tbodyRows = table.querySelectorAll('tbody tr');
            if(tbodyRows && tbodyRows.length>0){
                for(const r of tbodyRows){
                    rows.push(Array.from(r.querySelectorAll('td')).map(td => text(td)));
                }
            }
        }
        
        return {headers: headers, rows: rows, row_count: rows.length, header_count: headers.length};
    }
    """
    result = page.evaluate(script, table)
    headers = result.get("headers") or []
    rows = result.get("rows") or []
    row_count = result.get("row_count", 0)
    header_count = result.get("header_count", 0)
    
    logging.info("Extracted %d headers and %d rows", header_count, row_count)
    
    if not headers:
        logging.error("No headers found")
        raise RuntimeError("No table headers found")
    
    if not rows:
        logging.error("No data rows found")
        raise RuntimeError("No table rows found")

    df = pd.DataFrame(rows, columns=headers)
    return df


def normalize_team_names(team_name: str) -> str:
    """Normalize team names to match KenPom format.
    
    Removes emojis and applies custom mapping to standardize names.
    """
    import re
    
    # Remove emojis using a comprehensive pattern
    # This covers all emoji ranges including newer emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+", 
        flags=re.UNICODE
    )
    
    clean_name = emoji_pattern.sub('', team_name).strip()
    
    # Apply custom mapping if exists
    if clean_name in TEAM_NAME_MAPPING:
        return TEAM_NAME_MAPPING[clean_name]
    
    return clean_name


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Map header variants to canonical names
    mapping = {}
    for col in df.columns:
        key = col.strip()
        # simple exact matches or case-insensitive
        for want in WANTED_COLUMNS:
            if key.lower() == want.lower():
                mapping[col] = want
                break
        else:
            # some known variants
            if key.lower() in ["off rank", "off_rank", "offrank"]:
                mapping[col] = "Off Rank"
            if key.lower() in ["def rank", "def_rank", "defrank"]:
                mapping[col] = "Def Rank"
            if "kill" in key.lower() and "conced" in key.lower():
                mapping[col] = "Kill Shots Conceded Per Game"
            if "kill" in key.lower() and "per game" in key.lower() and "conced" not in key.lower():
                mapping[col] = "Kill Shots Per Game"
            if key.lower() in ["wins", "d1 wins"]:
                mapping[col] = "D1 Wins"
            if key.lower() in ["losses", "d1 losses"]:
                mapping[col] = "D1 Losses"
            if key.lower() in ["team"]:
                mapping[col] = "Team"
            if key.lower() in ["o-rate","o rate","off rate","offensive"]:
                mapping[col] = "O-Rate"
            if key.lower() in ["d-rate","d rate","defensive"]:
                mapping[col] = "D-Rate"
    df = df.rename(columns=mapping)
    # Keep requested columns that exist; add missing with NaN
    for want in WANTED_COLUMNS:
        if want not in df.columns:
            df[want] = pd.NA
    # Reorder
    df = df[WANTED_COLUMNS]
    
    # Normalize team names to match KenPom format
    if "Team" in df.columns:
        logging.info("Normalizing team names...")
        original_teams = df["Team"].head(5).tolist()
        df["Team"] = df["Team"].apply(normalize_team_names)
        normalized_teams = df["Team"].head(5).tolist()
        logging.info(f"Sample before: {original_teams}")
        logging.info(f"Sample after: {normalized_teams}")
    
    return df


def save_to_csv(df: pd.DataFrame, path: str, overwrite: bool = True):
    """Persist the current snapshot to CSV. Overwrites previous file by default."""
    timestamp = datetime.utcnow().isoformat()
    df_out = df.copy()
    df_out["scrape_time_utc"] = timestamp
    # Always overwrite for snapshot semantics
    try:
        df_out.to_csv(path, index=False)
        logging.info("Wrote fresh snapshot CSV (%d rows) to %s", len(df_out), path)
    except Exception as e:
        logging.error("Failed writing CSV: %s", e)
        raise


def save_to_sqlite(df: pd.DataFrame, db_path: str, table_name: str = "team_ratings"):
    """Persist current snapshot to SQLite, replacing previous contents."""
    df2 = df.copy()
    df2["scrape_time_utc"] = datetime.utcnow().isoformat()
    conn = sqlite3.connect(db_path)
    try:
        df2.to_sql(table_name, conn, if_exists="replace", index=False)
        logging.info("Replaced data in sqlite %s table %s (%d rows)", db_path, table_name, len(df2))
    finally:
        conn.close()


def zip_csv(csv_path: str, zip_path: str):
    if not os.path.exists(csv_path):
        logging.warning("CSV not found to zip: %s", csv_path)
        return
    with ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED) as zf:
        arcname = os.path.basename(csv_path)
        zf.write(csv_path, arcname=arcname)
    logging.info("Zipped CSV to %s", zip_path)


def _scrape_once() -> Optional[pd.DataFrame]:
    """Perform a single browser visit & attempt to pull the table."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(URL, timeout=60000)
        
        # Wait for the Shiny app to initialize and populate data
        time.sleep(3)
        selector = "#team_ratings_page-team_ratings"
        logging.info("Waiting for table container to populate with data")
        
        # Wait for actual data rows to appear, not just the container
        try:
            page.wait_for_selector(f"{selector} [role='row']", timeout=20000)
            logging.info("Data rows detected in table")
        except Exception:
            logging.warning("Timed out waiting for data rows; proceeding anyway")
        
        # Additional wait for JS to finish rendering
        time.sleep(2)
        
        # Check if table is paginated and expand to show all rows
        try:
            # Look for pagination controls
            page_info = page.query_selector(f"{selector} .rt-page-info")
            if page_info:
                page_text = page_info.inner_text()
                logging.info("Pagination info: %s", page_text)
            
            # Try different strategies to load all rows
            # Strategy 1: Look for page size dropdown
            page_size_selector = page.query_selector(f"{selector} select")
            if page_size_selector:
                logging.info("Found page size selector; checking available options")
                options_script = """
                    (select) => {
                        const options = Array.from(select.options);
                        return options.map(o => ({value: o.value, text: o.text}));
                    }
                """
                options = page.evaluate(options_script, page_size_selector)
                logging.info("Available page size options: %s", options)
                # Select the largest option by value
                if options:
                    max_option = max(options, key=lambda x: int(x['value']) if x['value'].isdigit() else 0)
                    logging.info("Selecting option: %s", max_option)
                    page_size_selector.select_option(value=max_option['value'])
                    time.sleep(3)
                    logging.info("Selected page size %s", max_option['value'])
                else:
                    logging.warning("No valid options found in page size selector")
            else:
                logging.info("No page size dropdown found; table might show all rows by default or need scrolling")
        except Exception as e:
            logging.warning("Could not expand pagination: %s", e)
        
        try:
            df = extract_table_from_page(page)
        finally:
            context.close(); browser.close()
    return df

def do_scrape(output_csv=OUT_CSV, output_db=OUT_DB, make_zip: bool = True, zip_path: str = ZIP_OUTPUT):
    logging.info("Starting scrape of %s", URL)
    attempt = 0
    last_exc: Optional[Exception] = None
    df: Optional[pd.DataFrame] = None
    while attempt < MAX_RETRIES:
        try:
            df = _scrape_once()
            if df is not None and not df.empty:
                break
            logging.warning("Empty dataframe on attempt %d", attempt + 1)
        except Exception as e:
            last_exc = e
            logging.warning("Attempt %d failed: %s", attempt + 1, e)
        attempt += 1
        if attempt < MAX_RETRIES:
            sleep_sec = RETRY_BASE_SLEEP * math.pow(2, attempt - 1)
            logging.info("Retrying in %.1f seconds (attempt %d/%d)", sleep_sec, attempt + 1, MAX_RETRIES)
            time.sleep(sleep_sec)

    if df is None or df.empty:
        logging.error("Failed to scrape data after %d attempts", MAX_RETRIES)
        if last_exc:
            logging.error("Last exception: %s", last_exc)
        return False

    try:
        df = normalize_columns(df)
        save_to_csv(df, output_csv)
        save_to_sqlite(df, output_db)
        if make_zip:
            zip_csv(output_csv, zip_path)
    except Exception as e:
        logging.error("Post-processing failed: %s", e)
        return False
    logging.info("Scrape complete: %d rows", len(df))
    return True


def main():
    parser = argparse.ArgumentParser(description="Scrape team ratings and save to CSV/SQLite")
    parser.add_argument("--once", action="store_true", help="Run one time and exit (default)")
    parser.add_argument("--daemon", action="store_true", help="Run as a background scheduler, scraping every N minutes")
    parser.add_argument("--minutes", type=int, default=60, help="Scheduler interval in minutes when using --daemon")
    parser.add_argument("--no-zip", action="store_true", help="Do not create a zipped CSV output")
    args = parser.parse_args()

    if args.daemon:
        sched = BackgroundScheduler()
        sched.add_job(lambda: do_scrape(make_zip=not args.no_zip), "interval", minutes=args.minutes, next_run_time=datetime.now())
        logging.info("Starting scheduler: scrape every %d minutes", args.minutes)
        sched.start()
        try:
            while True:
                time.sleep(30)
        except (KeyboardInterrupt, SystemExit):
            logging.info("Shutting down scheduler")
            sched.shutdown()
    else:
        success = do_scrape(make_zip=not args.no_zip)
        if not success:
            sys.exit(2)


if __name__ == "__main__":
    main()
