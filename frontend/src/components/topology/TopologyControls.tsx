import { useTopologyStore } from '../../stores/useTopologyStore';

const LAYOUTS = [
  { value: 'cose', label: 'Force-Directed' },
  { value: 'breadthfirst', label: 'Hierarchical' },
  { value: 'circle', label: 'Circle' },
  { value: 'grid', label: 'Grid' },
  { value: 'concentric', label: 'Concentric' },
];

export default function TopologyControls() {
  const { layout, setLayout } = useTopologyStore();

  return (
    <div className="flex items-center gap-3 bg-white rounded-lg shadow px-4 py-2">
      <span className="text-sm font-medium text-gray-700">Layout:</span>
      <select
        value={layout}
        onChange={(e) => setLayout(e.target.value)}
        className="text-sm border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
      >
        {LAYOUTS.map((l) => (
          <option key={l.value} value={l.value}>
            {l.label}
          </option>
        ))}
      </select>
    </div>
  );
}
