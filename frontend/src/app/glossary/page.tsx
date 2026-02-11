export default function GlossaryPage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <h1 className="text-4xl font-bold mb-8">Metrics Glossary</h1>
      
      <div className="space-y-4">
        <MetricCard
          name="AdjEM (Adjusted Efficiency Margin)"
          definition="Point differential per 100 possessions against an average Division I opponent on a neutral court."
          interpretation="Higher is better. Elite teams typically have AdjEM > 25."
          higherIsBetter={true}
        />
        
        <MetricCard
          name="AdjO (Adjusted Offensive Efficiency)"
          definition="Points scored per 100 possessions against an average D1 defense."
          interpretation="National average is ~100. Elite offenses score 115+."
          higherIsBetter={true}
        />
        
        <MetricCard
          name="AdjD (Adjusted Defensive Efficiency)"
          definition="Points allowed per 100 possessions against an average D1 offense."
          interpretation="National average is ~100. Elite defenses allow <92."
          higherIsBetter={false}
        />
        
        <MetricCard
          name="AdjTempo"
          definition="Possessions per 40 minutes against an average D1 opponent."
          interpretation="National average is ~68. Fast teams: >72, Slow teams: <65."
          higherIsBetter={null}
        />
        
        <div className="bg-gray-100 p-6 rounded-lg my-8">
          <h2 className="text-2xl font-bold mb-4">Four Factors of Basketball Success</h2>
          <p className="mb-4">Dean Oliver identified four key factors that determine basketball success, in order of importance:</p>
        </div>
        
        <MetricCard
          name="eFG% (Effective Field Goal %)"
          definition="(FGM + 0.5 * 3PM) / FGA. Adjusts for the fact that 3-pointers are worth more."
          interpretation="National average ~50%. Elite: >55% offensive, <45% defensive."
          higherIsBetter={true}
        />
        
        <MetricCard
          name="TOV% (Turnover Percentage)"
          definition="Turnovers per 100 possessions."
          interpretation="Lower is better offensively (~15%), higher is better defensively (>18%)."
          higherIsBetter={null}
        />
        
        <MetricCard
          name="ORB% / DRB% (Offensive/Defensive Rebound %)"
          definition="Percentage of available rebounds collected."
          interpretation="ORB%: >35% is elite. DRB%: >75% is elite."
          higherIsBetter={true}
        />
        
        <MetricCard
          name="FTR (Free Throw Rate)"
          definition="Free throws attempted per field goal attempt."
          interpretation="Measures ability to get to the line. >40 is excellent."
          higherIsBetter={true}
        />
        
        <div className="bg-gray-100 p-6 rounded-lg my-8">
          <h2 className="text-2xl font-bold mb-4">Resume Metrics</h2>
        </div>
        
        <MetricCard
          name="WAB (Wins Above Bubble)"
          definition="Wins above what a typical NCAA Tournament bubble team would have with the same schedule."
          interpretation="Positive WAB suggests NCAA Tournament-caliber performance."
          higherIsBetter={true}
        />
        
        <MetricCard
          name="Barthag"
          definition="Win probability against an average D1 team, derived from adjusted efficiency metrics."
          interpretation="0.5 = average, >0.85 = elite, >0.95 = championship contender."
          higherIsBetter={true}
        />
        
        <MetricCard
          name="SOS (Strength of Schedule)"
          definition="Average adjusted efficiency of opponents played."
          interpretation="Higher values indicate tougher schedules. Power conferences typically >5."
          higherIsBetter={null}
        />
        
        <MetricCard
          name="Luck"
          definition="Difference between actual winning percentage and expected winning percentage based on points scored/allowed."
          interpretation="Positive = team has been lucky in close games. Negative = unlucky."
          higherIsBetter={null}
        />
      </div>
    </div>
  );
}

function MetricCard({
  name,
  definition,
  interpretation,
  higherIsBetter,
}: {
  name: string;
  definition: string;
  interpretation: string;
  higherIsBetter: boolean | null;
}) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-xl font-bold text-primary">{name}</h3>
        {higherIsBetter !== null && (
          <span className={`text-sm px-3 py-1 rounded-full ${
            higherIsBetter ? 'bg-green/20 text-green' : 'bg-red-100 text-red-600'
          }`}>
            {higherIsBetter ? '↑ Higher is Better' : '↓ Lower is Better'}
          </span>
        )}
      </div>
      
      <p className="text-gray-700 mb-3">
        <strong>Definition:</strong> {definition}
      </p>
      
      <p className="text-gray-600 text-sm">
        <strong>Interpretation:</strong> {interpretation}
      </p>
    </div>
  );
}
