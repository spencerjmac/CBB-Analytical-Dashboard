"""
Core Django Models for CBB Analytics
Normalized schema for college basketball team statistics
"""

from django.db import models
from django.utils.text import slugify


class Season(models.Model):
    """Represents a basketball season (e.g., 2025-26)"""
    year = models.IntegerField(unique=True, help_text="Ending year (2026 for 2025-26 season)")
    display_name = models.CharField(max_length=20, help_text="Human-readable name")
    is_current = models.BooleanField(default=False, help_text="Is this the active season?")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year']
    
    def __str__(self):
        return self.display_name
    
    def save(self, *args, **kwargs):
        # Auto-set is_current to False for all others if this is current
        if self.is_current:
            Season.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Conference(models.Model):
    """NCAA conferences"""
    code = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Team(models.Model):
    """NCAA D1 basketball teams (365 teams)"""
    slug = models.SlugField(unique=True, db_index=True, max_length=100)
    name = models.CharField(max_length=100)
    aliases = models.JSONField(default=list, blank=True, help_text="Alternative names")
    logo_url = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TeamSeasonStats(models.Model):
    """
    Statistics for a team in a specific season
    This is the main table combining data from KenPom, Torvik, CBB Analytics
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='season_stats')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='team_stats')
    conference = models.ForeignKey(Conference, on_delete=models.SET_NULL, null=True, blank=True)
    
    # ==================== Record ====================
    games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    
    # ==================== National Rankings ====================
    rank = models.IntegerField(null=True, blank=True, help_text="Overall rank")
    rank_adj_em = models.IntegerField(null=True, blank=True)
    rank_adj_o = models.IntegerField(null=True, blank=True)
    rank_adj_d = models.IntegerField(null=True, blank=True)
    
    # ==================== Core Efficiency Metrics ====================
    adj_em = models.FloatField(help_text="Adjusted Efficiency Margin")
    adj_o = models.FloatField(help_text="Adjusted Offensive Efficiency")
    adj_d = models.FloatField(help_text="Adjusted Defensive Efficiency")
    adj_tempo = models.FloatField(help_text="Adjusted Tempo")
    
    # ==================== Four Factors - Offense ====================
    efg_pct = models.FloatField(help_text="Effective FG%")
    tov_pct = models.FloatField(help_text="Turnover %")
    orb_pct = models.FloatField(help_text="Offensive Rebound %")
    ftr = models.FloatField(help_text="Free Throw Rate")
    
    # ==================== Four Factors - Defense ====================
    efg_pct_d = models.FloatField(help_text="Opponent Effective FG%")
    tov_pct_d = models.FloatField(help_text="Opponent Turnover %")
    drb_pct = models.FloatField(help_text="Defensive Rebound %")
    ftr_d = models.FloatField(help_text="Opponent Free Throw Rate")
    
    # ==================== Shooting Splits ====================
    fg2_pct = models.FloatField(null=True, blank=True, help_text="2-point FG%")
    fg2_pct_d = models.FloatField(null=True, blank=True, help_text="Opponent 2-point FG%")
    fg3_pct = models.FloatField(null=True, blank=True, help_text="3-point FG%")
    fg3_pct_d = models.FloatField(null=True, blank=True, help_text="Opponent 3-point FG%")
    fg3_rate = models.FloatField(null=True, blank=True, help_text="3-point attempt rate")
    fg3_rate_d = models.FloatField(null=True, blank=True, help_text="Opponent 3-point attempt rate")
    
    # ==================== Resume Metrics ====================
    wab = models.FloatField(null=True, blank=True, help_text="Wins Above Bubble")
    sor = models.FloatField(null=True, blank=True, help_text="Strength of Record")
    barthag = models.FloatField(null=True, blank=True, help_text="Barthag win probability")
    luck = models.FloatField(null=True, blank=True, help_text="Luck rating")
    sos_adj_em = models.FloatField(null=True, blank=True, help_text="Strength of Schedule (AdjEM)")
    ncsos_adj_em = models.FloatField(null=True, blank=True, help_text="Non-conference SOS (AdjEM)")
    
    # ==================== Precomputed Margins ====================
    efg_margin = models.FloatField(default=0, help_text="eFG% - Opp eFG%")
    tov_edge = models.FloatField(default=0, help_text="Opp TOV% - TOV%")
    reb_edge = models.FloatField(default=0, help_text="ORB% - (100 - DRB%)")
    ftr_margin = models.FloatField(default=0, help_text="FTR - Opp FTR")
    
    # ==================== Data Provenance ====================
    has_kenpom = models.BooleanField(default=False)
    has_torvik = models.BooleanField(default=False)
    has_cbb_analytics = models.BooleanField(default=False)
    
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['team', 'season']]
        indexes = [
            models.Index(fields=['season', 'rank']),
            models.Index(fields=['season', 'conference']),
            models.Index(fields=['season', 'adj_em']),
        ]
        ordering = ['season', 'rank']
        verbose_name_plural = "Team Season Stats"
    
    def __str__(self):
        return f"{self.team.name} {self.season.display_name} (Rank #{self.rank})"
    
    @property
    def record(self):
        """Returns record as string (e.g., '22-3')"""
        return f"{self.wins}-{self.losses}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate margins
        self.efg_margin = self.efg_pct - self.efg_pct_d
        self.tov_edge = self.tov_pct_d - self.tov_pct
        self.reb_edge = self.orb_pct - (100 - self.drb_pct)
        self.ftr_margin = self.ftr - self.ftr_d
        super().save(*args, **kwargs)


class DataIngestionRun(models.Model):
    """Track data ingestion runs for auditing and debugging"""
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('running', 'Running'),
            ('success', 'Success'),
            ('error', 'Error'),
        ],
        default='running'
    )
    
    teams_ingested = models.IntegerField(default=0)
    error_log = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Ingestion {self.season.display_name} - {self.status} ({self.started_at})"
