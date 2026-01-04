import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_ENDPOINTS, getAuthHeaders } from '@/lib/api';
import { ChartSpec, Dataset, FilterOptions } from '@/lib/charts/types';
import { CHARTS_PER_PAGE } from '@/lib/charts/constants';

interface UseChartDataReturn {
  dataset: Dataset | null;
  charts: ChartSpec[];
  summaryCharts: ChartSpec[];
  filterOptions: FilterOptions;
  loading: boolean;
  loadingMore: boolean;
  hasMore: boolean;
  currentPage: number;
  loadMore: () => void;
  refetchSummary: () => Promise<void>;
  updateSummaryChart: (updatedChart: ChartSpec) => void;
}

export function useChartData(datasetUid: string): UseChartDataReturn {
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [charts, setCharts] = useState<ChartSpec[]>([]);
  const [summaryCharts, setSummaryCharts] = useState<ChartSpec[]>([]);
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    age_groups: [],
    genders: [],
    emirates: [],
  });
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const fetchData = useCallback(
    async (page = 1, append = false) => {
      try {
        if (page === 1) {
          setLoading(true);

          // Fetch dataset details
          const datasetResponse = await axios.get(
            API_ENDPOINTS.datasets.detail(datasetUid),
            { headers: getAuthHeaders() }
          );
          setDataset(datasetResponse.data);

          // Fetch summary charts (distribution + heatmaps) from database
          const summaryResponse = await axios.get(API_ENDPOINTS.charts.list, {
            headers: getAuthHeaders(),
            params: {
              dataset: datasetUid,
              page_size: 100, // Get all summary charts
            },
          });
          const summaryData = summaryResponse.data.results || summaryResponse.data;
          setSummaryCharts(summaryData);

          // Fetch filter options
          const filterOptsResponse = await axios.get(
            API_ENDPOINTS.charts.filterOptions(datasetUid),
            { headers: getAuthHeaders() }
          );
          setFilterOptions(filterOptsResponse.data);
        } else {
          setLoadingMore(true);
        }

        // Fetch respondent charts from the new on-demand endpoint
        const chartsResponse = await axios.get(
          API_ENDPOINTS.charts.respondents(datasetUid),
          {
            headers: getAuthHeaders(),
            params: {
              page: page,
              page_size: CHARTS_PER_PAGE,
            },
          }
        );

        const newCharts = chartsResponse.data.results || [];

        if (append) {
          setCharts((prev) => [...prev, ...newCharts]);
        } else {
          setCharts(newCharts);
        }

        // Check if there are more pages
        setHasMore(chartsResponse.data.next === true);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    },
    [datasetUid]
  );

  useEffect(() => {
    fetchData(1, false);
  }, [fetchData]);

  const loadMore = useCallback(() => {
    const nextPage = currentPage + 1;
    setCurrentPage(nextPage);
    fetchData(nextPage, true);
  }, [currentPage, fetchData]);

  const refetchSummary = useCallback(async () => {
    try {
      const summaryResponse = await axios.get(API_ENDPOINTS.charts.list, {
        headers: getAuthHeaders(),
        params: {
          dataset: datasetUid,
          page_size: 100,
        },
      });
      const summaryData = summaryResponse.data.results || summaryResponse.data;
      setSummaryCharts(summaryData);
    } catch (error) {
      console.error('Failed to refetch summary:', error);
    }
  }, [datasetUid]);

  const updateSummaryChart = useCallback((updatedChart: ChartSpec) => {
    setSummaryCharts((prev) =>
      prev.map((chart) =>
        chart.chart_type === updatedChart.chart_type ? updatedChart : chart
      )
    );
  }, []);

  return {
    dataset,
    charts,
    summaryCharts,
    filterOptions,
    loading,
    loadingMore,
    hasMore,
    currentPage,
    loadMore,
    refetchSummary,
    updateSummaryChart,
  };
}
