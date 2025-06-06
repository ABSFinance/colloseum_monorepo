"use client";

import { useEffect, useMemo, useState } from "react";
import { ArrowLeft } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Area,
  AreaChart,
} from "recharts";
import { cn } from "@/lib/utils";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/header";
import Link from "next/link";
import { useParams } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { VaultInfo } from "@/lib/types";

export default function CryptoDashboard() {
  const [depositAmount, setDepositAmount] = useState("");
  const [activeTab, setActiveTab] = useState("deposit");
  const [timeframe, setTimeframe] = useState("7D");
  const { vaultid, poolid } = useParams() as {
    vaultid: string;
    poolid: string;
  };
  const [vaultData, setVaultData] = useState<VaultInfo>();
  const [userVaultData, setUserVaultData] = useState<any[]>([]);
  const [lendingpoolname, setlendingpoolname] = useState<any[]>([]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (!vaultid) return;

      setLoading(true);

      const { data: vault, error: vaultError } = await supabase
        .from("abs_vault_info")
        .select("*")
        .eq("id", vaultid)
        .single();

      const { data: userVault, error: userVaultError } = await supabase
        .from("abs_vault_allocation_history")
        .select("*")
        .eq("pool_id", poolid);

      const allocatedPoolIds =
        userVault?.map((item) => item.allocated_pool_id) ?? [];

      const { data: lend_data, error: lend_data_error } = await supabase
        .from("lending_pool_info")
        .select("*")
        .in("pool_id", allocatedPoolIds);

      if (vaultError || userVaultError || lend_data_error) {
        console.error(
          "Supabase fetch error:",
          vaultError || userVaultError || lend_data_error
        );
      } else {
        setVaultData(vault);
        setUserVaultData(userVault);
        setlendingpoolname(lend_data);
      }

      setLoading(false);
    };

    fetchData();
  }, [vaultid, poolid]);

  console.log(vaultData, userVaultData, lendingpoolname);

  console.log("pool id ", poolid, "vault id", vaultid);

  // Vault allocation data
  const allocationData = useMemo(() => {
    const COLORS = [
      "#f43f5e",
      "#8b5cf6",
      "#22d3ee",
      "#34d399",
      "#facc15",
      "#fb923c",
    ];

    if (!userVaultData || userVaultData.length === 0) return [];

    const total = userVaultData.reduce(
      (sum: number, item: any) => sum + item.amount,
      0
    );

    return userVaultData.map((item: any, index: number) => {
      const poolInfo = lendingpoolname.find(
        (p: any) => p.pool_id === item.allocated_pool_id
      );
      const poolName = poolInfo?.name || `Pool ${item.allocated_pool_id}`;

      return {
        name: poolName,
        value: parseFloat(((item.amount / total) * 100).toFixed(2)),
        color: COLORS[index % COLORS.length],
      };
    });
  }, [userVaultData, lendingpoolname]);

  // Performance data with more variation for better visualization
  const performanceData = [
    { day: "May 1", value: 33.2, volume: 1200 },
    { day: "May 2", value: 33.5, volume: 1800 },
    { day: "May 3", value: 33.3, volume: 1400 },
    { day: "May 4", value: 33.5, volume: 2200 },
    { day: "May 5", value: 33.3, volume: 1900 },
    { day: "May 6", value: 33.6, volume: 2400 },
    { day: "May 7", value: 33.1, volume: 1600 },
  ];

  return (
    <div className="flex h-full bg-[#0d0d0d] text-white">
      <Sidebar />
      <div className="flex flex-col min-h-screen bg-gradient-to-br from-zinc-950 w-full to-zinc-900 text-white p-6">
        {/* Header */}
        <Header />
        <header className="flex items-center justify-between mt-7">
          <div className="flex items-center gap-3">
            <Link href={"/vaults"}>
              <Button
                variant="ghost"
                size="icon"
                className="rounded-full bg-zinc-800 hover:bg-zinc-900 hover:text-white cursor-pointer"
              >
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
              <MetricCard title="Stratergy" value={vaultData?.strategy ?? ""} />
              <MetricCard
                title="Adapters"
                value={vaultData?.adaptors?.join(", ") ?? ""}
              />
              <MetricCard
                title="Weight"
                value={vaultData?.weight?.join(", ") ?? ""}
              />
              <MetricCard
                title="Capacity (Lamports)"
                value={vaultData?.capacity?.toString() ?? ""}
              />
            </div>

            {/* Performance Chart */}
            <Card className="bg-zinc-800/50 border-zinc-700/50 backdrop-blur-sm overflow-hidden">
              <CardHeader className="pb-2">
                <div className="flex justify-between items-center">
                  <CardTitle className="text-lg font-medium text-white">
                    Vault Performance
                  </CardTitle>
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
                            : "text-zinc-400 hover:text-black cursor-pointer"
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
                    <AreaChart
                      data={performanceData}
                      margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
                    >
                      <defs>
                        <linearGradient
                          id="colorValue"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="5%"
                            stopColor="#8b5cf6"
                            stopOpacity={0.8}
                          />
                          <stop
                            offset="95%"
                            stopColor="#8b5cf6"
                            stopOpacity={0}
                          />
                        </linearGradient>
                      </defs>
                      <XAxis
                        dataKey="day"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: "#9ca3af", fontSize: 12 }}
                      />
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
                <CardTitle className="text-lg font-medium">
                  Vault Allocation
                </CardTitle>
                <CardDescription className="text-zinc-400">
                  Current distribution of assets
                </CardDescription>
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
                          {allocationData.map((entry: any, index: number) => (
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
                    {allocationData.map((item: any, index: number) => (
                      <div key={index} className="flex items-center gap-2">
                        <div
                          className="w-5 h-5 rounded-sm"
                          style={{ backgroundColor: item.color }}
                        ></div>
                        <div className="flex flex-col">
                          <span className="text-sm text-zinc-300">
                            {item.name}
                          </span>
                          <span className="text-sm font-medium">
                            {item.value}%
                          </span>
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
                <CardTitle className="text-lg font-medium">
                  Manage Assets
                </CardTitle>
                <CardDescription className="text-zinc-400">
                  Deposit or withdraw your assets
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Tabs
                  value={activeTab}
                  onValueChange={setActiveTab}
                  className="w-full"
                >
                  <TabsList className="grid w-full grid-cols-2 bg-zinc-900/80 p-1">
                    <TabsTrigger
                      value="deposit"
                      className={cn(
                        "data-[state=active]:shadow-lg cursor-pointer text-gray-300",
                        activeTab === "deposit" && "bg-white text-black"
                      )}
                    >
                      Deposit
                    </TabsTrigger>
                    <TabsTrigger
                      value="withdraw"
                      className={cn(
                        "data-[state=active]:shadow-lg text-gray-300 cursor-pointer",
                        activeTab === "withdraw" && "bg-white text-black"
                      )}
                    >
                      Withdraw
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="deposit" className="space-y-4 mt-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Amount to deposit</span>
                        <Button
                          variant="link"
                          className="h-auto p-0 text-blue-400"
                        >
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

                    <Button className="w-full h-12 bg-white text-black hover:bg-slate-200 hover:text-black cursor-pointer shadow-lg shadow-blue-700/20">
                      Connect Wallet to Deposit
                    </Button>
                  </TabsContent>

                  <TabsContent value="withdraw" className="space-y-4 mt-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Amount to withdraw</span>
                        <Button
                          variant="link"
                          className="h-auto p-0 text-blue-400"
                        >
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
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value }: { title: string; value: string }) {
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
            "bg-gradient-to-r from-green-500/0 via-green-500/30 to-green-500/0"
          )}
        />
      </CardContent>
    </Card>
  );
}
