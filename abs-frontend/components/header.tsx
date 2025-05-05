'use client';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Menu } from 'lucide-react';
import { useConnectWallet, useSolanaWallets } from '@privy-io/react-auth';
import { useEffect, useState } from 'react';

export default function Header() {
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const { connectWallet } = useConnectWallet();
  const { wallets } = useSolanaWallets();
  const [shouldLogin, setShouldLogin] = useState(false);

  const handleConnect = async () => {
    try {
      await connectWallet();
      setShouldLogin(true); // Trigger login after wallet is connected
    } catch (error) {
      console.error('Wallet connection failed:', error);
    }
  };

  useEffect(() => {
    const login = async () => {
      if (wallets.length > 0 && shouldLogin) {
        try {
          console.log('Logging in with wallet:', wallets[0]);
          await wallets[0].loginOrLink();
          setWalletAddress(wallets[0].address);
          setShouldLogin(false);
        } catch (error) {
          console.error('Login failed:', error);
        }
      }
    };

    login();

  }, [wallets, shouldLogin]);

  return (
    <header className="border-b border-gray-800 p-4 flex justify-end items-center gap-4">
      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="rounded-full">
              <Menu className="h-5 w-5" />
              <span className="sr-only">Menu</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuItem>Help</DropdownMenuItem>
            <DropdownMenuItem>About</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </motion.div>

      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {walletAddress ? (
          <span className="text-white font-mono text-sm">
            {walletAddress.slice(0, 4)}...{walletAddress.slice(-4)}
          </span>
        ) : (
          <Button
            onClick={handleConnect}
            className="bg-white text-black hover:bg-gray-200"
          >
            Connect Wallet
          </Button>
        )}
      </motion.div>
    </header>
  );
}
