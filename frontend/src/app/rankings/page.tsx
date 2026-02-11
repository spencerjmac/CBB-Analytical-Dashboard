'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import type { RankingsRow, Conference } from '@/types';

export default function RankingsPage() {
  const [data, setData] = useState<RankingsRow[]>([]);
  const [conferences, setConferences] = useState<Conference[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [search, setSearch] = useState('');
  const [conferenceFilter, setConferenceFilter] = useState('');
  const [sortField, setSortField] = useState('rank');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  
  useEffect(() => {
    loadData();
    loadConferences();
  }, [search, conferenceFilter, sortField, sortDir]);
  
  async function loadData() {
    try {
      setLoading(true);
      const response = await api.getRankings({
        search: search || undefined,
        conference: conferenceFilter || undefined,
        sort: sortField,
        dir: sortDir,
      });
      setData(response.results);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load rankings');
    } finally {
      setLoading(false);
    }
  }
  
  async function loadConferences() {
    try {
      const confs = await api.getConferences();
      setConferences(confs);
    } catch (err) {
      console.error('Failed to load conferences:', err);
    }
  }
  
  function handleSort(field: string) {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('asc');
    }
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Team Rankings</h1>
      
      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Teams
            </label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Michigan, Duke..."
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Conference
            </label>
            <select
              value={conferenceFilter}
              onChange={(e) => setConferenceFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary"
            >
              <option value="">All Conferences</option>
              {conferences.map((conf) => (
                <option key={conf.code} value={conf.code}>
                  {conf.name} ({conf.code})
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => {
                setSearch('');
                setConferenceFilter('');
                setSortField('rank');
                setSortDir('asc');
              }}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>
      
      {/* Loading/Error States */}
      {loading && (
        <div className="flex justify-center items-center py-20">
          <div className="spinner w-12 h-12"></div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p className="font-bold">Error</p>
          <p>{error}</p>
          <p className="text-sm mt-2">Make sure the Django backend is running on http://localhost:8000</p>
        </div>
      )}
      
      {/* Rankings Table */}
      {!loading && !error && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="stats-table">
              <thead>
                <tr>
                  <SortableHeader field="rank" current={sortField} dir={sortDir} onClick={handleSort}>
                    Rank
                  </SortableHeader>
                  <th>Team</th>
                  <SortableHeader field="conference" current={sortField} dir={sortDir} onClick={handleSort}>
                    Conf
                  </SortableHeader>
                  <th>Record</th>
                  <SortableHeader field="adj_em" current={sortField} dir={sortDir} onClick={handleSort}>
                    AdjEM
                  </SortableHeader>
                  <SortableHeader field="adj_o" current={sortField} dir={sortDir} onClick={handleSort}>
                    AdjO
                  </SortableHeader>
                  <SortableHeader field="adj_d" current={sortField} dir={sortDir} onClick={handleSort}>
                    AdjD
                  </SortableHeader>
                  <SortableHeader field="adj_tempo" current={sortField} dir={sortDir} onClick={handleSort}>
                    Tempo
                  </SortableHeader>
                  <SortableHeader field="efg_pct" current={sortField} dir={sortDir} onClick={handleSort}>
                    eFG%
                  </SortableHeader>
                  <SortableHeader field="tov_pct" current={sortField} dir={sortDir} onClick={handleSort}>
                    TOV%
                  </SortableHeader>
                  <SortableHeader field="orb_pct" current={sortField} dir={sortDir} onClick={handleSort}>
                    ORB%
                  </SortableHeader>
                  <SortableHeader field="ftr" current={sortField} dir={sortDir} onClick={handleSort}>
                    FTR
                  </SortableHeader>
                </tr>
              </thead>
              <tbody>
                {data.map((row) => (
                  <tr key={row.team_slug} className="hover:bg-gray-50">
                    <td className="font-bold">{row.rank}</td>
                    <td>
                      <Link 
                        href={`/team/${row.team_slug}`}
                        className="text-blue hover:underline font-medium"
                      >
                        {row.team_name}
                      </Link>
                    </td>
                    <td className="text-sm">{row.conference}</td>
                    <td className="mono text-sm">{row.record}</td>
                    <td className="mono font-bold">{row.adj_em.toFixed(2)}</td>
                    <td className="mono">{row.adj_o.toFixed(1)}</td>
                    <td className="mono">{row.adj_d.toFixed(1)}</td>
                    <td className="mono">{row.adj_tempo.toFixed(1)}</td>
                    <td className="mono">{row.efg_pct.toFixed(1)}</td>
                    <td className="mono">{row.tov_pct.toFixed(1)}</td>
                    <td className="mono">{row.orb_pct.toFixed(1)}</td>
                    <td className="mono">{row.ftr.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {data.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No teams found matching your filters.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SortableHeader({
  field,
  current,
  dir,
  onClick,
  children,
}: {
  field: string;
  current: string;
  dir: 'asc' | 'desc';
  onClick: (field: string) => void;
  children: React.ReactNode;
}) {
  const isActive = current === field;
  
  return (
    <th
      onClick={() => onClick(field)}
      className="cursor-pointer hover:bg-gray-200 select-none"
    >
      <div className="flex items-center gap-1">
        {children}
        {isActive && (
          <span className="text-primary">{dir === 'asc' ? '↑' : '↓'}</span>
        )}
      </div>
    </th>
  );
}
