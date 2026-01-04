'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Users, Loader2, Database, BarChart3 } from 'lucide-react';
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
  dataset_count?: number;
  chart_count?: number;
}

export default function UsersPage() {
  const { user } = useAuthStore();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(API_ENDPOINTS.users.adminList, {
        headers: getAuthHeaders(),
      });
      setUsers(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user?.is_staff) {
    return (
      <div className="max-w-4xl">
        <Card className="p-12 text-center">
          <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Access Denied
          </h3>
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

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Users</h1>
      <p className="text-gray-600 mb-8">
        Manage users and view their uploaded datasets
      </p>

      <div className="space-y-4">
        {users.map((u) => (
          <Card key={u.id} className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-semibold text-gray-900">
                    {u.full_name || u.email}
                  </h3>
                  {u.is_staff && (
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">
                      Admin
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-3">{u.email}</p>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <Database className="h-4 w-4" />
                    {u.dataset_count || 0} datasets
                  </span>
                  <span className="flex items-center gap-1">
                    <BarChart3 className="h-4 w-4" />
                    {u.chart_count || 0} charts
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  onClick={() =>
                    (window.location.href = `/dashboard/users/${u.id}`)
                  }
                >
                  View Data
                </Button>
              </div>
            </div>
          </Card>
        ))}

        {users.length === 0 && (
          <Card className="p-12 text-center">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No users found
            </h3>
            <p className="text-gray-600">No users have been registered yet</p>
          </Card>
        )}
      </div>
    </div>
  );
}
