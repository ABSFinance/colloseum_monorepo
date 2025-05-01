"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Menu } from "lucide-react"
import { usePrivy } from "@privy-io/react-auth"

export default function Header() {
  const { connectWallet } = usePrivy();

  const handleConnect = async () => {
    try {
      await connectWallet();
    } catch (error) {
      console.error('Wallet connection failed:', error);
    }
  };

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
        <Button onClick={handleConnect} className="bg-white text-black hover:bg-gray-200">Connect Wallet</Button>
      </motion.div>
    </header>
  )
}
