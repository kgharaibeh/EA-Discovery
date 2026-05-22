import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import type { DriftEvent, PaginatedResponse } from '../api/types';
import DriftTimeline from '../components/drift/DriftTimeline';

export default function DriftPage() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['drift-events'],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<DriftEvent>>('/drift/events');
      return data;
    },
  });

  const ackMutation = useMutation({
    mutationFn: (id: string) => api.post(`/drift/events/${id}/acknowledge`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drift-events'] });
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Configuration Drift</h1>
        <span className="text-sm text-gray-500">
          {data?.total ?? 0} events
        </span>
      </div>

      <p className="text-sm text-gray-600">
        Track changes detected between scans. Drift events highlight configuration, software,
        and service changes across your infrastructure.
      </p>

      <DriftTimeline
        events={data?.items || []}
        onAcknowledge={(id) => ackMutation.mutate(id)}
        isLoading={isLoading}
      />
    </div>
  );
}
