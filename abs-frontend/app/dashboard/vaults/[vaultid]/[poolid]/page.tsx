"use client"

import { useEffect, useState } from "react"
import { ArrowLeft, Info, TrendingUp, BarChart3, DollarSign, Clock, Zap, ChevronRight } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { PieChart, Pie, Cell, XAxis, YAxis, ResponsiveContainer, Tooltip, Area, AreaChart } from "recharts"
import { cn } from "@/lib/utils"
import Sidebar from "@/components/Sidebar"
import Header from "@/components/header"
import Link from "next/link"
import { useParams } from "next/navigation"
import { supabase } from "@/lib/supabase"
import { VaultInfo } from "@/lib/types"

export default function CryptoDashboard() {
    const [depositAmount, setDepositAmount] = useState("")
    const [activeTab, setActiveTab] = useState("deposit")
    const [timeframe, setTimeframe] = useState("7D")
    const { vaultid, poolid } = useParams() as { vaultid: string, poolid: string };
    const [vaultData, setVaultData] = useState<VaultInfo>();
    const [userVaultData, setUserVaultData] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            if (!vaultid) return

            setLoading(true)

            const { data: vault, error: vaultError } = await supabase
                .from("abs_vault_info")
                .select("*")
                .eq("id", vaultid)
                .single()

            const { data: userVault, error: userVaultError } = await supabase
                .from("abs_vault_allocation_history ")
                .select("*")
                .eq("pool_id", poolid);

            if (vaultError || userVaultError) {
                console.error("Supabase fetch error:", vaultError || userVaultError)
            } else {
                console.log(vault, userVault);
                setVaultData(vault)
                setUserVaultData(userVault)
            }

            setLoading(false)
        }

        fetchData()
    }, [vaultid,poolid]);

    console.log(vaultData, userVaultData);

    console.log("pool id ", poolid, "vault id", vaultid);

    // Vault allocation data
    const allocationData = [
        { name: "Kamino Lend USDC", value: 15.2, color: "#8b5cf6" },
        { name: "Kamino Market USDT", value: 12.7, color: "#f97316" },
        { name: "Kamino Lend USDC", value: 7.4, color: "#10b981" },
        { name: "Kamino Lend USDC", value: 5.2, color: "#7c3aed" },
        { name: "Kamino Lend USDC", value: 23, color: "#0ea5e9" },
        { name: "Lend JP-Market USDC", value: 19.2, color: "#22c55e" },
        { name: "Kamino Lend USDC", value: 10, color: "#a3e635" },
        { name: "Kamino Lend USDC", value: 22, color: "#ffffff" },
        { name: "Kamino Lend USDC", value: 8.4, color: "#3b82f6" },
    ]

    // Performance data with more variation for better visualization
    const performanceData = [
        { day: "May 1", value: 33.2, volume: 1200 },
        { day: "May 2", value: 33.5, volume: 1800 },
        { day: "May 3", value: 33.3, volume: 1400 },
        { day: "May 4", value: 33.5, volume: 2200 },
        { day: "May 5", value: 33.3, volume: 1900 },
        { day: "May 6", value: 33.6, volume: 2400 },
        { day: "May 7", value: 33.1, volume: 1600 },
    ]

    // Vault details
    const vaultDetails = [
        { label: "Current Vault Price", value: "$770", unit: "per SOL", icon: <DollarSign className="h-4 w-4" /> },
        { label: "Protocol", value: "Drift Protocol", icon: <BarChart3 className="h-4 w-4" /> },
        { label: "Capacity", value: "75%", icon: <TrendingUp className="h-4 w-4" /> },
        { label: "APY", value: "3.82%", icon: <Zap className="h-4 w-4" /> },
        { label: "Age", value: "90D", icon: <Clock className="h-4 w-4" /> },
    ]

    // Recent transactions
    const recentTransactions = [
        { type: "Deposit", amount: "+2.5 SOL", value: "$1,925", time: "2h ago", status: "completed" },
        { type: "Withdraw", amount: "-1.2 SOL", value: "$924", time: "1d ago", status: "completed" },
        { type: "Deposit", amount: "+0.8 SOL", value: "$616", time: "3d ago", status: "completed" },
    ]

    return (
        <div className="flex h-full bg-[#0d0d0d] text-white">
            <Sidebar />
            <div className="flex flex-col min-h-screen bg-gradient-to-br from-zinc-950 w-full to-zinc-900 text-white p-6">
                {/* Header */}
                <Header />
                <header className="flex items-center justify-between mt-7">
                    <div className="flex items-center gap-3">
                        <Link href={"/dashboard/vaults"}>
                            <Button variant="ghost" size="icon" className="rounded-full bg-zinc-800 hover:bg-zinc-900 hover:text-white cursor-pointer">
                                <ArrowLeft className="h-5 w-5" />
                            </Button>
                        </Link>
                        <div className="flex items-center gap-3">
                            <div className="bg-gradient-to-r from-blue-500 to-violet-500 rounded-full h-10 w-10 flex items-center justify-center shadow-lg shadow-blue-500/20">
                                <span className="text-sm font-bold">SOL</span>
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold">{vaultData?.name}</h1>
                            </div>
                        </div>
                    </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-5">
                    <div className="lg:col-span-2 space-y-6">
                        {/* Key metrics */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <MetricCard title="Stratergy" value={vaultData?.strategy ?? ''} />
                            <MetricCard title="Adapters" value={vaultData?.adaptors?.join(', ') ?? ''} />
                            <MetricCard title="Weight" value={vaultData?.weight?.join(', ') ?? ''} />
                            <MetricCard title="Capacity (Lamports)" value={vaultData?.capacity?.toString() ?? ''} />
                        </div>

                        {/* Performance Chart */}
                        <Card className="bg-zinc-800/50 border-zinc-700/50 backdrop-blur-sm overflow-hidden">
                            <CardHeader className="pb-2">
                                <div className="flex justify-between items-center">
                                    <CardTitle className="text-lg font-medium text-white">Vault Performance</CardTitle>
                                    <div className="flex gap-1 bg-zinc-900/80 rounded-lg p-1">
                                        {["24H", "7D", "30D", "90D"].map((period) => (
                                            <Button
                                                key={period}
                                                variant={timeframe === period ? "default" : "ghost"}
                                                size="sm"
                                                className={cn(
                                                    "h-7 text-xs rounded-md",
                                                    timeframe === period
                                                        ? "bg-gradient-to-r from-blue-600 to-violet-600 text-white"
                                                        : "text-zinc-400 hover:text-black cursor-pointer",
                                                )}
                                                onClick={() => setTimeframe(period)}
                                            >
                                                {period}
                                            </Button>
                                        ))}
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="p-0">
                                <div className="h-[300px] w-full pt-4">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <AreaChart data={performanceData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                                            <defs>
                                                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                                                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "#9ca3af", fontSize: 12 }} />
                                            <YAxis
                                                domain={[33.0, 33.8]}
                                                axisLine={false}
                                                tickLine={false}
                                                tick={{ fill: "#9ca3af", fontSize: 12 }}
                                                tickFormatter={(value) => `$${value}`}
                                            />
                                            <Tooltip
                                                contentStyle={{
                                                    backgroundColor: "#27272a",
                                                    borderColor: "#3f3f46",
                                                    borderRadius: "0.5rem",
                                                    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                                                }}
                                                itemStyle={{ color: "#e4e4e7" }}
                                                formatter={(value) => [`$${value}`, "Price"]}
                                                labelFormatter={(label) => `Date: ${label}`}
                                            />
                                            <Area
                                                type="monotone"
                                                dataKey="value"
                                                stroke="#8b5cf6"
                                                strokeWidth={2}
                                                fillOpacity={1}
                                                fill="url(#colorValue)"
                                            />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Vault Allocation */}
                        <Card className="bg-zinc-800/50 border-zinc-700/50 backdrop-blur-sm text-white">
                            <CardHeader>
                                <CardTitle className="text-lg font-medium">Vault Allocation</CardTitle>
                                <CardDescription className="text-zinc-400">Current distribution of assets</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="flex flex-col md:flex-row gap-8 items-center">
                                    <div className="w-full md:w-1/2 h-[250px] flex items-center justify-center">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <PieChart>
                                                <Pie
                                                    data={allocationData}
                                                    cx="50%"
                                                    cy="50%"
                                                    innerRadius={70}
                                                    outerRadius={90}
                                                    paddingAngle={3}
                                                    dataKey="value"
                                                    strokeWidth={2}
                                                    stroke="#18181b"
                                                >
                                                    {allocationData.map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                                    ))}
                                                </Pie>
                                                <Tooltip
                                                    contentStyle={{
                                                        backgroundColor: "#27272a",
                                                        borderColor: "#3f3f46",
                                                        borderRadius: "0.5rem",
                                                    }}
                                                    itemStyle={{ color: "#e4e4e7" }}
                                                    formatter={(value) => [`${value}%`, "Allocation"]}
                                                />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    </div>
                                    <div className="w-full md:w-1/2 grid grid-cols-2 gap-3">
                                        {allocationData.map((item, index) => (
                                            <div key={index} className="flex items-center gap-2">
                                                <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: item.color }}></div>
                                                <div className="flex flex-col">
                                                    <span className="text-xs text-zinc-300">{item.name}</span>
                                                    <span className="text-sm font-medium">{item.value}%</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="space-y-6">
                        {/* Deposit/Withdraw */}
                        <Card className="bg-zinc-800/50 border-zinc-700/50 backdrop-blur-sm text-white">
                            <CardHeader>
                                <CardTitle className="text-lg font-medium">Manage Assets</CardTitle>
                                <CardDescription className="text-zinc-400">Deposit or withdraw your assets</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                                    <TabsList className="grid w-full grid-cols-2 bg-zinc-900/80 p-1">
                                        <TabsTrigger
                                            value="deposit"
                                            className={cn(
                                                "data-[state=active]:shadow-lg cursor-pointer text-gray-300",
                                                activeTab === "deposit" &&
                                                "bg-white text-black",
                                            )}
                                        >
                                            Deposit
                                        </TabsTrigger>
                                        <TabsTrigger
                                            value="withdraw"
                                            className={cn(
                                                "data-[state=active]:shadow-lg text-gray-300 cursor-pointer",
                                                activeTab === "withdraw" &&
                                                "bg-white text-black",
                                            )}
                                        >
                                            Withdraw
                                        </TabsTrigger>
                                    </TabsList>

                                    <TabsContent value="deposit" className="space-y-4 mt-4">
                                        <div className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span>Amount to deposit</span>
                                                <Button variant="link" className="h-auto p-0 text-blue-400">
                                                    Max
                                                </Button>
                                            </div>
                                            <div className="relative">
                                                <Input
                                                    type="text"
                                                    value={depositAmount}
                                                    onChange={(e) => setDepositAmount(e.target.value)}
                                                    placeholder="0.00"
                                                    className="bg-zinc-900/80 border-zinc-700 pl-4 pr-20 h-12 text-lg"
                                                />
                                                <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2 bg-zinc-800 px-2 py-1 rounded-md">
                                                    <div className="bg-blue-500 rounded-full h-5 w-5 flex items-center justify-center">
                                                        <span className="text-[10px] font-bold">$</span>
                                                    </div>
                                                    <span className="text-sm font-medium">USDC</span>
                                                </div>
                                            </div>
                                            <div className="flex justify-between text-xs text-zinc-400 mt-1">
                                                <span>Available: 1,240 USDC</span>
                                                <span>≈ $1,240</span>
                                            </div>
                                        </div>

                                        <div className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span>You will receive (estimated)</span>
                                            </div>
                                            <div className="bg-zinc-900/80 border border-zinc-700 rounded-md p-3 flex justify-between items-center">
                                                <span className="text-lg">1.61 SOL</span>
                                                <span className="text-sm text-zinc-400">≈ $1,240</span>
                                            </div>
                                        </div>

                                        <Button className="w-full h-12 bg-white text-black hover:bg-slate-200 hover:text-black cursor-pointer shadow-lg shadow-blue-700/20">
                                            Connect Wallet to Deposit
                                        </Button>
                                    </TabsContent>

                                    <TabsContent value="withdraw" className="space-y-4 mt-4">
                                        <div className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span>Amount to withdraw</span>
                                                <Button variant="link" className="h-auto p-0 text-blue-400">
                                                    Max
                                                </Button>
                                            </div>
                                            <div className="relative">
                                                <Input
                                                    type="text"
                                                    placeholder="0.00"
                                                    className="bg-zinc-900/80 border-zinc-700 pl-4 pr-20 h-12 text-lg"
                                                />
                                                <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2 bg-zinc-800 px-2 py-1 rounded-md">
                                                    <div className="bg-violet-500 rounded-full h-5 w-5 flex items-center justify-center">
                                                        <span className="text-[10px] font-bold">S</span>
                                                    </div>
                                                    <span className="text-sm font-medium">SOL</span>
                                                </div>
                                            </div>
                                            <div className="flex justify-between text-xs text-zinc-400 mt-1">
                                                <span>Available: 6.75 SOL</span>
                                                <span>≈ $5,200</span>
                                            </div>
                                        </div>

                                        <Button className="w-full h-12 bg-white text-black hover:bg-slate-200 hover:text-black cursor-pointer shadow-lg shadow-blue-700/20">
                                            Connect Wallet to Withdraw
                                        </Button>
                                    </TabsContent>
                                </Tabs>
                            </CardContent>
                        </Card>

                        {/* Vault Details */}
                        <Card className="bg-zinc-800/50 border-zinc-700/50 backdrop-blur-sm">
                            <CardHeader>
                                <CardTitle className="text-lg font-medium text-white">Vault Details</CardTitle>
                                <CardDescription className="text-zinc-400">Current vault statistics</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {vaultDetails.map((detail, index) => (
                                    <div key={index}>
                                        <div className="flex justify-between items-center py-2">
                                            <div className="flex items-center gap-2 text-zinc-400">
                                                {detail.icon}
                                                <span>{detail.label}</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                {detail.label === "Current Vault Price" && <Info className="h-4 w-4 text-blue-400" />}
                                                <div className="flex items-center gap-1">
                                                    <span className="font-medium text-white">{detail.value}</span>
                                                    {detail.unit && <span className="text-sm text-white">{detail.unit}</span>}
                                                </div>
                                            </div>
                                        </div>
                                        {index < vaultDetails.length - 1 && <Separator className="bg-zinc-700/50" />}
                                    </div>
                                ))}
                            </CardContent>
                        </Card>

                        {/* Recent Transactions */}
                        <Card className="bg-zinc-800/50 border-zinc-700/50 backdrop-blur-sm text-white">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-lg font-medium">Recent Transactions</CardTitle>
                                <CardDescription className="text-zinc-400">Your latest activity</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {recentTransactions.map((tx, index) => (
                                    <div key={index} className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div
                                                className={cn(
                                                    "h-8 w-8 rounded-full flex items-center justify-center",
                                                    tx.type === "Deposit" ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400",
                                                )}
                                            >
                                                {tx.type === "Deposit" ? "+" : "-"}
                                            </div>
                                            <div>
                                                <p className="font-medium">{tx.type}</p>
                                                <p className="text-xs text-zinc-400">{tx.time}</p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p className={cn("font-medium", tx.type === "Deposit" ? "text-green-400" : "text-red-400")}>
                                                {tx.amount}
                                            </p>
                                            <p className="text-xs text-zinc-400">{tx.value}</p>
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                            <CardFooter className="pt-0">
                                <Button variant="secondary" className="w-full border-zinc-700 hover:bg-slate-200 cursor-pointer">
                                    View All Transactions
                                    <ChevronRight className="h-4 w-4 ml-2" />
                                </Button>
                            </CardFooter>
                        </Card>
                    </div>
                </div>
            </div>

        </div>
    )
}

function MetricCard({
    title,
    value,
}: { title: string; value: string }) {
    return (
        <Card className="bg-zinc-800/50 border-zinc-700/50 backdrop-blur-sm overflow-hidden">
            <CardContent className="p-4">
                <div className="flex flex-col">
                    <p className="text-md text-zinc-400">{title}</p>
                    <p className="text-lg font-bold mt-1 text-white">{value}</p>
                </div>
                <div
                    className={cn(
                        "absolute bottom-0 left-0 right-0 h-1",
                        "bg-gradient-to-r from-green-500/0 via-green-500/30 to-green-500/0",
                    )}
                />
            </CardContent>
        </Card>
    )
}
