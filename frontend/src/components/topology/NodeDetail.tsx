import { useQuery } from '@tanstack/react-query';
import { getAsset } from '../../api/assets';
import { X } from 'lucide-react';

interface NodeDetailProps {
  assetId: string;
  onClose: () => void;
}

export default function NodeDetail({ assetId, onClose }: NodeDetailProps) {
  const { data: asset, isLoading } = useQuery({
    queryKey: ['asset', assetId],
    queryFn: () => getAsset(assetId),
  });

  return (
    <div className="w-96 bg-white shadow-xl border-l h-full overflow-y-auto">
      <div className="sticky top-0 bg-white border-b px-4 py-3 flex items-center justify-between">
        <h2 className="font-semibold text-gray-900">Asset Detail</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X size={20} />
        </button>
      </div>

      {isLoading ? (
        <div className="p-4 text-gray-500">Loading...</div>
      ) : asset ? (
        <div className="p-4 space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{asset.hostname}</h3>
            <p className="text-sm text-gray-500">{asset.ip_addresses?.join(', ')}</p>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-500">Type</span>
              <p className="font-medium capitalize">{asset.asset_type?.replace('_', ' ')}</p>
            </div>
            <div>
              <span className="text-gray-500">Status</span>
              <p className="font-medium capitalize">{asset.status}</p>
            </div>
            <div>
              <span className="text-gray-500">OS</span>
              <p className="font-medium">{asset.os_family} {asset.os_version || ''}</p>
            </div>
            <div>
              <span className="text-gray-500">Last Scanned</span>
              <p className="font-medium">{asset.last_scanned ? new Date(asset.last_scanned).toLocaleDateString() : 'N/A'}</p>
            </div>
          </div>

          {asset.open_ports && asset.open_ports.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Open Ports</h4>
              <div className="flex flex-wrap gap-1">
                {asset.open_ports.map((p: any, i: number) => (
                  <span key={i} className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded">
                    {p.port}/{p.protocol}
                  </span>
                ))}
              </div>
            </div>
          )}

          {(asset as any).business_context && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Business Context</h4>
              <div className="bg-gray-50 rounded p-3 text-sm space-y-1">
                <p><span className="text-gray-500">Purpose:</span> {(asset as any).business_context.purpose}</p>
                <p><span className="text-gray-500">Department:</span> {(asset as any).business_context.department}</p>
                <p><span className="text-gray-500">Criticality:</span> {(asset as any).business_context.criticality}</p>
              </div>
            </div>
          )}

          {(asset as any).tags && (asset as any).tags.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Tags</h4>
              <div className="flex flex-wrap gap-1">
                {(asset as any).tags.map((tag: string) => (
                  <span key={tag} className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="p-4 text-gray-500">Asset not found</div>
      )}
    </div>
  );
}
