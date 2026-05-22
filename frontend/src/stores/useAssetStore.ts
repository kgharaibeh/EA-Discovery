import { create } from 'zustand';

interface AssetStoreState {
  selectedAssetId: string | null;
  assetTypeFilter: string | null;
  statusFilter: string | null;
  searchQuery: string;
  setSelectedAsset: (id: string | null) => void;
  setAssetTypeFilter: (type: string | null) => void;
  setStatusFilter: (status: string | null) => void;
  setSearchQuery: (query: string) => void;
  resetFilters: () => void;
}

export const useAssetStore = create<AssetStoreState>((set) => ({
  selectedAssetId: null,
  assetTypeFilter: null,
  statusFilter: null,
  searchQuery: '',
  setSelectedAsset: (id) => set({ selectedAssetId: id }),
  setAssetTypeFilter: (type) => set({ assetTypeFilter: type }),
  setStatusFilter: (status) => set({ statusFilter: status }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  resetFilters: () => set({ assetTypeFilter: null, statusFilter: null, searchQuery: '' }),
}));
