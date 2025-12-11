"""
Combined script to scrape KenPom data and automatically export to Tableau format.
This is the recommended script for daily automation.
"""
import sys
import os
from datetime import datetime
from main import scrape_and_store
from export_to_tableau import export_to_csv, export_to_excel

def log_message(message):
    """Log a message to both console and log file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    # Also write to log file
    log_file = "scrape_log.txt"
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")


def scrape_and_export_tableau(export_format='csv'):
    """
    Scrape KenPom data and export to Tableau format in one operation.
    
    Args:
        export_format: 'csv', 'excel', or 'both'
    """
    log_message("=" * 60)
    log_message("KenPom Scrape & Export to Tableau - Starting")
    log_message("=" * 60)
    
    # Step 1: Scrape data
    log_message("[Step 1/2] Scraping KenPom data...")
    success = scrape_and_store()
    
    if not success:
        log_message("ERROR: Scraping failed. Export cancelled.")
        return False
    
    # Step 2: Export to Tableau
    log_message("[Step 2/2] Exporting to Tableau format...")
    try:
        # Export only latest date's data (one row per team) for Tableau
        # This keeps the CSV file size manageable and shows current rankings
        if export_format.lower() == 'csv':
            export_to_csv(latest_only=True)  # Only latest date
        elif export_format.lower() == 'excel':
            export_to_excel()  # Excel still has multiple sheets including latest
        elif export_format.lower() == 'both':
            export_to_csv(latest_only=True)  # CSV: latest only
            export_to_excel()  # Excel: multiple sheets
        else:
            log_message(f"Unknown format: {export_format}. Using CSV.")
            export_to_csv(latest_only=True)  # Only latest date
        
        log_message("=" * 60)
        log_message("SUCCESS: Data scraped and exported to Tableau!")
        log_message("=" * 60)
        log_message("Next steps: Open Tableau Desktop and refresh your data source")
        return True
        
    except Exception as e:
        log_message(f"ERROR: Export failed: {e}")
        import traceback
        error_details = traceback.format_exc()
        log_message(f"Traceback: {error_details}")
        return False


if __name__ == "__main__":
    # Check for export format argument
    export_format = 'csv'
    if len(sys.argv) > 1:
        export_format = sys.argv[1].lower()
    
    scrape_and_export_tableau(export_format)

