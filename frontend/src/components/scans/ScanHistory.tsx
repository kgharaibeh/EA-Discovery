import type { Scan } from '../../api/types';

interface ScanHistoryProps {
  scans: Scan[];
  isLoading?: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  running: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-800',
};

export default function ScanHistory({ scans, isLoading }: ScanHistoryProps) {
  if (isLoading) {
    return <div className="text-center py-8 text-gray-500">Loading scans...</div>;
  }

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Targets</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Assets Found</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Relationships</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Started</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {scans.map((scan) => {
            const s = scan as any;
            return (
              <tr key={scan.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm capitalize">{s.scan_type || scan.scan_type}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded-full ${STATUS_COLORS[scan.status]}`}>
                    {scan.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">{s.total_targets || scan.targets?.length || 0}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{scan.assets_discovered || 0}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{scan.relationships_discovered || 0}</td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {scan.started_at ? new Date(scan.started_at).toLocaleString() : 'Pending'}
                </td>
              </tr>
            );
          })}
          {scans.length === 0 && (
            <tr><td colSpan={6} className="px-6 py-8 text-center text-gray-500">No scans yet</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
