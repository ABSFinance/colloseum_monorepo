"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { ArrowRight, TrendingUp, Shield, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Hero() {
    const [isVisible, setIsVisible] = useState(false)

    useEffect(() => {
        setIsVisible(true)
    }, [])

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                delayChildren: 0.3,
                staggerChildren: 0.2,
            },
        },
    }

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: { duration: 0.5 },
        },
    }

    const statsVariants = {
        hidden: { scale: 0.8, opacity: 0 },
        visible: {
            scale: 1,
            opacity: 1,
            transition: { duration: 0.6, delay: 0.8 },
        },
    }

    const glowVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: [0.1, 0.3, 0.1],
            transition: {
                duration: 5,
                repeat: Number.POSITIVE_INFINITY,
                repeatType: "reverse",
            },
        },
    }

    return (
        <section className="relative pt-24 pb-16 md:pt-32 md:pb-24 overflow-hidden">
            {/* Background glow effect */}
            <motion.div
                initial="hidden"
                animate={isVisible ? "visible" : "hidden"}
                variants={glowVariants}
                className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gray-500/10 rounded-full blur-[100px] z-0"
            />

            <div className="container mx-auto px-4 relative z-10">
                <motion.div
                    initial="hidden"
                    animate={isVisible ? "visible" : "hidden"}
                    variants={containerVariants}
                    className="max-w-5xl mx-auto text-center"
                >
                    <motion.div variants={itemVariants} className="mb-3">
                        <span className="inline-block py-1 px-3 border border-gray-700 rounded-full text-xs font-medium text-gray-400 tracking-wider">
                            MAXIMIZE YOUR CRYPTO YIELD
                        </span>
                    </motion.div>

                    <motion.h1 variants={itemVariants} className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-6">
                        Optimize Your{" "}
                        <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500">DeFi Yield</span>{" "}
                        Automatically
                    </motion.h1>

                    <motion.p variants={itemVariants} className="text-lg md:text-xl text-gray-400 max-w-3xl mx-auto mb-8">
                        ABS Finance uses advanced algorithms to find and allocate your assets to the highest-yielding opportunities
                        across multiple chains and protocols.
                    </motion.p>

                    <motion.div variants={itemVariants} className="flex flex-col sm:flex-row justify-center gap-4 mb-16">
                        <Button size="lg" className="bg-white text-black hover:bg-gray-200 transition-colors text-base">
                            Launch App
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                        <Button
                            size="lg"
                            variant="outline"
                            className="border-gray-700 text-white hover:bg-white/10 transition-colors text-base"
                        >
                            Learn How It Works
                        </Button>
                    </motion.div>

                    <motion.div variants={statsVariants} className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
                        <StatCard
                            icon={<TrendingUp className="h-6 w-6 text-white" />}
                            title="$245M+"
                            description="Total Value Locked"
                        />
                        <StatCard icon={<BarChart3 className="h-6 w-6 text-white" />} title="12.4%" description="Average APY" />
                        <StatCard icon={<Shield className="h-6 w-6 text-white" />} title="100%" description="Secure & Audited" />
                    </motion.div>
                </motion.div>
            </div>

            {/* Abstract grid pattern */}
            <div className="absolute inset-0 overflow-hidden z-0 opacity-20">
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gray-800 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gray-800 to-transparent" />
                <div className="absolute top-0 bottom-0 left-0 w-px bg-gradient-to-b from-transparent via-gray-800 to-transparent" />
                <div className="absolute top-0 bottom-0 right-0 w-px bg-gradient-to-b from-transparent via-gray-800 to-transparent" />

                {Array.from({ length: 10 }).map((_, i) => (
                    <div key={i} className="absolute top-0 left-0 right-0 h-px bg-gray-800" style={{ top: `${i * 10}%` }} />
                ))}
                {Array.from({ length: 10 }).map((_, i) => (
                    <div key={i} className="absolute top-0 bottom-0 left-0 w-px bg-gray-800" style={{ left: `${i * 10}%` }} />
                ))}
            </div>
        </section>
    )
}

function StatCard({
    icon,
    title,
    description,
}: {
    icon: React.ReactNode
    title: string
    description: string
}) {
    return (
        <motion.div
            whileHover={{ y: -5, transition: { duration: 0.2 } }}
            className="bg-white/5 backdrop-blur-sm border border-gray-800 rounded-xl p-6 text-center"
        >
            <div className="flex justify-center mb-4">
                <div className="p-2 bg-white/10 rounded-lg">{icon}</div>
            </div>
            <h3 className="text-2xl font-bold mb-1">{title}</h3>
            <p className="text-gray-400">{description}</p>
        </motion.div>
    )
}
