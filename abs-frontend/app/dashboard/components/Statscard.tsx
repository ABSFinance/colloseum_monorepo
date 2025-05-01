"use client"

import type { ReactNode } from "react"
import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { TrendingUp, TrendingDown } from "lucide-react"

interface StatCardProps {
  icon: ReactNode
  title: string
  value: string | number
  percentChange?: number
  delay?: number
}

export function StatCard({ icon, title, value, percentChange, delay = 0 }: StatCardProps) {
  const isPositive = percentChange ? percentChange > 0 : false

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 24,
        delay,
      },
    },
  }

  return (
    <motion.div variants={cardVariants} initial="hidden" animate="visible">
      <Card className="bg-zinc-900 border-0 overflow-hidden text-white">
        <CardContent className="p-6">
          <div className="flex items-center mb-2 text-white">
            <span className="mr-2">{icon}</span>
            <span>{title}</span>
          </div>
          <div className="flex items-end justify-between">
            <motion.h2
              className="text-3xl font-bold"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: delay + 0.1, type: "spring" }}
            >
              {value}
            </motion.h2>
            {percentChange !== undefined && (
              <motion.div
                className={`flex items-center ${isPositive ? "text-green-400" : "text-red-400"}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: delay + 0.2 }}
              >
                {isPositive ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
                <span>{Math.abs(percentChange)}%</span>
              </motion.div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
