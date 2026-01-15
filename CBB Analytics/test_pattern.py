import re

test_vals = ['587.1', '677.4', '949.3', '406.3', '062.9', '9993.9']
pattern = r'^(\d{2})(\d{1}\.\d+)$'

print("Testing pattern for small stats (STL/G, BLK/G):")
for val in test_vals:
    match = re.match(pattern, val)
    if match:
        print(f'{val} -> {match.group(2)} (percentile: {match.group(1)})')
    else:
        print(f'{val} -> NO MATCH')
