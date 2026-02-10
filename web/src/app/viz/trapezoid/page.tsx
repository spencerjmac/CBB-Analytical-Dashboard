import { Metadata } from 'next';
import { getAllTeams } from '@/lib/data';
import TrapezoidChart from '@/components/TrapezoidChart';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Trapezoid of Excellence | CBB Analytics',
  description: 'Interactive visualization showing championship-caliber teams by efficiency margin and tempo.',
};

export default function TrapezoidPage() {
  const teams = getAllTeams();
  
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Trapezoid of Excellence</h1>
        <p className="text-text-muted">
          Championship-caliber teams identified by their efficiency margin and tempo profile.
        </p>
      </div>
      
      {/* Chart */}
      <div className="bg-ui-card border border-ui-border rounded-lg p-6 mb-8">
        <TrapezoidChart teams={teams} />
      </div>
      
      {/* More Visualizations */}
      <div className="grid md:grid-cols-3 gap-6">
        <Link 
          href="/viz/landscape"
          className="p-6 bg-ui-surface border border-ui-border rounded-lg hover:border-brand-orange transition-colors text-center"
        >
          <div className="text-4xl mb-3">🗺️</div>
          <h3 className="font-bold text-lg mb-2">Efficiency Landscape</h3>
          <p className="text-text-muted text-sm">
            Offensive vs Defensive efficiency with contour overlay
          </p>
        </Link>
        
        <Link 
          href="/viz/kill-shot"
          className="p-6 bg-ui-surface border border-ui-border rounded-lg hover:border-brand-orange transition-colors text-center"
        >
          <div className="text-4xl mb-3">🎯</div>
          <h3 className="font-bold text-lg mb-2">Kill Shot Analysis</h3>
          <p className="text-text-muted text-sm">
            Game-changing possessions and momentum metrics
          </p>
        </Link>
        
        <Link 
          href="/viz/crystal-ball"
          className="p-6 bg-ui-surface border border-ui-border rounded-lg hover:border-brand-orange transition-colors text-center"
        >
          <div className="text-4xl mb-3">🔮</div>
          <h3 className="font-bold text-lg mb-2">Crystal Ball</h3>
          <p className="text-text-muted text-sm">
            Championship profile and predictive analysis
          </p>
        </Link>
      </div>
    </div>
  );
}
