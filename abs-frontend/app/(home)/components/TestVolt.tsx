'use client'

import React from 'react'
import { useVoltrClientStore } from "@/components/hooks/useVoltrClientStore";

const TestVolt = () => {
  const client = useVoltrClientStore((state) => state.client);

  return <div>{client ? "Client is ready ✅" : "Loading VoltrClient..."}</div>;

}

export default TestVolt