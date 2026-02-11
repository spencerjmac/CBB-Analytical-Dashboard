from django.contrib import admin
from .models import Season, Conference, Team, TeamSeasonStats, DataIngestionRun


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['year', 'display_name', 'is_current', 'created_at']
    list_filter = ['is_current']
    search_fields = ['display_name']


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'logo_url']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TeamSeasonStats)
class TeamSeasonStatsAdmin(admin.ModelAdmin):
    list_display = ['team', 'season', 'rank', 'record', 'adj_em', 'conference']
    list_filter = ['season', 'conference', 'has_kenpom', 'has_torvik']
    search_fields = ['team__name']
    readonly_fields = ['efg_margin', 'tov_edge', 'reb_edge', 'ftr_margin', 'last_updated', 'created_at']


@admin.register(DataIngestionRun)
class DataIngestionRunAdmin(admin.ModelAdmin):
    list_display = ['season', 'status', 'teams_ingested', 'started_at', 'completed_at']
    list_filter = ['status', 'season']
    readonly_fields = ['started_at']
