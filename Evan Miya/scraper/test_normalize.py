#!/usr/bin/env python3
"""Test script to verify team name normalization"""
import re

TEAM_NAME_MAPPING = {
    "Iowa State": "Iowa St.",
    "Michigan State": "Michigan St.",
    "Connecticut": "Connecticut",
    "NC State": "N.C. State",
    "Ohio State": "Ohio St.",
    "Saint Mary's": "Saint Mary's",
    "Miami (Fla.)": "Miami FL",
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
}

def normalize_team_names(team_name: str) -> str:
    """Normalize team names to match KenPom format."""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    clean_name = emoji_pattern.sub('', team_name).strip()
    
    if clean_name in TEAM_NAME_MAPPING:
        return TEAM_NAME_MAPPING[clean_name]
    
    return clean_name

# Test cases
test_names = [
    'Duke 🔥',
    'Iowa State',
    'Michigan State',
    'Connecticut 🤕',
    'NC State',
    'Ohio State 🤕',
    'Ole Miss',
    'Saint Mary\'s🚰',
    'Miami (Fla.) 🔥🤕',
    'Michigan',
    'St. John\'s',
]

print('Team Name Normalization Test:')
print('-' * 70)
for name in test_names:
    normalized = normalize_team_names(name)
    print(f'{name:35} -> {normalized}')
