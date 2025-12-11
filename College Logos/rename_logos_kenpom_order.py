#!/usr/bin/env python3
"""
Rename NCAA logo files to match KenPom team names in alphabetical order.
This ensures Tableau's shape palette matches your data exactly.
"""
import pandas as pd
import shutil
from pathlib import Path
import re
from team_name_mapping import KENPOM_TO_ESPN

# Read the KenPom team names in the EXACT order from the CSV
sheet_path = r"c:\Users\spenc\Downloads\Sheet 16_Summary.csv"
df = pd.read_csv(sheet_path)
# Keep teams in the exact order they appear in the CSV file
kenpom_teams = [t for t in df['Team Name'].tolist() if pd.notna(t) and str(t).strip() and t != 'Team']
# Reverse if CSV is in Z-A order (check first team)
if kenpom_teams and kenpom_teams[0] > kenpom_teams[-1]:
    kenpom_teams = list(reversed(kenpom_teams))

print(f"Loaded {len(kenpom_teams)} team names from KenPom data")
print(f"First 10 teams: {kenpom_teams[:10]}")
print(f"Last 10 teams: {kenpom_teams[-10:]}")

# Path to logo files
logos_dir = Path(r"c:\Users\spenc\OneDrive\Workspace\Tableau Final Project\College Logos\output\logos")
output_dir = Path(r"c:\Users\spenc\OneDrive\Workspace\Tableau Final Project\College Logos\output\logos_kenpom_order")
output_dir.mkdir(exist_ok=True)

# Get all existing logo files
existing_logos = list(logos_dir.glob("*.png")) + list(logos_dir.glob("*.svg")) + list(logos_dir.glob("*.jpg"))
print(f"\nFound {len(existing_logos)} existing logo files")

# Create a mapping function to match KenPom names to logo files
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
        'runnin_bulldogs', 'revolutionaries', 'golden_flashes', 'crimson',
        'rainbow_warriors', 'pride', 'crusaders', 'vandals', 'fighting_illini', 'redbirds',
        'hoosiers', 'sycamores', 'hawkeyes', 'dolphins', 'roos', 'lobos', 'waves',
        'sooners', 'ducks', 'beavers', 'quakers', 'boilermakers', 'mastodons', 'royals',
        'spiders', 'broncs', 'billikens', 'bearkats', 'aztecs', 'musketeers', 'penguins',
        'great_danes', 'anteaters', 'gauchos', 'tritons', 'warhawks', 'seahawks', 'keydets',
        'demon_deacons', 'shockers', 'leathernecks', 'wolves', 'skyhawks', 'beacons',
        'trailblazers', 'utes', 'wolverines', 'vaqueros', 'cardinal', 'orange', 'beach',
        'sharks', 'ragin_cajuns', 'ramblers', 'minutemen', 'black_bears', 'jaspers',
        'red_foxes', 'lakers', 'warriors', 'delta_devils', 'grizzlies', 'midshipmen',
        'wolf_pack', 'chargers', 'lopes', 'fighting_hawks', 'tommies',
        'texans', 'horned_frogs', 'golden_hurricane', 'islanders', 'red_raiders', 'rockets',
        'blazers', 'salukis', 'screaming_eagles', 'thunderbirds', 'hatters', 'red_storm',
        'colonels', 'demons', 'lions', 'bengals', 'blue_raiders', 'red_flash', 'pilots',
        'vikings', 'blue_hose', 'mavericks', 'monarchs', 'saints', 'bulls',
        'lancers', 'norse', 'bisons'
    ]
    
    # Sort by length (longest first) to match more specific mascots first
    mascots.sort(key=len, reverse=True)
    
    for mascot in mascots:
        if filename.endswith('_' + mascot):
            return filename[:-len(mascot)-1]
    
    return filename

def sanitize_for_matching(name):
    """Sanitize team name for matching - removes mascot, hyphens, and special chars."""
    name = name.lower()
    name = strip_mascot(name)
    # Remove hyphens and convert to underscores
    name = name.replace('-', '_')
    # Remove all non-alphanumeric except underscores
    name = re.sub(r'[^\w]', '', name)
    return name

# Create lookup dictionary for existing logos
logo_lookup = {}
for logo_file in existing_logos:
    clean_name = sanitize_for_matching(logo_file.stem)
    logo_lookup[clean_name] = logo_file

print(f"\nSample sanitized logo names:")
for i, (key, val) in enumerate(list(logo_lookup.items())[:10]):
    print(f"  {key:30} <- {val.name}")

# Match and rename logos
matched = 0
missing = []

for idx, team_name in enumerate(kenpom_teams, 1):
    if not team_name or team_name == "Team":
        continue
    
    # Try the manual mapping first
    found = False
    if team_name in KENPOM_TO_ESPN:
        espn_name = KENPOM_TO_ESPN[team_name]
        clean_espn = sanitize_for_matching(espn_name)
        
        if clean_espn in logo_lookup:
            source_logo = logo_lookup[clean_espn]
            ext = source_logo.suffix
            
            # New filename: sequential number + team name for proper sorting
            safe_name = team_name.replace('/', '-').replace('.', '').replace('&', 'and')
            new_filename = f"{idx:03d}_{safe_name}{ext}"
            dest_path = output_dir / new_filename
            
            # Copy file
            shutil.copy2(source_logo, dest_path)
            matched += 1
            found = True
            print(f"[OK] {idx:03d}. {team_name} -> {new_filename}")
    
    if not found:
        # Try direct sanitization matching
        clean_kenpom = sanitize_for_matching(team_name)
        if clean_kenpom in logo_lookup:
            source_logo = logo_lookup[clean_kenpom]
            ext = source_logo.suffix
            
            safe_name = team_name.replace('/', '-').replace('.', '').replace('&', 'and')
            new_filename = f"{idx:03d}_{safe_name}{ext}"
            dest_path = output_dir / new_filename
            
            shutil.copy2(source_logo, dest_path)
            matched += 1
            found = True
            print(f"[OK] {idx:03d}. {team_name} -> {new_filename} (direct match)")
        else:
            missing.append((team_name, f"Tried: '{clean_kenpom}'"))
            print(f"[MISS] {idx:03d}. {team_name} - NOT FOUND (tried '{clean_kenpom}')")

print(f"\n{'='*60}")
print(f"Summary:")
print(f"  Matched: {matched}/{len(kenpom_teams)}")
print(f"  Missing: {len(missing)}")
print(f"{'='*60}")

if missing:
    print(f"\nMissing logos:")
    for team, reason in missing:
        print(f"  - {team}: {reason}")
    
    # Save missing list
    missing_file = output_dir.parent / "missing_logos_kenpom.txt"
    with open(missing_file, 'w') as f:
        for team, reason in missing:
            f.write(f"{team}: {reason}\n")
    print(f"\nMissing logos list saved to: {missing_file}")

print(f"\nRenamed logos saved to:")
print(f"  {output_dir}")
print(f"\nNext steps:")
print(f"1. Zip the contents of logos_kenpom_order folder")
print(f"2. Extract to: My Tableau Repository/Shapes/NCAA_Basketball/")
print(f"3. Restart Tableau")
print(f"4. The shapes will now be in the exact order of your data!")
