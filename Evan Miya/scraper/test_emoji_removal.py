import re

def normalize_team_names(team_name: str) -> str:
    """Test function"""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    clean_name = emoji_pattern.sub('', team_name).strip()
    return clean_name

test_names = [
    'Duke 🔥',
    'Kentucky 🤕',
    'Connecticut 🤕',
    'Ohio State 🤕',
]

for name in test_names:
    result = normalize_team_names(name)
    print(f"{name:25} -> {result}")
