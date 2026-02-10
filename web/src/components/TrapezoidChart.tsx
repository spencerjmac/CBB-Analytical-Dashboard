'use client';

import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import { TeamSeason } from '@/types';

interface TrapezoidChartProps {
  teams: TeamSeason[];
}

export default function TrapezoidChart({ teams }: TrapezoidChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  
  useEffect(() => {
    if (!chartRef.current) return;
    
    // Initialize chart
    chartInstance.current = echarts.init(chartRef.current);
    
    // Trapezoid boundaries (simplified - you'll provide exact Tableau calculations)
    // This creates a championship-caliber region
    const trapezoidPoints = [
      [62, 15],   // Bottom-left (slow, good)
      [68, 20],   // Mid-left
      [72, 25],   // Mid-right
      [78, 20],   // Bottom-right (fast, good)
      [78, 40],   // Top-right
      [62, 40],   // Top-left
    ];
    
    // Check if point is inside trapezoid (simplified)
    function isInsideTrapezoid(tempo: number, adjEM: number): boolean {
      // Simplified check - elite teams (top 25ish)
      return adjEM > 18 && tempo > 60 && tempo < 80;
    }
    
    // Prepare data
    const insideData = teams
      .filter(t => isInsideTrapezoid(t.adjTempo, t.adjEM))
      .map(t => ({
        value: [t.adjTempo, t.adjEM],
        name: t.teamName,
        teamId: t.teamId,
        rank: t.rank,
      }));
    
    const outsideData = teams
      .filter(t => !isInsideTrapezoid(t.adjTempo, t.adjEM))
      .map(t => ({
        value: [t.adjTempo, t.adjEM],
        name: t.teamName,
        teamId: t.teamId,
        rank: t.rank,
      }));
    
    const option: echarts.EChartsOption = {
      title: {
        text: 'Trapezoid of Excellence',
        subtext: 'Championship-Caliber Teams by Tempo & Efficiency',
        left: 'center',
        textStyle: {
          fontSize: 24,
          fontWeight: 'bold',
        },
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          return `<strong>${params.data.name}</strong><br/>
                  Rank: #${params.data.rank}<br/>
                  Tempo: ${params.value[0].toFixed(1)}<br/>
                  AdjEM: ${params.value[1].toFixed(2)}`;
        },
      },
      xAxis: {
        name: 'Adjusted Tempo',
        nameLocation: 'middle',
        nameGap: 30,
        min: 58,
        max: 80,
        splitLine: { show: false },
      },
      yAxis: {
        name: 'Adjusted Efficiency Margin',
        nameLocation: 'middle',
        nameGap: 40,
        min: -20,
        max: 45,
        splitLine: { lineStyle: { type: 'dashed', color: '#E5E7EB' } },
      },
      grid: {
        left: 80,
        right: 60,
        top: 100,
        bottom: 60,
      },
      series: [
        // Trapezoid polygon
        {
          type: 'custom',
          renderItem: (params, api) => {
            const points = trapezoidPoints.map(p => api.coord?.(p) || [0, 0]);
            return {
              type: 'polygon',
              shape: {
                points,
              },
              style: {
                fill: 'rgba(237, 113, 58, 0.1)',
                stroke: '#ED713A',
                lineWidth: 2,
              },
            };
          },
          data: [0],
          silent: true,
          z: 0,
        },
        // Teams inside trapezoid
        {
          name: 'Inside Trapezoid',
          type: 'scatter',
          data: insideData,
          symbolSize: 8,
          itemStyle: {
            color: '#ED713A',
            borderColor: '#fff',
            borderWidth: 1,
          },
          emphasis: {
            itemStyle: {
              color: '#D85F2E',
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: '#ED713A',
            },
          },
          z: 2,
        },
        // Teams outside trapezoid
        {
          name: 'Outside Trapezoid',
          type: 'scatter',
          data: outsideData,
          symbolSize: 6,
          itemStyle: {
            color: '#8B8B8B',
            opacity: 0.4,
          },
          emphasis: {
            itemStyle: {
              color: '#6B7280',
              opacity: 0.8,
              borderWidth: 1,
              borderColor: '#374151',
            },
          },
          z: 1,
        },
      ],
    };
    
    chartInstance.current.setOption(option);
    
    // Handle click to navigate
    chartInstance.current.on('click', (params: any) => {
      if (params.data && params.data.teamId) {
        window.location.href = `/team/${params.data.teamId}`;
      }
    });
    
    // Responsive
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
      chartInstance.current?.dispose();
    };
  }, [teams]);
  
  return (
    <div>
      <div ref={chartRef} style={{ width: '100%', height: '600px' }} />
      
      <div className="mt-6 p-6 bg-ui-surface border border-ui-border rounded-lg">
        <h3 className="font-bold text-lg mb-3">About the Trapezoid</h3>
        <p className="text-text-muted mb-4">
          The "Trapezoid of Excellence" identifies teams with championship-caliber profiles based on 
          their efficiency margin and tempo. Teams inside the trapezoid have historically had the 
          highest success rates in tournament play.
        </p>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <strong className="text-brand-orange">Inside Trapezoid:</strong> Elite teams with 
            high efficiency margins across all tempo styles (slow, medium, fast).
          </div>
          <div>
            <strong className="text-text-muted">Outside Trapezoid:</strong> Teams that may excel 
            in regular season but lack the efficiency profile of champions.
          </div>
        </div>
      </div>
    </div>
  );
}
