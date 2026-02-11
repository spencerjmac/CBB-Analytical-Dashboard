"""
Django management command to ingest data from CSV files into the database

Usage:
    python manage.py ingest_data --season 2026
"""

import os
import pandas as pd
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from core.models import Season, Conference, Team, TeamSeasonStats, DataIngestionRun


class Command(BaseCommand):
    help = 'Ingest CBB data from CSV files into the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--season',
            type=int,
            required=True,
            help='Season year (e.g., 2026 for 2025-26 season)'
        )
        parser.add_argument(
            '--kenpom',
            type=str,
            help='Path to KenPom CSV file'
        )
        parser.add_argument(
            '--torvik',
            type=str,
            help='Path to Torvik CSV file'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-import even if data exists'
        )
    
    def handle(self, *args, **options):
        season_year = options['season']
        force = options.get('force', False)
        
        self.stdout.write(f"\n🏀 CBB Analytics Data Ingestion")
        self.stdout.write(f"{'=' * 50}\n")
        
        # Create or get season
        season, created = Season.objects.get_or_create(
            year=season_year,
            defaults={
                'display_name': f'{season_year-1}-{str(season_year)[-2:]}',
                'is_current': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created season: {season.display_name}'))
        else:
            self.stdout.write(f'Season: {season.display_name}')
        
        # Create ingestion run
        ingestion_run = DataIngestionRun.objects.create(
            season=season,
            status='running'
        )
        
        try:
            # Determine CSV paths
            base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
            
            kenpom_path = options.get('kenpom') or base_dir / 'KenPom Data' / 'kenpom_tableau.csv'
            torvik_path = options.get('torvik') or base_dir / 'Bart Torvik' / 'torvik_tableau.csv'
            
            self.stdout.write(f'\n📂 Loading CSVs...')
            self.stdout.write(f'  KenPom: {kenpom_path}')
            self.stdout.write(f'  Torvik: {torvik_path}')
            
            # Load CSVs
            df_kenpom = pd.read_csv(kenpom_path) if os.path.exists(kenpom_path) else None
            df_torvik = pd.read_csv(torvik_path) if os.path.exists(torvik_path) else None
            
            if df_kenpom is None and df_torvik is None:
                raise Exception('No CSV files found!')
            
            self.stdout.write(self.style.SUCCESS(f'✓ Loaded CSVs'))
            if df_kenpom is not None:
                self.stdout.write(f'  KenPom: {len(df_kenpom)} teams')
            if df_torvik is not None:
                self.stdout.write(f'  Torvik: {len(df_torvik)} teams')
            
            # Start ingestion
            teams_processed = self._ingest_data(season, df_kenpom, df_torvik, force)
            
            # Mark as success
            ingestion_run.status = 'success'
            ingestion_run.teams_ingested = teams_processed
            ingestion_run.completed_at = timezone.now()
            ingestion_run.save()
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Ingestion complete!'))
            self.stdout.write(f'   Teams processed: {teams_processed}')
            
        except Exception as e:
            ingestion_run.status = 'error'
            ingestion_run.error_log = str(e)
            ingestion_run.completed_at = timezone.now()
            ingestion_run.save()
            
            self.stdout.write(self.style.ERROR(f'\n❌ Error: {str(e)}'))
            raise
    
    @transaction.atomic
    def _ingest_data(self, season, df_kenpom, df_torvik, force):
        """Main ingestion logic"""
        
        # Team name normalization map (simplified - expand as needed)
        team_name_map = {
            'Michigan St.': 'Michigan State',
            'Miami FL': 'Miami (FL)',
            'Miami OH': 'Miami (OH)',
            'St. John\'s': 'St. John\'s',
            'Saint Louis': 'Saint Louis',
            'Saint Mary\'s': 'Saint Mary\'s',
            'N.C. State': 'NC State',
            'McNeese St.': 'McNeese',
            'Stephen F. Austin': 'Stephen F. Austin',
        }
        
        def normalize_name(name):
            return team_name_map.get(name, name)
        
        teams_processed = 0
        
        # Primary source is KenPom
        if df_kenpom is not None:
            for idx, row in df_kenpom.iterrows():
                team_name = normalize_name(row['team_name'])
                
                # Create or get team
                team, _ = Team.objects.get_or_create(
                    name=team_name,
                    defaults={'slug': team_name.lower().replace(' ', '-').replace('.', '')}
                )
                
                # Create or get conference
                conf_code = row.get('conference', 'IND')
                conference, _ = Conference.objects.get_or_create(
                    code=conf_code,
                    defaults={'name': conf_code}
                )
                
                # Parse record (e.g., "22-1")
                record_str = row.get('record', '0-0')
                wins, losses = 0, 0
                if isinstance(record_str, str) and '-' in record_str:
                    parts = record_str.split('-')
                    wins = int(parts[0])
                    losses = int(parts[1])
                
                # Find matching Torvik data
                torvik_row = None
                if df_torvik is not None:
                    torvik_match = df_torvik[
                        df_torvik['team_name'].apply(normalize_name) == team_name
                    ]
                    if not torvik_match.empty:
                        torvik_row = torvik_match.iloc[0]
                
                # Create or update stats
                stats, created = TeamSeasonStats.objects.update_or_create(
                    team=team,
                    season=season,
                    defaults={
                        'conference': conference,
                        'games': wins + losses,
                        'wins': wins,
                        'losses': losses,
                        'rank': int(row.get('rank', 0)) if pd.notna(row.get('rank')) else None,
                        
                        # KenPom metrics
                        'adj_em': float(row.get('adj_em', 0)),
                        'adj_o': float(row.get('adj_o', 100)),
                        'adj_d': float(row.get('adj_d', 100)),
                        'adj_tempo': float(row.get('adj_tempo', 68)),
                        'luck': float(row.get('luck', 0)) if pd.notna(row.get('luck')) else None,
                        'sos_adj_em': float(row.get('sos_adj_em', 0)) if pd.notna(row.get('sos_adj_em')) else None,
                        'ncsos_adj_em': float(row.get('ncsos_adj_em', 0)) if pd.notna(row.get('ncsos_adj_em')) else None,
                        
                        # Torvik metrics (if available)
                        'efg_pct': float(torvik_row.get('efg_pct', 50)) if torvik_row is not None else 50.0,
                        'tov_pct': float(torvik_row.get('tor', 15)) if torvik_row is not None else 15.0,
                        'orb_pct': float(torvik_row.get('orb', 30)) if torvik_row is not None else 30.0,
                        'ftr': float(torvik_row.get('ftr', 30)) if torvik_row is not None else 30.0,
                        
                        'efg_pct_d': float(torvik_row.get('efg_pct_d', 50)) if torvik_row is not None else 50.0,
                        'tov_pct_d': float(torvik_row.get('tord', 15)) if torvik_row is not None else 15.0,
                        'drb_pct': float(torvik_row.get('drb', 70)) if torvik_row is not None else 70.0,
                        'ftr_d': float(torvik_row.get('ftrd', 30)) if torvik_row is not None else 30.0,
                        
                        'fg2_pct': float(torvik_row.get('two_p_pct', 50)) if torvik_row is not None and pd.notna(torvik_row.get('two_p_pct')) else None,
                        'fg2_pct_d': float(torvik_row.get('two_p_pct_d', 50)) if torvik_row is not None and pd.notna(torvik_row.get('two_p_pct_d')) else None,
                        'fg3_pct': float(torvik_row.get('three_p_pct', 33)) if torvik_row is not None and pd.notna(torvik_row.get('three_p_pct')) else None,
                        'fg3_pct_d': float(torvik_row.get('three_p_pct_d', 33)) if torvik_row is not None and pd.notna(torvik_row.get('three_p_pct_d')) else None,
                        'fg3_rate': float(torvik_row.get('three_pr', 35)) if torvik_row is not None and pd.notna(torvik_row.get('three_pr')) else None,
                        'fg3_rate_d': float(torvik_row.get('three_prd', 35)) if torvik_row is not None and pd.notna(torvik_row.get('three_prd')) else None,
                        
                        'wab': float(torvik_row.get('wab', 0)) if torvik_row is not None and pd.notna(torvik_row.get('wab')) else None,
                        'barthag': float(torvik_row.get('barthag', 0.5)) if torvik_row is not None and pd.notna(torvik_row.get('barthag')) else None,
                        
                        # Data provenance
                        'has_kenpom': True,
                        'has_torvik': torvik_row is not None,
                        'has_cbb_analytics': False,
                    }
                )
                
                teams_processed += 1
                
                if teams_processed % 50 == 0:
                    self.stdout.write(f'  Processed {teams_processed} teams...')
        
        return teams_processed
