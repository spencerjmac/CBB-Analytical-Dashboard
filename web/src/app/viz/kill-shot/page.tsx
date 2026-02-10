import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Kill Shot Analysis | CBB Analytics',
};

export default function KillShotPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-4">Kill Shot Analysis</h1>
      <p className="text-text-muted mb-8">Game-changing possessions and momentum metrics.</p>
      
      <div className="bg-ui-card border border-ui-border rounded-lg p-12 text-center">
        <div className="text-6xl mb-4">🎯</div>
        <h2 className="text-2xl font-bold mb-2">Coming Soon</h2>
        <p className="text-text-muted mb-6">
          This visualization will analyze kill shot opportunities - possessions that swing 
          game momentum by 5+ points or occur in critical late-game situations.
        </p>
        <Link href="/viz/trapezoid" className="text-brand-orange hover:underline">
          ← Back to Trapezoid
        </Link>
      </div>
    </div>
  );
}
