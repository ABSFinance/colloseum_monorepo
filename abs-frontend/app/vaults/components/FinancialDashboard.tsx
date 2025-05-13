"use client";

import { Briefcase, Lock, Shield } from "lucide-react";
import { StatCard } from "./Statscard";
import { TabNavigation } from "./Tabsnav";
import { CreateVaultButton } from "./CreateVault";
import type { Position } from "./PositionList";
import Sidebar from "@/components/Sidebar";

export default function FinancialDashboard() {
  // Sample data for demonstration
  const portfolioData = {
    balance: "$111.81K",
    openPositions: 26,
    activeVaults: 16,
    percentChange: 3.2,
  };

  // Sample position data
  const positions: {
    open: Position[];
    closed: Position[];
    vaults: Position[];
  } = {
    open: [
      {
        id: 1,
        name: "AAPL",
        value: "$12,450",
        change: "+2.3%",
        isPositive: true,
      },
      {
        id: 2,
        name: "TSLA",
        value: "$8,720",
        change: "-1.5%",
        isPositive: false,
      },
      {
        id: 3,
        name: "MSFT",
        value: "$15,300",
        change: "+3.7%",
        isPositive: true,
      },
    ],
    closed: [
      {
        id: 4,
        name: "AMZN",
        value: "$9,870",
        change: "+5.2%",
        isPositive: true,
      },
      {
        id: 5,
        name: "GOOGL",
        value: "$11,230",
        change: "+2.8%",
        isPositive: true,
      },
    ],
    vaults: [
      {
        id: 6,
        name: "Retirement",
        value: "$45,600",
        change: "+1.2%",
        isPositive: true,
      },
      {
        id: 7,
        name: "Emergency",
        value: "$22,300",
        change: "+0.8%",
        isPositive: true,
      },
      {
        id: 8,
        name: "Education",
        value: "$18,750",
        change: "+1.5%",
        isPositive: true,
      },
    ],
  };

  return (
    <div className="flex h-screen bg-[#0d0d0d] text-white overflow-hidden">
      <Sidebar />

      <div className="min-h-screen bg-[#0d0d0d] text-white p-4 md:p-6 lg:p-8 flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h1 className="text-xl md:text-2xl font-bold">
              Financial Dashboard
            </h1>
            <CreateVaultButton />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <StatCard
              icon={<Briefcase className="h-5 w-5 text-[#8b5cf6]" />} // violet-500
              title="Portfolio Balance"
              value={portfolioData.balance}
              percentChange={portfolioData.percentChange}
              delay={0.1}
            />

            <StatCard
              icon={<Lock className="h-5 w-5 text-[#06b6d4]" />} // cyan-500
              title="Open Positions"
              value={portfolioData.openPositions}
              delay={0.2}
            />

            <StatCard
              icon={<Shield className="h-5 w-5 text-[#10b981]" />} // emerald-500
              title="Active Vaults"
              value={portfolioData.activeVaults}
              delay={0.3}
            />
          </div>

          <TabNavigation
            openPositions={positions.open}
            closedPositions={positions.closed}
            vaults={positions.vaults}
          />
        </div>
      </div>
    </div>
  );
}
