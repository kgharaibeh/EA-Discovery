import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createScan } from '../../api/scans';

interface ScanWizardProps {
  onClose: () => void;
}

export default function ScanWizard({ onClose }: ScanWizardProps) {
  const [step, setStep] = useState(1);
  const [targets, setTargets] = useState('');
  const [scanType, setScanType] = useState('full');
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createScan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scans'] });
      onClose();
    },
  });

  const handleLaunch = () => {
    const targetList = targets
      .split('\n')
      .map((t) => t.trim())
      .filter(Boolean)
      .map((host) => ({ host, credential_id: '' }));
    mutation.mutate({ targets: targetList, scan_type: scanType } as any);
  };

  return (
    <div className="bg-white rounded-lg shadow-xl border p-6 max-w-xl mx-auto">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">New Scan</h2>

      {step === 1 && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Scan Type</label>
            <select
              value={scanType}
              onChange={(e) => setScanType(e.target.value)}
              className="w-full border-gray-300 rounded-lg text-sm"
            >
              <option value="full">Full Scan</option>
              <option value="infrastructure">Infrastructure Only</option>
              <option value="traffic">Traffic Analysis</option>
              <option value="filesystem">Filesystem Scan</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Targets (one per line: IP or hostname)
            </label>
            <textarea
              value={targets}
              onChange={(e) => setTargets(e.target.value)}
              rows={6}
              placeholder="10.0.1.10&#10;10.0.2.20&#10;weblogic-prod-01"
              className="w-full border-gray-300 rounded-lg text-sm font-mono"
            />
          </div>
          <div className="flex justify-end gap-3">
            <button onClick={onClose} className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
              Cancel
            </button>
            <button
              onClick={() => setStep(2)}
              disabled={!targets.trim()}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Review
            </button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <div className="bg-gray-50 rounded-lg p-4 text-sm">
            <p className="font-medium">Scan Type: <span className="capitalize">{scanType}</span></p>
            <p className="mt-2 font-medium">
              Targets: {targets.split('\n').filter(Boolean).length} host(s)
            </p>
            <pre className="mt-1 text-xs text-gray-600">{targets}</pre>
          </div>
          <div className="flex justify-end gap-3">
            <button onClick={() => setStep(1)} className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
              Back
            </button>
            <button
              onClick={handleLaunch}
              disabled={mutation.isPending}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {mutation.isPending ? 'Launching...' : 'Launch Scan'}
            </button>
          </div>
          {mutation.isError && (
            <p className="text-sm text-red-600">Error: {(mutation.error as Error).message}</p>
          )}
        </div>
      )}
    </div>
  );
}
