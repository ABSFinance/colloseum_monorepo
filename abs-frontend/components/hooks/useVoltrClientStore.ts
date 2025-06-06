"use client";

import { create } from "zustand";
import { Connection } from "@solana/web3.js";
import { VoltrClient } from "@voltr/vault-sdk";

interface VoltrClientState {
    client: VoltrClient | null;
    initialize: () => void;
}
const ALCHEMY_RPC_URL = `https://go.getblock.io/${process.env.NEXT_PUBLIC_BLOCK_API_KEY}`;
export const connection = new Connection(ALCHEMY_RPC_URL);


export const useVoltrClientStore = create<VoltrClientState>((set) => ({
    client: null,
    initialize: () => {
   
        const client = new VoltrClient(connection);
        set({ client });
    },
}));
