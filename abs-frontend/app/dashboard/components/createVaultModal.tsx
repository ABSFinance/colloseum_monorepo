"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { X, ChevronRight, ChevronDown } from "lucide-react"

interface CreateVaultModalProps {
    isOpen: boolean
    onClose: () => void
}

export function CreateVaultModal({ isOpen, onClose }: CreateVaultModalProps) {
    const [activeTab, setActiveTab] = useState<"setup" | "allocation" | "preview">("setup")

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

                        <div className="space-y-8">
                            <div className="space-y-2">
                                <h3 className="text-lg font-medium">Vault Name</h3>
                                <p className="text-sm text-gray-400">What do you want to name your vault?</p>
                                <Input
                                    placeholder="Type something"
                                    className="mt-2 bg-[#2c2c2e] border-0 text-white placeholder:text-gray-500"
                                />
                            </div>

                            <div className="space-y-2">
                                <h3 className="text-lg font-medium">Description</h3>
                                <p className="text-sm text-gray-400">What do you want your vault to look like?</p>
                                <Textarea
                                    placeholder="Type something"
                                    className="mt-2 bg-[#2c2c2e] border-0 text-white placeholder:text-gray-500 min-h-[100px]"
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

                        <div className="mt-8 flex justify-end">
                            <Button className="bg-white text-black hover:bg-gray-200">
                                Next <ChevronRight className="ml-1 h-4 w-4" />
                            </Button>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    )
}
