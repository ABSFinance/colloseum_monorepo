"use client"
import { motion, AnimatePresence } from "framer-motion"
import type { TokenData } from "@/lib/types"
import TokenRow from "./token-row"
import { useVaultStore } from "@/stores/vaults-store"

interface TokenTableProps {
  tokens: TokenData[]
}

export default function TokenTable({ tokens }: TokenTableProps) {
  const vaults = useVaultStore((state) => state.vaults);

  return (
    <motion.div
      className="overflow-x-auto"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.3, duration: 0.5 }}
    >
      <table className="w-full">
        <thead>
          <tr className="text-gray-400 text-sm border-b border-gray-800">
            <th className="text-left py-4 px-4 font-medium">Token</th>
            <th className="text-right py-4 px-4 font-medium">TVL</th>
            <th className="text-right py-4 px-4 font-medium">24H Vol</th>
            <th className="text-right py-4 px-4 font-medium">24H Fees</th>
            <th className="text-right py-4 px-4 font-medium">24H Fee/TVL</th>
            <th className="text-right py-4 px-4 font-medium">Your Balance</th>
            <th className="py-4 px-4 w-10"></th>
          </tr>
        </thead>
        <tbody>
          <AnimatePresence>
            {vaults.map((token, index) => (
              <TokenRow key={token.id} token={token} index={index} />
            ))}
          </AnimatePresence>
        </tbody>
      </table>

      {tokens.length === 0 && (
        <motion.div className="text-center py-10 text-gray-400" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          No tokens found
        </motion.div>
      )}
    </motion.div>
  )
}
