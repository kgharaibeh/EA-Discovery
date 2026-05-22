import { useState } from 'react';
import type { IntelligenceSuggestion } from '../../api/types';
import ConfidenceBadge from './ConfidenceBadge';

interface SuggestionCardProps {
  suggestion: IntelligenceSuggestion;
  onReview: (id: string, status: 'accepted' | 'rejected', notes?: string) => void;
}

const TYPE_LABELS: Record<string, string> = {
  business_context: 'Business Context',
  relationship: 'Relationship',
  data_classification: 'Data Classification',
  schema_analysis: 'Schema Analysis',
};

export default function SuggestionCard({ suggestion, onReview }: SuggestionCardProps) {
  const [notes, setNotes] = useState('');
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white border rounded-lg p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
              {TYPE_LABELS[suggestion.suggestion_type] || suggestion.suggestion_type}
            </span>
            <ConfidenceBadge confidence={suggestion.confidence} />
            {suggestion.status !== 'pending' && (
              <span className={`text-xs px-2 py-0.5 rounded ${
                suggestion.status === 'accepted' ? 'bg-green-100 text-green-700' :
                suggestion.status === 'rejected' ? 'bg-red-100 text-red-700' :
                'bg-yellow-100 text-yellow-700'
              }`}>
                {suggestion.status}
              </span>
            )}
          </div>
          <h4 className="text-sm font-medium text-gray-900">{suggestion.title}</h4>
          <p className="text-sm text-gray-600 mt-1">{suggestion.description}</p>
        </div>
      </div>

      {Object.keys(suggestion.suggested_data).length > 0 && (
        <div className="mt-3">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            {expanded ? 'Hide details' : 'Show details'}
          </button>
          {expanded && (
            <pre className="mt-2 bg-gray-50 rounded p-3 text-xs text-gray-700 overflow-auto max-h-48">
              {JSON.stringify(suggestion.suggested_data, null, 2)}
            </pre>
          )}
        </div>
      )}

      {suggestion.status === 'pending' && (
        <div className="mt-3 pt-3 border-t">
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Optional review notes..."
            className="w-full text-sm border rounded px-3 py-1.5 mb-2 focus:ring-1 focus:ring-blue-500 focus:outline-none"
            rows={2}
          />
          <div className="flex gap-2">
            <button
              onClick={() => onReview(suggestion.id, 'accepted', notes)}
              className="px-3 py-1.5 text-xs font-medium text-white bg-green-600 hover:bg-green-700 rounded"
            >
              Accept
            </button>
            <button
              onClick={() => onReview(suggestion.id, 'rejected', notes)}
              className="px-3 py-1.5 text-xs font-medium text-white bg-red-600 hover:bg-red-700 rounded"
            >
              Reject
            </button>
          </div>
        </div>
      )}

      <p className="text-xs text-gray-400 mt-2">
        {new Date(suggestion.created_at).toLocaleString()}
      </p>
    </div>
  );
}
