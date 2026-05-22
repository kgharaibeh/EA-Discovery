const LEGEND_ITEMS = [
  { label: 'Server', color: '#dae8fc', shape: 'rounded' },
  { label: 'Database', color: '#d5e8d4', shape: 'circle' },
  { label: 'App Server', color: '#e1d5e7', shape: 'rounded' },
  { label: 'Application', color: '#fff2cc', shape: 'rounded' },
  { label: 'API Endpoint', color: '#f8cecc', shape: 'diamond' },
];

const EDGE_LEGEND = [
  { label: 'Queries', color: '#2563eb', dashed: true },
  { label: 'Calls API', color: '#16a34a', dashed: false },
  { label: 'Authenticates', color: '#7c3aed', dashed: false },
  { label: 'Connects To', color: '#6b7280', dashed: false },
];

export default function TopologyLegend() {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Legend</h3>
      <div className="space-y-2">
        {LEGEND_ITEMS.map((item) => (
          <div key={item.label} className="flex items-center gap-2">
            <span
              className={`w-4 h-4 border border-gray-400 ${item.shape === 'circle' ? 'rounded-full' : item.shape === 'diamond' ? 'rotate-45' : 'rounded-sm'}`}
              style={{ backgroundColor: item.color }}
            />
            <span className="text-xs text-gray-600">{item.label}</span>
          </div>
        ))}
        <div className="border-t pt-2 mt-2">
          {EDGE_LEGEND.map((item) => (
            <div key={item.label} className="flex items-center gap-2 mt-1">
              <div className="w-4 flex items-center">
                <div
                  className={`h-0.5 w-full ${item.dashed ? 'border-t border-dashed' : ''}`}
                  style={{ backgroundColor: item.dashed ? 'transparent' : item.color, borderColor: item.color }}
                />
              </div>
              <span className="text-xs text-gray-600">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
