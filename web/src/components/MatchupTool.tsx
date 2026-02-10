'use client';

import { useState, useMemo } from 'react';
import { TeamSeason } from '@/types';

interface MatchupToolProps {
  teams: TeamSeason[];
}

export default function MatchupTool({ teams }: MatchupToolProps) {
  const [teamA, setTeamA] = useState<TeamSeason | null>(null);
  const [teamB, setTeamB] = useState<TeamSeason | null>(null);
  const [location, setLocation] = useState<'neutral' | 'teamA' | 'teamB'>('neutral');
  const [searchA, setSearchA] = useState('');
  const [searchB, setSearchB] = useState('');
  
  // Filter teams for search
  const filteredTeamsA = useMemo(() => {
    if (!searchA) return [];
    const query = searchA.toLowerCase();
    return teams
      .filter(t => t.teamName.toLowerCase().includes(query))
      .slice(0, 10);
  }, [searchA, teams]);
  
  const filteredTeamsB = useMemo(() => {
    if (!searchB) return [];
    const query = searchB.toLowerCase();
    return teams
      .filter(t => t.teamName.toLowerCase().includes(query))
      .slice(0, 10);
  }, [searchB, teams]);
  
  // Calculate matchup metrics
  const matchup = useMemo(() => {
    if (!teamA || !teamB) return null;
    
    // Home court advantage adjustment (roughly +3 points in AdjEM)
    const homeAdj = location === 'teamA' ? 3 : location === 'teamB' ? -3 : 0;
    
    const adjEM_diff = teamA.adjEM - teamB.adjEM + homeAdj;
    const tempo_diff = teamA.adjTempo - teamB.adjTempo;
    
    // Four Factor edges
    const eFG_edge = teamA.eFG_margin - teamB.eFG_margin;
    const tov_edge = teamA.tov_edge - teamB.tov_edge;
    const reb_edge = teamA.reb_edge - teamB.reb_edge;
    const ftr_edge = teamA.ftr_margin - teamB.ftr_margin;
    
    // Projected score (simplified model)
    const avgTempo = (teamA.adjTempo + teamB.adjTempo) / 2;
    const projectedA = teamA.adjO + teamB.adjD - 100;
    const projectedB = teamB.adjO + teamA.adjD - 100;
    
    return {
      adjEM_diff,
      tempo_diff,
      eFG_edge,
      tov_edge,
      reb_edge,
      ftr_edge,
      avgTempo,
      projectedA,
      projectedB,
      projectedMargin: projectedA - projectedB + homeAdj,
    };
  }, [teamA, teamB, location]);
  
  return (
    <div className="space-y-8">
      {/* Team Selectors */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Team A */}
        <div>
          <label className="block text-sm font-medium text-text-muted mb-2">
            Team A
          </label>
          <div className="relative">
            <input
              type="text"
              value={teamA?.teamName || searchA}
              onChange={(e) => {
                setSearchA(e.target.value);
                setTeamA(null);
              }}
              placeholder="Search for a team..."
              className="w-full px-4 py-3 border border-ui-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-orange"
            />
            
            {/* Dropdown */}
            {searchA && !teamA && filteredTeamsA.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-ui-card border border-ui-border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                {filteredTeamsA.map((team) => (
                  <button
                    key={team.teamId}
                    onClick={() => {
                      setTeamA(team);
                      setSearchA('');
                    }}
                    className="w-full px-4 py-2 text-left hover:bg-ui-surface flex items-center gap-2"
                  >
                    <img src={team.logoUrl} alt="" className="w-6 h-6" />
                    <span>{team.teamName}</span>
                    <span className="text-text-muted text-sm ml-auto">#{team.rank}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
          
          {/* Selected Team Card */}
          {teamA && (
            <div className="mt-4 p-4 bg-primary/10 border-2 border-primary rounded-lg">
              <div className="flex items-center gap-3 mb-3">
                <img src={teamA.logoUrl} alt="" className="w-12 h-12" />
                <div>
                  <div className="font-bold text-lg">{teamA.teamName}</div>
                  <div className="text-text-muted text-sm">
                    #{teamA.rank} • {teamA.conference}
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2 text-sm">
                <div>
                  <div className="text-text-muted">AdjEM</div>
                  <div className="font-mono font-bold">{teamA.adjEM.toFixed(1)}</div>
                </div>
                <div>
                  <div className="text-text-muted">AdjO</div>
                  <div className="font-mono font-bold">{teamA.adjO.toFixed(1)}</div>
                </div>
                <div>
                  <div className="text-text-muted">AdjD</div>
                  <div className="font-mono font-bold">{teamA.adjD.toFixed(1)}</div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Team B */}
        <div>
          <label className="block text-sm font-medium text-text-muted mb-2">
            Team B
          </label>
          <div className="relative">
            <input
              type="text"
              value={teamB?.teamName || searchB}
              onChange={(e) => {
                setSearchB(e.target.value);
                setTeamB(null);
              }}
              placeholder="Search for a team..."
              className="w-full px-4 py-3 border border-ui-border rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary"
            />
            
            {/* Dropdown */}
            {searchB && !teamB && filteredTeamsB.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-ui-card border border-ui-border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                {filteredTeamsB.map((team) => (
                  <button
                    key={team.teamId}
                    onClick={() => {
                      setTeamB(team);
                      setSearchB('');
                    }}
                    className="w-full px-4 py-2 text-left hover:bg-ui-surface flex items-center gap-2"
                  >
                    <img src={team.logoUrl} alt="" className="w-6 h-6" />
                    <span>{team.teamName}</span>
                    <span className="text-text-muted text-sm ml-auto">#{team.rank}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
          
          {/* Selected Team Card */}
          {teamB && (
            <div className="mt-4 p-4 bg-secondary/10 border-2 border-secondary rounded-lg">
              <div className="flex items-center gap-3 mb-3">
                <img src={teamB.logoUrl} alt="" className="w-12 h-12" />
                <div>
                  <div className="font-bold text-lg">{teamB.teamName}</div>
                  <div className="text-text-muted text-sm">
                    #{teamB.rank} • {teamB.conference}
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2 text-sm">
                <div>
                  <div className="text-text-muted">AdjEM</div>
                  <div className="font-mono font-bold">{teamB.adjEM.toFixed(1)}</div>
                </div>
                <div>
                  <div className="text-text-muted">AdjO</div>
                  <div className="font-mono font-bold">{teamB.adjO.toFixed(1)}</div>
                </div>
                <div>
                  <div className="text-text-muted">AdjD</div>
                  <div className="font-mono font-bold">{teamB.adjD.toFixed(1)}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Location Toggle */}
      {teamA && teamB && (
        <div className="flex justify-center">
          <div className="inline-flex border border-ui-border rounded-lg p-1 bg-ui-surface">
            <button
              onClick={() => setLocation('teamA')}
              className={`px-6 py-2 rounded font-medium transition-colors ${
                location === 'teamA'
                  ? 'bg-primary text-white'
                  : 'text-text-muted hover:text-text-primary'
              }`}
            >
              @ {teamA.teamName}
            </button>
            <button
              onClick={() => setLocation('neutral')}
              className={`px-6 py-2 rounded font-medium transition-colors ${
                location === 'neutral'
                  ? 'bg-neutral text-white'
                  : 'text-text-muted hover:text-text-primary'
              }`}
            >
              Neutral
            </button>
            <button
              onClick={() => setLocation('teamB')}
              className={`px-6 py-2 rounded font-medium transition-colors ${
                location === 'teamB'
                  ? 'bg-secondary text-white'
                  : 'text-text-muted hover:text-text-primary'
              }`}
            >
              @ {teamB.teamName}
            </button>
          </div>
        </div>
      )}
      
      {/* Matchup Analysis */}
      {matchup && teamA && teamB && (
        <div className="space-y-6">
          {/* Projected Score */}
          <div className="bg-ui-card border border-ui-border rounded-lg p-8 text-center">
            <h2 className="text-2xl font-bold mb-6">Projected Outcome</h2>
            <div className="flex items-center justify-center gap-12">
              <div>
                <div className="text-sm text-text-muted mb-2">{teamA.teamName}</div>
                <div className="text-5xl font-bold font-mono text-primary">
                  {matchup.projectedA.toFixed(0)}
                </div>
              </div>
              <div className="text-2xl text-text-muted">vs</div>
              <div>
                <div className="text-sm text-text-muted mb-2">{teamB.teamName}</div>
                <div className="text-5xl font-bold font-mono text-secondary">
                  {matchup.projectedB.toFixed(0)}
                </div>
              </div>
            </div>
            <div className="mt-6 text-text-muted">
              Projected at {matchup.avgTempo.toFixed(1)} tempo
              {location !== 'neutral' && ' (includes home court advantage)'}
            </div>
          </div>
          
          {/* Four Factor Edges */}
          <div>
            <h2 className="text-2xl font-bold mb-4">Four Factor Matchup Edges</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <EdgeCard
                label="eFG% Margin Edge"
                value={(matchup.eFG_edge * 100).toFixed(1) + '%'}
                favorsA={matchup.eFG_edge > 0}
                teamA={teamA.teamName}
                teamB={teamB.teamName}
              />
              <EdgeCard
                label="Turnover Edge"
                value={(matchup.tov_edge * 100).toFixed(1) + '%'}
                favorsA={matchup.tov_edge > 0}
                teamA={teamA.teamName}
                teamB={teamB.teamName}
              />
              <EdgeCard
                label="Rebounding Edge"
                value={(matchup.reb_edge * 100).toFixed(1) + '%'}
                favorsA={matchup.reb_edge > 0}
                teamA={teamA.teamName}
                teamB={teamB.teamName}
              />
              <EdgeCard
                label="FTR Margin Edge"
                value={(matchup.ftr_edge * 100).toFixed(1) + '%'}
                favorsA={matchup.ftr_edge > 0}
                teamA={teamA.teamName}
                teamB={teamB.teamName}
              />
            </div>
          </div>
          
          {/* Other Metrics */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-6 bg-ui-surface border border-ui-border rounded-lg">
              <div className="text-text-muted text-sm mb-2">Efficiency Margin Diff</div>
              <div className="text-3xl font-bold font-mono">
                {matchup.adjEM_diff > 0 ? '+' : ''}{matchup.adjEM_diff.toFixed(2)}
              </div>
              <div className="text-sm text-text-muted mt-2">
                Favors {matchup.adjEM_diff > 0 ? teamA.teamName : teamB.teamName}
              </div>
            </div>
            
            <div className="p-6 bg-ui-surface border border-ui-border rounded-lg">
              <div className="text-text-muted text-sm mb-2">Tempo Difference</div>
              <div className="text-3xl font-bold font-mono">
                {matchup.tempo_diff > 0 ? '+' : ''}{matchup.tempo_diff.toFixed(1)}
              </div>
              <div className="text-sm text-text-muted mt-2">
                {Math.abs(matchup.tempo_diff) < 2 ? 'Similar pace' : 
                  matchup.tempo_diff > 0 ? `${teamA.teamName} faster` : `${teamB.teamName} faster`}
              </div>
            </div>
          </div>
          
          {/* Win Probability Placeholder */}
          <div className="p-6 bg-ui-surface border-2 border-dashed border-ui-border rounded-lg text-center">
            <div className="text-text-muted">
              <strong>Win Probability Model:</strong> Coming soon
            </div>
          </div>
        </div>
      )}
      
      {/* Empty State */}
      {(!teamA || !teamB) && (
        <div className="text-center py-16 text-text-muted">
          <div className="text-6xl mb-4">⚔️</div>
          <p className="text-lg">Select two teams to see matchup analysis</p>
        </div>
      )}
    </div>
  );
}

function EdgeCard({
  label,
  value,
  favorsA,
  teamA,
  teamB,
}: {
  label: string;
  value: string;
  favorsA: boolean;
  teamA: string;
  teamB: string;
}) {
  return (
    <div className="p-4 bg-ui-card border border-ui-border rounded-lg">
      <div className="text-text-muted text-sm mb-2">{label}</div>
      <div className={`text-2xl font-bold font-mono ${
        favorsA ? 'text-primary' : 'text-secondary'
      }`}>
        {value}
      </div>
      <div className="text-sm text-text-muted mt-1">
        Edge: {favorsA ? teamA : teamB}
      </div>
    </div>
  );
}
