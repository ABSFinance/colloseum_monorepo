"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { X, ChevronRight, ChevronDown, ChevronLeft, Search, Trash2 } from "lucide-react"
import { Slider } from "@/components/ui/slider"
import { SliderRange, SliderThumb, SliderTrack } from "@radix-ui/react-slider"

interface CreateVaultModalProps {
  isOpen: boolean
  onClose: () => void
}

interface AllocationItem {
  id: string
  name: string
  strategy: string
  percentage: number
  token?: string
  tokenIcon?: string
}

export function CreateVaultModal({ isOpen, onClose }: CreateVaultModalProps) {
  const [activeTab, setActiveTab] = useState<"setup" | "allocation" | "preview">("setup")
  const [vaultName, setVaultName] = useState<string>("")
  const [vaultDescription, setVaultDescription] = useState<string>("")
  const [allocations, setAllocations] = useState<AllocationItem[]>([
    {
      id: "1",
      name: "ABS",
      strategy: "strat",
      percentage: 30,
      token: "Leverage and hedge JLP (USDC)",
    },
    {
      id: "2",
      name: "ABS",
      strategy: "strat",
      percentage: 30,
      token: "USDT",
      tokenIcon: "T",
    },
    {
      id: "3",
      name: "ABS",
      strategy: "strategy",
      percentage: 40,
    },
  ])

  const totalAllocated = allocations.reduce((sum, item) => sum + item.percentage, 0)
  const isFullyAllocated = totalAllocated === 100

  const handleAllocationChange = (id: string, value: number) => {
    setAllocations((prev) => prev.map((item) => (item.id === id ? { ...item, percentage: value } : item)))
  }

  const handleNext = () => {
    if (activeTab === "setup") setActiveTab("allocation")
    else if (activeTab === "allocation") setActiveTab("preview")
  }

  const handleBack = () => {
    if (activeTab === "allocation") setActiveTab("setup")
    else if (activeTab === "preview") setActiveTab("allocation")
  }

  const handleCreateVault = () => {
    // Logic to create the vault would go here
    console.log("Creating vault with:", {
      name: vaultName,
      description: vaultDescription,
      allocations,
    })
    onClose()
  }

  const handleRemoveAllocation = (id: string) => {
    setAllocations((prev) => prev.filter((item) => item.id !== id))
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="relative w-full max-w-xl rounded-lg bg-[#1c1c1e] p-6 text-white shadow-xl"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <button onClick={onClose} className="absolute right-4 top-4 text-gray-400 hover:text-white">
              <X className="h-5 w-5" />
            </button>

            <div className="mb-8 flex border-b border-gray-700">
              <button
                className={`px-8 py-4 text-sm font-medium ${activeTab === "setup" ? "border-b-2 border-white" : "text-gray-400"}`}
                onClick={() => setActiveTab("setup")}
              >
                Set Up
              </button>
              <button
                className={`px-8 py-4 text-sm font-medium ${activeTab === "allocation" ? "border-b-2 border-white" : "text-gray-400"}`}
                onClick={() => setActiveTab("allocation")}
              >
                Allocation
              </button>
              <button
                className={`px-8 py-4 text-sm font-medium ${activeTab === "preview" ? "border-b-2 border-white" : "text-gray-400"}`}
                onClick={() => setActiveTab("preview")}
              >
                Preview
              </button>
            </div>

            {activeTab === "setup" && (
              <div className="space-y-8">
                <div className="space-y-2">
                  <h3 className="text-lg font-medium">Vault Name</h3>
                  <p className="text-sm text-gray-400">What do you want to name your vault?</p>
                  <Input
                    placeholder="Type something"
                    className="mt-2 bg-[#2c2c2e] border-0 text-white placeholder:text-gray-500"
                    value={vaultName}
                    onChange={(e) => setVaultName(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <h3 className="text-lg font-medium">Description</h3>
                  <p className="text-sm text-gray-400">What do you want your vault to look like?</p>
                  <Textarea
                    placeholder="Type something"
                    className="mt-2 bg-[#2c2c2e] border-0 text-white placeholder:text-gray-500 min-h-[100px]"
                    value={vaultDescription}
                    onChange={(e) => setVaultDescription(e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-2 gap-8">
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium">Underlying Token</h3>
                    <p className="text-sm text-gray-400">Choose your preferred token</p>
                    <button className="mt-2 flex w-full items-center justify-between rounded bg-[#2c2c2e] px-4 py-2 text-white">
                      <div className="flex items-center">
                        <div className="mr-2 flex h-6 w-6 items-center justify-center rounded-full bg-blue-500 text-xs">
                          Ⓤ
                        </div>
                        USDC
                      </div>
                      <ChevronDown className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>

                  <div className="space-y-2">
                    <h3 className="text-lg font-medium mt-2">Initial Deposit</h3>
                    <div className="relative mt-2">
                      <Input className="pr-16 bg-[#2c2c2e] border-0 text-white" />
                      <button className="absolute right-2 top-1/2 -translate-y-1/2 rounded bg-[#3c3c3e] px-2 py-1 text-xs">
                        Max
                      </button>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Balance</span>
                      <div className="flex items-center">
                        <div className="mr-1 h-3 w-3 rounded-sm bg-teal-500"></div>
                        13,530
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "allocation" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-medium">Allocation</h3>
                  <p className="text-sm text-gray-400">What do you want to name your vault?</p>
                </div>

                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                  <Input
                    placeholder="search lending pools"
                    className="pl-9 bg-[#2c2c2e] border-0 text-white placeholder:text-gray-500"
                  />
                </div>

                <div className="flex justify-end">
                  <div
                    className={`px-3 py-1 rounded-full text-sm ${isFullyAllocated ? "bg-green-600" : "bg-yellow-600"}`}
                  >
                    {totalAllocated}% used
                  </div>
                </div>

                <div className="space-y-4">
                  {allocations.map((allocation) => (
                    <div key={allocation.id} className="bg-[#2c2c2e] rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <div className="flex items-center gap-2">
                          <div className="h-6 w-6 rounded-full bg-blue-500 flex items-center justify-center">
                            <span className="text-xs">A</span>
                          </div>
                          <div>
                            <div className="font-medium">{allocation.name}</div>
                            <div className="text-xs text-gray-400">{allocation.strategy}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span>{allocation.percentage}%</span>
                          <ChevronDown className="h-4 w-4 text-gray-400" />
                        </div>
                      </div>
                      <div className="pt-2">
                        <Slider
                          value={[allocation.percentage]}
                          min={0}
                          max={100}
                          step={1}
                          onValueChange={(value) => handleAllocationChange(allocation.id, value[0])}
                          className="cursor-pointer"
                        >
                          <SliderTrack className="bg-blue-600 h-2 rounded-full">
                            <SliderRange className="bg-blue-400" />
                          </SliderTrack>
                          <SliderThumb className="h-4 w-4 bg-white rounded-full border-2 border-blue-600" />
                        </Slider>
                      </div>
                    </div>
                  ))}
                </div>

                <div>
                  <div className="text-sm mb-2">Token Allocation</div>
                  <div className="h-3 bg-[#2c2c2e] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                      style={{ width: `${totalAllocated}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "preview" && (
              <div className="space-y-6">
                <div className="space-y-2">
                  <h3 className="text-xl font-medium">Vault Name</h3>
                  <p className="text-sm text-gray-400">What do you want to name your vault?</p>
                  <Input
                    placeholder="Type something"
                    className="mt-2 bg-[#2c2c2e] border-0 text-white placeholder:text-gray-500"
                    value={vaultName}
                    onChange={(e) => setVaultName(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <h3 className="text-xl font-medium">Description</h3>
                  <p className="text-sm text-gray-400">What do you want your vault to look like?</p>
                  <Textarea
                    placeholder="Type something"
                    className="mt-2 bg-[#2c2c2e] border-0 text-white placeholder:text-gray-500 min-h-[100px]"
                    value={vaultDescription}
                    onChange={(e) => setVaultDescription(e.target.value)}
                  />
                </div>

                <div className="space-y-4">
                  {allocations.slice(0, 2).map((allocation) => (
                    <div key={allocation.id} className="bg-[#2c2c2e] rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <div className="flex items-center gap-2">
                          <div className="h-6 w-6 rounded-full bg-blue-500 flex items-center justify-center">
                            <span className="text-xs">A</span>
                          </div>
                          <div>
                            <div className="font-medium">{allocation.name}</div>
                            <div className="text-xs text-gray-400">{allocation.strategy}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span>{allocation.percentage}%</span>
                          <ChevronDown className="h-4 w-4 text-gray-400" />
                        </div>
                      </div>
                      <div className="pt-2">
                        <Slider
                          value={[allocation.percentage]}
                          min={0}
                          max={100}
                          step={1}
                          disabled
                          className="cursor-default"
                        >
                          <SliderTrack className="bg-blue-600 h-2 rounded-full">
                            <SliderRange className="bg-blue-400" />
                          </SliderTrack>
                          <SliderThumb className="h-4 w-4 bg-white rounded-full border-2 border-blue-600" />
                        </Slider>
                      </div>

                      <div className="mt-4 border-t border-gray-700 pt-3">
                        <div className="text-sm mb-2">Token Allocation</div>
                        <div className="flex items-center justify-between bg-[#2c2c2e] rounded px-3 py-2">
                          <div className="flex items-center gap-2">
                            {allocation.tokenIcon ? (
                              <div className="h-5 w-5 rounded-full bg-teal-500 flex items-center justify-center">
                                <span className="text-xs">{allocation.tokenIcon}</span>
                              </div>
                            ) : (
                              <div className="h-5 w-5 rounded-full bg-gray-500 flex items-center justify-center">
                                <span className="text-xs">L</span>
                              </div>
                            )}
                            <span className="text-sm">{allocation.token}</span>
                          </div>
                          <button
                            className="text-gray-400 hover:text-red-500 transition-colors"
                            onClick={() => handleRemoveAllocation(allocation.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-8 flex justify-between">
              {activeTab !== "setup" && (
                <Button
                  variant="outline"
                  onClick={handleBack}
                  className="border-gray-700 bg-[#2c2c2e] text-white hover:bg-zinc-800 hover:text-white cursor-pointer"
                >
                  <ChevronLeft className="mr-1 h-4 w-4" /> Back
                </Button>
              )}
              <div className="flex-1"></div>
              {activeTab === "preview" ? (
                <Button onClick={handleCreateVault} className="bg-white text-black hover:bg-gray-200 cursor-pointer">
                  Create Vault
                  <ChevronRight className="ml-1 h-4 w-4" />
                </Button>
              ) : (
                <Button onClick={handleNext} className="bg-white text-black hover:bg-gray-200 cursor-pointer">
                  Next
                  <ChevronRight className="ml-1 h-4 w-4" />
                </Button>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
