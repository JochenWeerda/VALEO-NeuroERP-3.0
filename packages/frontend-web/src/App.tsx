import { type ReactElement, useCallback } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import { useSSE } from '@/hooks/useSSE'
import { routeMCPEvent } from '@/lib/event-router'
import type { MCPEvent } from '@/lib/mcp-events'

import { Toaster } from './components/ui/toaster'
import Contracts from './features/contracts/Contracts'
import Dashboard from './features/dashboard/Dashboard'
import Inventory from './features/inventory/Inventory'
import Sales from './features/sales/Sales'
import Weighing from './features/weighing/Weighing'
import LiveMonitorPage from './pages/system/live-monitor'
import { createQueryClient } from './lib/query'
import './App.css'

const queryClient = createQueryClient()

function AppContent(): ReactElement {
  return (
    <AppShell>
      <Routes>
        <Route element={<Dashboard />} path="/" />
        <Route element={<Contracts />} path="/contracts" />
        <Route element={<Inventory />} path="/inventory" />
        <Route element={<Weighing />} path="/weighing" />
        <Route element={<Sales />} path="/sales" />
        <Route element={<LiveMonitorPage />} path="/system/live-monitor" />
      </Routes>
    </AppShell>
  )
}

function App(): ReactElement {
  const handleEvent = useCallback((event: MCPEvent): void => {
    routeMCPEvent(event);
  }, []);
  const sseUrl = (import.meta.env?.VITE_MCP_EVENTS_URL as string | undefined) ?? undefined;
  useSSE(handleEvent, sseUrl);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppContent />
        <Toaster />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
