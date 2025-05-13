"use client";
import MobileSidebar from "@/components/Mobile-sidebar";
import FinancialDashboard from "./FinancialDashboard";

export default function MobileDashboard() {
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
      </header>
      <FinancialDashboard />
    </div>
  );
}
