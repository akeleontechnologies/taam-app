'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth-store';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { UploadCloud, BarChart3, Users, LogOut, Home } from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, fetchCurrentUser, logout, isLoading } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    fetchCurrentUser();
  }, [fetchCurrentUser]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  if (isLoading || !isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md">
        <div className="flex h-16 items-center border-b px-6">
          <h1 className="text-xl font-bold text-blue-600">TAAM Dashboard</h1>
        </div>
        
        <div className="flex flex-col justify-between h-[calc(100vh-4rem)]">
          <nav className="space-y-1 p-4">
            <Link
              href="/dashboard"
              className="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100"
            >
              <Home className="h-5 w-5" />
              Dashboard
            </Link>
            
            <Link
              href="/dashboard/upload"
              className="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100"
            >
              <UploadCloud className="h-5 w-5" />
              Upload Data
            </Link>
            
            <Link
              href="/dashboard/charts"
              className="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100"
            >
              <BarChart3 className="h-5 w-5" />
              Charts
            </Link>
            
            {user?.is_staff && (
              <Link
                href="/dashboard/users"
                className="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100"
              >
                <Users className="h-5 w-5" />
                Users
              </Link>
            )}
          </nav>

          <div className="border-t p-4">
            <div className="mb-4 px-3">
              <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
              <p className="text-xs text-gray-500">{user?.email}</p>
            </div>
            <Button
              onClick={handleLogout}
              className="w-full justify-start gap-3"
            >
              <LogOut className="h-5 w-5" />
              Logout
            </Button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
