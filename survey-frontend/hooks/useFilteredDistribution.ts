import { useState, useCallback } from 'react';
import axios from 'axios';
import { API_ENDPOINTS, getAuthHeaders } from '@/lib/api';
import { Filters, ChartSpec } from '@/lib/charts/types';

interface UseFilteredDistributionReturn {
  filters: Filters;
  handleFilterChange: (
    filterType: string,
    value: string,
    distributionChart: ChartSpec,
    onUpdate: (updatedChart: ChartSpec) => void
  ) => Promise<void>;
}

export function useFilteredDistribution(datasetUid: string): UseFilteredDistributionReturn {
  const [filters, setFilters] = useState<Filters>({});

  const handleFilterChange = useCallback(
    async (
      filterType: string,
      value: string,
      distributionChart: ChartSpec,
      onUpdate: (updatedChart: ChartSpec) => void
    ) => {
      const newFilters = {
        ...filters,
        [filterType]: value === 'all' ? undefined : value,
      };
      setFilters(newFilters);

      // Fetch filtered distribution
      try {
        const params = new URLSearchParams();
        if (newFilters.age_group) params.append('age_group', newFilters.age_group);
        if (newFilters.gender) params.append('gender', newFilters.gender);
        if (newFilters.emirate) params.append('emirate', newFilters.emirate);

        const response = await axios.get(
          `${API_ENDPOINTS.charts.filteredDistribution(datasetUid)}?${params.toString()}`,
          { headers: getAuthHeaders() }
        );

        // Update the summary chart with filtered data
        const filteredDist = response.data.distribution;
        const updatedSummary = { ...distributionChart };
        updatedSummary.derived_metrics = {
          ...updatedSummary.derived_metrics,
          total_respondents: response.data.filtered_respondents,
          persona_distribution: filteredDist.reduce(
            (
              acc: Record<string, { count: number; percentage: number }>,
              item: { persona: string; count: number; percentage: number }
            ) => {
              acc[item.persona] = { count: item.count, percentage: item.percentage };
              return acc;
            },
            {}
          ),
        };

        onUpdate(updatedSummary);
      } catch (error) {
        console.error('Failed to fetch filtered distribution:', error);
      }
    },
    [filters, datasetUid]
  );

  return {
    filters,
    handleFilterChange,
  };
}
