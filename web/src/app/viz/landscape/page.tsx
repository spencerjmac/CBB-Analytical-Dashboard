import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Efficiency Landscape | CBB Analytics',
};

export default function LandscapePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-4">Efficiency Landscape</h1>
      <p className="text-text-muted mb-8">Offensive vs Defensive efficiency with contour overlay.</p>
      
      <div className="bg-ui-card border border-ui-border rounded-lg p-12 text-center">
        <div className="text-6xl mb-4">🗺️</div>
        <h2 className="text-2xl font-bold mb-2">Coming Soon</h2>
        <p className="text-text-muted mb-6">
          This visualization will show the efficiency landscape with teams plotted by 
          offensive and defensive ratings, with heatmap/contour overlay.
        </p>
        <Link href="/viz/trapezoid" className="text-brand-orange hover:underline">
          ← Back to Trapezoid
        </Link>
      </div>
    </div>
  );
}
