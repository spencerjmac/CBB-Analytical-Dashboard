'use client';

import { useState } from 'react';
import { TeamSeason } from '@/types';
import clsx from 'clsx';

interface TeamPageTabsProps {
  team: TeamSeason;
}

type TabId = 'overview' | 'four-factors' | 'offense-defense' | 'resume' | 'charts';

export default function TeamPageTabs({ team }: TeamPageTabsProps) {
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  
  const tabs = [
    { id: 'overview' as TabId, label: 'Overview' },
    { id: 'four-factors' as TabId, label: 'Four Factors' },
    { id: 'offense-defense' as TabId, label: 'Off/Def' },
    { id: 'resume' as TabId, label: 'Resume' },
    { id: 'charts' as TabId, label: 'Charts' },
  ];
  
  return (
    <div>
      {/* Tab Navigation */}
      <div className="border-b border-ui-border mb-6">
        <div className="flex space-x-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'px-6 py-3 font-medium transition-colors border-b-2',
                activeTab === tab.id
                  ? 'border-brand-orange text-brand-orange'
                  : 'border-transparent text-text-muted hover:text-text-primary'
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      
      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && <OverviewTab team={team} />}
        {activeTab === 'four-factors' && <FourFactorsTab team={team} />}
        {activeTab === 'offense-defense' && <OffenseDefenseTab team={team} />}
        {activeTab === 'resume' && <ResumeTab team={team} />}
        {activeTab === 'charts' && <ChartsTab team={team} />}
      </div>
    </div>
  );
}

// Overview Tab
function OverviewTab({ team }: { team: TeamSeason }) {
  const stats = [
    { label: 'Adjusted Efficiency Margin', value: team.adjEM.toFixed(2), rank: team.rank, color: 'text-brand-orange' },
    { label: 'Adjusted Offensive Efficiency', value: team.adjO.toFixed(1), color: 'text-success' },
    { label: 'Adjusted Defensive Efficiency', value: team.adjD.toFixed(1), color: 'text-secondary' },
    { label: 'Adjusted Tempo', value: team.adjTempo.toFixed(1), color: 'text-text-primary' },
  ];
  
  return (
    <div className="space-y-8">
      {/* Core Metrics */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Core Metrics</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {stats.map((stat, i) => (
            <div key={i} className="p-6 bg-ui-surface border border-ui-border rounded-lg">
              <div className="text-text-muted text-sm mb-2">{stat.label}</div>
              <div className={clsx('text-4xl font-bold font-mono', stat.color)}>
                {stat.value}
              </div>
              {stat.rank && (
                <div className="text-text-muted text-sm mt-2">
                  National Rank: #{stat.rank}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      
      {/* Four Factors Overview */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Four Factors Snapshot</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="eFG%" value={(team.eFG * 100).toFixed(1) + '%'} />
          <StatCard label="TOV%" value={(team.tov * 100).toFixed(1) + '%'} />
          <StatCard label="ORB%" value={(team.orb * 100).toFixed(1) + '%'} />
          <StatCard label="FTR" value={(team.ftr * 100).toFixed(1) + '%'} />
        </div>
      </div>
    </div>
  );
}

// Four Factors Tab
function FourFactorsTab({ team }: { team: TeamSeason }) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Four Factors Breakdown</h2>
        <p className="text-text-muted mb-6">
          The Four Factors of Basketball Success, showing both offensive and defensive performance 
          plus the margin/edge for each factor.
        </p>
        
        <div className="space-y-6">
          {/* eFG% */}
          <FactorCard
            name="Effective Field Goal %"
            offense={(team.eFG * 100).toFixed(1) + '%'}
            defense={(team.eFG_d * 100).toFixed(1) + '%'}
            margin={(team.eFG_margin * 100).toFixed(1) + '%'}
            marginPositive={team.eFG_margin > 0}
            description="Field goal percentage adjusted for 3-pointers being worth more"
          />
          
          {/* TOV% */}
          <FactorCard
            name="Turnover Rate"
            offense={(team.tov * 100).toFixed(1) + '%'}
            defense={(team.tov_d * 100).toFixed(1) + '%'}
            margin={(team.tov_edge * 100).toFixed(1) + '%'}
            marginPositive={team.tov_edge > 0}
            description="Turnovers per 100 plays (forcing > committing is good)"
          />
          
          {/* ORB% */}
          <FactorCard
            name="Rebounding Rate"
            offense={(team.orb * 100).toFixed(1) + '%'}
            defense={(team.drb * 100).toFixed(1) + '%'}
            margin={(team.reb_edge * 100).toFixed(1) + '%'}
            marginPositive={team.reb_edge > 0}
            description="Offensive rebound % vs Defensive rebound %"
          />
          
          {/* FTR */}
          <FactorCard
            name="Free Throw Rate"
            offense={(team.ftr * 100).toFixed(1) + '%'}
            defense={(team.ftr_d * 100).toFixed(1) + '%'}
            margin={(team.ftr_margin * 100).toFixed(1) + '%'}
            marginPositive={team.ftr_margin > 0}
            description="Free throw attempts per field goal attempt"
          />
        </div>
      </div>
    </div>
  );
}

// Offense/Defense Tab
function OffenseDefenseTab({ team }: { team: TeamSeason }) {
  return (
    <div className="space-y-8">
      <div className="grid md:grid-cols-2 gap-6">
        {/* Offense */}
        <div>
          <h2 className="text-2xl font-bold mb-4 text-success">Offensive Profile</h2>
          <div className="space-y-4">
            <StatCard label="Adj Offensive Efficiency" value={team.adjO.toFixed(1)} />
            {team.fg2_pct !== null && (
              <StatCard label="2P%" value={(team.fg2_pct * 100).toFixed(1) + '%'} />
            )}
            {team.fg3_pct !== null && (
              <StatCard label="3P%" value={(team.fg3_pct * 100).toFixed(1) + '%'} />
            )}
            {team.fg3_rate !== null && (
              <StatCard label="3P Rate" value={(team.fg3_rate * 100).toFixed(1) + '%'} />
            )}
            <StatCard label="eFG%" value={(team.eFG * 100).toFixed(1) + '%'} />
            <StatCard label="TOV%" value={(team.tov * 100).toFixed(1) + '%'} />
            <StatCard label="ORB%" value={(team.orb * 100).toFixed(1) + '%'} />
            <StatCard label="FTR" value={(team.ftr * 100).toFixed(1) + '%'} />
          </div>
        </div>
        
        {/* Defense */}
        <div>
          <h2 className="text-2xl font-bold mb-4 text-secondary">Defensive Profile</h2>
          <div className="space-y-4">
            <StatCard label="Adj Defensive Efficiency" value={team.adjD.toFixed(1)} />
            {team.fg2_pct_d !== null && (
              <StatCard label="Opp 2P%" value={(team.fg2_pct_d * 100).toFixed(1) + '%'} />
            )}
            {team.fg3_pct_d !== null && (
              <StatCard label="Opp 3P%" value={(team.fg3_pct_d * 100).toFixed(1) + '%'} />
            )}
            {team.fg3_rate_d !== null && (
              <StatCard label="Opp 3P Rate" value={(team.fg3_rate_d * 100).toFixed(1) + '%'} />
            )}
            <StatCard label="Opp eFG%" value={(team.eFG_d * 100).toFixed(1) + '%'} />
            <StatCard label="Forced TOV%" value={(team.tov_d * 100).toFixed(1) + '%'} />
            <StatCard label="DRB%" value={(team.drb * 100).toFixed(1) + '%'} />
            <StatCard label="Opp FTR" value={(team.ftr_d * 100).toFixed(1) + '%'} />
          </div>
        </div>
      </div>
    </div>
  );
}

// Resume Tab
function ResumeTab({ team }: { team: TeamSeason }) {
  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold mb-4">Team Resume</h2>
      
      <div className="grid md:grid-cols-2 gap-6">
        {team.wab !== null && (
          <div className="p-6 bg-ui-surface border border-ui-border rounded-lg">
            <div className="text-text-muted text-sm mb-2">Wins Above Bubble</div>
            <div className="text-4xl font-bold font-mono text-brand-orange">
              {team.wab > 0 ? '+' : ''}{team.wab.toFixed(2)}
            </div>
            <p className="text-text-muted text-sm mt-2">
              Expected wins above a bubble team with the same schedule
            </p>
          </div>
        )}
        
        {team.barthag !== null && (
          <div className="p-6 bg-ui-surface border border-ui-border rounded-lg">
            <div className="text-text-muted text-sm mb-2">Barthag Rating</div>
            <div className="text-4xl font-bold font-mono text-brand-orange">
              {team.barthag.toFixed(4)}
            </div>
            <p className="text-text-muted text-sm mt-2">
              Power rating (win probability vs average team on neutral court)
            </p>
          </div>
        )}
        
        {team.sos_adjEM !== null && (
          <div className="p-6 bg-ui-surface border border-ui-border rounded-lg">
            <div className="text-text-muted text-sm mb-2">Strength of Schedule (AdjEM)</div>
            <div className="text-4xl font-bold font-mono">
              {team.sos_adjEM.toFixed(2)}
            </div>
            <p className="text-text-muted text-sm mt-2">
              Average opponent efficiency margin
            </p>
          </div>
        )}
        
        {team.luck !== null && (
          <div className="p-6 bg-ui-surface border border-ui-border rounded-lg">
            <div className="text-text-muted text-sm mb-2">Luck Rating</div>
            <div className="text-4xl font-bold font-mono">
              {team.luck > 0 ? '+' : ''}{team.luck.toFixed(3)}
            </div>
            <p className="text-text-muted text-sm mt-2">
              How "lucky" a team has been in close games
            </p>
          </div>
        )}
      </div>
      
      {!team.wab && !team.sos_adjEM && !team.luck && (
        <div className="p-6 bg-ui-surface border border-ui-border rounded-lg text-center text-text-muted">
          Resume metrics not available for this team.
        </div>
      )}
    </div>
  );
}

// Charts Tab (placeholder)
function ChartsTab({ team }: { team: TeamSeason }) {
  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold mb-4">Visualizations</h2>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="p-12 bg-ui-surface border border-ui-border rounded-lg text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="font-bold text-lg mb-2">Trapezoid of Excellence</h3>
          <p className="text-text-muted text-sm">Coming soon</p>
        </div>
        <div className="p-12 bg-ui-surface border border-ui-border rounded-lg text-center">
          <div className="text-6xl mb-4">🔮</div>
          <h3 className="font-bold text-lg mb-2">Crystal Ball Analysis</h3>
          <p className="text-text-muted text-sm">Coming soon</p>
        </div>
      </div>
    </div>
  );
}

// Helper Components
function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="p-4 bg-ui-card border border-ui-border rounded-lg">
      <div className="text-text-muted text-xs mb-1">{label}</div>
      <div className="text-2xl font-bold font-mono">{value}</div>
    </div>
  );
}

function FactorCard({
  name,
  offense,
  defense,
  margin,
  marginPositive,
  description,
}: {
  name: string;
  offense: string;
  defense: string;
  margin: string;
  marginPositive: boolean;
  description: string;
}) {
  return (
    <div className="p-6 bg-ui-card border border-ui-border rounded-lg">
      <h3 className="font-bold text-lg mb-2">{name}</h3>
      <p className="text-text-muted text-sm mb-4">{description}</p>
      
      <div className="grid grid-cols-3 gap-4">
        <div>
          <div className="text-text-muted text-xs mb-1">Offense</div>
          <div className="text-2xl font-mono font-bold text-success">{offense}</div>
        </div>
        <div>
          <div className="text-text-muted text-xs mb-1">Defense</div>
          <div className="text-2xl font-mono font-bold text-secondary">{defense}</div>
        </div>
        <div>
          <div className="text-text-muted text-xs mb-1">Margin</div>
          <div className={clsx(
            'text-2xl font-mono font-bold',
            marginPositive ? 'text-success' : 'text-warning'
          )}>
            {marginPositive && '+'}{margin}
          </div>
        </div>
      </div>
    </div>
  );
}
