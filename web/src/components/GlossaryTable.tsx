'use client';

import { useState, useMemo } from 'react';
import { MetricDefinition } from '@/types';
import { BlockMath } from 'react-katex';

interface GlossaryTableProps {
  metrics: MetricDefinition[];
}

export default function GlossaryTable({ metrics }: GlossaryTableProps) {
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  
  const categories = useMemo(() => {
    const cats = new Set(metrics.map(m => m.category));
    return Array.from(cats).sort();
  }, [metrics]);
  
  const filteredMetrics = useMemo(() => {
    return metrics.filter(m => {
      const matchesSearch = !search || 
        m.name.toLowerCase().includes(search.toLowerCase()) ||
        m.definition.toLowerCase().includes(search.toLowerCase());
      
      const matchesCategory = categoryFilter === 'all' || m.category === categoryFilter;
      
      return matchesSearch && matchesCategory;
    });
  }, [metrics, search, categoryFilter]);
  
  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <input
          type="text"
          placeholder="Search metrics..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 max-w-md px-4 py-2 border border-ui-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-orange"
        />
        
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-3 py-2 border border-ui-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-orange"
        >
          <option value="all">All Categories</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>
      
      {/* Metrics List */}
      <div className="space-y-6">
        {filteredMetrics.map((metric) => (
          <div 
            key={metric.id}
            className="p-6 bg-ui-card border border-ui-border rounded-lg hover:border-brand-orange transition-colors"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-2xl font-bold mb-1">{metric.name}</h3>
                <span className="text-sm text-text-muted uppercase tracking-wide">
                  {metric.category}
                </span>
              </div>
              <span className={`px-3 py-1 rounded text-sm font-medium ${
                metric.higherIsBetter 
                  ? 'bg-success/10 text-success' 
                  : 'bg-secondary/10 text-secondary'
              }`}>
                {metric.higherIsBetter ? '↑ Higher is Better' : '↓ Lower is Better'}
              </span>
            </div>
            
            <p className="text-text-primary mb-4">{metric.definition}</p>
            
            {/* Formula */}
            <div className="bg-ui-surface border border-ui-border rounded p-4 mb-4 overflow-x-auto">
              <div className="text-text-muted text-xs mb-2 font-medium">Formula:</div>
              <BlockMath math={metric.formula} />
            </div>
            
            {/* Interpretation & Range */}
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-text-muted font-medium mb-1">Interpretation:</div>
                <p className="text-text-primary">{metric.interpretation}</p>
              </div>
              {metric.range && (
                <div>
                  <div className="text-text-muted font-medium mb-1">Typical Range:</div>
                  <p className="text-text-primary font-mono">{metric.range}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {filteredMetrics.length === 0 && (
        <div className="text-center py-12 text-text-muted">
          No metrics found matching your search.
        </div>
      )}
    </div>
  );
}
