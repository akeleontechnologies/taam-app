'use client';

import { useParams, useRouter } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2, TrendingUp } from 'lucide-react';
import { useChartData } from '@/hooks/useChartData';
import { useFilteredDistribution } from '@/hooks/useFilteredDistribution';
import { RespondentRadarCard } from '@/components/charts/RespondentRadarCard';
import { DistributionChart } from '@/components/charts/DistributionChart';
import { CHARTS_PER_PAGE } from '@/lib/charts/constants';

export default function ChartViewPage() {
  const params = useParams();
  const router = useRouter();
  const datasetUid = params.uid as string;

  // Use custom hooks for data fetching
  const {
    dataset,
    charts: respondentCharts,
    summaryCharts,
    filterOptions,
    loading,
    loadingMore,
    hasMore,
    loadMore,
    updateSummaryChart,
  } = useChartData(datasetUid);

  const { filters, handleFilterChange } = useFilteredDistribution(datasetUid);

  const distributionChart = summaryCharts.find((c) => c.chart_type === 'persona_distribution');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!dataset) {
    return (
      <div className="max-w-4xl">
        <Card className="p-12 text-center">
          <h3 className="text-lg font-medium bg-black text-white mb-2">Dataset not found</h3>
          <Button onClick={() => router.push('/dashboard/charts')}>Back to Charts</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-7xl">
      <div className="mb-8">
        <Button
          onClick={() => router.push('/dashboard/charts')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Charts
        </Button>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {dataset.filename}
        </h1>
        <p className="text-gray-600">
          {distributionChart?.derived_metrics?.total_respondents || dataset.row_count} total respondents
          {respondentCharts.length > 0 && ` • Showing ${respondentCharts.length} charts`}
        </p>
      </div>

      {/* Summary Statistics */}
      {distributionChart && (
        <DistributionChart
          distributionChart={distributionChart}
          filters={filters}
          filterOptions={filterOptions}
          onFilterChange={(filterType, value) => {
            if (!distributionChart) return;
            handleFilterChange(filterType, value, distributionChart, updateSummaryChart);
          }}
        />
      )}

      {/* Individual Respondent Charts */}
      {respondentCharts.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp className="h-6 w-6" />
            Individual Respondent Analysis
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {respondentCharts.map((chart) => (
              <RespondentRadarCard key={chart.uid} chart={chart} />
            ))}
          </div>

          {/* Load More Button */}
          {hasMore && (
            <div className="mt-8 text-center">
              <Button onClick={loadMore} disabled={loadingMore} className="min-w-[200px]">
                {loadingMore ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Loading more...
                  </>
                ) : (
                  `Load More Charts (${CHARTS_PER_PAGE} at a time)`
                )}
              </Button>
              <p className="text-sm text-gray-600 mt-2">
                Showing {respondentCharts.length} of {dataset.row_count} respondents
              </p>
            </div>
          )}
        </div>
      )}

      {respondentCharts.length === 0 && (
        <Card className="p-12 text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No charts generated yet
          </h3>
          <Button onClick={() => router.push('/dashboard/charts')}>Back to Charts</Button>
        </Card>
      )}
    </div>
  );
}
