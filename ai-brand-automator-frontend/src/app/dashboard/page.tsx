'use client';

import { OverviewCards } from '@/components/dashboard/OverviewCards';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { useAuth } from '@/hooks/useAuth';

export default function DashboardPage() {
  useAuth(); // Protect this route
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <OverviewCards />
            <div className="mt-6">
              <RecentActivity />
            </div>
          </div>
          <div>
            <QuickActions />
          </div>
        </div>
      </div>
    </div>
  );
}