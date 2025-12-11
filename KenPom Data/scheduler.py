"""
Daily scheduler for KenPom data scraping and Tableau export.
Run this script to set up daily automatic scraping and export.
"""
import schedule
import time
import sys
import importlib

# Force fresh imports to avoid cached module issues
# This ensures the scheduler always uses the latest scraper code
def reload_modules():
    """Reload modules to ensure latest code is used."""
    modules_to_reload = ['scraper', 'main', 'scrape_and_export']
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])

from scrape_and_export import scrape_and_export_tableau


def run_daily():
    """Run the scraper and exporter daily at a specified time."""
    # Schedule to run daily at 2:00 AM (adjust as needed)
    # This will scrape AND export to Tableau automatically
    # Reload modules before each scheduled run to ensure latest code
    def scheduled_scrape():
        reload_modules()
        from scrape_and_export import scrape_and_export_tableau
        scrape_and_export_tableau(export_format='csv')
    
    schedule.every().day.at("02:00").do(scheduled_scrape)
    
    # Or run every day at a specific time
    # schedule.every().day.at("06:00").do(scrape_and_export_tableau, export_format='csv')
    
    print("Scheduler started. KenPom scraper and Tableau export will run daily at 02:00 AM")
    print("Press Ctrl+C to stop the scheduler")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nScheduler stopped.")


if __name__ == "__main__":
    # Reload modules to ensure we're using latest code
    reload_modules()
    from scrape_and_export import scrape_and_export_tableau
    
    # You can also run immediately on start
    print("Running initial scrape and export...")
    scrape_and_export_tableau(export_format='csv')
    
    print("\nStarting daily scheduler...")
    run_daily()


