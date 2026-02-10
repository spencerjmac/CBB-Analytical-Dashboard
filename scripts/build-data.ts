/**
 * Data Pipeline: Transform raw CSV data into unified TeamSeason JSON
 * 
 * This script:
 * 1. Reads KenPom, Torvik, and CBB Analytics CSV files
 * 2. Normalizes team names using team-name-map.json
 * 3. Merges data sources by team
 * 4. Resolves logo paths
 * 5. Calculates derived metrics (margins, edges)
 * 6. Outputs unified teams.json for the web app
 */

import * as fs from 'fs';
import * as path from 'path';
import { parse } from 'csv-parse/sync';

// Types
interface TeamSeason {
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

interface TeamNameMapping {
  slug: string;
  display: string;
  aliases: string[];
}

// Helper: Load CSV
function loadCSV(filePath: string): any[] {
  const content = fs.readFileSync(filePath, 'utf-8');
  return parse(content, { columns: true, skip_empty_lines: true });
}

// Helper: Normalize team name to slug
function normalizeTeamName(name: string, mapping: Record<string, TeamNameMapping>): string {
  // Direct match
  if (mapping[name]) return mapping[name].slug;
  
  // Try aliases
  for (const [key, value] of Object.entries(mapping)) {
    if (value.aliases.some(alias => alias.toLowerCase() === name.toLowerCase())) {
      return value.slug;
    }
  }
  
  // Fallback: slugify
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

// Helper: Get logo path
function getLogoPath(teamSlug: string): string {
  const logoDir = path.join(__dirname, '..', 'College Logos', 'output', 'logos');
  
  // Try exact match
  const exactPath = `${teamSlug}.png`;
  if (fs.existsSync(path.join(logoDir, exactPath))) {
    return `/logos/${exactPath}`;
  }
  
  // Try with variations (underscore conversion)
  const files = fs.readdirSync(logoDir);
  const match = files.find(f => 
    f.toLowerCase().replace(/_/g, '-').replace('.png', '') === teamSlug
  );
  
  return match ? `/logos/${match}` : '/logos/default.png';
}

// Helper: Parse percentage string to decimal
function parsePercentage(value: string | number | null | undefined): number | null {
  if (value === null || value === undefined || value === '') return null;
  if (typeof value === 'number') return value;
  const str = String(value).replace('%', '');
  const num = parseFloat(str);
  return isNaN(num) ? null : (str.includes('%') ? num / 100 : num);
}

// Helper: Parse number
function parseNum(value: any): number | null {
  if (value === null || value === undefined || value === '') return null;
  const num = typeof value === 'number' ? value : parseFloat(String(value));
  return isNaN(num) ? null : num;
}

// Main pipeline
function buildData() {
  console.log('🏀 CBB Analytics Data Pipeline');
  console.log('================================\n');
  
  // Load team name mapping
  const teamNameMap: Record<string, TeamNameMapping> = JSON.parse(
    fs.readFileSync(path.join(__dirname, 'team-name-map.json'), 'utf-8')
  );
  
  // Load CSVs
  console.log('📂 Loading source data...');
  const kenpomPath = path.join(__dirname, '..', 'KenPom Data', 'kenpom_tableau.csv');
  const torvikPath = path.join(__dirname, '..', 'Bart Torvik', 'torvik_tableau.csv');
  const cbbAnalyticsPath = path.join(__dirname, '..', 'CBB Analytics', 'cbb_analytics_tableau_cleaned.csv');
  
  const kenpomData = loadCSV(kenpomPath);
  const torvikData = loadCSV(torvikPath);
  const cbbAnalyticsData = loadCSV(cbbAnalyticsPath);
  
  console.log(`  ✓ KenPom: ${kenpomData.length} teams`);
  console.log(`  ✓ Torvik: ${torvikData.length} teams`);
  console.log(`  ✓ CBB Analytics: ${cbbAnalyticsData.length} teams\n`);
  
  // Build unified dataset
  console.log('🔗 Merging data sources...');
  const teamsMap = new Map<string, TeamSeason>();
  
  // Process Torvik first (has most complete Four Factors data)
  for (const row of torvikData) {
    const teamName = row.team_name;
    const teamSlug = normalizeTeamName(teamName, teamNameMap);
    
    const team: TeamSeason = {
      // Identity
      teamId: teamSlug,
      teamName: teamNameMap[teamName]?.display || teamName,
      teamNameAlt: teamNameMap[teamName]?.aliases || [teamName],
      conference: row.conference || '',
      logoUrl: getLogoPath(teamSlug),
      
      // Season Context
      season: '2025-26',
      lastUpdated: row.date || new Date().toISOString().split('T')[0],
      games: parseNum(row.games) || 0,
      record: row.record || '',
      
      // Core Ratings (Torvik names: adj_oe, adj_de, barthag, adj_tempo)
      rank: parseNum(row.rank) || 999,
      adjEM: parseNum(row.adj_oe) && parseNum(row.adj_de) 
        ? parseNum(row.adj_oe)! - parseNum(row.adj_de)! 
        : 0,
      adjO: parseNum(row.adj_oe) || 0,
      adjD: parseNum(row.adj_de) || 0,
      adjTempo: parseNum(row.adj_tempo) || 0,
      
      // Four Factors - Offense
      eFG: parsePercentage(row.efg_pct) || 0,
      tov: parsePercentage(row.tor) || 0,
      orb: parsePercentage(row.orb) || 0,
      ftr: parsePercentage(row.ftr) || 0,
      
      // Four Factors - Defense
      eFG_d: parsePercentage(row.efg_pct_d) || 0,
      tov_d: parsePercentage(row.tord) || 0,
      drb: parsePercentage(row.drb) || 0,
      ftr_d: parsePercentage(row.ftrd) || 0,
      
      // Margins (calculate)
      eFG_margin: 0, // calculated below
      tov_edge: 0,
      reb_edge: 0,
      ftr_margin: 0,
      
      // Shooting Splits
      fg2_pct: parsePercentage(row.two_p_pct),
      fg2_pct_d: parsePercentage(row.two_p_pct_d),
      fg3_pct: parsePercentage(row.three_p_pct),
      fg3_pct_d: parsePercentage(row.three_p_pct_d),
      fg3_rate: parsePercentage(row.three_pr),
      fg3_rate_d: parsePercentage(row.three_prd),
      
      // Resume Metrics
      wab: parseNum(row.wab),
      sor: null,
      luck: null,
      sos_adjEM: null,
      ncsos_adjEM: null,
      barthag: parseNum(row.barthag),
      
      // Sources
      sources: {
        kenpom: false,
        torvik: true,
        cbbAnalytics: false,
      },
    };
    
    // Calculate margins
    team.eFG_margin = team.eFG - team.eFG_d;
    team.tov_edge = team.tov_d - team.tov;
    team.reb_edge = team.orb - team.drb;
    team.ftr_margin = team.ftr - team.ftr_d;
    
    teamsMap.set(teamSlug, team);
  }
  
  // Merge KenPom data
  for (const row of kenpomData) {
    const teamName = row.team_name;
    const teamSlug = normalizeTeamName(teamName, teamNameMap);
    
    const existing = teamsMap.get(teamSlug);
    if (existing) {
      // Update with KenPom data
      existing.rank = parseNum(row.rank) || existing.rank;
      existing.adjEM = parseNum(row.adj_em) || existing.adjEM;
      existing.adjO = parseNum(row.adj_o) || existing.adjO;
      existing.adjD = parseNum(row.adj_d) || existing.adjD;
      existing.adjTempo = parseNum(row.adj_tempo) || existing.adjTempo;
      existing.luck = parseNum(row.luck);
      existing.sos_adjEM = parseNum(row.sos_adj_em);
      existing.ncsos_adjEM = parseNum(row.ncsos_adj_em);
      existing.sources.kenpom = true;
    } else {
      // Create new entry from KenPom
      const team: TeamSeason = {
        teamId: teamSlug,
        teamName: teamNameMap[teamName]?.display || teamName,
        teamNameAlt: teamNameMap[teamName]?.aliases || [teamName],
        conference: row.conference || '',
        logoUrl: getLogoPath(teamSlug),
        season: '2025-26',
        lastUpdated: row.date || new Date().toISOString().split('T')[0],
        games: 0,
        record: '',
        rank: parseNum(row.rank) || 999,
        adjEM: parseNum(row.adj_em) || 0,
        adjO: parseNum(row.adj_o) || 0,
        adjD: parseNum(row.adj_d) || 0,
        adjTempo: parseNum(row.adj_tempo) || 0,
        eFG: 0, tov: 0, orb: 0, ftr: 0,
        eFG_d: 0, tov_d: 0, drb: 0, ftr_d: 0,
        eFG_margin: 0, tov_edge: 0, reb_edge: 0, ftr_margin: 0,
        fg2_pct: null, fg2_pct_d: null,
        fg3_pct: null, fg3_pct_d: null,
        fg3_rate: null, fg3_rate_d: null,
        wab: null, sor: null,
        luck: parseNum(row.luck),
        sos_adjEM: parseNum(row.sos_adj_em),
        ncsos_adjEM: parseNum(row.ncsos_adj_em),
        barthag: null,
        sources: { kenpom: true, torvik: false, cbbAnalytics: false },
      };
      teamsMap.set(teamSlug, team);
    }
  }
  
  // Merge CBB Analytics data (supplemental)
  for (const row of cbbAnalyticsData) {
    const teamName = row['Team Name'];
    if (!teamName) continue;
    
    const teamSlug = normalizeTeamName(teamName, teamNameMap);
    const existing = teamsMap.get(teamSlug);
    
    if (existing) {
      existing.sources.cbbAnalytics = true;
      // CBB Analytics has adjusted metrics but we prefer Torvik/KenPom
      // Only use if missing
      if (!existing.adjO && row.OrtgAdj) {
        existing.adjO = parseNum(row.OrtgAdj) || existing.adjO;
      }
      if (!existing.adjD && row.DRtgAdj) {
        existing.adjD = parseNum(row.DRtgAdj) || existing.adjD;
      }
    }
  }
  
  console.log(`  ✓ Merged ${teamsMap.size} unique teams\n`);
  
  // Convert to array and sort by rank
  const teams = Array.from(teamsMap.values()).sort((a, b) => a.rank - b.rank);
  
  // Generate metadata
  const metadata = {
    lastUpdated: new Date().toISOString(),
    season: '2025-26',
    teamCount: teams.length,
    sources: {
      kenpom: teams.filter(t => t.sources.kenpom).length,
      torvik: teams.filter(t => t.sources.torvik).length,
      cbbAnalytics: teams.filter(t => t.sources.cbbAnalytics).length,
    },
  };
  
  // Write output
  const outputDir = path.join(__dirname, '..', 'web', 'public', 'data');
  fs.mkdirSync(outputDir, { recursive: true });
  
  const outputPath = path.join(outputDir, 'teams.json');
  fs.writeFileSync(
    outputPath,
    JSON.stringify({ metadata, teams }, null, 2)
  );
  
  console.log('✅ Data pipeline complete!');
  console.log(`   Output: ${outputPath}`);
  console.log(`   Teams: ${teams.length}`);
  console.log(`   Size: ${(fs.statSync(outputPath).size / 1024).toFixed(1)} KB\n`);
  
  // Print sample
  console.log('📊 Sample (Top 5):');
  teams.slice(0, 5).forEach((t, i) => {
    console.log(`   ${i + 1}. ${t.teamName} (${t.conference}) - AdjEM: ${t.adjEM.toFixed(2)}`);
  });
}

// Run pipeline
try {
  buildData();
} catch (error) {
  console.error('❌ Pipeline failed:', error);
  process.exit(1);
}
