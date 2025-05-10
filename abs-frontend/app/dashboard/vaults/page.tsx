'use client';

import { useEffect, useState } from 'react';
import { useMediaQuery } from '@/hooks/use-mobile';
import Dashboard from './components/desktop-page';
import MobileDashboard from './components/mobile-page';
import { supabase } from '@/lib/supabase';
import { VaultInfo } from '@/lib/types';

export default function Page() {
  const [data, setData] = useState<VaultInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMounted, setIsMounted] = useState(false);
  const isMobile = useMediaQuery('(max-width: 768px)');

  useEffect(() => {
    const fetchData = async () => {
      const { data, error } = await supabase.from('drift_vault_info').select('*');
      if (error) {
        setError(error.message);
      } else {
        setData(data || []);
      }
      setLoading(false);
    };

    fetchData();
  }, []);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null;
  if (loading) return <p>Loading...</p>;
  if (error) return <p className="text-red-500">Error: {error}</p>;

  console.log(data);

  return (
    <>
      {isMobile ? <MobileDashboard /> : <Dashboard />}
    </>
  );
}
