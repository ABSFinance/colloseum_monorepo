"use client";

import { useEffect } from "react";
import { useVoltrClientStore } from "../hooks/useVoltrClientStore";

export const VoltrClientProvider = ({ children }: { children: React.ReactNode }) => {
  const initialize = useVoltrClientStore((state) => state.initialize);

  useEffect(() => {
    initialize(); 
  }, [initialize]);

  return <>{children}</>;
};