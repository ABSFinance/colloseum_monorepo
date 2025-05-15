"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface PositionItemProps {
  id: number;
  name: string;
  value: string;
  change: string;
  isPositive: boolean;
  icon: ReactNode;
}

export function PositionItem({
  id,
  name,
  value,
  change,
  isPositive,
  icon,
}: PositionItemProps) {
  return (
    <motion.li
      key={id}
      className="flex justify-between items-center p-3 bg-zinc-800 rounded-lg hover:bg-gray-600 transition-colors text-white"
      whileHover={{ x: 5 }}
      initial={{ opacity: 0, x: -20 }}
      animate={{
        opacity: 1,
        x: 0,
        transition: {
          type: "spring",
          stiffness: 300,
          damping: 24,
          delay: id * 0.05,
        },
      }}
    >
      <div className="flex items-center">
        <div className="bg-gray-600 p-2 rounded-md mr-3">{icon}</div>
        <span>{name}</span>
      </div>
      <div className="flex items-center">
        <span className="mr-4 font-medium">{value}</span>
        <span className={isPositive ? "text-green-400" : "text-red-400"}>
          {change}
        </span>
      </div>
    </motion.li>
  );
}
