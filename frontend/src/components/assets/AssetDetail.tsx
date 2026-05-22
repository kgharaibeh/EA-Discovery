import { useState } from 'react';
import type { Asset } from '../../api/types';

interface AssetDetailProps {
  asset: Asset;
}

const TABS = ['Overview', 'Ports', 'Services', 'Software', 'Config', 'AI Context'];

export default function AssetDetail({ asset }: AssetDetailProps) {
  const [activeTab, setActiveTab] = useState('Overview');
  const a = asset as any;

  return (
    <div>
      <div className="border-b border-gray-200">
        <nav className="flex space-x-6 px-1" aria-label="Tabs">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-3 px-1 text-sm font-medium border-b-2 ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      <div className="mt-4">
        {activeTab === 'Overview' && (
          <div className="grid grid-cols-2 gap-4">
            <InfoCard label="Hostname" value={asset.hostname} />
            <InfoCard label="IP Addresses" value={asset.ip_addresses?.join(', ')} />
            <InfoCard label="Type" value={asset.asset_type?.replace('_', ' ')} />
            <InfoCard label="Status" value={asset.status} />
            <InfoCard label="OS" value={`${asset.os_family || ''} ${asset.os_version || ''}`} />
            <InfoCard label="Last Scanned" value={asset.last_scanned ? new Date(asset.last_scanned).toLocaleString() : 'N/A'} />
            {a.app_server_type && <InfoCard label="App Server" value={a.app_server_type} />}
            {a.db_engine && <InfoCard label="Database Engine" value={`${a.db_engine} ${a.db_version || ''}`} />}
          </div>
        )}

        {activeTab === 'Ports' && (
          <SimpleTable
            headers={['Port', 'Protocol', 'Service']}
            rows={(asset.open_ports || []).map((p: any) => [p.port, p.protocol || 'tcp', p.service || 'N/A'])}
          />
        )}

        {activeTab === 'Services' && (
          <SimpleTable
            headers={['Name', 'PID', 'User']}
            rows={(a.running_services || []).map((s: any) => [s.name, s.pid || '', s.user || ''])}
          />
        )}

        {activeTab === 'Software' && (
          <SimpleTable
            headers={['Name', 'Version']}
            rows={(a.installed_software || []).map((s: any) => [s.name, s.version || ''])}
          />
        )}

        {activeTab === 'Config' && (
          <SimpleTable
            headers={['Path', 'Type']}
            rows={(a.config_files || []).map((c: any) => [c.path, c.type || ''])}
          />
        )}

        {activeTab === 'AI Context' && (
          <div>
            {a.business_context ? (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
                <p><span className="font-medium">Purpose:</span> {a.business_context.purpose}</p>
                <p><span className="font-medium">Department:</span> {a.business_context.department}</p>
                <p><span className="font-medium">Criticality:</span> {a.business_context.criticality}</p>
                {a.business_context.application_name && (
                  <p><span className="font-medium">Application:</span> {a.business_context.application_name}</p>
                )}
                <p className="text-xs text-gray-500 mt-2">
                  {a.human_verified ? 'Verified by human' : 'AI-inferred, pending review'}
                </p>
              </div>
            ) : (
              <p className="text-gray-500">No AI context available yet. Run intelligence analysis to generate suggestions.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-sm font-medium text-gray-900 mt-0.5 capitalize">{value || 'N/A'}</p>
    </div>
  );
}

function SimpleTable({ headers, rows }: { headers: string[]; rows: any[][] }) {
  return (
    <div className="bg-white rounded-lg border overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {headers.map((h) => (
              <th key={h} className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {rows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td key={j} className="px-4 py-2 text-sm text-gray-700">{String(cell)}</td>
              ))}
            </tr>
          ))}
          {rows.length === 0 && (
            <tr><td colSpan={headers.length} className="px-4 py-4 text-center text-gray-500 text-sm">No data</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
