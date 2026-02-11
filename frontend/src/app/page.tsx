import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue to-primary">
      <div className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h1 className="text-6xl font-bold mb-6">
            🏀 CBB Analytics
          </h1>
          <p className="text-2xl mb-12 text-white/90">
            Advanced College Basketball Analytics Dashboard
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            <FeatureCard
              icon="📊"
              title="Team Rankings"
              description="Sortable, filterable rankings for 365 D1 teams"
              href="/rankings"
            />
            <FeatureCard
              icon="🎯"
              title="Team Profiles"
              description="Detailed stats, Four Factors, and resume metrics"
              href="/rankings"
            />
            <FeatureCard
              icon="⚔️"
              title="Matchup Tool"
              description="Head-to-head analysis with win probabilities"
              href="/matchup"
            />
            <FeatureCard
              icon="📈"
              title="Visualizations"
              description="Trapezoid of Excellence, efficiency landscapes, and more"
              href="/viz/trapezoid"
            />
          </div>
          
          <Link
            href="/rankings"
            className="inline-block bg-white text-primary px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors"
          >
            View Rankings →
          </Link>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  href,
}: {
  icon: string;
  title: string;
  description: string;
  href: string;
}) {
  return (
    <Link href={href}>
      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 hover:bg-white/20 transition-colors cursor-pointer">
        <div className="text-4xl mb-3">{icon}</div>
        <h3 className="text-xl font-bold mb-2">{title}</h3>
        <p className="text-white/80">{description}</p>
      </div>
    </Link>
  );
}
