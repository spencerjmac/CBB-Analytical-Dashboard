export default function TrapezoidPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Trapezoid of Excellence</h1>
      
      <div className="bg-yellow-100 border border-yellow-400 text-yellow-800 px-6 py-4 rounded-lg mb-8">
        <p className="font-semibold">🚧 Visualization In Progress</p>
        <p className="mt-2">
          The Trapezoid of Excellence visualization is being implemented. This will show teams plotted 
          by Tempo vs Efficiency with the championship-caliber region highlighted.
        </p>
        <p className="mt-2 text-sm">
          See the implementation checklist in the README for progress.
        </p>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4">Concept</h2>
        <p className="mb-4">
          The Trapezoid of Excellence identifies teams that combine elite efficiency with optimal tempo. 
          Championship teams historically cluster in this region.
        </p>
        
        <h3 className="text-xl font-bold mb-3">Axes</h3>
        <ul className="list-disc list-inside space-y-2 mb-6">
          <li><strong>X-axis:</strong> Adjusted Tempo</li>
          <li><strong>Y-axis:</strong> Adjusted Efficiency Margin</li>
        </ul>
        
        <h3 className="text-xl font-bold mb-3">The Trapezoid</h3>
        <p>
          The trapezoid boundary represents the statistical profile of recent national champions. 
          Teams inside the trapezoid have championship-caliber metrics.
        </p>
      </div>
    </div>
  );
}
