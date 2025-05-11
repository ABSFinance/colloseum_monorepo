'use client';

import { useMediaQuery } from '@/hooks/use-mobile';
import Dashboard from './components/desktop-page';
import MobileDashboard from './components/mobile-page';

export default function Page() {
  const isMobile = useMediaQuery('(max-width: 768px)');

  return (
    <>
      {isMobile ? <MobileDashboard /> : <Dashboard />}
    </>
  );
}
