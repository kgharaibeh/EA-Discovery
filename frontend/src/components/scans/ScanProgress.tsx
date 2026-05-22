import type { Scan } from '../../api/types';

interface ScanProgressProps {
  scan: Scan;
}

export default function ScanProgress({ scan }: ScanProgressProps) {
  const s = scan as any;
  const total = s.total_targets || s.targets?.length || 1;
  const completed = s.completed_targets || 0;
  const percent = Math.round((completed / total) * 100);

  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">Scan Progress</span>
        <StatusBadge status={scan.status} />
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${percent}%` }}
        />
      </div>
      <p className="text-xs text-gray-500 mt-1">
        {completed} / {total} targets completed ({percent}%)
      </p>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800',
  };
  return (
    <span className={`px-2 py-0.5 text-xs rounded-full ${colors[status] || 'bg-gray-100'}`}>
      {status}
    </span>
  );
}
