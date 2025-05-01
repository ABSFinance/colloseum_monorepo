"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import Sidebar from "@/components/Sidebar"
import Header from "@/components/header"
import SearchBar from "./searchbar"
import TokenTable from "./token-table"
import { tokenData } from "@/lib/data"

export default function Dashboard() {
  const [searchQuery, setSearchQuery] = useState("")
  const [isFilterOpen, setIsFilterOpen] = useState(false)

  const filteredTokens = tokenData.filter((token) => token.name.toLowerCase().includes(searchQuery.toLowerCase()))

  return (
    <div className="flex h-screen bg-black text-white overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <motion.main
        className="flex-1 overflow-auto"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Header />

        <div className="p-6">
          <motion.div
            className="mb-8"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1, duration: 0.5 }}
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <div className="bg-gray-800 p-2 rounded-full">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
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
                </motion.div>
                <h1 className="text-2xl font-bold">All Vaults</h1>
              </div>
              <div className="text-right">
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.2, duration: 0.5 }}
                >
                  <h2 className="text-3xl font-bold">5,274</h2>
                  <p className="text-gray-400 text-sm">Pools available</p>
                </motion.div>
              </div>
            </div>

            <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
              <SearchBar searchQuery={searchQuery} setSearchQuery={setSearchQuery} />
              <button
                onClick={() => setIsFilterOpen(!isFilterOpen)}
                className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg transition-colors"
              >
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
                >
                  <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
                </svg>
                Filter
              </button>
            </div>
          </motion.div>

          <TokenTable tokens={filteredTokens} />
        </div>
      </motion.main>
    </div>
  )
}
