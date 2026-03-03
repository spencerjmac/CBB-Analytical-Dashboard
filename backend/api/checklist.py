"""
National Champion Checklist Logic

Computes the 15-item checklist for championship contenders based on 
historical champion thresholds.
"""

from typing import Dict, List, Optional, Any
from core.models import TeamSeasonStats
from .trapezoid_views import compute_trapezoid_boundaries, is_inside_trapezoid
import numpy as np


def compute_national_champion_checklist(
    team_stats: TeamSeasonStats,
    season_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compute the National Champion Checklist for a team.
    
    Args:
        team_stats: TeamSeasonStats instance for the team
        season_context: Pre-computed season-wide stats including:
            - max_adj_em: Maximum AdjEM in the season
            - trapezoid: Trapezoid boundaries
            - adj_o_ranks: Dict mapping team_id to AdjO rank
            - adj_d_ranks: Dict mapping team_id to AdjD rank
    
    Returns:
        Dictionary with checklist results
    """
    items = []
    passed_count = 0
    
    # 1) Trapezoid of Excellence
    item = _check_trapezoid(team_stats, season_context)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 2) KenPom Contender
    item = _check_kenpom_contender(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 3) Predicted Efficiency "Title Favorite"
    item = _check_title_favorite(team_stats, season_context)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 4) Win%
    item = _check_win_pct(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 5) Elite Off/Def ranks
    item = _check_elite_ranks(team_stats, season_context)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 6) 3P%
    item = _check_three_point_pct(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 7) T-Rank
    item = _check_t_rank(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 8) AP Poll Week 6
    item = _check_ap_poll_week6(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 9) eFG Margin
    item = _check_efg_margin(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 10) FTR Margin
    item = _check_ftr_margin(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 11) Rebounding Edge
    item = _check_rebounding_edge(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 12) Turnover Edge
    item = _check_turnover_edge(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 13) Four Factor Index
    item = _check_four_factor_index(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 14) WAB
    item = _check_wab(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    # 15) FT%
    item = _check_ft_pct(team_stats)
    items.append(item)
    if item['pass']:
        passed_count += 1
    
    return {
        "passedCount": passed_count,
        "totalCount": 15,
        "items": items
    }


def compute_season_context(season) -> Dict[str, Any]:
    """
    Pre-compute season-wide statistics needed for checklist computation.
    This should be called once per season and cached/reused for all teams.
    
    Args:
        season: Season instance
    
    Returns:
        Dictionary with season context
    """
    # Get all teams in the season
    teams = TeamSeasonStats.objects.filter(season=season).select_related('team')
    
    if not teams:
        return {
            "max_adj_em": None,
            "trapezoid": None,
            "adj_o_ranks": {},
            "adj_d_ranks": {},
        }
    
    # Compute max AdjEM
    max_adj_em = max((t.adj_em for t in teams), default=None)
    
    # Compute trapezoid boundaries
    tempo_values = np.array([t.adj_tempo for t in teams])
    em_values = np.array([t.adj_em for t in teams])
    trapezoid = compute_trapezoid_boundaries(tempo_values, em_values)
    
    # Compute AdjO ranks (higher is better, rank 1 = highest AdjO)
    adj_o_sorted = sorted(teams, key=lambda t: t.adj_o, reverse=True)
    adj_o_ranks = {t.team_id: rank + 1 for rank, t in enumerate(adj_o_sorted)}
    
    # Compute AdjD ranks (lower is better, rank 1 = lowest AdjD)
    adj_d_sorted = sorted(teams, key=lambda t: t.adj_d)
    adj_d_ranks = {t.team_id: rank + 1 for rank, t in enumerate(adj_d_sorted)}
    
    return {
        "max_adj_em": max_adj_em,
        "trapezoid": trapezoid,
        "adj_o_ranks": adj_o_ranks,
        "adj_d_ranks": adj_d_ranks,
    }


# ==================== Individual Check Functions ====================

def _check_trapezoid(team_stats: TeamSeasonStats, context: Dict[str, Any]) -> Dict[str, Any]:
    """Check if team is inside the Trapezoid of Excellence"""
    trapezoid = context.get('trapezoid')
    
    if trapezoid is None:
        return {
            "key": "trapezoid",
            "label": "Trapezoid of Excellence",
            "pass": False,
            "value": "N/A",
            "threshold": "Inside trapezoid",
            "details": "Trapezoid data unavailable"
        }
    
    inside = is_inside_trapezoid(team_stats.adj_tempo, team_stats.adj_em, trapezoid)
    
    return {
        "key": "trapezoid",
        "label": "Trapezoid of Excellence",
        "pass": inside,
        "value": "Inside" if inside else "Outside",
        "threshold": "Inside trapezoid",
        "details": f"Tempo: {team_stats.adj_tempo:.1f}, AdjEM: {team_stats.adj_em:.1f}"
    }


def _check_kenpom_contender(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check KenPom contender thresholds"""
    adj_o = team_stats.adj_o
    adj_d = team_stats.adj_d
    adj_em = team_stats.adj_em
    
    # Pass if (AdjO > 113.8 AND AdjD < 95.0) OR (AdjEM > 30.0)
    condition1 = adj_o > 113.8 and adj_d < 95.0
    condition2 = adj_em > 30.0
    passes = condition1 or condition2
    
    return {
        "key": "kenpom_contender",
        "label": "KenPom Contender",
        "pass": passes,
        "value": f"O: {adj_o:.1f}, D: {adj_d:.1f}",
        "threshold": "(O > 113.8 & D < 95.0) OR EM > 30.0",
        "details": f"AdjO: {adj_o:.1f}, AdjD: {adj_d:.1f}, AdjEM: {adj_em:.1f}"
    }


def _check_title_favorite(team_stats: TeamSeasonStats, context: Dict[str, Any]) -> Dict[str, Any]:
    """Check if team is within 6 points of max AdjEM"""
    max_adj_em = context.get('max_adj_em')
    adj_em = team_stats.adj_em
    
    if max_adj_em is None:
        return {
            "key": "title_favorite",
            "label": "Title Favorite (AdjEM)",
            "pass": False,
            "value": "N/A",
            "threshold": "Within 6.0 of max",
            "details": "Season max unavailable"
        }
    
    threshold = max_adj_em - 6.0
    passes = adj_em >= threshold
    
    return {
        "key": "title_favorite",
        "label": "Title Favorite (AdjEM)",
        "pass": passes,
        "value": f"{adj_em:.1f}",
        "threshold": f"≥ {threshold:.1f} (max: {max_adj_em:.1f})",
        "details": f"AdjEM {adj_em:.1f}, needs ≥ {threshold:.1f} (max is {max_adj_em:.1f})"
    }


def _check_win_pct(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check win percentage > 74%"""
    if team_stats.games == 0:
        win_pct = 0.0
    else:
        win_pct = team_stats.wins / team_stats.games
    
    passes = win_pct > 0.74
    
    return {
        "key": "win_pct",
        "label": "Win Percentage",
        "pass": passes,
        "value": f"{win_pct * 100:.1f}%",
        "threshold": "> 74%",
        "details": f"{team_stats.record} ({win_pct * 100:.1f}%)"
    }


def _check_elite_ranks(team_stats: TeamSeasonStats, context: Dict[str, Any]) -> Dict[str, Any]:
    """Check OffRtgRank <= 21 AND DefRtgRank <= 37"""
    adj_o_ranks = context.get('adj_o_ranks', {})
    adj_d_ranks = context.get('adj_d_ranks', {})
    
    off_rank = adj_o_ranks.get(team_stats.team_id)
    def_rank = adj_d_ranks.get(team_stats.team_id)
    
    if off_rank is None or def_rank is None:
        return {
            "key": "elite_ranks",
            "label": "Elite Off/Def Ranks",
            "pass": False,
            "value": "N/A",
            "threshold": "Off ≤ 21, Def ≤ 37",
            "details": "Rank data unavailable"
        }
    
    passes = off_rank <= 21 and def_rank <= 37
    
    return {
        "key": "elite_ranks",
        "label": "Elite Off/Def Ranks",
        "pass": passes,
        "value": f"Off: #{off_rank}, Def: #{def_rank}",
        "threshold": "Off ≤ 21, Def ≤ 37",
        "details": f"Offensive rank: #{off_rank}, Defensive rank: #{def_rank}"
    }


def _check_three_point_pct(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check 3P% > 32%"""
    fg3_pct = team_stats.fg3_pct
    
    if fg3_pct is None:
        return {
            "key": "three_point_pct",
            "label": "3-Point %",
            "pass": False,
            "value": "N/A",
            "threshold": "> 32%",
            "details": "3P% data unavailable"
        }
    
    # Assuming fg3_pct is stored as 0-100 scale (e.g., 34.5 for 34.5%)
    # If it's stored as 0-1 scale, adjust the threshold
    threshold = 32.0
    if fg3_pct < 1.0:  # Stored as decimal (0-1)
        threshold = 0.32
        passes = fg3_pct > threshold
        display_value = f"{fg3_pct * 100:.1f}%"
    else:  # Stored as percentage (0-100)
        passes = fg3_pct > threshold
        display_value = f"{fg3_pct:.1f}%"
    
    return {
        "key": "three_point_pct",
        "label": "3-Point %",
        "pass": passes,
        "value": display_value,
        "threshold": "> 32%",
        "details": f"Team 3P%: {display_value}"
    }


def _check_t_rank(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check T-Rank <= 17"""
    t_rank = team_stats.t_rank
    
    if t_rank is None:
        return {
            "key": "t_rank",
            "label": "T-Rank",
            "pass": False,
            "value": "N/A",
            "threshold": "≤ 17",
            "details": "T-Rank unavailable"
        }
    
    passes = t_rank <= 17
    
    return {
        "key": "t_rank",
        "label": "T-Rank",
        "pass": passes,
        "value": f"#{t_rank}",
        "threshold": "≤ 17",
        "details": f"T-Rank: #{t_rank}"
    }


def _check_ap_poll_week6(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check AP Poll Week 6 <= 12"""
    ap_rank = team_stats.ap_poll_week6
    
    if ap_rank is None:
        return {
            "key": "ap_poll_week6",
            "label": "AP Poll Week 6",
            "pass": False,
            "value": "N/A",
            "threshold": "≤ 12",
            "details": "AP Poll data unavailable"
        }
    
    passes = ap_rank <= 12
    
    return {
        "key": "ap_poll_week6",
        "label": "AP Poll Week 6",
        "pass": passes,
        "value": f"#{ap_rank}",
        "threshold": "≤ 12",
        "details": f"AP Poll Week 6: #{ap_rank}"
    }


def _check_efg_margin(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check eFG Margin >= 6.0"""
    efg_margin = team_stats.efg_margin
    threshold = 6.0
    passes = efg_margin >= threshold
    
    return {
        "key": "efg_margin",
        "label": "eFG Margin",
        "pass": passes,
        "value": f"{efg_margin:.3f}",
        "threshold": "≥ 6.0",
        "details": f"eFG Margin: {efg_margin:.3f}"
    }


def _check_ftr_margin(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check FTR Margin >= -5.5"""
    ftr_margin = team_stats.ftr_margin
    threshold = -5.5
    passes = ftr_margin >= threshold
    
    return {
        "key": "ftr_margin",
        "label": "FTR Margin",
        "pass": passes,
        "value": f"{ftr_margin:.2f}",
        "threshold": "≥ -5.5",
        "details": f"FTR Margin: {ftr_margin:.2f}"
    }


def _check_rebounding_edge(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check Rebounding Edge >= 0"""
    reb_edge = team_stats.reb_edge
    threshold = 0.0
    passes = reb_edge >= threshold
    
    return {
        "key": "rebounding_edge",
        "label": "Rebounding Edge",
        "pass": passes,
        "value": f"{reb_edge:.2f}",
        "threshold": "≥ 0",
        "details": f"Rebounding Edge: {reb_edge:.2f}"
    }


def _check_turnover_edge(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check Turnover Edge >= 1.5"""
    to_edge = team_stats.tov_edge
    threshold = 1.5
    passes = to_edge >= threshold
    
    return {
        "key": "turnover_edge",
        "label": "Turnover Edge",
        "pass": passes,
        "value": f"{to_edge:.2f}",
        "threshold": "≥ 1.5",
        "details": f"Turnover Edge: {to_edge:.2f}"
    }


def _check_four_factor_index(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check Four Factor Index > 80.0"""
    ffi = team_stats.four_factor_index_100
    
    if ffi is None:
        return {
            "key": "four_factor_index",
            "label": "Four Factor Index",
            "pass": False,
            "value": "N/A",
            "threshold": "> 80.0",
            "details": "Four Factor Index unavailable"
        }
    
    threshold = 80.0
    passes = ffi > threshold
    
    return {
        "key": "four_factor_index",
        "label": "Four Factor Index",
        "pass": passes,
        "value": f"{ffi:.1f}",
        "threshold": "> 80.0",
        "details": f"Four Factor Index: {ffi:.1f}"
    }


def _check_wab(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check WAB > 5"""
    # Try to get WAB from TeamSeasonStats first, then from TeamSeasonRatings
    wab = team_stats.wab
    
    if wab is None:
        # Fallback to TeamSeasonRatings
        try:
            from core.models import TeamSeasonRatings
            ratings = TeamSeasonRatings.objects.get(
                team=team_stats.team,
                season=team_stats.season
            )
            wab = ratings.wab
        except (TeamSeasonRatings.DoesNotExist, AttributeError):
            pass
    
    if wab is None:
        return {
            "key": "wab",
            "label": "WAB (Wins Above Bubble)",
            "pass": False,
            "value": "N/A",
            "threshold": "> 5",
            "details": "WAB unavailable"
        }
    
    threshold = 5.0
    passes = wab > threshold
    
    return {
        "key": "wab",
        "label": "WAB (Wins Above Bubble)",
        "pass": passes,
        "value": f"{wab:.1f}",
        "threshold": "> 5",
        "details": f"WAB: {wab:.1f}"
    }


def _check_ft_pct(team_stats: TeamSeasonStats) -> Dict[str, Any]:
    """Check FT% > 70%"""
    ft_pct = team_stats.ft_pct
    
    if ft_pct is None:
        return {
            "key": "ft_pct",
            "label": "Free Throw %",
            "pass": False,
            "value": "N/A",
            "threshold": "> 70%",
            "details": "FT% data unavailable"
        }
    
    # Assuming ft_pct is stored as 0-100 scale (e.g., 72.5 for 72.5%)
    # If it's stored as 0-1 scale, adjust the threshold
    threshold = 70.0
    if ft_pct < 1.0:  # Stored as decimal (0-1)
        threshold = 0.70
        passes = ft_pct > threshold
        display_value = f"{ft_pct * 100:.1f}%"
    else:  # Stored as percentage (0-100)
        passes = ft_pct > threshold
        display_value = f"{ft_pct:.1f}%"
    
    return {
        "key": "ft_pct",
        "label": "Free Throw %",
        "pass": passes,
        "value": display_value,
        "threshold": "> 70%",
        "details": f"Team FT%: {display_value}"
    }
