#!/usr/bin/env python3
"""
Verify that team names match between KenPom and Evan Miya datasets.
Run this after scraping both sources to check alignment.
"""
import pandas as pd
import sys
from pathlib import Path

# File paths
KENPOM_CSV = Path(__file__).parent.parent.parent / "KenPom Data" / "kenpom_tableau.csv"
EVAN_MIYA_CSV = Path(__file__).parent / "team_ratings.csv"

def verify_team_names():
    """Compare team names between KenPom and Evan Miya datasets."""
    
    # Check if files exist
    if not KENPOM_CSV.exists():
        print(f"❌ KenPom CSV not found: {KENPOM_CSV}")
        return False
    
    if not EVAN_MIYA_CSV.exists():
        print(f"❌ Evan Miya CSV not found: {EVAN_MIYA_CSV}")
        return False
    
    # Load data
    print("📊 Loading datasets...")
    kenpom_df = pd.read_csv(KENPOM_CSV)
    evan_miya_df = pd.read_csv(EVAN_MIYA_CSV)
    
    # Get unique team names
    kenpom_teams = set(kenpom_df['team_name'].dropna().unique())
    evan_miya_teams = set(evan_miya_df['Team'].dropna().unique())
    
    # Remove header rows if present
    kenpom_teams.discard('Team')
    evan_miya_teams.discard('Team')
    
    print(f"\n📈 KenPom teams: {len(kenpom_teams)}")
    print(f"📈 Evan Miya teams: {len(evan_miya_teams)}")
    
    # Find teams in both datasets
    common_teams = kenpom_teams & evan_miya_teams
    print(f"✅ Teams in both datasets: {len(common_teams)}")
    
    # Find mismatches
    kenpom_only = kenpom_teams - evan_miya_teams
    evan_miya_only = evan_miya_teams - kenpom_teams
    
    print(f"\n{'='*70}")
    if kenpom_only or evan_miya_only:
        print("⚠️  MISMATCHES FOUND")
        print(f"{'='*70}")
        
        if kenpom_only:
            print(f"\n🔴 Teams only in KenPom ({len(kenpom_only)}):")
            for team in sorted(kenpom_only):
                print(f"  - {team}")
        
        if evan_miya_only:
            print(f"\n🔵 Teams only in Evan Miya ({len(evan_miya_only)}):")
            for team in sorted(evan_miya_only):
                print(f"  - {team}")
        
        # Try to find potential matches
        print(f"\n💡 Potential matches (similar names):")
        for em_team in sorted(evan_miya_only):
            for kp_team in sorted(kenpom_only):
                # Simple similarity check
                em_clean = em_team.lower().replace('.', '').replace(' ', '')
                kp_clean = kp_team.lower().replace('.', '').replace(' ', '')
                if em_clean in kp_clean or kp_clean in em_clean:
                    print(f"  '{em_team}' (EM) ≈ '{kp_team}' (KP)")
        
        return False
    else:
        print("✅ ALL TEAM NAMES MATCH!")
        print(f"{'='*70}")
        print(f"\n🎉 Success! All {len(common_teams)} teams have matching names.")
        print("You can now safely join the datasets in Tableau using team names.")
        return True

def main():
    print("=" * 70)
    print("Team Name Verification Tool")
    print("Checking alignment between KenPom and Evan Miya datasets")
    print("=" * 70)
    
    try:
        success = verify_team_names()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()
