/**
 * API configuration and utilities
 */

interface UserData {
  id: number;
  email: string;
  firstname: string;
  lastname: string;
  full_name: string;
  is_active: boolean;
  is_staff?: boolean;
}

export type { UserData };

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const API_ENDPOINTS = {
  // Auth
  auth: {
    login: `${API_BASE_URL}/commons/auth/login/`,
    logout: `${API_BASE_URL}/commons/auth/logout/`,
    tokenStatus: `${API_BASE_URL}/commons/auth/token-status/`,
  },
  // Users
  users: {
    list: `${API_BASE_URL}/users/`,
    create: `${API_BASE_URL}/users/`,
    detail: (id: number) => `${API_BASE_URL}/users/${id}/`,
    me: `${API_BASE_URL}/users/me/`,
    adminList: `${API_BASE_URL}/users/admin/list/`,
    userDatasets: (id: number) => `${API_BASE_URL}/users/${id}/datasets/`,
    userCharts: (id: number) => `${API_BASE_URL}/users/${id}/charts/`,
  },
  // Datasets
  datasets: {
    list: `${API_BASE_URL}/datasets/`,
    upload: `${API_BASE_URL}/datasets/upload/`,
    detail: (uid: string) => `${API_BASE_URL}/datasets/${uid}/`,
    delete: (uid: string) => `${API_BASE_URL}/datasets/${uid}/`,
    profile: (uid: string) => `${API_BASE_URL}/datasets/${uid}/profile/`,
    records: (uid: string) => `${API_BASE_URL}/datasets/${uid}/records/`,
  },
  // Charts
  charts: {
    list: `${API_BASE_URL}/charts/`,
    summary: `${API_BASE_URL}/charts/summary/`,
    generate: `${API_BASE_URL}/charts/generate/`,
    detail: (uid: string) => `${API_BASE_URL}/charts/${uid}/`,
    select: (uid: string) => `${API_BASE_URL}/charts/${uid}/select/`,
    respondents: (datasetUid: string) => `${API_BASE_URL}/charts/dataset/${datasetUid}/respondents/`,
    filterOptions: (datasetUid: string) => `${API_BASE_URL}/charts/dataset/${datasetUid}/filter-options/`,
    filteredDistribution: (datasetUid: string) => `${API_BASE_URL}/charts/dataset/${datasetUid}/filtered-distribution/`,
  },
  // Selections
  selections: {
    list: `${API_BASE_URL}/selections/`,
    detail: (uid: string) => `${API_BASE_URL}/selections/${uid}/`,
  },
};

/**
 * Get auth token from localStorage
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/**
 * Set auth token in localStorage
 */
export function setAuthToken(token: string): void {
  localStorage.setItem('access_token', token);
}

/**
 * Remove auth token from localStorage
 */
export function removeAuthToken(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_data');
}

/**
 * Save user data to localStorage
 */
export function setUserData(userData: UserData): void {
  localStorage.setItem('user_data', JSON.stringify(userData));
}

/**
 * Get user data from localStorage
 */
export function getUserData(): UserData | null {
  if (typeof window === 'undefined') return null;
  const data = localStorage.getItem('user_data');
  return data ? JSON.parse(data) : null;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getAuthToken();
}

/**
 * Create axios instance with auth header
 */
export function getAuthHeaders() {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}
