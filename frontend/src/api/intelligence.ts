import api from './client';
import type { IntelligenceSuggestion, SuggestionReview, PaginatedResponse } from './types';

export async function listSuggestions(status = 'pending', page = 1, pageSize = 50) {
  const { data } = await api.get<PaginatedResponse<IntelligenceSuggestion>>('/intelligence/suggestions', {
    params: { status, page, page_size: pageSize },
  });
  return data;
}

export async function getSuggestion(id: string) {
  const { data } = await api.get<IntelligenceSuggestion>(`/intelligence/suggestions/${id}`);
  return data;
}

export async function reviewSuggestion(id: string, review: SuggestionReview) {
  const { data } = await api.post(`/intelligence/suggestions/${id}/review`, review);
  return data;
}

export async function triggerAnalysis(assetId: string) {
  const { data } = await api.post(`/intelligence/analyze/${assetId}`);
  return data;
}
