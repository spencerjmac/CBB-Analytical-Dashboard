"""
Main script to scrape KenPom data and store in SQLite database.
Can be run manually or scheduled for daily execution.
"""
import sys
from datetime import datetime
from scraper_playwright import KenPomScraperPlaywright
from database import KenPomDB


def format_value(value, default='N/A'):
    """Format a value for display, handling None."""
    if value is None:
        return default
    return value


def scrape_and_store():
    """Main function to scrape KenPom data and store in database."""
    print("=" * 60)
    print(f"KenPom Data Scraper - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Initialize components
    scraper = KenPomScraperPlaywright()
    db = KenPomDB()
    
    try:
        # Scrape rankings
        print("\n[1/3] Scraping KenPom rankings...")
        rankings_data = scraper.scrape_rankings()
        
        if not rankings_data:
            print("ERROR: No data scraped. Exiting.")
            return False
        
        print(f"Found {len(rankings_data)} teams")
        
        # Store data in database
        print("\n[2/3] Storing data in database...")
        today = datetime.now().strftime('%Y-%m-%d')
        
        stored_count = 0
        for team_data in rankings_data:
            try:
                # Insert or get team
                team_id = db.insert_team(
                    team_name=team_data.get('team_name'),
                    conference=team_data.get('conference')
                )
                
                if not team_id:
                    print(f"Warning: Could not get team_id for {team_data.get('team_name')}")
                    continue
                
                # Prepare ranking data
                ranking_data = {
                    'rank': team_data.get('rank'),
                    'adj_em': team_data.get('adj_em'),
                    'adj_o': team_data.get('adj_o'),
                    'adj_d': team_data.get('adj_d'),
                    'adj_tempo': team_data.get('adj_tempo'),
                    'luck': team_data.get('luck'),
                    'sos_adj_em': team_data.get('sos_adj_em'),
                    'opp_o': team_data.get('opp_o'),
                    'opp_d': team_data.get('opp_d'),
                    'ncsos_adj_em': team_data.get('ncsos_adj_em')
                }
                
                # Insert ranking
                db.insert_ranking(team_id, today, ranking_data)
                stored_count += 1
                
            except Exception as e:
                print(f"Error storing data for {team_data.get('team_name', 'unknown')}: {e}")
                continue
        
        print(f"Successfully stored {stored_count} team rankings")
        
        # Display summary
        print("\n[3/3] Summary:")
        latest = db.get_latest_rankings(limit=10)
        if latest:
            print(f"\nTop 10 Teams (as of {today}):")
            print("-" * 80)
            print(f"{'Rank':<6} {'Team':<30} {'AdjEM':<10} {'AdjO':<10} {'AdjD':<10}")
            print("-" * 80)
            for team in latest[:10]:
                rank = format_value(team.get('rank'))
                team_name = format_value(team.get('team_name'))
                adj_em = format_value(team.get('adj_em'))
                adj_o = format_value(team.get('adj_o'))
                adj_d = format_value(team.get('adj_d'))
                print(f"{rank!s:<6} "
                      f"{team_name!s:<30} "
                      f"{adj_em!s:<10} "
                      f"{adj_o!s:<10} "
                      f"{adj_d!s:<10}")
        
        print("\n" + "=" * 60)
        print("Scraping completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


def view_data():
    """View stored data from database."""
    db = KenPomDB()
    
    try:
        print("\nLatest KenPom Rankings:")
        print("=" * 100)
        
        rankings = db.get_latest_rankings(limit=50)
        
        if not rankings:
            print("No data found in database.")
            return
        
        print(f"\n{'Rank':<6} {'Team':<35} {'Conf':<12} {'AdjEM':<10} {'AdjO':<10} {'AdjD':<10} {'AdjT':<10} {'Date':<12}")
        print("-" * 100)
        
        for team in rankings:
            rank = format_value(team.get('rank'))
            team_name = format_value(team.get('team_name'))
            conference = format_value(team.get('conference'))
            adj_em = format_value(team.get('adj_em'))
            adj_o = format_value(team.get('adj_o'))
            adj_d = format_value(team.get('adj_d'))
            adj_tempo = format_value(team.get('adj_tempo'))
            date = format_value(team.get('date'))
            print(f"{rank!s:<6} "
                  f"{team_name!s:<35} "
                  f"{conference!s:<12} "
                  f"{adj_em!s:<10} "
                  f"{adj_o!s:<10} "
                  f"{adj_d!s:<10} "
                  f"{adj_tempo!s:<10} "
                  f"{date!s:<12}")
        
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "view":
        view_data()
    else:
        scrape_and_store()

