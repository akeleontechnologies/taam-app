import React from 'react';
import { Filters, FilterOptions } from '@/lib/charts/types';

interface FilterPanelProps {
  filters: Filters;
  filterOptions: FilterOptions;
  onFilterChange: (filterType: string, value: string) => void;
}

export function FilterPanel({ filters, filterOptions, onFilterChange }: FilterPanelProps) {
  return (
    <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Age Group</label>
        <select
          className="w-full p-2 border border-gray-300 rounded-md text-sm"
          value={filters.age_group || 'all'}
          onChange={(e) => onFilterChange('age_group', e.target.value)}
        >
          <option value="all">All Ages</option>
          {filterOptions.age_groups.map((age) => (
            <option key={age} value={age}>
              {age}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
        <select
          className="w-full p-2 border border-gray-300 rounded-md text-sm"
          value={filters.gender || 'all'}
          onChange={(e) => onFilterChange('gender', e.target.value)}
        >
          <option value="all">All Genders</option>
          {filterOptions.genders.map((gender) => (
            <option key={gender} value={gender}>
              {gender}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Emirate</label>
        <select
          className="w-full p-2 border border-gray-300 rounded-md text-sm"
          value={filters.emirate || 'all'}
          onChange={(e) => onFilterChange('emirate', e.target.value)}
        >
          <option value="all">All Emirates</option>
          {filterOptions.emirates.map((emirate) => (
            <option key={emirate} value={emirate}>
              {emirate}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
