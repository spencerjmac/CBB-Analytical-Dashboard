from fix_csv_structure import clean_percentile_value

test_vals = {
    '462.9': 'Air Force PTS/G',
    '587.1': 'Alabama STL/G',  
    '677.4': 'A&M STL/G',
    '996.3': 'Alabama BLK/G',
    '9993.9': 'Alabama PTS/G',
    '292.8': 'Abilene BLK/G',
    '949.3': 'Abilene STL/G'
}

print("Testing clean_percentile_value function:")
for val, desc in test_vals.items():
    result = clean_percentile_value(val)
    print(f'{desc:25s} {val:10s} -> {result}')
