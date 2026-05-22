import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listScans } from '../api/scans';
import ScanHistory from '../components/scans/ScanHistory';
import ScanWizard from '../components/scans/ScanWizard';

export default function ScansPage() {
  const [showWizard, setShowWizard] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['scans'],
    queryFn: () => listScans(),
    refetchInterval: 5000,
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Scans</h1>
        <button
          onClick={() => setShowWizard(true)}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
        >
          New Scan
        </button>
      </div>

      {showWizard && (
        <ScanWizard onClose={() => setShowWizard(false)} />
      )}

      <ScanHistory scans={data?.items || []} isLoading={isLoading} />
    </div>
  );
}
