import apiClient from './client';
import type { Scan, ScanCreate, PaginatedResponse } from './types';

export async function createScan(scan: ScanCreate): Promise<Scan> {
  const { data } = await apiClient.post<Scan>('/scans', scan);
  return data;
}

export async function listScans(page = 1, size = 20): Promise<PaginatedResponse<Scan>> {
  const { data } = await apiClient.get<PaginatedResponse<Scan>>('/scans', {
    params: { page, size },
  });
  return data;
}

export async function getScan(id: string): Promise<Scan> {
  const { data } = await apiClient.get<Scan>(`/scans/${id}`);
  return data;
}

export async function cancelScan(id: string): Promise<Scan> {
  const { data } = await apiClient.post<Scan>(`/scans/${id}/cancel`);
  return data;
}
