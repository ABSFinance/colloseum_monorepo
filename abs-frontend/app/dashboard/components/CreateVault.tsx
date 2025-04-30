"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

export function CreateVaultButton() {
  return (
    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
      <Button className="bg-white text-black hover:bg-gray-200 rounded-md">
        <Plus className="mr-2 h-4 w-4" /> Create Vault
      </Button>
    </motion.div>
  )
}
