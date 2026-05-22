import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { generateExport } from '../api/exports';
import { Download } from 'lucide-react';

const FORMATS = [
  { value: 'drawio', label: 'Draw.io (XML)', description: 'Interactive diagrams editable in Draw.io/diagrams.net' },
  { value: 'csv', label: 'CSV', description: 'Spreadsheet-compatible format for assets and relationships' },
  { value: 'json', label: 'JSON', description: 'Machine-readable format with full detail' },
];

const ASSET_TYPES = ['server', 'database', 'app_server', 'application', 'api_endpoint', 'load_balancer'];
const REL_TYPES = ['connects_to', 'depends_on', 'hosts', 'queries', 'calls_api', 'authenticates_via'];

export default function ExportsPage() {
  const [format, setFormat] = useState('drawio');
  const [selectedAssetTypes, setSelectedAssetTypes] = useState<string[]>([]);
  const [selectedRelTypes, setSelectedRelTypes] = useState<string[]>([]);

  const mutation = useMutation({
    mutationFn: () => generateExport(
      format,
      selectedAssetTypes.length > 0 ? selectedAssetTypes : undefined,
      selectedRelTypes.length > 0 ? selectedRelTypes : undefined,
    ),
    onSuccess: (data) => {
      const blob = data instanceof Blob ? data : new Blob([data], { type: 'text/plain' });
      const ext = format === 'drawio' ? 'xml' : format;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ea-export-${new Date().toISOString().slice(0, 10)}.${ext}`;
      a.click();
      URL.revokeObjectURL(url);
    },
  });

  const toggleItem = (list: string[], item: string, setter: (v: string[]) => void) => {
    setter(list.includes(item) ? list.filter((i) => i !== item) : [...list, item]);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Export</h1>

      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        <div>
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Export Format</h2>
          <div className="grid grid-cols-3 gap-3">
            {FORMATS.map((f) => (
              <button
                key={f.value}
                onClick={() => setFormat(f.value)}
                className={`text-left p-4 border-2 rounded-lg transition ${
                  format === f.value ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <p className="text-sm font-medium">{f.label}</p>
                <p className="text-xs text-gray-500 mt-1">{f.description}</p>
              </button>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Asset Types (optional filter)</h2>
          <div className="flex flex-wrap gap-2">
            {ASSET_TYPES.map((t) => (
              <button
                key={t}
                onClick={() => toggleItem(selectedAssetTypes, t, setSelectedAssetTypes)}
                className={`px-3 py-1.5 text-xs rounded-full capitalize ${
                  selectedAssetTypes.includes(t)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {t.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Relationship Types (optional filter)</h2>
          <div className="flex flex-wrap gap-2">
            {REL_TYPES.map((t) => (
              <button
                key={t}
                onClick={() => toggleItem(selectedRelTypes, t, setSelectedRelTypes)}
                className={`px-3 py-1.5 text-xs rounded-full capitalize ${
                  selectedRelTypes.includes(t)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {t.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <Download className="h-4 w-4" />
          {mutation.isPending ? 'Generating...' : 'Generate Export'}
        </button>

        {mutation.isError && (
          <p className="text-sm text-red-600">Export failed. Make sure the backend is running.</p>
        )}
      </div>
    </div>
  );
}
