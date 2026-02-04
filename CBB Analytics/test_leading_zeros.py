from scrape_cbb_analytics_clean import clean_percentile_value

test_cases = [
    ('0130.4', '130.4', 'Leading 0 with DRtg'),
    ('093.6', '93.6', 'Leading 0 with ORtg'),  
    ('1130.4', '130.4', 'Percentile 1 + DRtg'),
    ('30130.4', '130.4', 'Percentile 30 + DRtg'),
    ('130.4', '130.4', 'Already clean DRtg'),
    ('93.6', '93.6', 'Already clean ORtg'),
    ('30.4', '30.4', 'Already clean small value'),
    ('1993.6', '93.6', 'Percentile 19 + ORtg'),
]

print("Testing clean_percentile_value:")
print("="*70)

for input_val, expected, description in test_cases:
    result = clean_percentile_value(input_val)
    passed = (result == expected)
    status = "✓" if passed else "✗"
    print(f"{status} {description:30s} {input_val:10s} -> {result:10s} (expected {expected})")

print("="*70)
