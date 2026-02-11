export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-4xl font-bold mb-8">About CBB Analytics</h1>
      
      <div className="prose max-w-none space-y-6">
        <section className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4">Data Sources</h2>
          <p className="mb-4">
            This dashboard combines data from multiple respected sources in college basketball analytics:
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li><strong>KenPom.com</strong> - Adjusted efficiency metrics, tempo, and ratings</li>
            <li><strong>Bart Torvik</strong> - Four Factors, shooting splits, and advanced metrics</li>
            <li><strong>CBB Analytics</strong> - Additional ratings and resume metrics</li>
          </ul>
        </section>
        
        <section className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4">Methodology</h2>
          <p className="mb-4">
            The analytics in this dashboard are based on possession-adjusted statistics that account for 
            pace of play and strength of schedule. Key concepts:
          </p>
          
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-2">Adjusted Efficiency Metrics</h3>
              <p>
                <strong>AdjEM (Efficiency Margin)</strong> measures the point differential per 100 possessions 
                against an average D1 opponent. <strong>AdjO (Offensive Efficiency)</strong> and <strong>AdjD 
                (Defensive Efficiency)</strong> measure points scored/allowed per 100 possessions, adjusted for 
                opponent strength.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-2">Four Factors</h3>
              <p>
                Dean Oliver's Four Factors of Basketball Success:
              </p>
              <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
                <li><strong>eFG% (Effective FG%)</strong> - Shooting efficiency (accounts for 3-pointers)</li>
                <li><strong>TOV% (Turnover %)</strong> - Turnovers per possession</li>
                <li><strong>ORB%/DRB% (Rebound %)</strong> - Offensive/Defensive rebounding rate</li>
                <li><strong>FTR (Free Throw Rate)</strong> - Free throws attempted per field goal attempt</li>
              </ul>
            </div>
          </div>
        </section>
        
        <section className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4">Technology Stack</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">Backend</h3>
              <ul className="list-disc list-inside space-y-1">
                <li>Django 5.0</li>
                <li>Django REST Framework</li>
                <li>SQLite (dev) / PostgreSQL (prod)</li>
                <li>Pandas for data ingestion</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-2">Frontend</h3>
              <ul className="list-disc list-inside space-y-1">
                <li>Next.js 14 (App Router)</li>
                <li>TypeScript</li>
                <li>Tailwind CSS</li>
                <li>Apache ECharts</li>
              </ul>
            </div>
          </div>
        </section>
        
        <section className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4">Last Updated</h2>
          <p>
            Data is refreshed daily during the season. Check the data provenance indicators on each 
            team's page to see which sources have been included.
          </p>
        </section>
        
        <section className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4">Disclaimer</h2>
          <p className="text-sm text-gray-600">
            This is an independent analytics project. All data is sourced from publicly available 
            statistics. Team logos and trademarks are property of their respective institutions. 
            This dashboard is not affiliated with or endorsed by KenPom, Bart Torvik, or CBB Analytics.
          </p>
        </section>
      </div>
    </div>
  );
}
