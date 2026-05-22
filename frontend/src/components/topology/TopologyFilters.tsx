import { useTopologyStore } from '../../stores/useTopologyStore';

const ASSET_TYPES = [
  { value: 'server', label: 'Servers', color: '#dae8fc' },
  { value: 'database', label: 'Databases', color: '#d5e8d4' },
  { value: 'app_server', label: 'App Servers', color: '#e1d5e7' },
  { value: 'application', label: 'Applications', color: '#fff2cc' },
  { value: 'api_endpoint', label: 'API Endpoints', color: '#f8cecc' },
];

const REL_TYPES = [
  { value: 'queries', label: 'Queries', color: '#2563eb' },
  { value: 'calls_api', label: 'Calls API', color: '#16a34a' },
  { value: 'connects_to', label: 'Connects To', color: '#6b7280' },
  { value: 'depends_on', label: 'Depends On', color: '#ea580c' },
  { value: 'authenticates_via', label: 'Authenticates', color: '#7c3aed' },
  { value: 'hosts', label: 'Hosts', color: '#9ca3af' },
];

export default function TopologyFilters() {
  const { assetTypeFilters, relationshipTypeFilters, toggleAssetTypeFilter, toggleRelationshipTypeFilter, resetFilters } =
    useTopologyStore();

  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">Filters</h3>
        <button onClick={resetFilters} className="text-xs text-blue-600 hover:text-blue-800">
          Reset
        </button>
      </div>

      <div>
        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">Asset Types</h4>
        <div className="space-y-1">
          {ASSET_TYPES.map((t) => (
            <label key={t.value} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={assetTypeFilters.length === 0 || assetTypeFilters.includes(t.value)}
                onChange={() => toggleAssetTypeFilter(t.value)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: t.color }} />
              <span className="text-sm text-gray-700">{t.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">Relationships</h4>
        <div className="space-y-1">
          {REL_TYPES.map((t) => (
            <label key={t.value} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={relationshipTypeFilters.length === 0 || relationshipTypeFilters.includes(t.value)}
                onChange={() => toggleRelationshipTypeFilter(t.value)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: t.color }} />
              <span className="text-sm text-gray-700">{t.label}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
