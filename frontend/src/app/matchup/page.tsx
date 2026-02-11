'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import type { MatchupResult } from '@/types';

export default function MatchupPage() {
  const [teamA, setTeamA] = useState('');
  const [teamB, setTeamB] = useState('');
  const [site, setSite] = useState<'neutral' | 'home' | 'away'>('neutral');
  const [result, setResult] = useState<MatchupResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    if (!teamA || !teamB) {
      setError('Please enter both team names');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      const data = await api.getMatchup(
        teamA.toLowerCase().replace(/\s+/g, '-'),
        teamB.toLowerCase().replace(/\s+/g, '-'),
        site
      );
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load matchup');
      setResult(null);
    } finally {
      setLoading(false);
    }
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Matchup Tool</h1>
      
      {/* Input Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Team A
              </label>
              <input
                type="text"
                value={teamA}
                onChange={(e) => setTeamA(e.target.value)}
                placeholder="michigan"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Team B
              </label>
              <input
                type="text"
                value={teamB}
                onChange={(e) => setTeamB(e.target.value)}
                placeholder="duke"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Site
              </label>
              <select
                value={site}
                onChange={(e) => setSite(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary"
              >
                <option value="neutral">Neutral Court</option>
                <option value="home">Team A Home</option>
                <option value="away">Team B Home</option>
              </select>
            </div>
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full md:w-auto px-8 py-3 bg-primary text-white font-bold rounded-md hover:bg-primary-dark disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Compare Teams'}
          </button>
        </form>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-8">
          {error}
        </div>
      )}
      
      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Win Probability */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-6 text-center">Predicted Outcome</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="text-center">
                <p className="text-lg font-semibold mb-2">{result.teamA.team_name}</p>
                <p className="text-4xl font-bold text-blue">
                  {(result.matchup.win_probability_a * 100).toFixed(1)}%
                </p>
                <p className="text-sm text-gray-600 mt-1">Win Probability</p>
              </div>
              
              <div className="text-center flex items-center justify-center">
                <div>
                  <p className="text-3xl font-bold mono">
                    {result.matchup.predicted_margin > 0 ? '+' : ''}
                    {result.matchup.predicted_margin.toFixed(1)}
                  </p>
                  <p className="text-sm text-gray-600">Predicted Margin</p>
                </div>
              </div>
              
              <div className="text-center">
                <p className="text-lg font-semibold mb-2">{result.teamB.team_name}</p>
                <p className="text-4xl font-bold text-primary">
                  {(result.matchup.win_probability_b * 100).toFixed(1)}%
                </p>
                <p className="text-sm text-gray-600 mt-1">Win Probability</p>
              </div>
            </div>
            
            {/* Progress bar */}
            <div className="w-full h-8 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue transition-all"
                style={{ width: `${result.matchup.win_probability_a * 100}%` }}
              />
            </div>
          </div>
          
          {/* Key Edges */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-6">Key Edges</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <EdgeBar label="Efficiency" value={result.matchup.edges.efficiency} />
              <EdgeBar label="Offensive" value={result.matchup.edges.offensive} />
              <EdgeBar label="Defensive" value={result.matchup.edges.defensive} />
              <EdgeBar label="Tempo" value={result.matchup.edges.tempo} />
              <EdgeBar label="eFG%" value={result.matchup.edges.efg} />
              <EdgeBar label="Turnovers" value={result.matchup.edges.tov} />
              <EdgeBar label="Rebounding" value={result.matchup.edges.reb} />
              <EdgeBar label="Free Throws" value={result.matchup.edges.ftr} />
            </div>
          </div>
          
          {/* Team Stats Comparison */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-6">Team Stats</h2>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Metric</th>
                    <th className="text-center py-2">{result.teamA.team_name}</th>
                    <th className="text-center py-2">{result.teamB.team_name}</th>
                  </tr>
                </thead>
                <tbody>
                  <CompareRow label="Rank" a={`#${result.teamA.rank}`} b={`#${result.teamB.rank}`} />
                  <CompareRow label="Record" a={result.teamA.record} b={result.teamB.record} />
                  <CompareRow label="AdjEM" a={result.teamA.adj_em.toFixed(2)} b={result.teamB.adj_em.toFixed(2)} />
                  <CompareRow label="AdjO" a={result.teamA.adj_o.toFixed(1)} b={result.teamB.adj_o.toFixed(1)} />
                  <CompareRow label="AdjD" a={result.teamA.adj_d.toFixed(1)} b={result.teamB.adj_d.toFixed(1)} />
                  <CompareRow label="Tempo" a={result.teamA.adj_tempo.toFixed(1)} b={result.teamB.adj_tempo.toFixed(1)} />
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function EdgeBar({ label, value }: { label: string; value: number }) {
  const percentage = Math.min(Math.abs(value) / 20 * 100, 100);
  const color = value > 0 ? 'bg-blue' : 'bg-primary';
  
  return (
    <div>
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm font-medium">{label}</span>
        <span className="text-sm font-bold mono">
          {value > 0 ? '+' : ''}{value.toFixed(2)}
        </span>
      </div>
      <div className="w-full h-6 bg-gray-200 rounded overflow-hidden">
        <div
          className={`h-full ${color} transition-all`}
          style={{
            width: `${percentage}%`,
            marginLeft: value < 0 ? `${100 - percentage}%` : '0',
          }}
        />
      </div>
    </div>
  );
}

function CompareRow({ label, a, b }: { label: string; a: string; b: string }) {
  return (
    <tr className="border-b">
      <td className="py-2 text-gray-700">{label}</td>
      <td className="py-2 text-center mono font-semibold">{a}</td>
      <td className="py-2 text-center mono font-semibold">{b}</td>
    </tr>
  );
}
