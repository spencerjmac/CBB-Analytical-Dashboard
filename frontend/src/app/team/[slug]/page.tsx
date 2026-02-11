'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import type { TeamProfile } from '@/types';

export default function TeamProfilePage() {
  const params = useParams();
  const slug = params.slug as string;
  
  const [profile, setProfile] = useState<TeamProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'four-factors' | 'splits' | 'resume'>('overview');
  
  useEffect(() => {
    loadProfile();
  }, [slug]);
  
  async function loadProfile() {
    try {
      setLoading(true);
      const data = await api.getTeamProfile(slug);
      setProfile(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load team profile');
    } finally {
      setLoading(false);
    }
  }
  
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-20">
        <div className="flex justify-center items-center">
          <div className="spinner w-12 h-12"></div>
        </div>
      </div>
    );
  }
  
  if (error || !profile || !profile.current_season_stats) {
    return (
      <div className="container mx-auto px-4 py-20">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p className="font-bold">Error</p>
          <p>{error || 'Team not found'}</p>
        </div>
      </div>
    );
  }
  
  const stats = profile.current_season_stats;
  
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-8 mb-6">
        <div className="flex items-start gap-6">
          {stats.team_logo && (
            <img
              src={stats.team_logo}
              alt={stats.team_name}
              className="w-24 h-24 object-contain"
              onError={(e) => {
                e.currentTarget.style.display = 'none';
              }}
            />
          )}
          
          <div className="flex-1">
            <h1 className="text-4xl font-bold mb-2">{stats.team_name}</h1>
            <p className="text-xl text-gray-600 mb-4">
              {stats.conference_name} • {stats.record}
            </p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatBox label="Rank" value={`#${stats.rank}`} />
              <StatBox label="AdjEM" value={stats.adj_em.toFixed(2)} />
              <StatBox label="AdjO" value={stats.adj_o.toFixed(1)} />
              <StatBox label="AdjD" value={stats.adj_d.toFixed(1)} />
            </div>
          </div>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="border-b border-gray-200">
          <div className="flex">
            <TabButton active={activeTab === 'overview'} onClick={() => setActiveTab('overview')}>
              Overview
            </TabButton>
            <TabButton active={activeTab === 'four-factors'} onClick={() => setActiveTab('four-factors')}>
              Four Factors
            </TabButton>
            <TabButton active={activeTab === 'splits'} onClick={() => setActiveTab('splits')}>
              Shooting Splits
            </TabButton>
            <TabButton active={activeTab === 'resume'} onClick={() => setActiveTab('resume')}>
              Resume
            </TabButton>
          </div>
        </div>
        
        <div className="p-6">
          {activeTab === 'overview' && <OverviewTab stats={stats} />}
          {activeTab === 'four-factors' && <FourFactorsTab stats={stats} />}
          {activeTab === 'splits' && <SplitsTab stats={stats} />}
          {activeTab === 'resume' && <ResumeTab stats={stats} />}
        </div>
      </div>
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <p className="text-sm text-gray-600">{label}</p>
      <p className="text-2xl font-bold mono">{value}</p>
    </div>
  );
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-3 font-medium transition-colors ${
        active
          ? 'border-b-2 border-primary text-primary'
          : 'text-gray-600 hover:text-gray-900'
      }`}
    >
      {children}
    </button>
  );
}

function OverviewTab({ stats }: { stats: any }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h3 className="text-lg font-bold mb-4">Efficiency Metrics</h3>
        <div className="space-y-2">
          <MetricRow label="Adjusted Efficiency Margin" value={stats.adj_em.toFixed(2)} />
          <MetricRow label="Adjusted Offense" value={stats.adj_o.toFixed(1)} />
          <MetricRow label="Adjusted Defense" value={stats.adj_d.toFixed(1)} />
          <MetricRow label="Adjusted Tempo" value={stats.adj_tempo.toFixed(1)} />
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-bold mb-4">National Ranks</h3>
        <div className="space-y-2">
          <MetricRow label="Overall Rank" value={`#${stats.rank}`} />
          <MetricRow label="AdjEM Rank" value={stats.rank_adj_em ? `#${stats.rank_adj_em}` : 'N/A'} />
          <MetricRow label="AdjO Rank" value={stats.rank_adj_o ? `#${stats.rank_adj_o}` : 'N/A'} />
          <MetricRow label="AdjD Rank" value={stats.rank_adj_d ? `#${stats.rank_adj_d}` : 'N/A'} />
        </div>
      </div>
    </div>
  );
}

function FourFactorsTab({ stats }: { stats: any }) {
  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div>
          <h3 className="text-lg font-bold mb-4 text-green">Offense</h3>
          <div className="space-y-2">
            <MetricRow label="eFG%" value={`${stats.efg_pct.toFixed(1)}%`} />
            <MetricRow label="TOV%" value={`${stats.tov_pct.toFixed(1)}%`} />
            <MetricRow label="ORB%" value={`${stats.orb_pct.toFixed(1)}%`} />
            <MetricRow label="FTR" value={stats.ftr.toFixed(1)} />
          </div>
        </div>
        
        <div>
          <h3 className="text-lg font-bold mb-4 text-red-600">Defense</h3>
          <div className="space-y-2">
            <MetricRow label="Opp eFG%" value={`${stats.efg_pct_d.toFixed(1)}%`} />
            <MetricRow label="Opp TOV%" value={`${stats.tov_pct_d.toFixed(1)}%`} />
            <MetricRow label="DRB%" value={`${stats.drb_pct.toFixed(1)}%`} />
            <MetricRow label="Opp FTR" value={stats.ftr_d.toFixed(1)} />
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-bold mb-4">Margins</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MarginBox label="eFG Margin" value={stats.efg_margin.toFixed(1)} />
          <MarginBox label="TOV Edge" value={stats.tov_edge.toFixed(1)} />
          <MarginBox label="Reb Edge" value={stats.reb_edge.toFixed(1)} />
          <MarginBox label="FTR Margin" value={stats.ftr_margin.toFixed(1)} />
        </div>
      </div>
    </div>
  );
}

function SplitsTab({ stats }: { stats: any }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div>
        <h3 className="text-lg font-bold mb-4 text-green">Offense</h3>
        <div className="space-y-2">
          <MetricRow label="2P%" value={stats.fg2_pct ? `${stats.fg2_pct.toFixed(1)}%` : 'N/A'} />
          <MetricRow label="3P%" value={stats.fg3_pct ? `${stats.fg3_pct.toFixed(1)}%` : 'N/A'} />
          <MetricRow label="3P Rate" value={stats.fg3_rate ? `${stats.fg3_rate.toFixed(1)}%` : 'N/A'} />
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-bold mb-4 text-red-600">Defense</h3>
        <div className="space-y-2">
          <MetricRow label="Opp 2P%" value={stats.fg2_pct_d ? `${stats.fg2_pct_d.toFixed(1)}%` : 'N/A'} />
          <MetricRow label="Opp 3P%" value={stats.fg3_pct_d ? `${stats.fg3_pct_d.toFixed(1)}%` : 'N/A'} />
          <MetricRow label="Opp 3P Rate" value={stats.fg3_rate_d ? `${stats.fg3_rate_d.toFixed(1)}%` : 'N/A'} />
        </div>
      </div>
    </div>
  );
}

function ResumeTab({ stats }: { stats: any }) {
  return (
    <div className="space-y-2">
      <MetricRow label="Wins Above Bubble (WAB)" value={stats.wab !== null ? stats.wab.toFixed(2) : 'N/A'} />
      <MetricRow label="Strength of Record (SOR)" value={stats.sor !== null ? stats.sor.toFixed(2) : 'N/A'} />
      <MetricRow label="Barthag" value={stats.barthag !== null ? stats.barthag.toFixed(3) : 'N/A'} />
      <MetricRow label="Luck" value={stats.luck !== null ? stats.luck.toFixed(3) : 'N/A'} />
      <MetricRow label="SOS (AdjEM)" value={stats.sos_adj_em !== null ? stats.sos_adj_em.toFixed(2) : 'N/A'} />
      <MetricRow label="Non-Conf SOS" value={stats.ncsos_adj_em !== null ? stats.ncsos_adj_em.toFixed(2) : 'N/A'} />
    </div>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-100">
      <span className="text-gray-700">{label}</span>
      <span className="mono font-semibold">{value}</span>
    </div>
  );
}

function MarginBox({ label, value }: { label: string; value: string }) {
  const numValue = parseFloat(value);
  const color = numValue > 0 ? 'text-green' : numValue < 0 ? 'text-red-600' : 'text-gray-600';
  
  return (
    <div className="bg-gray-50 p-4 rounded-lg text-center">
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <p className={`text-2xl font-bold mono ${color}`}>
        {numValue > 0 ? '+' : ''}{value}
      </p>
    </div>
  );
}
