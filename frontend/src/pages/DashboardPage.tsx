import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Server, Network, Radar, Brain, GitCompare } from 'lucide-react';
import api from '../api/client';
import type { DashboardStats } from '../api/types';

const PIE_COLORS = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#6366f1'];

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const { data } = await api.get<DashboardStats>('/dashboard/stats');
      return data;
    },
  });

  if (isLoading || !stats) {
    return <div className="flex items-center justify-center h-64 text-gray-500">Loading dashboard...</div>;
  }

  const assetTypeData = Object.entries(stats.assets_by_type || {}).map(([name, value]) => ({
    name: name.replace('_', ' '),
    value,
  }));

  const relTypeData = Object.entries(stats.relationships_by_type || {}).map(([name, value]) => ({
    name: name.replace('_', ' '),
    value,
  }));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard icon={Server} label="Assets" value={stats.total_assets} color="blue" />
        <StatCard icon={Network} label="Relationships" value={stats.total_relationships} color="green" />
        <StatCard icon={Radar} label="Recent Scans" value={stats.recent_scans} color="purple" />
        <StatCard icon={Brain} label="Pending Suggestions" value={stats.pending_suggestions} color="yellow" />
        <StatCard icon={GitCompare} label="Drift Events" value={stats.drift_events} color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Assets by Type</h2>
          {assetTypeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={assetTypeData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={({ name, value }) => `${name} (${value})`}>
                  {assetTypeData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-8">No asset data yet</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Relationships by Type</h2>
          {relTypeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={relTypeData}>
                <XAxis dataKey="name" fontSize={11} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-8">No relationship data yet</p>
          )}
        </div>
      </div>

      {(stats.scan_activity?.length ?? 0) > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Scan Activity</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={stats.scan_activity}>
              <XAxis dataKey="date" fontSize={11} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

const COLOR_MAP: Record<string, string> = {
  blue: 'bg-blue-50 text-blue-600',
  green: 'bg-green-50 text-green-600',
  purple: 'bg-purple-50 text-purple-600',
  yellow: 'bg-yellow-50 text-yellow-600',
  red: 'bg-red-50 text-red-600',
};

function StatCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: number; color: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-4 flex items-center gap-4">
      <div className={`p-3 rounded-lg ${COLOR_MAP[color]}`}>
        <Icon className="h-6 w-6" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  );
}
