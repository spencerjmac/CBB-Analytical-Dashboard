"""
DRF Serializers for CBB Analytics API
"""

from rest_framework import serializers
from core.models import Season, Conference, Team, TeamSeasonStats


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id', 'year', 'display_name', 'is_current']


class ConferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conference
        fields = ['id', 'code', 'name']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'slug', 'name', 'aliases', 'logo_url']


class TeamSeasonStatsSerializer(serializers.ModelSerializer):
    """Full stats for a team in a season"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    team_slug = serializers.CharField(source='team.slug', read_only=True)
    team_logo = serializers.CharField(source='team.logo_url', read_only=True)
    conference_code = serializers.CharField(source='conference.code', read_only=True)
    conference_name = serializers.CharField(source='conference.name', read_only=True)
    season_year = serializers.IntegerField(source='season.year', read_only=True)
    record = serializers.CharField(read_only=True)
    
    class Meta:
        model = TeamSeasonStats
        fields = [
            # Identifiers
            'id', 'team_name', 'team_slug', 'team_logo', 
            'conference_code', 'conference_name', 'season_year',
            
            # Record
            'games', 'wins', 'losses', 'record',
            
            # Rankings
            'rank', 'rank_adj_em', 'rank_adj_o', 'rank_adj_d',
            
            # Core Metrics
            'adj_em', 'adj_o', 'adj_d', 'adj_tempo',
            
            # Four Factors - Offense
            'efg_pct', 'tov_pct', 'orb_pct', 'ftr',
            
            # Four Factors - Defense
            'efg_pct_d', 'tov_pct_d', 'drb_pct', 'ftr_d',
            
            # Margins
            'efg_margin', 'tov_edge', 'reb_edge', 'ftr_margin',
            
            # Shooting Splits
            'fg2_pct', 'fg2_pct_d', 'fg3_pct', 'fg3_pct_d', 
            'fg3_rate', 'fg3_rate_d',
            
            # Resume
            'wab', 'sor', 'barthag', 'luck', 'sos_adj_em', 'ncsos_adj_em',
            
            # Provenance
            'has_kenpom', 'has_torvik', 'has_cbb_analytics',
            'last_updated',
        ]


class RankingsSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for rankings table
    Only includes fields needed for the sortable/filterable table
    """
    team_name = serializers.CharField(source='team.name', read_only=True)
    team_slug = serializers.CharField(source='team.slug', read_only=True)
    team_logo = serializers.CharField(source='team.logo_url', read_only=True)
    conference = serializers.CharField(source='conference.code', read_only=True)
    record = serializers.CharField(read_only=True)
    
    class Meta:
        model = TeamSeasonStats
        fields = [
            'rank', 'team_name', 'team_slug', 'team_logo', 'conference', 
            'record', 'adj_em', 'adj_o', 'adj_d', 'adj_tempo',
            'efg_pct', 'tov_pct', 'orb_pct', 'ftr',
            'efg_pct_d', 'tov_pct_d', 'drb_pct', 'ftr_d',
        ]


class TeamDetailSerializer(serializers.Serializer):
    """
    Combined serializer for team detail page
    Includes team info + stats across all available seasons
    """
    team = TeamSerializer()
    seasons = TeamSeasonStatsSerializer(many=True)
    current_season_stats = TeamSeasonStatsSerializer()
