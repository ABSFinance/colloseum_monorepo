"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { ChevronDown } from "lucide-react"
import type { VaultInfo } from "@/lib/types"
import TokenIcon from "./token-icon"

interface TokenRowProps {
  token: VaultInfo
  index: number
}

export default function TokenRow({ token, index }: TokenRowProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  console.log(token);
  return (
    <motion.tr
      className="border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.05 * index, duration: 0.3 }}
      onClick={() => setIsExpanded(!isExpanded)}
      layout
    >
      <td className="py-4 px-4">
        <div className="flex items-center gap-3">
          <TokenIcon symbol={token.id} />
          <span className="font-medium">{token.name.slice(0, 5)}</span>
        </div>
      </td>
      <td className="text-right py-4 px-4">${token.description.slice(0, 5)}</td>
      <td className="text-right py-4 px-4">${token.market_tokens?.slice(0, 5)}</td>
      <td className="text-right py-4 px-4">${token.underlying_token}</td>
      <td className="text-right py-4 px-4">{token.strategy.slice(0, 5)}</td>
      <td className="text-right py-4 px-4 font-medium">{token.created_at}</td>
      <td className="py-4 px-4">
        <motion.div animate={{ rotate: isExpanded ? 180 : 0 }} transition={{ duration: 0.3 }}>
          <ChevronDown className="w-5 h-5 text-gray-400" />
        </motion.div>
      </td>
    </motion.tr>
  )
}
