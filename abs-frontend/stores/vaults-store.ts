import { create } from 'zustand';
import { VaultInfo } from '@/lib/types';

interface VaultState {
  vaults: VaultInfo[];
  setVaults: (vaults: VaultInfo[]) => void;
}

export const useVaultStore = create<VaultState>((set) => ({
  vaults: [],
  setVaults: (vaults) => set({ vaults }),
}));
