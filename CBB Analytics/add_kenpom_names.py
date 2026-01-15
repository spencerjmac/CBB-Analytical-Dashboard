"""
Add KenPom team name column to CBB Analytics data for easier merging in Tableau
"""
import pandas as pd

# Manual mapping from CBB Analytics team names to KenPom team names
TEAM_NAME_MAPPING = {
    # A
    'A&M-Corpus Christi': 'Texas A&M Corpus Chris',
    'Alcorn': 'Alcorn St.',
    'App State': 'Appalachian St.',
    'Ark.-Pine Bluff': 'Arkansas Pine Bluff',
    'Army West Point': 'Army',
    
    # B
    'Boston U.': 'Boston University',
    
    # C
    'CSU Bakersfield': 'Cal St. Bakersfield',
    'California Baptist': 'Cal Baptist',
    'Central Ark.': 'Central Arkansas',
    'Central Conn. St.': 'Central Connecticut',
    'Central Mich.': 'Central Michigan',
    'Charleston So.': 'Charleston Southern',
    'Col. of Charleston': 'Charleston',
    
    # D
    'Detroit': 'Detroit Mercy',
    
    # E
    'ETSU': 'East Tennessee St.',
    'Eastern Ill.': 'Eastern Illinois',
    'Eastern Ky.': 'Eastern Kentucky',
    'Eastern Mich.': 'Eastern Michigan',
    'Eastern Wash.': 'Eastern Washington',
    
    # F
    'FDU': 'Fairleigh Dickinson',
    'FGCU': 'Florida Gulf Coast',
    'Fla. Atlantic': 'Florida Atlantic',
    
    # G
    'Ga. Southern': 'Georgia Southern',
    'Gardner-Webb': 'Gardner Webb',
    'Grambling': 'Grambling St.',
    
    # L
    'LMU (CA)': 'Loyola Marymount',
    'Lamar University': 'Lamar',
    
    # M
    'Middle Tenn.': 'Middle Tennessee',
    'Mississippi Val.': 'Mississippi Valley St.',
    
    # N
    'N.C. A&T': 'North Carolina A&T',
    'N.C. Central': 'North Carolina Central',
    'NC State': 'N.C. State',
    'NIU': 'Northern Illinois',
    'North Ala.': 'North Alabama',
    'Northern Ariz.': 'Northern Arizona',
    'Northern Colo.': 'Northern Colorado',
    'Northern Ky.': 'Northern Kentucky',
    
    # O
    'Ole Miss': 'Mississippi',
    
    # Q
    'Queens (NC)': 'Queens',
    
    # S
    'SFA': 'Stephen F. Austin',
    'Saint Mary\'s (CA)': 'Saint Mary\'s',
    'Sam Houston': 'Sam Houston St.',
    'Seattle U': 'Seattle',
    'South Fla.': 'South Florida',
    'Southeast Mo. St.': 'Southeast Missouri',
    'Southeastern La.': 'Southeastern Louisiana',
    'Southern California': 'USC',
    'Southern Ill.': 'Southern Illinois',
    'Southern Ind.': 'Southern Indiana',
    'Southern Miss.': 'Southern Miss',
    'Southern U.': 'Southern',
    'St. John\'s (NY)': 'St. John\'s',
    
    # U
    'UAlbany': 'Albany',
    'UConn': 'Connecticut',
    'UIC': 'Illinois Chicago',
    'UIW': 'Incarnate Word',
    'ULM': 'Louisiana Monroe',
    'UMES': 'Maryland Eastern Shore',
    'UNCW': 'UNC Wilmington',
    'UNI': 'Northern Iowa',
    'UT Martin': 'Tennessee Martin',
    'UTRGV': 'UT Rio Grande Valley',
    
    # W
    'WI Green Bay': 'Green Bay',
    'West Ga.': 'West Georgia',
    'Western Caro.': 'Western Carolina',
    'Western Ill.': 'Western Illinois',
    'Western Ky.': 'Western Kentucky',
    'Western Mich.': 'Western Michigan',
}


def add_kenpom_team_names():
    """Add KenPom team name column to CBB Analytics cleaned data"""
    
    # Load the cleaned CBB Analytics data
    df = pd.read_csv('cbb_analytics_tableau_cleaned.csv')
    
    print(f"Loaded {len(df)} teams from CBB Analytics")
    
    # Add the kenpom_team_name column
    # Use the mapping if available, otherwise use the same name
    df['kenpom_team_name'] = df['team_kenpom'].apply(
        lambda x: TEAM_NAME_MAPPING.get(x, x)
    )
    
    # Verify the mapping
    print(f"\nAdded 'kenpom_team_name' column")
    
    # Count how many were mapped vs unchanged
    mapped = df['kenpom_team_name'] != df['team_kenpom']
    print(f"  Mapped {mapped.sum()} team names")
    print(f"  Unchanged {(~mapped).sum()} team names")
    
    # Show some examples of mappings
    print("\nSample mappings:")
    mapped_examples = df[mapped][['team_kenpom', 'kenpom_team_name']].drop_duplicates().head(10)
    for _, row in mapped_examples.iterrows():
        print(f"  {row['team_kenpom']} -> {row['kenpom_team_name']}")
    
    # Verify against actual KenPom data
    try:
        kenpom_df = pd.read_csv('../KenPom Data/kenpom_tableau.csv')
        kenpom_teams = set(kenpom_df['team_name'].unique())
        
        # Check for any teams that still don't match
        unmatched = []
        for team in df['kenpom_team_name'].unique():
            if team not in kenpom_teams:
                unmatched.append(team)
        
        if unmatched:
            print(f"\n⚠️ Warning: {len(unmatched)} teams still don't match KenPom names:")
            for team in sorted(unmatched)[:20]:
                cbb_name = df[df['kenpom_team_name'] == team]['team_kenpom'].iloc[0]
                print(f"  CBB: '{cbb_name}' -> Mapped: '{team}' (NOT IN KENPOM)")
        else:
            print(f"\n✓ All {len(df['kenpom_team_name'].unique())} teams successfully mapped to KenPom names!")
    except Exception as e:
        print(f"\nCouldn't verify against KenPom data: {e}")
    
    # Save the updated file
    df.to_csv('cbb_analytics_tableau_cleaned.csv', index=False)
    print(f"\n✓ Saved updated file with {len(df.columns)} columns")
    print(f"  New column 'kenpom_team_name' added at position {df.columns.get_loc('kenpom_team_name') + 1}")


if __name__ == '__main__':
    add_kenpom_team_names()
