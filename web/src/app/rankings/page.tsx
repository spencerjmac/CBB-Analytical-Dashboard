import { Metadata } from 'next';
import { getAllTeams, getMetadata } from '@/lib/data';
import RankingsTable from '@/components/RankingsTable';

export const metadata: Metadata = {
  title: 'Rankings | CBB Analytics',
  description: 'Complete NCAA Division I men\'s basketball rankings with adjusted efficiency metrics, four factors, and advanced statistics.',
};

export default function RankingsPage() {
  const teams = getAllTeams();
  const meta = getMetadata();
  
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Team Rankings</h1>
        <p className="text-text-muted">
          Complete rankings for {meta.teamCount} NCAA Division I teams. 
          <span className="ml-2 text-sm">
            Last updated: {new Date(meta.lastUpdated).toLocaleDateString()}
          </span>
        </p>
      </div>
      
      {/* Rankings Table */}
      <RankingsTable data={teams} />
      
      {/* Legend */}
      <div className="mt-8 p-6 bg-ui-surface border border-ui-border rounded-lg">
        <h2 className="font-bold text-lg mb-4">Metric Definitions</h2>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <strong className="text-brand-orange">AdjEM:</strong> Adjusted Efficiency Margin 
            (AdjO - AdjD), the predicted point margin vs average team on neutral court
          </div>
          <div>
            <strong className="text-success">AdjO:</strong> Adjusted Offensive Efficiency, 
            points scored per 100 possessions vs average D1 defense
          </div>
          <div>
            <strong className="text-secondary">AdjD:</strong> Adjusted Defensive Efficiency, 
            points allowed per 100 possessions vs average D1 offense
          </div>
          <div>
            <strong>Tempo:</strong> Adjusted possessions per 40 minutes
          </div>
          <div>
            <strong>eFG%:</strong> Effective Field Goal Percentage 
            (FG% adjusted for 3-pointers being worth more)
          </div>
          <div>
            <strong>TOV%:</strong> Turnover percentage 
            (turnovers per 100 plays)
          </div>
          <div>
            <strong>ORB%:</strong> Offensive Rebound percentage 
            (% of available offensive rebounds secured)
          </div>
          <div>
            <strong>FTR:</strong> Free Throw Rate 
            (free throws attempted per field goal attempt)
          </div>
        </div>
      </div>
    </div>
  );
}
