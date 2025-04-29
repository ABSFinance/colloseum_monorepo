"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import MobileSidebar from "@/components/Mobile-sidebar"
import SearchBar from "./searchbar"
import TokenTable from "./token-table"
import { tokenData } from "@/lib/data"

export default function MobileDashboard() {
  const [searchQuery, setSearchQuery] = useState("")

  const filteredTokens = tokenData.filter((token) => token.name.toLowerCase().includes(searchQuery.toLowerCase()))

  return (
    <div className="min-h-screen bg-black text-white md:hidden">
      <header className="border-b border-gray-800 p-4 flex justify-between items-center">
        <MobileSidebar />

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-white rounded-md flex items-center justify-center">
            <div className="w-4 h-4 bg-black transform rotate-45" />
          </div>
          <span className="text-lg font-bold">ABS Finance</span>
        </div>

        <button className="bg-white text-black px-3 py-1.5 rounded-lg text-sm font-medium">Connect</button>
      </header>

      <div className="p-4">
        <motion.div
          className="mb-6"
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.5 }}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="bg-gray-800 p-1.5 rounded-full">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="text-gray-400"
                >
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
              </div>
              <h1 className="text-xl font-bold">All Vaults</h1>
            </div>
            <div className="text-right">
              <h2 className="text-2xl font-bold">5,274</h2>
              <p className="text-gray-400 text-xs">Pools available</p>
            </div>
          </div>

          <div className="space-y-3">
            <SearchBar searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
            <button className="w-full flex items-center justify-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg transition-colors">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
              </svg>
              Filter
            </button>
          </div>
        </motion.div>

        <TokenTable tokens={filteredTokens} />
      </div>
    </div>
  )
}
