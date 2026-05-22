import apiClient from './client';
import type { Asset, PaginatedResponse } from './types';

export interface AssetFilters {
  asset_type?: string;
  status?: string;
  os_family?: string;
  search?: string;
  page?: number;
  size?: number;
}

export async function listAssets(filters: AssetFilters = {}): Promise<PaginatedResponse<Asset>> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== '') {
      params.append(key, String(value));
    }
  });
  const { data } = await apiClient.get<PaginatedResponse<Asset>>('/assets', { params });
  return data;
}

export async function getAsset(id: string): Promise<Asset> {
  const { data } = await apiClient.get<Asset>(`/assets/${id}`);
  return data;
}

export async function updateAsset(id: string, updates: Partial<Asset>): Promise<Asset> {
  const { data } = await apiClient.patch<Asset>(`/assets/${id}`, updates);
  return data;
}

export async function searchAssets(query: string): Promise<Asset[]> {
  const { data } = await apiClient.get<Asset[]>('/assets/search', {
    params: { q: query },
  });
  return data;
}
