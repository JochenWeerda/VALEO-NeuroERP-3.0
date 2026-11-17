/** Isolated rendering of the real start page with synthetic, read-only data. */
import React from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createMemoryHistory, createRootRoute, createRoute, createRouter, Outlet, RouterProvider } from '@tanstack/react-router'
import StartDashboardPage from '../../src/pages/start-dashboard'
import { apiClient } from '../../src/lib/api-client'
import { auth } from '../../src/lib/auth'
import '../../src/i18n/config'
import '../../src/index.css'

// A fresh document has no credentials. Override auth accessors explicitly, including refresh.
for (const [method, value] of Object.entries({
  getUser: () => null, getAccessToken: () => null, isAuthenticated: () => false,
  canRefresh: () => false, hasScope: () => false, hasRole: () => false,
  getFreshAccessToken: async () => null,
  login: () => { throw new Error('Synthetic visual fixture cannot authenticate') },
  logout: () => { throw new Error('Synthetic visual fixture cannot authenticate') },
  handleCallback: () => { throw new Error('Synthetic visual fixture cannot authenticate') },
})) Object.defineProperty(auth, method, { value })

Object.defineProperty(apiClient, 'get', { value: async (url: string) => {
  if (url === '/api/v1/kontrakte') return { data: { items: [], total: 0, skip: 0, limit: 20 } }
  if (url === '/api/v1/agrar/contracts') return { data: { items: [], total: 0 } }
  if (url === '/api/mcp/documents/inbox/queue') return { data: { ok: true, available: true, booking_allowed: false, count: 0, items: [], gaps: [] } }
  if (url === '/api/v1/workflows/approvals?assignee=me&status=pending') return { data: { items: [], total: 0 } }
  if (url === '/api/v1/workspace/agrar-chain') return { data: { items: [], total: 0 } }
  throw new Error(`Unexpected synthetic read: ${url}`)
} })
for (const method of ['post', 'put', 'patch', 'delete']) {
  Object.defineProperty(apiClient, method, { value: () => { throw new Error('Synthetic visual fixture cannot write') } })
}
class SilentEventSource {
  constructor(_url: string) {}
  addEventListener(): void {}
  removeEventListener(): void {}
  close(): void {}
}
window.EventSource = SilentEventSource as unknown as typeof EventSource

const client = new QueryClient({ defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } } })
const rootRoute = createRootRoute({ component: Outlet })
const route = createRoute({ getParentRoute: () => rootRoute, path: '/', component: () => (
  <main className="min-h-screen bg-background p-4 text-foreground"><StartDashboardPage /></main>
) })
const router = createRouter({ routeTree: rootRoute.addChildren([route]), history: createMemoryHistory({ initialEntries: ['/'] }) })
const container = document.getElementById('root')
if (!container) throw new Error('Harness braucht #root')
createRoot(container).render(<QueryClientProvider client={client}><RouterProvider router={router} /></QueryClientProvider>)
