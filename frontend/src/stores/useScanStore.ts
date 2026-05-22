import { create } from 'zustand';

interface ScanStoreState {
  activeScanId: string | null;
  showWizard: boolean;
  setActiveScan: (id: string | null) => void;
  setShowWizard: (show: boolean) => void;
}

export const useScanStore = create<ScanStoreState>((set) => ({
  activeScanId: null,
  showWizard: false,
  setActiveScan: (id) => set({ activeScanId: id }),
  setShowWizard: (show) => set({ showWizard: show }),
}));
