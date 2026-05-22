import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getAsset } from '../api/assets';
import { listRelationships } from '../api/relationships';
import AssetDetail from '../components/assets/AssetDetail';
import { ArrowLeft } from 'lucide-react';

export default function AssetDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: asset, isLoading: assetLoading } = useQuery({
    queryKey: ['asset', id],
    queryFn: () => getAsset(id!),
    enabled: !!id,
  });

  const { data: relationships } = useQuery({
    queryKey: ['asset-relationships', id],
    queryFn: () => listRelationships(id!),
    enabled: !!id,
  });

  if (assetLoading) {
    return <div className="text-center py-8 text-gray-500">Loading asset...</div>;
  }

  if (!asset) {
    return <div className="text-center py-8 text-gray-500">Asset not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/assets" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{asset.hostname}</h1>
          <p className="text-sm text-gray-500">{asset.ip_addresses?.join(', ')}</p>
        </div>
        <span className={`ml-auto px-3 py-1 rounded-full text-sm capitalize ${
          asset.status === 'active' ? 'bg-green-100 text-green-800' :
          asset.status === 'inactive' ? 'bg-gray-100 text-gray-800' :
          'bg-red-100 text-red-800'
        }`}>
          {asset.status}
        </span>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <AssetDetail asset={asset} />
      </div>

      {relationships && relationships.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Relationships ({relationships.length})</h2>
          <div className="space-y-2">
            {relationships.map((rel) => (
              <div key={rel.id} className="flex items-center justify-between py-2 border-b last:border-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                    {rel.relationship_type.replace('_', ' ')}
                  </span>
                  <span className="text-sm text-gray-600">
                    {rel.source_asset_id === id ? 'to' : 'from'}{' '}
                    <Link
                      to={`/assets/${rel.source_asset_id === id ? rel.target_asset_id : rel.source_asset_id}`}
                      className="text-blue-600 hover:underline"
                    >
                      {rel.source_asset_id === id ? rel.target_asset_id : rel.source_asset_id}
                    </Link>
                  </span>
                </div>
                <span className="text-xs text-gray-400">
                  {Math.round(rel.confidence * 100)}% confidence
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
