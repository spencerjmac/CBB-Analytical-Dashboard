import { Metadata } from 'next';
import { getAllTeams } from '@/lib/data';
import MatchupTool from '@/components/MatchupTool';

export const metadata: Metadata = {
  title: 'Matchup Tool | CBB Analytics',
  description: 'Compare any two NCAA Division I teams head-to-head with efficiency projections and four factor matchup edges.',
};

export default function MatchupPage() {
  const teams = getAllTeams();
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Matchup Tool</h1>
        <p className="text-text-muted">
          Compare any two teams head-to-head with efficiency projections and four factor analysis.
        </p>
      </div>
      
      <MatchupTool teams={teams} />
    </div>
  );
}
