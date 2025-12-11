"""
Verification script to check if scraper is working correctly.
Run this to verify the scraper is getting correct values.
"""
from scraper import KenPomScraper
from database import KenPomDB
from datetime import datetime

print("=" * 60)
print("KenPom Scraper Verification")
print("=" * 60)

# Test scraper
print("\n[1/3] Testing scraper...")
scraper = KenPomScraper()
data = scraper.scrape_rankings()

if not data:
    print("ERROR: No data scraped!")
    exit(1)

print(f"Successfully scraped {len(data)} teams")

# Check Duke values
duke = [d for d in data if d.get('team_name') == 'Duke'][0] if data else None

if duke:
    print("\n[2/3] Verifying Duke values (reference team):")
    print(f"  AdjEM: {duke.get('adj_em')}")
    print(f"  AdjO: {duke.get('adj_o')}")
    print(f"  AdjD: {duke.get('adj_d')} (calculated: {duke.get('adj_o') - duke.get('adj_em') if duke.get('adj_o') and duke.get('adj_em') else 'N/A'})")
    print(f"  AdjT: {duke.get('adj_tempo')}")
    print(f"  Luck: {duke.get('luck')}")
    
    # Verify AdjD calculation
    if duke.get('adj_o') and duke.get('adj_em'):
        calculated = duke.get('adj_o') - duke.get('adj_em')
        stored = duke.get('adj_d')
        if abs(calculated - stored) < 0.1:
            print("  AdjD calculation: CORRECT")
        else:
            print(f"  AdjD calculation: ERROR (calculated: {calculated}, stored: {stored})")
else:
    print("WARNING: Duke not found in scraped data")

# Check database
print("\n[3/3] Checking database...")
db = KenPomDB()
try:
    latest = db.get_latest_rankings(limit=5)
    if latest:
        print(f"Latest data in database: {latest[0].get('date')}")
        print(f"Number of teams in latest data: {len(latest)}")
    else:
        print("No data found in database")
finally:
    db.close()

print("\n" + "=" * 60)
print("Verification complete!")
print("=" * 60)

