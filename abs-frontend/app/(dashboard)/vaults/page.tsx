"use client"

import { useEffect, useState } from "react"
import { useMediaQuery } from "@/hooks/use-mobile"
import Dashboard from "./components/desktop-page"
import MobileDashboard from "./components/mobile-page"

export default function Page() {
  const [isMounted, setIsMounted] = useState(false)
  const isMobile = useMediaQuery("(max-width: 768px)")

  useEffect(() => {
    setIsMounted(true)
  }, [])

  if (!isMounted) {
    return null
  }

  return isMobile ? <MobileDashboard /> : <Dashboard />
}
