
"use client"
import { useEffect, useState } from "react";
import FinancialDashboard from "./components/FinancialDashboard";
import { useMediaQuery } from "@/hooks/use-mobile";
import MobileDashboard from "./components/Mobiledash";
import { supabase } from "@/lib/supabase";
import { useVaultStore } from "@/stores/vaults-store";


export default function Page() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMounted, setIsMounted] = useState(false);
  const isMobile = useMediaQuery('(max-width: 768px)');
  const setVaults = useVaultStore((state) => state.setVaults);

  useEffect(() => {
    const fetchData = async () => {
      const { data, error } = await supabase.from('drift_vault_info').select('*');
      if (error) {
        setError(error.message);
      } else {
        setVaults(data || []);
      }
      setLoading(false);
    };

    fetchData();
  }, [setVaults]);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null;
  if (loading) return <p>Loading...</p>;
  if (error) return <p className="text-red-500">Error: {error}</p>;

  return (
    <>
      {isMobile ? <MobileDashboard /> : <FinancialDashboard />}
    </>
  );
}