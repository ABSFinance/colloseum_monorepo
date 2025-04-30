"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { PositionsList, type Position } from "./PositionList"

interface TabNavigationProps {
  openPositions: Position[]
  closedPositions: Position[]
  vaults: Position[]
}

export function TabNavigation({ openPositions, closedPositions, vaults }: TabNavigationProps) {
  const [activeTab, setActiveTab] = useState("open")

  return (
    <Tabs defaultValue="open" value={activeTab} onValueChange={setActiveTab} className="w-full text-white">
      <TabsList className="bg-zinc-900 w-full mb-6 p-1 rounded-md">
        <TabsTrigger value="open" className="flex-1 data-[state=active]:bg-zinc-800  data-[state=active]:text-white p-4">
          Open Positions
        </TabsTrigger>
        <TabsTrigger value="closed" className="flex-1 text-gray-400 data-[state=active]:bg-zinc-800 data-[state=active]:text-white p-4">
          Closed Positions
        </TabsTrigger>
        <TabsTrigger value="vaults" className="flex-1 text-gray-400 data-[state=active]:bg-zinc-800 data-[state=active]:text-white p-4">
          Active Vaults
        </TabsTrigger>
      </TabsList>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          <TabsContent value="open" className="mt-0">
            <PositionsList positions={openPositions} type="open" />
          </TabsContent>

          <TabsContent value="closed" className="mt-0">
            <PositionsList positions={closedPositions} type="closed" />
          </TabsContent>

          <TabsContent value="vaults" className="mt-0">
            <PositionsList positions={vaults} type="vaults" />
          </TabsContent>
        </motion.div>
      </AnimatePresence>
    </Tabs>
  )
}
