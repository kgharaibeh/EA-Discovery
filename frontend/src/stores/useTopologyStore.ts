import { create } from 'zustand';

interface TopologyStoreState {
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  layout: string;
  assetTypeFilters: string[];
  relationshipTypeFilters: string[];
  setSelectedNode: (id: string | null) => void;
  setSelectedEdge: (id: string | null) => void;
  setLayout: (layout: string) => void;
  toggleAssetTypeFilter: (type: string) => void;
  toggleRelationshipTypeFilter: (type: string) => void;
  resetFilters: () => void;
}

export const useTopologyStore = create<TopologyStoreState>((set) => ({
  selectedNodeId: null,
  selectedEdgeId: null,
  layout: 'cose',
  assetTypeFilters: [],
  relationshipTypeFilters: [],
  setSelectedNode: (id) => set({ selectedNodeId: id, selectedEdgeId: null }),
  setSelectedEdge: (id) => set({ selectedEdgeId: id, selectedNodeId: null }),
  setLayout: (layout) => set({ layout }),
  toggleAssetTypeFilter: (type) =>
    set((state) => ({
      assetTypeFilters: state.assetTypeFilters.includes(type)
        ? state.assetTypeFilters.filter((t) => t !== type)
        : [...state.assetTypeFilters, type],
    })),
  toggleRelationshipTypeFilter: (type) =>
    set((state) => ({
      relationshipTypeFilters: state.relationshipTypeFilters.includes(type)
        ? state.relationshipTypeFilters.filter((t) => t !== type)
        : [...state.relationshipTypeFilters, type],
    })),
  resetFilters: () => set({ assetTypeFilters: [], relationshipTypeFilters: [] }),
}));
