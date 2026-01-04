import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { ChartSpec } from '@/lib/charts/types';
import { PERSONA_COLORS } from '@/lib/charts/constants';

interface RespondentRadarCardProps {
  chart: ChartSpec;
}

export function RespondentRadarCard({ chart }: RespondentRadarCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const config = chart.chart_config;
  const userData = config.user_data || [];
  const canonicalData = config.canonical_data || [];
  const surveyAnswers = chart.derived_metrics?.survey_answers || {};

  return (
    <Card className="p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold">{config.title}</h3>
        <div className="flex items-center gap-2 mt-2">
          <div
            className="w-4 h-4 rounded-full"
            style={{ backgroundColor: PERSONA_COLORS[config.persona_code || ''] }}
          />
          <span className="text-sm font-medium text-gray-700">
            {config.persona_name}
          </span>
        </div>
        {config.persona_description && (
          <p className="text-xs text-gray-600 mt-1">{config.persona_description}</p>
        )}
      </div>

      <ResponsiveContainer width="100%" height={350}>
        <RadarChart data={userData.length > 0 ? userData : canonicalData}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis dataKey="axis" tick={{ fill: '#374151', fontSize: 11 }} />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 5]}
            tick={{ fill: '#6b7280', fontSize: 10 }}
          />
          <Radar
            name={config.persona_name || 'Profile'}
            dataKey="value"
            stroke="#1e40af"
            fill="#1e40af"
            fillOpacity={0.5}
          />
          <Legend />
          <Tooltip />
        </RadarChart>
      </ResponsiveContainer>

      {/* More Details Button */}
      <div className="mt-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full"
        >
          {isExpanded ? 'Hide Details' : 'More Details'}
        </Button>
      </div>

      {/* Survey Answers Details */}
      {isExpanded && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200 max-h-96 overflow-y-auto">
          <h4 className="font-semibold text-sm text-gray-900 mb-3">Survey Answers</h4>
          <div className="space-y-2">
            {Object.entries(surveyAnswers).map(([question, answer]) => (
              <div key={question} className="text-xs">
                <span className="font-medium text-gray-700">{question}:</span>
                <span className="ml-2 text-gray-600">{String(answer)}</span>
              </div>
            ))}
            {Object.keys(surveyAnswers).length === 0 && (
              <p className="text-xs text-gray-500 italic">No survey answers available</p>
            )}
          </div>

          {/* Computed Axes Values */}
          <h4 className="font-semibold text-sm text-gray-900 mt-4 mb-3">Computed Axes</h4>
          <div className="space-y-2">
            {userData.map((axis: { axis: string; value: number; percent: number }) => (
              <div key={axis.axis} className="flex justify-between text-xs">
                <span className="font-medium text-gray-700">{axis.axis}:</span>
                <span className="text-gray-600">
                  {axis.value.toFixed(2)} ({axis.percent}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
