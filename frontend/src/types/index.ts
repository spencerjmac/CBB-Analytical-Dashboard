/**
 * TypeScript types for CBB Analytics API
 * These mirror the Django models and API responses
 */

export interface Season {
  id: number;
  year: number;
  display_name: string;
  is_current: boolean;
}

export interface Conference {
  id: number;
  code: string;
  name: string;
}

export interface Team {
  id: number;
  slug: string;
  name: string;
  aliases: string[];
  logo_url: string | null;
}

export interface TeamSeasonStats {
  // Identifiers
  id: number;
  team_name: string;
  team_slug: string;
  team_logo: string | null;
  conference_code: string;
  conference_name: string;
  season_year: number;
  
  // Record
  games: number;
  wins: number;
  losses: number;
  record: string;
  
  // Rankings
  rank: number | null;
  rank_adj_em: number | null;
  rank_adj_o: number | null;
  rank_adj_d: number | null;
  
  // Core Metrics
  adj_em: number;
  adj_o: number;
  adj_d: number;
  adj_tempo: number;
  
  // Four Factors - Offense
  efg_pct: number;
  tov_pct: number;
  orb_pct: number;
  ftr: number;
  
  // Four Factors - Defense
  efg_pct_d: number;
  tov_pct_d: number;
  drb_pct: number;
  ftr_d: number;
  
  // Margins
  efg_margin: number;
  tov_edge: number;
  reb_edge: number;
  ftr_margin: number;
  
  // Shooting Splits
  fg2_pct: number | null;
  fg2_pct_d: number | null;
  fg3_pct: number | null;
  fg3_pct_d: number | null;
  fg3_rate: number | null;
  fg3_rate_d: number | null;
  
  // Resume
  wab: number | null;
  sor: number | null;
  barthag: number | null;
  luck: number | null;
  sos_adj_em: number | null;
  ncsos_adj_em: number | null;
  
  // Provenance
  has_kenpom: boolean;
  has_torvik: boolean;
  has_cbb_analytics: boolean;
  last_updated: string;
}

export interface RankingsRow {
  rank: number;
  team_name: string;
  team_slug: string;
  team_logo: string | null;
  conference: string;
  record: string;
  adj_em: number;
  adj_o: number;
  adj_d: number;
  adj_tempo: number;
  efg_pct: number;
  tov_pct: number;
  orb_pct: number;
  ftr: number;
  efg_pct_d: number;
  tov_pct_d: number;
  drb_pct: number;
  ftr_d: number;
}

export interface TeamProfile {
  team: Team;
  current_season_stats: TeamSeasonStats | null;
  seasons: TeamSeasonStats[];
}

export interface MatchupEdges {
  efficiency: number;
  offensive: number;
  defensive: number;
  tempo: number;
  efg: number;
  tov: number;
  reb: number;
  ftr: number;
}

export interface MatchupResult {
  teamA: TeamSeasonStats;
  teamB: TeamSeasonStats;
  matchup: {
    site: 'neutral' | 'home' | 'away';
    win_probability_a: number;
    win_probability_b: number;
    predicted_margin: number;
    edges: MatchupEdges;
  };
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
