"""
Export Bart Torvik data to Tableau-ready CSV.
Normalizes team names to match KenPom naming conventions.
"""
import pandas as pd
from datetime import datetime
from scraper_torvik import BartTorvikScraper


# Team name mapping from Bart Torvik to KenPom format
# KenPom uses full names, not abbreviations
TEAM_NAME_MAPPING = {
    # Common variations that need normalization - must match KenPom exactly
    'Arkansas Pine Bluff': 'Arkansas Pine Bluff',
    'Cal St. Bakersfield': 'Cal St. Bakersfield',
    'Cal St. Fullerton': 'Cal St. Fullerton',
    'Cal St. Northridge': 'CSUN',
    'Central Connecticut': 'Central Connecticut',
    'Charleston Southern': 'Charleston Southern',
    'Coastal Carolina': 'Coastal Carolina',
    'Eastern Illinois': 'Eastern Illinois',
    'Eastern Kentucky': 'Eastern Kentucky',
    'Eastern Michigan': 'Eastern Michigan',
    'Eastern Washington': 'Eastern Washington',
    'Fairleigh Dickinson': 'Fairleigh Dickinson',
    'Florida Atlantic': 'Florida Atlantic',
    'Florida Gulf Coast': 'Florida Gulf Coast',
    'Georgia St.': 'Georgia St.',
    'Grambling St.': 'Grambling St.',
    'Illinois Chicago': 'Illinois Chicago',
    'IU Indy': 'IU Indy',
    'Le Moyne': 'Le Moyne',
    'Lindenwood': 'Lindenwood',
    'Long Beach St.': 'Long Beach St.',
    'LIU': 'LIU',
    'Louisiana Monroe': 'Louisiana Monroe',
    'Loyola Chicago': 'Loyola Chicago',
    'Loyola Marymount': 'Loyola Marymount',
    'McNeese St.': 'McNeese',
    'Maryland Eastern Shore': 'Maryland Eastern Shore',
    'Miami FL': 'Miami FL',
    'Miami OH': 'Miami OH',
    'Mississippi St.': 'Mississippi St.',
    'Montana St.': 'Montana St.',
    'Nebraska Omaha': 'Nebraska Omaha',
    'New Mexico St.': 'New Mexico St.',
    'Nicholls St.': 'Nicholls',
    'North Carolina A&T': 'North Carolina A&T',
    'North Dakota': 'North Dakota',
    'Northern Colorado': 'Northern Colorado',
    'Northern Illinois': 'Northern Illinois',
    'Northern Iowa': 'Northern Iowa',
    'Northern Kentucky': 'Northern Kentucky',
    'Northwestern': 'Northwestern',
    'Oklahoma St.': 'Oklahoma St.',
    'Oregon St.': 'Oregon St.',
    'Penn St.': 'Penn St.',
    'Portland St.': 'Portland St.',
    'Purdue Fort Wayne': 'Purdue Fort Wayne',
    'Queens': 'Queens',
    'Saint Francis': 'Saint Francis',
    'Saint Joseph\'s': 'Saint Joseph\'s',
    'Saint Louis': 'Saint Louis',
    'Saint Mary\'s': 'Saint Mary\'s',
    'Saint Peter\'s': 'Saint Peter\'s',
    'San Diego St.': 'San Diego St.',
    'San Jose St.': 'San Jose St.',
    'Southeastern Louisiana': 'Southeastern Louisiana',
    'Southeast Missouri St.': 'Southeast Missouri',
    'Southern': 'Southern',
    'Southern Illinois': 'Southern Illinois',
    'SIU Edwardsville': 'SIUE',
    'Southern Indiana': 'Southern Indiana',
    'Southern Miss': 'Southern Miss',
    'South Carolina St.': 'South Carolina St.',
    'St. Bonaventure': 'St. Bonaventure',
    'St. John\'s': 'St. John\'s',
    'St. Thomas': 'St. Thomas',
    'Stony Brook': 'Stony Brook',
    'TCU': 'TCU',
    'Tennessee Tech': 'Tennessee Tech',
    'Texas A&M Corpus Chris': 'Texas A&M Corpus Chris',
    'Texas Southern': 'Texas Southern',
    'UC Davis': 'UC Davis',
    'UC Irvine': 'UC Irvine',
    'UC Riverside': 'UC Riverside',
    'UC San Diego': 'UC San Diego',
    'UC Santa Barbara': 'UC Santa Barbara',
    'UCF': 'UCF',
    'UMBC': 'UMBC',
    'UMKC': 'Kansas City',
    'UMass Lowell': 'UMass Lowell',
    'UNC Asheville': 'UNC Asheville',
    'UNC Greensboro': 'UNC Greensboro',
    'UNC Wilmington': 'UNC Wilmington',
    'USC Upstate': 'USC Upstate',
    'UT Rio Grande Valley': 'UT Rio Grande Valley',
    'UTEP': 'UTEP',
    'Utah St.': 'Utah St.',
    'Utah Tech': 'Utah Tech',
    'Utah Valley': 'Utah Valley',
    'VMI': 'VMI',
    'VCU': 'VCU',
    'West Virginia': 'West Virginia',
    'Western Carolina': 'Western Carolina',
    'Western Illinois': 'Western Illinois',
    'Western Kentucky': 'Western Kentucky',
    'Western Michigan': 'Western Michigan',
    'Wright St.': 'Wright St.',
    'Youngstown St.': 'Youngstown St.',
}


def normalize_team_name(torvik_name: str) -> str:
    """Normalize Bart Torvik team name to KenPom format."""
    # Check if we have an explicit mapping
    if torvik_name in TEAM_NAME_MAPPING:
        return TEAM_NAME_MAPPING[torvik_name]
    return torvik_name


def export_to_csv(filename='torvik_tableau.csv'):
    """
    Scrape Bart Torvik data and export to CSV for Tableau.
    """
    print("=" * 60)
    print(f"Bart Torvik Data Export for Tableau")
    print("=" * 60)
    
    # Scrape data
    print("\nScraping Bart Torvik rankings...")
    scraper = BartTorvikScraper()
    teams_data = scraper.scrape_rankings()
    
    if not teams_data:
        print("ERROR: No data scraped!")
        return False
    
    print(f"Successfully scraped {len(teams_data)} teams")
    
    # Convert to DataFrame
    df = pd.DataFrame(teams_data)
    
    # Normalize team names
    print("\nNormalizing team names to match KenPom...")
    df['team_name_normalized'] = df['team_name'].apply(normalize_team_name)
    
    # Add date components for Tableau
    df['year'] = pd.to_datetime(df['date']).dt.year
    df['month'] = pd.to_datetime(df['date']).dt.month
    df['day'] = pd.to_datetime(df['date']).dt.day
    
    # Reorder columns for Tableau
    column_order = [
        'date', 'year', 'month', 'day',
        'rank', 'team_name', 'team_name_normalized', 'conference',
        'games', 'record',
        'adj_oe', 'adj_de', 'barthag', 'adj_tempo', 'wab',
        'efg_pct', 'efg_pct_d', 'tor', 'tord', 
        'orb', 'drb', 'ftr', 'ftrd',
        'two_p_pct', 'two_p_pct_d', 'three_p_pct', 'three_p_pct_d',
        'three_pr', 'three_prd'
    ]
    
    # Only include columns that exist
    existing_cols = [col for col in column_order if col in df.columns]
    df = df[existing_cols]
    
    # Export to CSV
    print(f"\nExporting to {filename}...")
    df.to_csv(filename, index=False)
    
    print(f"\n[SUCCESS] Exported {len(df)} teams to {filename}")
    print(f"Date: {df['date'].iloc[0]}")
    print(f"\nFirst 5 teams:")
    for _, row in df.head().iterrows():
        print(f"  {row['rank']}. {row['team_name_normalized']} ({row['conference']}) - Barthag: {row['barthag']:.5f}")
    
    print("\n" + "=" * 60)
    print("Export completed successfully!")
    print("=" * 60)
    
    return True


def main():
    """Main function."""
    export_to_csv()


if __name__ == '__main__':
    main()
