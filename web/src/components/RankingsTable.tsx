'use client';

import { useMemo, useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  ColumnDef,
  flexRender,
  SortingState,
  ColumnFiltersState,
} from '@tanstack/react-table';
import { TeamSeason } from '@/types';
import Link from 'next/link';
import clsx from 'clsx';

interface RankingsTableProps {
  data: TeamSeason[];
}

export default function RankingsTable({ data }: RankingsTableProps) {
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'rank', desc: false }
  ]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [conferenceFilter, setConferenceFilter] = useState<string>('all');
  
  // Get unique conferences
  const conferences = useMemo(() => {
    const confs = new Set(data.map(t => t.conference).filter(Boolean));
    return Array.from(confs).sort();
  }, [data]);
  
  // Filter data by conference
  const filteredData = useMemo(() => {
    if (conferenceFilter === 'all') return data;
    return data.filter(t => t.conference === conferenceFilter);
  }, [data, conferenceFilter]);
  
  const columns = useMemo<ColumnDef<TeamSeason>[]>(
    () => [
      {
        accessorKey: 'rank',
        header: 'Rk',
        cell: (info) => (
          <span className="font-mono font-semibold">
            {info.getValue<number>()}
          </span>
        ),
        size: 50,
      },
      {
        accessorKey: 'teamName',
        header: 'Team',
        cell: (info) => {
          const team = info.row.original;
          return (
            <Link 
              href={`/team/${team.teamId}`}
              className="flex items-center space-x-2 hover:text-brand-orange transition-colors"
            >
              <img 
                src={team.logoUrl} 
                alt={team.teamName}
                className="w-6 h-6 object-contain"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/logos/default.png';
                }}
              />
              <span className="font-medium">{team.teamName}</span>
            </Link>
          );
        },
        size: 200,
      },
      {
        accessorKey: 'conference',
        header: 'Conf',
        cell: (info) => (
          <span className="text-text-muted text-xs uppercase">
            {info.getValue<string>()}
          </span>
        ),
        size: 80,
      },
      {
        accessorKey: 'record',
        header: 'Record',
        cell: (info) => (
          <span className="font-mono text-sm">
            {info.getValue<string>() || '-'}
          </span>
        ),
        size: 80,
      },
      {
        accessorKey: 'adjEM',
        header: 'AdjEM',
        cell: (info) => (
          <span className="stat-number font-semibold">
            {info.getValue<number>().toFixed(2)}
          </span>
        ),
        size: 80,
        sortDescFirst: true,
      },
      {
        accessorKey: 'adjO',
        header: 'AdjO',
        cell: (info) => (
          <span className="stat-number text-success">
            {info.getValue<number>().toFixed(1)}
          </span>
        ),
        size: 70,
        sortDescFirst: true,
      },
      {
        accessorKey: 'adjD',
        header: 'AdjD',
        cell: (info) => (
          <span className="stat-number text-secondary">
            {info.getValue<number>().toFixed(1)}
          </span>
        ),
        size: 70,
        sortDescFirst: false, // Lower is better for defense
      },
      {
        accessorKey: 'adjTempo',
        header: 'Tempo',
        cell: (info) => (
          <span className="stat-number">
            {info.getValue<number>().toFixed(1)}
          </span>
        ),
        size: 70,
      },
      {
        accessorKey: 'eFG',
        header: 'eFG%',
        cell: (info) => (
          <span className="stat-number">
            {(info.getValue<number>() * 100).toFixed(1)}%
          </span>
        ),
        size: 80,
        sortDescFirst: true,
      },
      {
        accessorKey: 'tov',
        header: 'TOV%',
        cell: (info) => (
          <span className="stat-number">
            {(info.getValue<number>() * 100).toFixed(1)}%
          </span>
        ),
        size: 80,
        sortDescFirst: false, // Lower is better
      },
      {
        accessorKey: 'orb',
        header: 'ORB%',
        cell: (info) => (
          <span className="stat-number">
            {(info.getValue<number>() * 100).toFixed(1)}%
          </span>
        ),
        size: 80,
        sortDescFirst: true,
      },
      {
        accessorKey: 'ftr',
        header: 'FTR',
        cell: (info) => (
          <span className="stat-number">
            {(info.getValue<number>() * 100).toFixed(1)}%
          </span>
        ),
        size: 80,
        sortDescFirst: true,
      },
    ],
    []
  );
  
  const table = useReactTable({
    data: filteredData,
    columns,
    state: {
      sorting,
      columnFilters,
      globalFilter,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });
  
  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search teams..."
            value={globalFilter ?? ''}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="w-full px-4 py-2 border border-ui-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-orange"
          />
        </div>
        
        {/* Conference Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm text-text-muted font-medium">Conference:</label>
          <select
            value={conferenceFilter}
            onChange={(e) => setConferenceFilter(e.target.value)}
            className="px-3 py-2 border border-ui-border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-orange"
          >
            <option value="all">All Conferences</option>
            {conferences.map(conf => (
              <option key={conf} value={conf}>{conf}</option>
            ))}
          </select>
        </div>
        
        {/* Results count */}
        <div className="text-sm text-text-muted">
          <span className="font-mono font-semibold">
            {table.getFilteredRowModel().rows.length}
          </span>{' '}
          teams
        </div>
      </div>
      
      {/* Table */}
      <div className="border border-ui-border rounded-lg overflow-hidden bg-ui-card">
        <div className="overflow-x-auto">
          <table className="rankings-table">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      style={{ width: header.getSize() }}
                      className={clsx(
                        header.column.getCanSort() && 'cursor-pointer select-none'
                      )}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      <div className="flex items-center gap-2">
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                        {header.column.getIsSorted() && (
                          <span className="text-brand-orange">
                            {header.column.getIsSorted() === 'desc' ? '↓' : '↑'}
                          </span>
                        )}
                      </div>
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
