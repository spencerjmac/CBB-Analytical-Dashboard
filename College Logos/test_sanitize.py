import re

# Test the sanitization logic
test_names = [
    "air_force_falcons",
    "boston_university_terriers",
    "bethune-cookman_wildcats",
    "stanford_cardinal"
]

def sanitize_for_matching(name):
    """Sanitize team name for matching - removes mascot and special chars."""
    name = name.lower()
    # Remove common mascot-related words
    mascots = r'_(wildcats|eagles|bulldogs|tigers|crimson_tide|hornets|braves|mountaineers|sun_devils|golden_lions|razorbacks|red_wolves|black_knights|governors|cardinals|bears|knights|aggies|badgers|huskies|rams|trojans|bruins|golden_bears|cowboys|buffaloes|volunteers|gators|fighting_irish|spartans|buckeyes|longhorns|jayhawks|wolfpack|tar_heels|blue_devils|seminoles|hurricanes|hokies|cavaliers|cougars|panthers|pirates|rebels|terrapins|hoyas|retrievers|jaguars|gaels|explorers|peacocks|raiders|owls|griffins|seawolves|patriots|tribe|yellow_jackets|miners|roadrunners|highlanders|flames|bison|colonials|pioneers|privateers|racers|phoenix|huskies|river_hawks|redhawks|bobcats|golden_eagles|lumberjacks|ospreys|leopards|greyhounds|mean_green|hilltoppers|blackbirds|bonnies|purple_eagles|hawks|flyers|mountain_hawks|chanticleers|green_wave|friars|scarlet_knights|toreros|dons|broncos|zips|commodores|catamounts|thundering_herd|bearcats|runnin_rebels|cornhuskers|cyclones|nittany_lions|falcons).*$'
    name = re.sub(mascots, '', name)
    # Remove all non-alphanumeric
    name = re.sub(r'[^\w]', '', name)
    return name

for test in test_names:
    print(f"{test:40} -> {sanitize_for_matching(test)}")
