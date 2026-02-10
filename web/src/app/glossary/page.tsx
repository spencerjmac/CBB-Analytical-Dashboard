import { Metadata } from 'next';
import { metricDefinitions } from '@/lib/metrics';
import GlossaryTable from '@/components/GlossaryTable';

export const metadata: Metadata = {
  title: 'Glossary | CBB Analytics',
  description: 'Complete definitions and formulas for all college basketball analytics metrics including efficiency ratings, four factors, and advanced statistics.',
};

export default function GlossaryPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Metrics Glossary</h1>
        <p className="text-text-muted">
          Comprehensive definitions and formulas for all metrics used in our analytics. 
          All formulas are rendered with proper mathematical notation.
        </p>
      </div>
      
      <GlossaryTable metrics={metricDefinitions} />
    </div>
  );
}
