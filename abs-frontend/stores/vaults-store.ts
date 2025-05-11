import { create } from 'zustand'
import { supabase } from '@/lib/supabase'
import { VaultInfo } from '@/lib/types'

type VaultStore = {
  vaults: VaultInfo[]
  loading: boolean
  error: string | null
  fetchVaults: () => Promise<void>
}

export const useVaultStore = create<VaultStore>((set) => ({
  vaults: [],
  loading: false,
  error: null,
  fetchVaults: async () => {
    set({ loading: true, error: null })
    const { data, error } = await supabase.from('abs_vault_info').select('*')
    if (error) {
      set({ error: error.message, loading: false })
    } else {
      set({ vaults: data || [], loading: false })
    }
  },
}))
