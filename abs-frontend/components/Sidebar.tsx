"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

export default function Sidebar() {
    const pathname = usePathname()

    const navItems = [
        { name: "All Vaults", path: "/", icon: "shield" },
        { name: "Dashboard", path: "/dashboard", icon: "home" },
        { name: "Reward Center", path: "/rewards", icon: "gift" },
    ]

    return (
        <motion.aside
            className="w-64 border-r border-gray-800 h-full flex-shrink-0 overflow-hidden hidden md:block"
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
        >
            <div className="p-6">
                <motion.div className="flex items-center gap-3" whileHover={{ scale: 1.03 }}>
                    <div className="w-10 h-10 bg-white rounded-md flex items-center justify-center">
                        <div className="w-6 h-6 bg-black transform rotate-45" />
                    </div>
                    <span className="text-xl font-bold">ABS Finance</span>
                </motion.div>
            </div>

            <nav className="mt-6 px-3">
                <ul className="space-y-2">
                    {navItems.map((item) => (
                        <motion.li key={item.path} whileHover={{ x: 5 }} whileTap={{ scale: 0.95 }}>
                            <Link
                                href={item.path}
                                className={cn(
                                    "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                                    pathname === item.path
                                        ? "bg-gray-800 text-white"
                                        : "text-gray-400 hover:text-white hover:bg-gray-800/50",
                                )}
                            >
                                <Icon name={item.icon} />
                                <span>{item.name}</span>
                            </Link>
                        </motion.li>
                    ))}
                </ul>
            </nav>
        </motion.aside>
    )
}

function Icon({ name }: { name: string }) {
    switch (name) {
        case "shield":
            return (
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
            )
        case "home":
            return (
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                    <polyline points="9 22 9 12 15 12 15 22" />
                </svg>
            )
        case "gift":
            return (
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <polyline points="20 12 20 22 4 22 4 12" />
                    <rect x="2" y="7" width="20" height="5" />
                    <line x1="12" y1="22" x2="12" y2="7" />
                    <path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z" />
                    <path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z" />
                </svg>
            )
        default:
            return null
    }
}
