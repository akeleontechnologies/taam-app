'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2, Database, BarChart3, FileText, Calendar } from 'lucide-react';
import axios from 'axios';
import { API_ENDPOINTS, getAuthHeaders } from '@/lib/api';
import { useAuthStore } from '@/store/auth-store';

interface User {
  id: number;
  email: string;
  firstname: string;
  lastname: string;
  full_name: string;
  is_staff: boolean;
}

interface Dataset {
  uid: string;
  filename: string;
  row_count: number;
  created_at: string;
  parsed_ok: boolean;
}

interface ChartSpec {
  uid: string;
  chart_type: string;
  created_at: string;
  dataset_uid: string;
  dataset_filename: string;
}

export default function UserDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user: currentUser } = useAuthStore();
  const [user, setUser] = useState<User | null>(null);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [charts, setCharts] = useState<ChartSpec[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchUserData = useCallback(async () => {
    try {
      setLoading(true);
      const userId = params.id;

      // Fetch user details
      const userResponse = await axios.get(
        API_ENDPOINTS.users.detail(Number(userId)),
        { headers: getAuthHeaders() }
      );
      setUser(userResponse.data);

      // Fetch user's datasets
      const datasetsResponse = await axios.get(
        API_ENDPOINTS.users.userDatasets(Number(userId)),
        { headers: getAuthHeaders() }
      );
      setDatasets(datasetsResponse.data.datasets || datasetsResponse.data.results || []);

      // Fetch user's charts
      const chartsResponse = await axios.get(
        API_ENDPOINTS.users.userCharts(Number(userId)),
        { headers: getAuthHeaders() }
      );
      setCharts(chartsResponse.data.charts || chartsResponse.data.results || []);
    } catch (error) {
      console.error('Failed to fetch user data:', error);
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    fetchUserData();
  }, [fetchUserData]);

  if (!currentUser?.is_staff) {
    return (
      <div className="max-w-6xl mx-auto">
        <Card className="p-12 text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
          <p className="text-gray-600">
            You need administrator privileges to view this page
          </p>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="max-w-6xl mx-auto">
        <Card className="p-12 text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">User Not Found</h3>
          <p className="text-gray-600 mb-6">The requested user could not be found</p>
          <Button onClick={() => router.push('/dashboard/users')}>
            Back to Users
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <Button
        onClick={() => router.push('/dashboard/users')}
        className="mb-4"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Users
      </Button>

      {/* User Info Header */}
      <Card className="p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {user.full_name || user.email}
            </h1>
            <p className="text-gray-600 mb-4">{user.email}</p>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span className="flex items-center gap-1">
                <Database className="h-4 w-4" />
                {datasets.length} dataset{datasets.length !== 1 ? 's' : ''}
              </span>
              <span className="flex items-center gap-1">
                <BarChart3 className="h-4 w-4" />
                {charts.length} chart{charts.length !== 1 ? 's' : ''}
              </span>
            </div>
          </div>
          {user.is_staff && (
            <span className="px-3 py-1 text-sm font-medium bg-blue-100 text-blue-700 rounded">
              Admin
            </span>
          )}
        </div>
      </Card>

      {/* Datasets Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Datasets</h2>
        {datasets.length === 0 ? (
          <Card className="p-8 text-center">
            <Database className="h-10 w-10 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">No datasets uploaded yet</p>
          </Card>
        ) : (
          <div className="space-y-3">
            {datasets.map((dataset) => (
              <Card key={dataset.uid} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-blue-600" />
                    <div>
                      <h3 className="font-medium text-gray-900">{dataset.filename}</h3>
                      <div className="flex items-center gap-3 text-sm text-gray-600">
                        <span>{dataset.row_count} rows</span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(dataset.created_at).toLocaleDateString()}
                        </span>
                        <span>•</span>
                        <span
                          className={
                            dataset.parsed_ok ? 'text-green-600' : 'text-red-600'
                          }
                        >
                          {dataset.parsed_ok ? 'Parsed' : 'Parse Failed'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Charts Section */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Charts</h2>
        {charts.length === 0 ? (
          <Card className="p-8 text-center">
            <BarChart3 className="h-10 w-10 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">No charts generated yet</p>
          </Card>
        ) : (
          <div className="space-y-3">
            {charts.map((chart) => (
              <Card key={chart.uid} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <BarChart3 className="h-5 w-5 text-green-600" />
                    <div>
                      <h3 className="font-medium text-gray-900">
                        {chart.chart_type.replace(/_/g, ' ').toUpperCase()}
                      </h3>
                      <div className="flex items-center gap-3 text-sm text-gray-600">
                        <span>{chart.dataset_filename}</span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(chart.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      router.push(`/dashboard/charts/${chart.dataset_uid}`)
                    }
                  >
                    View Chart
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
