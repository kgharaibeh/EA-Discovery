import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listAssets, type AssetFilters } from '../api/assets';
import AssetTable from '../components/assets/AssetTable';
import AssetSearch from '../components/assets/AssetSearch';

export default function AssetsPage() {
  const [filters, setFilters] = useState<AssetFilters>({ page: 1, size: 20 });
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['assets', filters],
    queryFn: () => listAssets(filters),
  });

  const handleSearchChange = (q: string) => {
    setSearchQuery(q);
    setFilters((f) => ({ ...f, search: q || undefined, page: 1 }));
  };

  const handleTypeChange = (t: string | null) => {
    setTypeFilter(t);
    setFilters((f) => ({ ...f, asset_type: t || undefined, page: 1 }));
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Assets</h1>
        <span className="text-sm text-gray-500">{data?.total ?? 0} total</span>
      </div>

      <AssetSearch
        query={searchQuery}
        onQueryChange={handleSearchChange}
        typeFilter={typeFilter}
        onTypeChange={handleTypeChange}
      />

      <AssetTable assets={data?.items || []} isLoading={isLoading} />

      {data && data.pages > 1 && (
        <div className="flex items-center justify-center gap-2 py-4">
          <button
            disabled={filters.page === 1}
            onClick={() => setFilters((f) => ({ ...f, page: (f.page || 1) - 1 }))}
            className="px-3 py-1.5 text-sm border rounded disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-gray-600">
            Page {filters.page || 1} of {data.pages}
          </span>
          <button
            disabled={(filters.page || 1) >= data.pages}
            onClick={() => setFilters((f) => ({ ...f, page: (f.page || 1) + 1 }))}
            className="px-3 py-1.5 text-sm border rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
