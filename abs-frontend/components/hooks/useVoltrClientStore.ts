"use client";

import { create } from "zustand";
import { Connection } from "@solana/web3.js";
import { VoltrClient } from "@voltr/vault-sdk";

interface VoltrClientState {
    client: VoltrClient | null;
    initialize: () => void;
}

export const useVoltrClientStore = create<VoltrClientState>((set) => ({
    client: null,
    initialize: () => {
        const connection = new Connection("https://api.mainnet-beta.solana.com");
        const client = new VoltrClient(connection);
        set({ client });
    },
}));
