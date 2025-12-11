"""
Export KenPom data to CSV/Excel for Tableau import.
Creates a flattened, Tableau-friendly dataset.
"""
import pandas as pd
from database import KenPomDB
from datetime import datetime
import os


def export_to_csv(output_file='kenpom_tableau.csv', latest_only=True):
    """
    Export rankings data to CSV for Tableau.
    
    Args:
        output_file: Output CSV file path
        latest_only: If True, only export the most recent date's data (one row per team).
                     If False, export all historical data.
    """
    db = KenPomDB()
    conn = db._get_connection()
    
    try:
        if latest_only:
            # Export only the latest date's data (one row per team)
            query = """
                SELECT 
                    r.date,
                    t.team_name,
                    t.conference,
                    r.rank,
                    r.adj_em,
                    r.adj_o,
                    r.adj_d,
                    r.adj_tempo,
                    r.luck,
                    r.sos_adj_em,
                    r.opp_o,
                    r.opp_d,
                    r.ncsos_adj_em,
                    r.created_at
                FROM rankings r
                JOIN teams t ON r.team_id = t.id
                WHERE r.date = (SELECT MAX(date) FROM rankings)
                ORDER BY r.rank ASC
            """
        else:
            # Export all historical data
            query = """
                SELECT 
                    r.date,
                    t.team_name,
                    t.conference,
                    r.rank,
                    r.adj_em,
                    r.adj_o,
                    r.adj_d,
                    r.adj_tempo,
                    r.luck,
                    r.sos_adj_em,
                    r.opp_o,
                    r.opp_d,
                    r.ncsos_adj_em,
                    r.created_at
                FROM rankings r
                JOIN teams t ON r.team_id = t.id
                ORDER BY r.date DESC, r.rank ASC
            """
        
        # Read into pandas DataFrame
        df = pd.read_sql_query(query, conn)
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Add some calculated fields that might be useful in Tableau
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        
        # Export to CSV
        df.to_csv(output_file, index=False)
        
        if latest_only:
            print(f"[SUCCESS] Exported {len(df)} records (latest date only) to {output_file}")
            print(f"  Date: {df['date'].max()}")
            print(f"  Teams: {len(df)}")
        else:
            print(f"[SUCCESS] Exported {len(df)} records (all historical data) to {output_file}")
            print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"  Teams: {df['team_name'].nunique()}")
            print(f"  Unique dates: {df['date'].nunique()}")
        
        return output_file
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        raise
    finally:
        db.close()


def export_to_excel(output_file='kenpom_tableau.xlsx'):
    """Export data to Excel with multiple sheets for Tableau."""
    db = KenPomDB()
    conn = db._get_connection()
    
    try:
        # Main rankings data
        rankings_query = """
            SELECT 
                r.date,
                t.team_name,
                t.conference,
                r.rank,
                r.adj_em,
                r.adj_o,
                r.adj_d,
                r.adj_tempo,
                r.luck,
                r.sos_adj_em,
                r.opp_o,
                r.opp_d,
                r.ncsos_adj_em
            FROM rankings r
            JOIN teams t ON r.team_id = t.id
            ORDER BY r.date DESC, r.rank ASC
        """
        
        # Latest rankings only
        latest_query = """
            SELECT 
                t.team_name,
                t.conference,
                r.rank,
                r.adj_em,
                r.adj_o,
                r.adj_d,
                r.adj_tempo,
                r.luck,
                r.sos_adj_em,
                r.opp_o,
                r.opp_d,
                r.ncsos_adj_em,
                r.date
            FROM rankings r
            JOIN teams t ON r.team_id = t.id
            WHERE r.date = (SELECT MAX(date) FROM rankings)
            ORDER BY r.rank ASC
        """
        
        # Teams reference
        teams_query = """
            SELECT 
                id,
                team_name,
                conference,
                created_at
            FROM teams
            ORDER BY team_name
        """
        
        # Read queries into DataFrames
        df_latest = pd.read_sql_query(latest_query, conn)
        df_all = pd.read_sql_query(all_rankings_query, conn)
        df_teams = pd.read_sql_query(teams_query, conn)
        
        # Convert dates
        df_latest['date'] = pd.to_datetime(df_latest['date'])
        df_all['date'] = pd.to_datetime(df_all['date'])
        df_teams['created_at'] = pd.to_datetime(df_teams['created_at'])
        
        # Write to Excel with multiple sheets
        # Latest Rankings is the main sheet (for Tableau)
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_latest.to_excel(writer, sheet_name='Latest Rankings', index=False)
            df_all.to_excel(writer, sheet_name='All Rankings (Historical)', index=False)
            df_teams.to_excel(writer, sheet_name='Teams', index=False)
        
        print(f"[SUCCESS] Exported to {output_file}")
        print(f"  Sheet 'Latest Rankings' (for Tableau): {len(df_latest)} records (one per team)")
        print(f"  Sheet 'All Rankings (Historical)': {len(df_all)} records")
        print(f"  Sheet 'Teams': {len(df_teams)} teams")
        
        return output_file
        
    except ImportError:
        print("openpyxl not installed. Installing...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
        return export_to_excel(output_file)
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        raise
    finally:
        db.close()


def export_latest_only(output_file='kenpom_latest.csv'):
    """Export only the latest rankings (most recent date)."""
    # This function is now just a wrapper for export_to_csv with latest_only=True
    return export_to_csv(output_file, latest_only=True)


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("KenPom Data Export for Tableau")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        format_type = sys.argv[1].lower()
        
        if format_type == "excel":
            export_to_excel()
        elif format_type == "latest":
            export_latest_only()
        elif format_type == "csv":
            # Default: export latest only (one row per team)
            export_to_csv(latest_only=True)
        elif format_type == "all":
            # Export all historical data
            export_to_csv(latest_only=False)
        else:
            print(f"Unknown format: {format_type}")
            print("Usage: python export_to_tableau.py [csv|excel|latest|all]")
            print("  csv: Export latest date only (default, ~366 rows)")
            print("  all: Export all historical data")
            print("  excel: Export to Excel with multiple sheets")
            print("  latest: Same as csv (latest only)")
    else:
        # Default: export CSV (latest only) and Excel
        print("\nExporting to CSV (latest date only, ~366 rows)...")
        export_to_csv(latest_only=True)
        print("\nExporting to Excel...")
        try:
            export_to_excel()
        except Exception as e:
            print(f"Excel export failed: {e}")
            print("CSV export completed successfully.")

