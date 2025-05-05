'use client';

import { PrivyProvider } from '@privy-io/react-auth';
import { toSolanaWalletConnectors } from "@privy-io/react-auth/solana";

export default function Providers({ children }: { children: React.ReactNode }) {
    const appID = process.env.NEXT_PUBLIC_PRIVY_APP_ID;
    const clientID = process.env.NEXT_PUBLIC_PRIVY_CLIENT_ID;
    if (!appID || !clientID) {
        throw new Error("Privy App ID or Client ID not found");
    }

    return (
        <PrivyProvider
            appId={appID}
            clientId={clientID}
            config={{
                embeddedWallets: {
                    solana: {
                        createOnLogin: 'users-without-wallets',
                    },
                },
                externalWallets: {
                    solana: { connectors: toSolanaWalletConnectors() }
                },
                appearance: {
                    theme: 'dark',
                    landingHeader: 'ABS Finance',
                    showWalletLoginFirst: true,
                    walletList: ["phantom", "solflare", "detected_solana_wallets", "backpack"],
                    walletChainType: 'solana-only'
                },
                loginMethods: ['wallet'],
                solanaClusters: [{ name: 'mainnet-beta', rpcUrl: 'https://api.mainnet-beta.solana.com' }]
            }}
        >
            {children}
        </PrivyProvider>
    );
}
