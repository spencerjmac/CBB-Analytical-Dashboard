import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Crystal Ball | CBB Analytics',
};

export default function CrystalBallPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-4">The Crystal Ball</h1>
      <p className="text-text-muted mb-8">Championship profile and predictive analysis.</p>
      
      <div className="bg-ui-card border border-ui-border rounded-lg p-12 text-center">
        <div className="text-6xl mb-4">🔮</div>
        <h2 className="text-2xl font-bold mb-2">Coming Soon</h2>
        <p className="text-text-muted mb-6">
          This tool will evaluate teams against historical championship profiles using 
          a rules engine with configurable thresholds for efficiency margins, Four Factors, 
          and other key metrics.
        </p>
        <Link href="/viz/trapezoid" className="text-brand-orange hover:underline">
          ← Back to Trapezoid
        </Link>
      </div>
    </div>
  );
}
