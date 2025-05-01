
"use client"
import { useEffect, useState } from "react";
import FinancialDashboard from "./components/FinancialDashboard";
import { useMediaQuery } from "@/hooks/use-mobile";
import MobileDashboard from "./components/Mobiledash";


export default function Page() {
  const [isMounted, setIsMounted] = useState(false)
  const isMobile = useMediaQuery("(max-width: 768px)")
  useEffect(() => {
    setIsMounted(true)
  }, [])

  if (!isMounted) {
    return null
  }

  return isMobile ? <MobileDashboard /> : <FinancialDashboard />
}
