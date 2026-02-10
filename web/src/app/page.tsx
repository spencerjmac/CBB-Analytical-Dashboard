import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold mb-4">
          College Basketball Analytics
        </h1>
        <p className="text-xl text-text-muted max-w-2xl mx-auto">
          Advanced efficiency metrics, four factors analysis, and predictive models 
          for NCAA Division I men's basketball.
        </p>
      </div>
      
      {/* Feature Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <Link 
          href="/rankings" 
          className="block p-6 bg-ui-card border border-ui-border rounded-lg hover:border-brand-orange transition-colors"
        >
          <div className="text-4xl mb-3">📊</div>
          <h2 className="text-2xl font-bold mb-2">Team Rankings</h2>
          <p className="text-text-muted">
            Sortable, filterable rankings table with adjusted efficiency metrics 
            and four factors for all 365 D1 teams.
          </p>
        </Link>
        
        <Link 
          href="/matchup" 
          className="block p-6 bg-ui-card border border-ui-border rounded-lg hover:border-brand-orange transition-colors"
        >
          <div className="text-4xl mb-3">⚔️</div>
          <h2 className="text-2xl font-bold mb-2">Matchup Tool</h2>
          <p className="text-text-muted">
            Compare any two teams head-to-head with efficiency projections 
            and four factor matchup edges.
          </p>
        </Link>
        
        <Link 
          href="/viz/trapezoid" 
          className="block p-6 bg-ui-card border border-ui-border rounded-lg hover:border-brand-orange transition-colors"
        >
          <div className="text-4xl mb-3">📈</div>
          <h2 className="text-2xl font-bold mb-2">Visualizations</h2>
          <p className="text-text-muted">
            Interactive charts including the Trapezoid of Excellence, 
            Efficiency Landscape, Kill Shot analysis, and Crystal Ball.
          </p>
        </Link>
        
        <Link 
          href="/glossary" 
          className="block p-6 bg-ui-card border border-ui-border rounded-lg hover:border-brand-orange transition-colors"
        >
          <div className="text-4xl mb-3">📖</div>
          <h2 className="text-2xl font-bold mb-2">Glossary</h2>
          <p className="text-text-muted">
            Comprehensive definitions and formulas for all metrics, 
            from adjusted efficiency to four factors.
          </p>
        </Link>
        
        <Link 
          href="/about" 
          className="block p-6 bg-ui-card border border-ui-border rounded-lg hover:border-brand-orange transition-colors"
        >
          <div className="text-4xl mb-3">ℹ️</div>
          <h2 className="text-2xl font-bold mb-2">About</h2>
          <p className="text-text-muted">
            Learn about our data sources, methodology, and how we calculate 
            our advanced metrics.
          </p>
        </Link>
        
        <div className="p-6 bg-ui-surface border border-ui-border rounded-lg">
          <div className="text-4xl mb-3">🎓</div>
          <h2 className="text-2xl font-bold mb-2">Open Source</h2>
          <p className="text-text-muted">
            Built with Next.js, TypeScript, and Tailwind CSS. 
            All calculations and visualizations are transparent.
          </p>
        </div>
      </div>
      
      {/* Quick Stats */}
      <div className="bg-ui-surface border border-ui-border rounded-lg p-8 text-center">
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <div className="text-4xl font-bold text-brand-orange font-mono">365</div>
            <div className="text-text-muted mt-1">NCAA D1 Teams</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-brand-orange font-mono">40+</div>
            <div className="text-text-muted mt-1">Advanced Metrics</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-brand-orange font-mono">Daily</div>
            <div className="text-text-muted mt-1">Data Updates</div>
          </div>
        </div>
      </div>
    </div>
  );
}
