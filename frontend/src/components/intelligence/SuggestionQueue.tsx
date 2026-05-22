import { useState } from 'react';
import type { IntelligenceSuggestion } from '../../api/types';
import SuggestionCard from './SuggestionCard';

interface SuggestionQueueProps {
  suggestions: IntelligenceSuggestion[];
  onReview: (id: string, status: 'accepted' | 'rejected', notes?: string) => void;
  isLoading?: boolean;
}

const FILTER_OPTIONS = ['all', 'pending', 'accepted', 'rejected'] as const;

export default function SuggestionQueue({ suggestions, onReview, isLoading }: SuggestionQueueProps) {
  const [filter, setFilter] = useState<string>('pending');

  const filtered = filter === 'all'
    ? suggestions
    : suggestions.filter((s) => s.status === filter);

  if (isLoading) {
    return <div className="text-center py-8 text-gray-500">Loading suggestions...</div>;
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        {FILTER_OPTIONS.map((opt) => (
          <button
            key={opt}
            onClick={() => setFilter(opt)}
            className={`px-3 py-1.5 text-sm rounded-full capitalize ${
              filter === opt
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {opt}
            {opt !== 'all' && (
              <span className="ml-1 text-xs">
                ({suggestions.filter((s) => s.status === opt).length})
              </span>
            )}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {filtered.map((suggestion) => (
          <SuggestionCard
            key={suggestion.id}
            suggestion={suggestion}
            onReview={onReview}
          />
        ))}
        {filtered.length === 0 && (
          <p className="text-center py-8 text-gray-500">
            No {filter === 'all' ? '' : filter} suggestions
          </p>
        )}
      </div>
    </div>
  );
}
