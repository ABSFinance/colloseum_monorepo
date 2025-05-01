'use client';

import { PrivyProvider } from '@privy-io/react-auth';
const appID = process.env.NEXT_PUBLIC_PRIVY_APP_ID;
const clientID = process.env.NEXT_PUBLIC_PRIVY_CLIENT_ID;

export default function Providers({ children }: { children: React.ReactNode }) {
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
                appearance: {
                    theme: 'dark',
                    landingHeader: 'ABS Finance',
                    showWalletLoginFirst: true,
                    walletList:["phantom","solflare","detected_solana_wallets","backpack","wallet_connect"]
                },
                loginMethods: ['wallet'],
                solanaClusters: [{name: 'mainnet-beta', rpcUrl: 'https://api.mainnet-beta.solana.com'}]
            }}
        >
            {children}
        </PrivyProvider>
    );
}
