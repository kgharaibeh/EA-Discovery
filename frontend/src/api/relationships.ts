import apiClient from './client';
import type { Relationship, TopologyResponse } from './types';

export async function listRelationships(assetId?: string): Promise<Relationship[]> {
  const params = assetId ? { asset_id: assetId } : {};
  const { data } = await apiClient.get<Relationship[]>('/relationships', { params });
  return data;
}

export async function getTopology(): Promise<TopologyResponse> {
  const { data } = await apiClient.get<TopologyResponse>('/topology');
  return data;
}

export async function createRelationship(relationship: {
  source_asset_id: string;
  target_asset_id: string;
  relationship_type: string;
  properties?: Record<string, unknown>;
}): Promise<Relationship> {
  const { data } = await apiClient.post<Relationship>('/relationships', relationship);
  return data;
}

export async function deleteRelationship(id: string): Promise<void> {
  await apiClient.delete(`/relationships/${id}`);
}
