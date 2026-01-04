/**
 * Chart-related TypeScript interfaces and types
 */

export interface ChartSpec {
  uid: string;
  chart_type: string;
  chart_config: {
    title?: string;
    respondent_index?: number;
    persona_code?: string;
    persona_name?: string;
    persona_description?: string;
    user_data?: Array<{ axis: string; value: number; percent: number }>;
    canonical_data?: Array<{ axis: string; value: number; percent: number }>;
    axes?: string[];
    data?: Record<string, unknown>;
  };
  derived_metrics: {
    respondent_index?: number;
    persona_code?: string;
    persona_name?: string;
    total_respondents?: number;
    persona_distribution?: Record<string, { count: number; percentage: number }>;
    survey_answers?: Record<string, string | number | boolean>;
  };
  is_canonical: boolean;
}

export interface Dataset {
  uid: string;
  filename: string;
  row_count: number;
}

export interface FilterOptions {
  age_groups: string[];
  genders: string[];
  emirates: string[];
}

export interface Filters {
  age_group?: string;
  gender?: string;
  emirate?: string;
}

export interface PersonaDistribution {
  persona: string;
  count: number;
  percentage: number;
}
