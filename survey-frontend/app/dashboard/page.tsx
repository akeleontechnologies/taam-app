'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { UploadCloud, BarChart3, Users } from 'lucide-react';
import { useAuthStore } from '@/store/auth-store';

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.firstname || 'User'}!
        </h1>
        <p className="mt-2 text-gray-600">
          Manage your TAAM survey data and analytics
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-blue-100 p-3">
                <UploadCloud className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <CardTitle>Upload Dataset</CardTitle>
                <CardDescription>Import CSV or XLSX files</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/upload">
              <Button className="w-full">Go to Upload</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-green-100 p-3">
                <BarChart3 className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <CardTitle>View Charts</CardTitle>
                <CardDescription>Explore your analytics</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/charts">
              <Button className="w-full" variant="outline">View Charts</Button>
            </Link>
          </CardContent>
        </Card>

        {user?.is_staff && (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-purple-100 p-3">
                  <Users className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <CardTitle>Manage Users</CardTitle>
                  <CardDescription>Admin panel</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Link href="/dashboard/users">
                <Button className="w-full" variant="outline">Manage Users</Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
          <CardDescription>Quick guide to using the TAAM Dashboard</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-medium mb-2">1. Upload Your Data</h3>
            <p className="text-sm text-gray-600">
              Start by uploading a CSV or XLSX file containing your TAAM survey responses.
              The system will automatically detect TAAM questions and persona data.
            </p>
          </div>
          <div>
            <h3 className="font-medium mb-2">2. Generate Charts</h3>
            <p className="text-sm text-gray-600">
              Once uploaded, the system will generate personalized radar charts, heatmaps,
              and distribution charts based on the TAAM persona framework.
            </p>
          </div>
          <div>
            <h3 className="font-medium mb-2">3. Explore Insights</h3>
            <p className="text-sm text-gray-600">
              View canonical persona profiles, compare against observed data, and analyze
              demographic distributions across different personas.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
