import React from 'react';
import { Card } from '@/components/ui/card';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { ChartSpec, Filters, FilterOptions, PersonaDistribution } from '@/lib/charts/types';
import { PERSONA_COLORS } from '@/lib/charts/constants';
import { FilterPanel } from './FilterPanel';

interface DistributionChartProps {
  distributionChart: ChartSpec;
  filters: Filters;
  filterOptions: FilterOptions;
  onFilterChange: (filterType: string, value: string) => void;
}

export function DistributionChart({
  distributionChart,
  filters,
  filterOptions,
  onFilterChange,
}: DistributionChartProps) {
  const distribution = distributionChart.derived_metrics?.persona_distribution || {};
  const chartData: PersonaDistribution[] = Object.entries(distribution).map(
    ([persona, data]) => ({
      persona,
      count: (data as { count: number; percentage: number }).count,
      percentage: (data as { count: number; percentage: number }).percentage,
    })
  );

  return (
    <Card className="p-6 mb-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">📊 Summary Statistics</h2>

      {/* Filters */}
      <FilterPanel
        filters={filters}
        filterOptions={filterOptions}
        onFilterChange={onFilterChange}
      />

      {/* Total Stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-600 font-medium">Total Respondents</p>
          <p className="text-3xl font-bold text-blue-900">
            {distributionChart.derived_metrics?.total_respondents || 0}
          </p>
        </div>
        <div className="p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-green-600 font-medium">Unique Personas</p>
          <p className="text-3xl font-bold text-green-900">
            {chartData.filter((d) => d.count > 0).length}
          </p>
        </div>
      </div>

      {/* Bar Chart */}
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="persona" tick={{ fill: '#374151', fontSize: 12 }} />
          <YAxis tick={{ fill: '#6b7280', fontSize: 10 }} />
          <Tooltip
            formatter={(value: number | undefined, name: string | undefined) => {
              if (value === undefined) return [0, name || ''];
              if (name === 'count') return [value, 'Count'];
              return [value.toFixed(1) + '%', 'Percentage'];
            }}
          />
          <Legend />
          <Bar dataKey="count" name="Count">
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={PERSONA_COLORS[entry.persona.charAt(0)] || '#94a3b8'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Persona Breakdown */}
      <div className="mt-6 grid grid-cols-5 gap-2">
        {chartData
          .filter((d) => d.count > 0)
          .map((item) => (
            <div
              key={item.persona}
              className="text-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div
                className="w-6 h-6 rounded-full mx-auto mb-2"
                style={{ backgroundColor: PERSONA_COLORS[item.persona.charAt(0)] }}
              />
              <p className="text-xs font-semibold">{item.persona}</p>
              <p className="text-lg font-bold text-gray-900">{item.count}</p>
              <p className="text-xs text-gray-600">{item.percentage.toFixed(1)}%</p>
            </div>
          ))}
      </div>
    </Card>
  );
}
