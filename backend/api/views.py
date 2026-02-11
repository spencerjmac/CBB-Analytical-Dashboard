"""
DRF Views for CBB Analytics API
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from core.models import Season, Conference, Team, TeamSeasonStats
from .serializers import (
    SeasonSerializer, 
    ConferenceSerializer, 
    TeamSerializer,
    TeamSeasonStatsSerializer,
    RankingsSerializer,
    TeamDetailSerializer,
)


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/seasons
    Returns list of all available seasons
    """
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


class ConferenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/conferences
    Returns list of all conferences
    """
    queryset = Conference.objects.all()
    serializer_class = ConferenceSerializer


class RankingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/rankings?season=2026&sort=adj_em&dir=desc&conference=B10&search=mich
    
    Returns sortable/filterable rankings table
    
    Query Params:
    - season: year (default: current season)
    - sort: field to sort by (default: rank)
    - dir: asc or desc (default: asc)
    - conference: conference code filter
    - search: team name search
    """
    serializer_class = RankingsSerializer
    
    def get_queryset(self):
        # Get season (default to current)
        season_year = self.request.query_params.get('season')
        if season_year:
            season = get_object_or_404(Season, year=season_year)
        else:
            season = Season.objects.filter(is_current=True).first()
        
        queryset = TeamSeasonStats.objects.filter(season=season).select_related(
            'team', 'conference'
        )
        
        # Filter by conference
        conference = self.request.query_params.get('conference')
        if conference:
            queryset = queryset.filter(conference__code=conference)
        
        # Search by team name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(team__name__icontains=search) | Q(team__slug__icontains=search)
            )
        
        # Sorting
        sort_field = self.request.query_params.get('sort', 'rank')
        sort_dir = self.request.query_params.get('dir', 'asc')
        
        # Validate sort field (prevent SQL injection)
        allowed_fields = [
            'rank', 'adj_em', 'adj_o', 'adj_d', 'adj_tempo',
            'efg_pct', 'tov_pct', 'orb_pct', 'ftr',
            'efg_pct_d', 'tov_pct_d', 'drb_pct', 'ftr_d',
            'team__name', 'conference__code',
        ]
        
        if sort_field in allowed_fields:
            order_prefix = '-' if sort_dir == 'desc' else ''
            queryset = queryset.order_by(f'{order_prefix}{sort_field}')
        
        return queryset


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/teams?season=2026&search=michigan
    GET /api/teams/{slug}?season=2026
    
    Returns team information and stats
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def stats(self, request, slug=None):
        """
        GET /api/teams/{slug}/stats?season=2026
        
        Returns detailed stats for a team in a specific season
        """
        team = self.get_object()
        
        # Get season
        season_year = request.query_params.get('season')
        if season_year:
            season = get_object_or_404(Season, year=season_year)
        else:
            season = Season.objects.filter(is_current=True).first()
        
        # Get stats
        stats = get_object_or_404(
            TeamSeasonStats,
            team=team,
            season=season
        )
        
        serializer = TeamSeasonStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def profile(self, request, slug=None):
        """
        GET /api/teams/{slug}/profile?season=2026
        
        Returns complete team profile with historical data
        """
        team = self.get_object()
        
        # Get requested season or current
        season_year = request.query_params.get('season')
        if season_year:
            season = get_object_or_404(Season, year=season_year)
        else:
            season = Season.objects.filter(is_current=True).first()
        
        # Get current season stats
        current_stats = TeamSeasonStats.objects.filter(
            team=team,
            season=season
        ).select_related('conference').first()
        
        # Get all historical stats
        all_stats = TeamSeasonStats.objects.filter(
            team=team
        ).select_related('season', 'conference').order_by('-season__year')
        
        response_data = {
            'team': TeamSerializer(team).data,
            'current_season_stats': TeamSeasonStatsSerializer(current_stats).data if current_stats else None,
            'seasons': TeamSeasonStatsSerializer(all_stats, many=True).data,
        }
        
        return Response(response_data)


class MatchupViewSet(viewsets.ViewSet):
    """
    GET /api/matchup?season=2026&teamA=michigan&teamB=duke&site=neutral
    
    Returns head-to-head matchup analysis
    """
    
    def list(self, request):
        team_a_slug = request.query_params.get('teamA')
        team_b_slug = request.query_params.get('teamB')
        site = request.query_params.get('site', 'neutral')  # neutral, home, away
        
        if not team_a_slug or not team_b_slug:
            return Response(
                {'error': 'teamA and teamB required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get season
        season_year = request.query_params.get('season')
        if season_year:
            season = get_object_or_404(Season, year=season_year)
        else:
            season = Season.objects.filter(is_current=True).first()
        
        # Get teams
        team_a = get_object_or_404(Team, slug=team_a_slug)
        team_b = get_object_or_404(Team, slug=team_b_slug)
        
        # Get stats
        stats_a = get_object_or_404(TeamSeasonStats, team=team_a, season=season)
        stats_b = get_object_or_404(TeamSeasonStats, team=team_b, season=season)
        
        # Calculate matchup metrics
        # Home court advantage: ~3.5 points in college basketball
        hca = 3.5
        
        if site == 'home':
            em_diff = stats_a.adj_em - stats_b.adj_em + hca
        elif site == 'away':
            em_diff = stats_a.adj_em - stats_b.adj_em - hca
        else:  # neutral
            em_diff = stats_a.adj_em - stats_b.adj_em
        
        # Win probability using log5 formula
        pythag_a = stats_a.barthag if stats_a.barthag else 0.5
        pythag_b = stats_b.barthag if stats_b.barthag else 0.5
        
        win_prob_a = (pythag_a - pythag_a * pythag_b) / (pythag_a + pythag_b - 2 * pythag_a * pythag_b)
        
        # Key edges
        edges = {
            'efficiency': em_diff,
            'offensive': stats_a.adj_o - stats_b.adj_o,
            'defensive': stats_b.adj_d - stats_a.adj_d,  # Lower is better for defense
            'tempo': stats_a.adj_tempo - stats_b.adj_tempo,
            'efg': stats_a.efg_margin - stats_b.efg_margin,
            'tov': stats_a.tov_edge - stats_b.tov_edge,
            'reb': stats_a.reb_edge - stats_b.reb_edge,
            'ftr': stats_a.ftr_margin - stats_b.ftr_margin,
        }
        
        return Response({
            'teamA': TeamSeasonStatsSerializer(stats_a).data,
            'teamB': TeamSeasonStatsSerializer(stats_b).data,
            'matchup': {
                'site': site,
                'win_probability_a': round(win_prob_a, 3),
                'win_probability_b': round(1 - win_prob_a, 3),
                'predicted_margin': round(em_diff, 1),
                'edges': edges,
            }
        })
