import { useNavigate } from 'react-router-dom';
import type { Asset } from '../../api/types';

interface AssetTableProps {
  assets: Asset[];
  isLoading?: boolean;
}

const TYPE_COLORS: Record<string, string> = {
  server: 'bg-blue-100 text-blue-800',
  database: 'bg-green-100 text-green-800',
  app_server: 'bg-purple-100 text-purple-800',
  application: 'bg-yellow-100 text-yellow-800',
  api_endpoint: 'bg-red-100 text-red-800',
};

const STATUS_COLORS: Record<string, string> = {
  active: 'bg-emerald-100 text-emerald-800',
  inactive: 'bg-gray-100 text-gray-800',
  unknown: 'bg-amber-100 text-amber-800',
};

export default function AssetTable({ assets, isLoading }: AssetTableProps) {
  const navigate = useNavigate();

  if (isLoading) {
    return <div className="text-center py-8 text-gray-500">Loading assets...</div>;
  }

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hostname</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">OS</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ports</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Scanned</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {assets.map((asset) => (
            <tr
              key={asset.id}
              onClick={() => navigate(`/assets/${asset.id}`)}
              className="hover:bg-gray-50 cursor-pointer"
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="text-sm font-medium text-gray-900">{asset.hostname}</span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 text-xs rounded-full ${TYPE_COLORS[asset.asset_type] || 'bg-gray-100 text-gray-800'}`}>
                  {asset.asset_type?.replace('_', ' ')}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {asset.os_family || 'N/A'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 text-xs rounded-full ${STATUS_COLORS[asset.status] || 'bg-gray-100'}`}>
                  {asset.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {asset.ip_addresses?.[0] || 'N/A'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {asset.open_ports?.length || 0}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {asset.last_scanned ? new Date(asset.last_scanned).toLocaleDateString() : 'Never'}
              </td>
            </tr>
          ))}
          {assets.length === 0 && (
            <tr>
              <td colSpan={7} className="px-6 py-8 text-center text-gray-500">No assets found</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
