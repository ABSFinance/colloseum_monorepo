"use client"

import { redirect } from "next/navigation"

// import FinancialDashboard from "./components/FinancialDashboard"
// import MobileDashboard from "./components/Mobiledash"
// import { useMediaQuery } from "@/hooks/use-mobile"

export default function Page() {
  // const isMobile = useMediaQuery('(max-width: 768px)')

  return (
    redirect("/dashboard/vaults")
  )


  // return isMobile ? <MobileDashboard /> : <FinancialDashboard />
}
