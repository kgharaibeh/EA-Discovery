import type { DriftEvent } from '../../api/types';

interface DriftDiffProps {
  event: DriftEvent;
}

export default function DriftDiff({ event }: DriftDiffProps) {
  const formatValue = (val: unknown): string => {
    if (val === null || val === undefined) return '(empty)';
    if (typeof val === 'object') return JSON.stringify(val, null, 2);
    return String(val);
  };

  return (
    <div className="bg-white border rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xs font-medium text-purple-600 bg-purple-50 px-2 py-0.5 rounded">
          {event.drift_type}
        </span>
        <span className="text-sm font-medium text-gray-700">{event.field}</span>
        <span className="text-xs text-gray-400 ml-auto">
          {new Date(event.detected_at).toLocaleString()}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-xs font-medium text-red-600 mb-1">Previous</p>
          <pre className="bg-red-50 border border-red-200 rounded p-2 text-xs text-gray-700 overflow-auto max-h-32">
            {formatValue(event.old_value)}
          </pre>
        </div>
        <div>
          <p className="text-xs font-medium text-green-600 mb-1">Current</p>
          <pre className="bg-green-50 border border-green-200 rounded p-2 text-xs text-gray-700 overflow-auto max-h-32">
            {formatValue(event.new_value)}
          </pre>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between">
        <span className="text-xs text-gray-500">
          Asset: <span className="font-medium">{event.asset_hostname}</span>
        </span>
        {event.acknowledged && (
          <span className="text-xs text-green-600">
            Acknowledged{event.acknowledged_by ? ` by ${event.acknowledged_by}` : ''}
          </span>
        )}
      </div>
    </div>
  );
}
