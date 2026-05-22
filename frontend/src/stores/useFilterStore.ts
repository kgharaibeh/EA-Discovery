import { create } from 'zustand';

interface FilterStoreState {
  globalSearch: string;
  setGlobalSearch: (q: string) => void;
}

export const useFilterStore = create<FilterStoreState>((set) => ({
  globalSearch: '',
  setGlobalSearch: (q) => set({ globalSearch: q }),
}));
