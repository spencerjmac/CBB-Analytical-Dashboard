// Core data types for the application

export interface TeamSeason {
  // Identity
  teamId: string;
  teamName: string;
  teamNameAlt: string[];
  conference: string;
  logoUrl: string;
  
  // Season Context
  season: string;
  lastUpdated: string;
  games: number;
  record: string;
  
  // Core Ratings
  rank: number;
  adjEM: number;
  adjO: number;
  adjD: number;
  adjTempo: number;
  
  // Four Factors - Offense
  eFG: number;
  tov: number;
  orb: number;
  ftr: number;
  
  // Four Factors - Defense
  eFG_d: number;
  tov_d: number;
  drb: number;
  ftr_d: number;
  
  // Four Factors - Margins (derived)
  eFG_margin: number;
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
  
  // Resume Metrics
  wab: number | null;
  sor: number | null;
  luck: number | null;
  sos_adjEM: number | null;
  ncsos_adjEM: number | null;
  barthag: number | null;
  
  // Source metadata
  sources: {
    kenpom: boolean;
    torvik: boolean;
    cbbAnalytics: boolean;
  };
}

export interface DatasetMetadata {
  lastUpdated: string;
  season: string;
  teamCount: number;
  sources: {
    kenpom: number;
    torvik: number;
    cbbAnalytics: number;
  };
}

export interface TeamsData {
  metadata: DatasetMetadata;
  teams: TeamSeason[];
}

export interface MetricDefinition {
  id: string;
  name: string;
  category: string;
  definition: string;
  formula: string; // LaTeX
  interpretation: string;
  range?: string;
  higherIsBetter: boolean;
}
