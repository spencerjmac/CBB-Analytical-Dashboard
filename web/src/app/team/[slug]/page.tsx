import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getTeamBySlug, getAllTeams } from '@/lib/data';
import TeamPageTabs from '@/components/TeamPageTabs';
import Link from 'next/link';

interface TeamPageProps {
  params: {
    slug: string;
  };
}

export async function generateStaticParams() {
  const teams = getAllTeams();
  return teams.map((team) => ({
    slug: team.teamId,
  }));
}

export async function generateMetadata({ params }: TeamPageProps): Promise<Metadata> {
  const team = getTeamBySlug(params.slug);
  
  if (!team) {
    return {
      title: 'Team Not Found | CBB Analytics',
    };
  }
  
  return {
    title: `${team.teamName} - ${team.season} | CBB Analytics`,
    description: `Advanced analytics and statistics for ${team.teamName} ${team.season} season. Efficiency metrics, four factors, and predictive analysis.`,
  };
}

export default function TeamPage({ params }: TeamPageProps) {
  const team = getTeamBySlug(params.slug);
  
  if (!team) {
    notFound();
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Back Link */}
      <Link 
        href="/rankings" 
        className="inline-flex items-center text-brand-orange hover:text-brand-orange-hover mb-6"
      >
        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Rankings
      </Link>
      
      {/* Team Header */}
      <div className="bg-ui-card border border-ui-border rounded-lg p-8 mb-8">
        <div className="flex items-start gap-6">
          {/* Logo */}
          <img 
            src={team.logoUrl}
            alt={team.teamName}
            className="w-24 h-24 object-contain"
            onError={(e) => {
              (e.target as HTMLImageElement).src = '/logos/default.png';
            }}
          />
          
          {/* Info */}
          <div className="flex-1">
            <div className="flex items-baseline gap-4 mb-2">
              <h1 className="text-4xl font-bold">{team.teamName}</h1>
              <span className="text-xl text-text-muted">{team.conference}</span>
            </div>
            
            <div className="flex items-center gap-6 text-lg">
              {team.record && (
                <div>
                  <span className="text-text-muted">Record:</span>{' '}
                  <span className="font-mono font-bold">{team.record}</span>
                </div>
              )}
              <div>
                <span className="text-text-muted">Rank:</span>{' '}
                <span className="font-mono font-bold text-brand-orange">#{team.rank}</span>
              </div>
              <div>
                <span className="text-text-muted">AdjEM:</span>{' '}
                <span className="font-mono font-bold text-brand-orange">
                  {team.adjEM.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Tabs */}
      <TeamPageTabs team={team} />
    </div>
  );
}
