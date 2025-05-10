"use client"
import { useEffect, useState } from "react"
import FinancialDashboard from "./components/FinancialDashboard"
import MobileDashboard from "./components/Mobiledash"
import { useMediaQuery } from "@/hooks/use-mobile"

export default function Page() {
  const [isMounted, setIsMounted] = useState(false)
  const isMobile = useMediaQuery('(max-width: 768px)')

  useEffect(() => {
    setIsMounted(true)
  }, []);

  return isMobile ? <MobileDashboard /> : <FinancialDashboard />
}
