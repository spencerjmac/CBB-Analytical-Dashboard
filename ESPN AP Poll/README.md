# ESPN AP Poll Week 6 Scraper

Scraper for ESPN's AP Top 25 Poll - Men's College Basketball (Week 6, December 2025)

## Files

- **scrape_ap_poll.py**: Playwright-based scraper for ESPN AP Poll
- **ap_poll_week6.csv**: AP Poll Week 6 data with KenPom-formatted team names

## Features

- Scrapes Top 25 teams from ESPN AP Poll
- **Team name normalization** to match KenPom format
  - `UConn` → `Connecticut`
  - `Michigan State` → `Michigan St.`
  - All other teams match KenPom exactly
- Includes rank, record, points, previous rank

## Usage

```powershell
python scrape_ap_poll.py
```

This will create `ap_poll_week6.csv` with the following structure:

## Data Dictionary

| Column | Description |
|--------|-------------|
| `rank` | AP Poll rank (1-25) |
| `team_espn` | Original ESPN team name |
| `team_kenpom` | Team name normalized to match KenPom format |
| `record` | Win-loss record |
| `points` | Total poll points |
| `previous_rank` | Previous week's rank (or "-" for new) |
| `poll` | Poll name ("AP") |
| `week` | Week number (6) |
| `date` | Scrape date (2025-12-08) |

## AP Poll Week 6 Results

1. Arizona (8-0) - 1461 pts
2. Michigan (8-0) - 1440 pts
3. Duke (10-0) - 1400 pts
4. Iowa State (9-0) - 1304 pts
5. Connecticut (8-1) - 1263 pts
6. Purdue (8-1) - 1173 pts
7. Houston (8-1) - 1064 pts
8. Gonzaga (9-1) - 1054 pts
9. Michigan St. (8-1) - 1017 pts
10. BYU (7-1) - 1007 pts

...and 15 more teams through #25 UCLA

## Team Name Compatibility

All team names in the `team_kenpom` column match the exact naming used in:
- `KenPom Data/kenpom_tableau.csv`
- `Evan Miya/scraper/team_ratings.csv`
- `Bart Torvik/torvik_tableau.csv`

This allows for seamless joins in Tableau!

## Requirements

- Python 3.10+
- playwright
- beautifulsoup4
- pandas

## Notes

- This is a one-time scrape for Week 6 only
- Does not require updates or scheduling
- Ready for Tableau import
