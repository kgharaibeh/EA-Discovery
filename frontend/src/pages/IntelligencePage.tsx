import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listSuggestions, reviewSuggestion } from '../api/intelligence';
import SuggestionQueue from '../components/intelligence/SuggestionQueue';

export default function IntelligencePage() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['suggestions'],
    queryFn: () => listSuggestions('pending'),
  });

  const reviewMutation = useMutation({
    mutationFn: ({ id, status, notes }: { id: string; status: 'accepted' | 'rejected'; notes?: string }) =>
      reviewSuggestion(id, { status, notes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suggestions'] });
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">AI Intelligence</h1>
        <span className="text-sm text-gray-500">
          {data?.total ?? 0} suggestions
        </span>
      </div>

      <p className="text-sm text-gray-600">
        Review AI-generated suggestions for business context, relationships, and data classifications.
        Accept, reject, or modify each suggestion before it's applied.
      </p>

      <SuggestionQueue
        suggestions={data?.items || []}
        onReview={(id, status, notes) => reviewMutation.mutate({ id, status, notes })}
        isLoading={isLoading}
      />
    </div>
  );
}
