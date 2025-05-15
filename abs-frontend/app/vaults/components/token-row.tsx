"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import type { VaultInfo } from "@/lib/types";
import TokenIcon from "./token-icon";
import { useRouter } from "next/navigation";

interface TokenRowProps {
  token: VaultInfo;
  index: number;
}

export default function TokenRow({ token, index }: TokenRowProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const router = useRouter();
  return (
    <motion.tr
      className="border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.05 * index, duration: 0.3 }}
      onClick={() => {
        router.push(`/vaults/${token.id}/${token.pool_id}`);
      }}
      layout
    >
      <td className="text-right py-4">{token.name}</td>
      <td className="text-right py-4 px-4">{token.strategy}</td>
      <td className="text-right py-4 px-4">{token.adaptors.join(", ")}</td>
      <td className="text-right py-4 px-4">{token.weight.join(" / ")}</td>
      {/* <td className="text-right py-4 px-4">{token.allowed_pools.join(', ')}</td> */}
      <td className="text-right py-4 px-4 font-medium">
        {new Date(token.created_at).toLocaleDateString()}
      </td>
      <td className="py-4 px-4">
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <ChevronDown className="w-5 h-5 text-gray-400" />
        </motion.div>
      </td>
    </motion.tr>
  );
}
