import { Metadata } from 'next';
import { getMetadata } from '@/lib/data';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'About | CBB Analytics',
  description: 'Learn about our data sources, methodology, and how we calculate advanced college basketball metrics.',
};

export default function AboutPage() {
  const meta = getMetadata();
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-4xl font-bold mb-8">About CBB Analytics</h1>
      
      {/* Overview */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-4">Project Overview</h2>
        <p className="text-text-primary mb-4">
          CBB Analytics is a comprehensive college basketball analytics platform that aggregates and analyzes 
          data from multiple sources to provide advanced metrics, efficiency ratings, and predictive models 
          for all 365 NCAA Division I men's basketball teams.
        </p>
        <p className="text-text-primary">
          Our mission is to make advanced basketball analytics accessible and understandable, combining 
          the best features of sites like KenPom and T-Rank with original analysis and visualizations.
        </p>
      </section>
      
      {/* Data Sources */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-4">Data Sources</h2>
        <p className="text-text-muted mb-6">
          We aggregate data from three primary sources, each providing unique insights:
        </p>
        
        <div className="space-y-6">
          <div className="p-6 bg-ui-surface border border-ui-border rounded-lg">
            <h3 className="text-xl font-bold mb-2">KenPom.com</h3>
            <p className="text-text-primary mb-2">
              Provides adjusted efficiency metrics (AdjEM, AdjO, AdjD), tempo, luck ratings, and strength of schedule.
            </p>
            <ul className="list-disc list-inside text-text-muted text-sm space-y-1">
              <li>Adjusted for opponent quality and pace</li>
              <li>Updated daily throughout the season</li>
              <li>Gold standard for efficiency metrics</li>
            </ul>
          </div>
          
          <div className="p-6 bg-ui-surface border border-ui-border rounded-lg">
            <h3 className="text-xl font-bold mb-2">Bart Torvik (T-Rank)</h3>
            <p className="text-text-primary mb-2">
              Comprehensive Four Factors data, shooting splits, and advanced team statistics.
            </p>
            <ul className="list-disc list-inside text-text-muted text-sm space-y-1">
              <li>Detailed Four Factors breakdown (eFG%, TOV%, ORB%, FTR)</li>
              <li>2P% and 3P% shooting splits</li>
              <li>Wins Above Bubble (WAB) and Barthag ratings</li>
            </ul>
          </div>
          
          <div className="p-6 bg-ui-surface border border-ui-border rounded-lg">
            <h3 className="text-xl font-bold mb-2">CBB Analytics</h3>
            <p className="text-text-primary mb-2">
              Additional adjusted metrics and supplemental data validation.
            </p>
            <ul className="list-disc list-inside text-text-muted text-sm space-y-1">
              <li>Alternative adjusted efficiency calculations</li>
              <li>Cross-validation of Four Factors</li>
              <li>Independent data verification</li>
            </ul>
          </div>
        </div>
      </section>
      
      {/* Methodology */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-4">Methodology</h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-bold mb-2">Data Collection</h3>
            <p className="text-text-primary">
              We use automated Python scripts with browser automation (Playwright) to collect data from public 
              sources daily. All scraping is done ethically with appropriate rate limiting and respects robots.txt 
              policies.
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-bold mb-2">Data Normalization</h3>
            <p className="text-text-primary">
              Team names are normalized across all three sources using a comprehensive mapping system. This ensures 
              that "UConn", "Connecticut", and "CONN" all refer to the same team, enabling seamless cross-dataset analysis.
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-bold mb-2">Metric Calculations</h3>
            <p className="text-text-primary mb-3">
              Our derived metrics (margins, edges) are calculated using standard formulas:
            </p>
            <ul className="list-disc list-inside text-text-muted space-y-2">
              <li><strong>eFG% Margin:</strong> Team eFG% minus Opponent eFG%</li>
              <li><strong>Turnover Edge:</strong> Forced TOV% minus Team TOV%</li>
              <li><strong>Rebounding Edge:</strong> ORB% minus (100% - DRB%)</li>
              <li><strong>FTR Margin:</strong> Team FTR minus Opponent FTR</li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-bold mb-2">Update Frequency</h3>
            <p className="text-text-primary">
              Data is scraped and processed daily during the season. The website is rebuilt with fresh data each day 
              to ensure you're always seeing the most current statistics.
            </p>
            <div className="mt-3 p-4 bg-ui-surface border border-ui-border rounded">
              <strong className="text-brand-orange">Last Updated:</strong>{' '}
              <span className="font-mono">{new Date(meta.lastUpdated).toLocaleString()}</span>
            </div>
          </div>
        </div>
      </section>
      
      {/* Technology */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-4">Technology Stack</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 bg-ui-surface border border-ui-border rounded-lg">
            <h3 className="font-bold mb-2">Frontend</h3>
            <ul className="text-sm text-text-muted space-y-1">
              <li>Next.js 14 (App Router)</li>
              <li>TypeScript</li>
              <li>Tailwind CSS</li>
              <li>Apache ECharts</li>
              <li>TanStack Table</li>
            </ul>
          </div>
          <div className="p-4 bg-ui-surface border border-ui-border rounded-lg">
            <h3 className="font-bold mb-2">Data Pipeline</h3>
            <ul className="text-sm text-text-muted space-y-1">
              <li>Python 3.14</li>
              <li>Playwright</li>
              <li>pandas + BeautifulSoup</li>
              <li>SQLite</li>
              <li>CSV/JSON export</li>
            </ul>
          </div>
        </div>
      </section>
      
      {/* Disclaimers */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-4">Disclaimers & Attribution</h2>
        <div className="p-6 bg-ui-surface border-l-4 border-brand-orange">
          <p className="text-text-primary mb-3">
            <strong>Not Affiliated:</strong> This project is not affiliated with, endorsed by, or officially 
            connected to KenPom.com, barttorvik.com, or CBB Analytics. We are an independent project created 
            for educational and analytical purposes.
          </p>
          <p className="text-text-primary mb-3">
            <strong>Data Attribution:</strong> All efficiency metrics are calculated using methodologies 
            pioneered by Ken Pomeroy. Four Factors analysis is based on Dean Oliver's work. We gratefully 
            acknowledge these contributions to basketball analytics.
          </p>
          <p className="text-text-primary">
            <strong>Accuracy:</strong> While we strive for accuracy, this tool is provided "as is" for 
            informational and entertainment purposes. Always verify critical information with official sources.
          </p>
        </div>
      </section>
      
      {/* Contact */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-4">Project Stats</h2>
        <div className="grid md:grid-cols-3 gap-4 text-center">
          <div className="p-6 bg-ui-card border border-ui-border rounded-lg">
            <div className="text-4xl font-bold font-mono text-brand-orange">{meta.teamCount}</div>
            <div className="text-text-muted mt-2">Teams Tracked</div>
          </div>
          <div className="p-6 bg-ui-card border border-ui-border rounded-lg">
            <div className="text-4xl font-bold font-mono text-brand-orange">
              {meta.sources.kenpom + meta.sources.torvik + meta.sources.cbbAnalytics}
            </div>
            <div className="text-text-muted mt-2">Data Points</div>
          </div>
          <div className="p-6 bg-ui-card border border-ui-border rounded-lg">
            <div className="text-4xl font-bold font-mono text-brand-orange">Daily</div>
            <div className="text-text-muted mt-2">Updates</div>
          </div>
        </div>
      </section>
      
      {/* Links */}
      <section className="text-center">
        <h2 className="text-2xl font-bold mb-4">Explore More</h2>
        <div className="flex flex-wrap justify-center gap-4">
          <Link 
            href="/rankings" 
            className="px-6 py-3 bg-brand-orange text-white rounded-lg hover:bg-brand-orange-hover transition-colors"
          >
            View Rankings
          </Link>
          <Link 
            href="/glossary" 
            className="px-6 py-3 bg-ui-surface border border-ui-border rounded-lg hover:border-brand-orange transition-colors"
          >
            Metrics Glossary
          </Link>
          <Link 
            href="/matchup" 
            className="px-6 py-3 bg-ui-surface border border-ui-border rounded-lg hover:border-brand-orange transition-colors"
          >
            Matchup Tool
          </Link>
        </div>
      </section>
    </div>
  );
}
