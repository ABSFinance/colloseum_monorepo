"use client"

import { motion } from "framer-motion"
import { Search } from "lucide-react"

interface SearchBarProps {
  searchQuery: string
  setSearchQuery: (query: string) => void
}

export default function SearchBar({ searchQuery, setSearchQuery }: SearchBarProps) {
  return (
    <motion.div
      className="relative w-full md:max-w-md"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
        <Search className="w-5 h-5 text-gray-400" />
      </div>
      <input
        type="text"
        className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded-lg focus:ring-gray-600 focus:border-gray-600 block pl-10 p-2.5"
        placeholder="Search tokens"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
    </motion.div>
  )
}
