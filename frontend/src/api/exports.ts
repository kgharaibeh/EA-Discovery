import api from './client';

export async function generateExport(format: string, assetTypes?: string[], relationshipTypes?: string[]) {
  const { data } = await api.post('/exports', {
    format,
    asset_types: assetTypes,
    relationship_types: relationshipTypes,
  }, { responseType: format === 'csv' ? 'text' : 'blob' });
  return data;
}
