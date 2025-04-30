"use client"

import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { PositionItem } from "./PositionItem"
import { Lock, Clock, Shield } from "lucide-react"
import type { ReactNode } from "react"

export interface Position {
  id: number
  name: string
  value: string
  change: string
  isPositive: boolean
}

interface PositionsListProps {
  positions: Position[]
  type: "open" | "closed" | "vaults"
}

export function PositionsList({ positions, type }: PositionsListProps) {
  const getIcon = (type: string): ReactNode => {
    switch (type) {
      case "open":
        return <Lock className="h-4 w-4" />
      case "closed":
        return <Clock className="h-4 w-4" />
      case "vaults":
        return <Shield className="h-4 w-4" />
      default:
        return <Lock className="h-4 w-4" />
    }
  }

  const listVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  return (
    <Card className="bg-zinc-900 border-0">
      <CardContent className="p-6">
        <motion.ul className="space-y-4" variants={listVariants} initial="hidden" animate="visible">
          {positions.map((position) => (
            <PositionItem
              key={position.id}
              id={position.id}
              name={position.name}
              value={position.value}
              change={position.change}
              isPositive={position.isPositive}
              icon={getIcon(type)}
            />
          ))}
        </motion.ul>
      </CardContent>
    </Card>
  )
}
