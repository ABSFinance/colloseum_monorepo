'use client';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { useConnectWallet, useSolanaWallets } from '@privy-io/react-auth';
import { useEffect, useState } from 'react';
import { Plus } from 'lucide-react';
import { CreateVaultModal } from '@/app/dashboard/components/createVaultModal';

export default function Header() {
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const { connectWallet } = useConnectWallet();
  const { wallets, ready } = useSolanaWallets();
  const wallet = wallets[0];
  const [shouldLogin, setShouldLogin] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleConnect = async () => {
    try {
      await connectWallet();
      setShouldLogin(true);
    } catch (error) {
      console.error('Wallet connection failed:', error);
    }
  };
  useEffect(() => {
    if (!ready || wallets.length === 0 || !shouldLogin) return;

    const doLogin = async () => {
      try {
        console.log("Logging in...");
        await wallets[0].loginOrLink(); // Ensure wallet is hydrated
        setWalletAddress(wallets[0].address);
        setShouldLogin(false);
      } catch (err) {
        console.error("Login failed:", err);
      }
    };

    // Delay slightly to ensure hydration
    const timeout = setTimeout(() => doLogin(), 300);
    return () => clearTimeout(timeout);
  }, [ready, wallets, shouldLogin]);

  useEffect(() => {
    if (ready && wallet?.address) {
      setWalletAddress(wallet.address);
    }
  }, [ready, wallet]);

  return (
    <header className="border-b border-gray-800 p-4 items-center gap-4">
      <motion.div
        // whileHover={{ scale: 1.05 }}
        // whileTap={{ scale: 0.95 }}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {walletAddress ? (
          <>
            <div className="flex justify-between">
              <motion.div onClick={() => setIsModalOpen(true)}>
                <Button className="bg-white text-black hover:bg-gray-200 rounded-md cursor-pointer">
                  <Plus className="mr-2 h-4 w-4" /> Create Vault
                </Button>
              </motion.div>

              <CreateVaultModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />

              <div className="flex items-center gap-7">
                <span className="text-white font-mono text-sm">
                  {walletAddress.slice(0, 4)}...{walletAddress.slice(-4)}
                </span>
                <Button
                  onClick={async () => {
                    try {
                      await wallet.disconnect();
                      setWalletAddress(null);
                    } catch (err) {
                      console.error('Failed to disconnect:', err);
                    }
                  }}
                  variant="secondary"
                  className="text-white border-white bg-red-600 hover:bg-red-500 cursor-pointer"
                >
                  Disconnect
                </Button>
              </div>
            </div>
          </>
        ) : (
          <Button
            onClick={handleConnect}
            className="bg-white text-black hover:bg-gray-200 cursor-pointer"
            disabled={!ready}
          >
            {ready ? "Connect Wallet" : "Loading..."}
          </Button>
        )}
      </motion.div>
    </header>
  );
}
