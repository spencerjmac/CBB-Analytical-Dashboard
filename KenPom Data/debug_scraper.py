"""
Debug script to inspect KenPom table structure and verify parsing.
"""
from scraper import KenPomScraper
from bs4 import BeautifulSoup
import requests

scraper = KenPomScraper()
url = "https://kenpom.com/index.php"

print("Fetching KenPom page...")
response = scraper.session.get(url, timeout=30)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the table
table = soup.find('table', {'id': 'ratings-table'})
if not table:
    tables = soup.find_all('table')
    for t in tables:
        if t.find('th') and ('Rank' in str(t.find('th')) or 'Team' in str(t.find('th'))):
            table = t
            break

if table:
    # Get header row
    header_row = table.find('tr')
    if header_row:
        headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        print("\nTable Headers:")
        for i, header in enumerate(headers):
            print(f"  Column {i}: {header}")
    
    # Get first few data rows
    rows = table.find_all('tr')[1:6]  # First 5 data rows
    print("\nFirst 5 Data Rows (showing first 10 columns):")
    for row_idx, row in enumerate(rows, 1):
        cells = row.find_all(['td', 'th'])
        print(f"\nRow {row_idx}:")
        for i, cell in enumerate(cells[:10]):  # First 10 columns
            text = cell.get_text(strip=True)
            print(f"  Col {i}: '{text}'")
        
        # Test parsing and show raw HTML
        if len(cells) > 6:
            print(f"  AdjO (col 5) raw HTML: {cells[5]}")
            print(f"  AdjO (col 5) text: '{cells[5].get_text(strip=True)}'")
            print(f"  AdjO (col 5) parsed: {scraper._parse_value_and_rank(cells[5].get_text(strip=True))}")
            print(f"  AdjD (col 6) raw HTML: {cells[6]}")
            print(f"  AdjD (col 6) text: '{cells[6].get_text(strip=True)}'")
            print(f"  AdjD (col 6) parsed: {scraper._parse_value_and_rank(cells[6].get_text(strip=True))}")
else:
    print("Could not find table!")

