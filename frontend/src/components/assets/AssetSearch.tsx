import { Search } from 'lucide-react';

interface AssetSearchProps {
  query: string;
  onQueryChange: (q: string) => void;
  typeFilter: string | null;
  onTypeChange: (t: string | null) => void;
}

const ASSET_TYPES = ['server', 'database', 'app_server', 'application', 'api_endpoint'];

export default function AssetSearch({ query, onQueryChange, typeFilter, onTypeChange }: AssetSearchProps) {
  return (
    <div className="flex gap-3 items-center">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search assets by hostname, IP, or tag..."
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
        />
      </div>
      <select
        value={typeFilter || ''}
        onChange={(e) => onTypeChange(e.target.value || null)}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
      >
        <option value="">All Types</option>
        {ASSET_TYPES.map((t) => (
          <option key={t} value={t}>
            {t.replace('_', ' ')}
          </option>
        ))}
      </select>
    </div>
  );
}
