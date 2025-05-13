"use client";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useConnectWallet, useSolanaWallets } from "@privy-io/react-auth";
import { useEffect, useState } from "react";

export default function Header() {
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const { connectWallet } = useConnectWallet();
  const { wallets, ready } = useSolanaWallets();
  const wallet = wallets[0];
  const [shouldLogin, setShouldLogin] = useState(false);
  const [hasSignedBefore, setHasSignedBefore] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedWalletState = localStorage.getItem("walletHasSigned");
      if (savedWalletState) {
        setHasSignedBefore(true);
      }
    }
  }, []);

  useEffect(() => {
    if (hasSignedBefore && ready && !walletAddress && !shouldLogin) {
      console.log("Auto-connecting wallet for returning user");
      handleConnect();
    }
  }, [hasSignedBefore, ready]);

  const handleConnect = async () => {
    try {
      await connectWallet();
      setShouldLogin(true);
    } catch (error) {
      console.error("Wallet connection failed:", error);
    }
  };

  useEffect(() => {
    if (!ready || wallets.length === 0 || !shouldLogin) return;

    const doLogin = async () => {
      try {
        console.log("Logging in...");

        if (hasSignedBefore) {
          console.log("User has signed before, skipping signature");
          setWalletAddress(wallets[0].address);
          setShouldLogin(false);
          return;
        }

        await wallets[0].loginOrLink(); // Ensure wallet is hydrated

        localStorage.setItem("walletHasSigned", "true");
        setHasSignedBefore(true);

        setWalletAddress(wallets[0].address);
        setShouldLogin(false);
      } catch (err) {
        console.error("Login failed:", err);
      }
    };

    // Delay slightly to ensure hydration
    const timeout = setTimeout(() => doLogin(), 300);
    return () => clearTimeout(timeout);
  }, [ready, wallets, shouldLogin, hasSignedBefore]);

  useEffect(() => {
    if (ready && wallet?.address) {
      setWalletAddress(wallet.address);
    }
  }, [ready, wallet]);

  const handleDisconnect = async () => {
    try {
      await wallet.disconnect();
      setWalletAddress(null);
    } catch (err) {
      console.error("Failed to disconnect:", err);
    }
  };

  return (
    <header className="border-b border-gray-800 p-4 items-center gap-4">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {walletAddress ? (
          <div className="flex justify-end">
            <div className="flex items-center gap-7">
              <span className="text-white font-mono text-sm">
                {walletAddress.slice(0, 4)}...{walletAddress.slice(-4)}
              </span>
              <Button
                onClick={handleDisconnect}
                variant="secondary"
                className="text-white border-white bg-red-600 hover:bg-red-500 cursor-pointer"
              >
                Disconnect
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex justify-end">
            <Button
              onClick={handleConnect}
              className="bg-white text-black hover:bg-gray-200 cursor-pointer"
              disabled={!ready}
            >
              {ready ? "Connect Wallet" : "Loading..."}
            </Button>
          </div>
        )}
      </motion.div>
    </header>
  );
}
