"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { CreateVaultModal } from "./createVaultModal"
import { useState } from "react"

export function CreateVaultButton() {
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <>
      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={() => setIsModalOpen(true)}>
        <Button className="bg-white text-black hover:bg-gray-200 rounded-md cursor-pointer">
          <Plus className="mr-2 h-4 w-4" /> Create Vault
        </Button>
      </motion.div>

      <CreateVaultModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </>
  )
}
