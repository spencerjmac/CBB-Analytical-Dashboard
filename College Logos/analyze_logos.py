"""
Generate improved KenPom to ESPN logo filename mapping by examining actual files.
"""
import re
from pathlib import Path
import pandas as pd

# Get all logo files
logos_dir = Path(r"c:\Users\spenc\OneDrive\Workspace\Tableau Final Project\College Logos\output\logos")
existing_logos = list(logos_dir.glob("*.png"))

# Read KenPom teams
sheet_path = r"c:\Users\spenc\Downloads\Sheet 16_Summary.csv"
df = pd.read_csv(sheet_path)
kenpom_teams = sorted([t for t in df['Team Name'].tolist() if pd.notna(t) and t != 'Team'])

# Build a comprehensive list of all the mascots found in filenames
all_mascots = set()
for logo_file in existing_logos:
    parts = logo_file.stem.split('_')
    if len(parts) > 1:
        # Last part is likely mascot
        last_parts = '_'.join(parts[-2:]) if len(parts) > 2 else parts[-1]
        all_mascots.add(last_parts)

print("Top 50 unique mascot patterns found:")
for i, mascot in enumerate(sorted(all_mascots)[:50]):
    print(f"  {mascot}")

# Create a simple mapping by removing mascots
def strip_mascot(filename):
    """Remove mascot from end of filename."""
    # Comprehensive mascot list (all found patterns)
    mascots = [
        'wildcats', 'eagles', 'bulldogs', 'tigers', 'hornets', 'braves', 'mountaineers',
        'sun_devils', 'golden_lions', 'razorbacks', 'red_wolves', 'black_knights',
        'governors', 'cardinals', 'bears', 'knights', 'aggies', 'badgers', 'huskies',
        'rams', 'trojans', 'bruins', 'golden_bears', 'cowboys', 'buffaloes', 'volunteers',
        'gators', 'fighting_irish', 'spartans', 'buckeyes', 'longhorns', 'jayhawks',
        'wolfpack', 'tar_heels', 'blue_devils', 'seminoles', 'hurricanes', 'hokies',
        'cavaliers', 'cougars', 'panthers', 'pirates', 'rebels', 'terrapins', 'hoyas',
        'retrievers', 'jaguars', 'gaels', 'explorers', 'peacocks', 'raiders', 'owls',
        'griffins', 'seawolves', 'patriots', 'tribe', 'yellow_jackets', 'miners',
        'roadrunners', 'highlanders', 'flames', 'bison', 'colonials', 'pioneers',
        'privateers', 'racers', 'phoenix', 'river_hawks', 'redhawks', 'bobcats',
        'golden_eagles', 'lumberjacks', 'ospreys', 'leopards', 'greyhounds', 'mean_green',
        'hilltoppers', 'blackbirds', 'bonnies', 'purple_eagles', 'hawks', 'flyers',
        'mountain_hawks', 'chanticleers', 'green_wave', 'friars', 'scarlet_knights',
        'toreros', 'dons', 'broncos', 'zips', 'commodores', 'catamounts', 'thundering_herd',
        'bearcats', 'runnin_rebels', 'cornhuskers', 'cyclones', 'nittany_lions', 'falcons',
        'crimson_tide', 'golden_gophers', 'terriers', 'lancers', 'mustangs', 'titans',
        'matadors', 'fighting_camels', 'golden_griffins', 'chippewas', 'buccaneers', 
        '49ers', 'mocs', 'big_red', 'bluejays', 'big_green', 'blue_hens', 'blue_demons',
        'dragons', 'dukes', 'purple_aces', 'stags', 'rattlers', 'gamecocks', 'paladins',
        'runnin_bulldogs', 'patriots', 'revolutionaries', 'golden_flashes', 'crimson',
        'rainbow_warriors', 'pride', 'crusaders', 'vandals', 'fighting_illini', 'redbirds',
        'hoosiers', 'sycamores', 'hawkeyes', 'dolphins', 'roos', 'lobos', 'waves',
        'sooners', 'ducks', 'beavers', 'quakers', 'boilermakers', 'mastodons', 'royals',
        'spiders', 'broncs', 'billikens', 'bearkats', 'aztecs', 'musketeers', 'penguins',
        'great_danes', 'anteaters', 'gauchos', 'tritons', 'warhawks', 'seahawks', 'keydets',
        'demon_deacons', 'shockers', 'leathernecks', 'wolves', 'skyhawks', 'beacons',
        'trailblazers', 'utes', 'wolverines', 'vaqueros', 'cardinal', 'orange', 'beach',
        'sharks', 'ragin_cajuns', 'ramblers', 'minutemen', 'black_bears', 'jaspers',
        'red_foxes', 'lakers', 'warriors', 'delta_devils', 'grizzlies', 'midshipmen',
        'wolf_pack', 'chargers', 'purple_eagles', 'lopes', 'fighting_hawks', 'tommies',
        'texans', 'horned_frogs', 'golden_hurricane', 'islanders', 'red_raiders', 'rockets',
        'blazers', 'salukis', 'screaming_eagles', 'thunderbirds', 'hatters', 'red_storm',
        'colonels', 'demons', 'lions', 'bengals', 'blue_raiders', 'red_flash', 'pilots',
        'vikings', 'blue_hose', 'mavericks', 'monarchs', 'saints', 'bulls', 'redhawks',
        'lancers', 'norse'
    ]
    
    # Sort by length (longest first) to match more specific mascots first
    mascots.sort(key=len, reverse=True)
    
    for mascot in mascots:
        if filename.endswith('_' + mascot):
            return filename[:-len(mascot)-1]
    
    return filename

# Test on some examples
print("\n\nTest mappings:")
test_cases = [
    "air_force_falcons",
    "boston_university_terriers",
    "stanford_cardinal",
    "illinois_fighting_illini",
]

for test in test_cases:
    stripped = strip_mascot(test)
    print(f"{test:40} -> {stripped}")
