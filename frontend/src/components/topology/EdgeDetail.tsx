import { X } from 'lucide-react';
import type { TopologyEdge } from '../../api/types';

interface EdgeDetailProps {
  edge: TopologyEdge;
  onClose: () => void;
}

export default function EdgeDetail({ edge, onClose }: EdgeDetailProps) {
  return (
    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white shadow-xl rounded-lg border p-4 w-80 z-10">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-900 text-sm">Relationship</h3>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X size={16} />
        </button>
      </div>
      <div className="space-y-2 text-sm">
        <div>
          <span className="text-gray-500">Type:</span>{' '}
          <span className="font-medium capitalize">{edge.relationship_type.replace('_', ' ')}</span>
        </div>
        <div>
          <span className="text-gray-500">Confidence:</span>{' '}
          <span className="font-medium">{Math.round(edge.confidence * 100)}%</span>
        </div>
      </div>
    </div>
  );
}
