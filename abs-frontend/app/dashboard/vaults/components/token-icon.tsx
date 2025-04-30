"use client"

import { motion } from "framer-motion"

interface TokenIconProps {
  symbol: string
}

export default function TokenIcon({ symbol }: TokenIconProps) {
  // Get the first token from the pair (e.g., SOL from SOL/USDC)
  const baseToken = symbol.split("/")[0]

  // Generate a color based on the token name
  const getTokenColor = (token: string) => {
    const colors = {
      SOL: "#14F195",
      AVAX: "#E84142",
      USDT: "#26A17B",
      USDC: "#2775CA",
      BERA: "#FFD700",
      default: "#6366F1",
    }

    return colors[token as keyof typeof colors] || colors.default
  }

  const color = getTokenColor(baseToken)

  return (
    <motion.div
      className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs relative"
      style={{ backgroundColor: color }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
    >
      {baseToken.substring(0, 1)}
      <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-gray-800 rounded-full flex items-center justify-center">
        <div className="w-3 h-3 rounded-full bg-blue-500 flex items-center justify-center">
          <span className="text-[8px]">$</span>
        </div>
      </div>
    </motion.div>
  )
}
