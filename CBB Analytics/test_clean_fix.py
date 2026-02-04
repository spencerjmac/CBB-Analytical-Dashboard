"""Test the fix for the clean_percentile_value function."""

# Import the cleaning function from the scraper
import sys
sys.path.insert(0, '.')
from scrape_cbb_analytics_clean import clean_percentile_value

# Test cases
test_values = [
    ("130.4", "130.4"),  # Already clean DRtg - should NOT be modified
    ("1130.4", "130.4"),  # Percentile 1 + actual 130.4
    ("30130.4", "130.4"),  # Percentile 30 + actual 130.4
    ("93.6", "93.6"),  # Already clean ORtg
    ("1993.6", "93.6"),  # Percentile 19 + actual 93.6
    ("2347.9%", "47.9%"),  # Percentage with percentile
    ("66.1%", "66.1%"),  # Already clean percentage
    ("75.2", "75.2"),  # Already clean (PTS/G range)
    ("2075.2", "75.2"),  # Percentile 20 + actual 75.2
]

print("Testing clean_percentile_value fix:")
print("="*70)

all_passed = True
for input_val, expected in test_values:
    result = clean_percentile_value(input_val)
    passed = (result == expected)
    all_passed = all_passed and passed
    
    status = "✓" if passed else "✗"
    print(f"{status} Input: {input_val:15s} → Expected: {expected:10s} → Got: {result:10s}")

print("="*70)
if all_passed:
    print("✓ All tests passed!")
else:
    print("✗ Some tests failed!")
