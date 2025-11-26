import { type ReactElement, useCallback } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import { useSSE } from '@/hooks/useSSE'
import { routeMCPEvent } from '@/lib/event-router'
import type { MCPEvent } from '@/lib/mcp-events'

import { Toaster } from './components/ui/toaster'
import ContractsPageV2 from './pages/contracts-v2'
import Dashboard from './features/dashboard/Dashboard'
import Inventory from './features/inventory/Inventory'
import Sales from './features/sales/Sales'
import Weighing from './features/weighing/Weighing'
import LiveMonitorPage from './pages/system/live-monitor'
import PSMAbgabedokumentationPage from './pages/agrar/psm/abgabedokumentation'
import { createQueryClient } from './lib/query'
import './App.css'

const queryClient = createQueryClient()

function AppContent(): ReactElement {
  return (
    <AppShell>
      <Routes>
        <Route element={<Dashboard />} path="/" />
        <Route element={<ContractsPageV2 />} path="/contracts" />
        <Route element={<Inventory />} path="/inventory" />
        <Route element={<Weighing />} path="/weighing" />
        <Route element={<Sales />} path="/sales" />
        <Route element={<LiveMonitorPage />} path="/system/live-monitor" />
        <Route element={<PSMAbgabedokumentationPage />} path="/agrar/psm/abgabedokumentation/:psmId" />
      </Routes>
    </AppShell>
  )
}

function App(): ReactElement {
  const handleEvent = useCallback((event: MCPEvent): void => {
    routeMCPEvent(event)
  }, [])
  useSSE(handleEvent)

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
