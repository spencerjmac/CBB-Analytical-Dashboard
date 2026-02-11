"""
URL configuration for API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SeasonViewSet,
    ConferenceViewSet,
    RankingsViewSet,
    TeamViewSet,
    MatchupViewSet,
)

router = DefaultRouter()
router.register(r'seasons', SeasonViewSet, basename='season')
router.register(r'conferences', ConferenceViewSet, basename='conference')
router.register(r'rankings', RankingsViewSet, basename='rankings')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'matchup', MatchupViewSet, basename='matchup')

urlpatterns = [
    path('', include(router.urls)),
]
