/** Actual portal inspection shell with synthetic read-only content; no native business mask or real authentication. */
import React from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createMemoryHistory, createRootRoute, createRoute, createRouter, Outlet, RouterProvider } from '@tanstack/react-router'
import CustomerPortalLayout from '../../src/layouts/CustomerPortalLayout'
import { beginPortalInspection, usePortalKonto } from '../../src/lib/portal-konto'
import { apiClient } from '../../src/lib/api-client'
import { auth } from '../../src/lib/auth'
import '../../src/i18n/config'
import '../../src/index.css'

const syntheticToken = `e30.${btoa(JSON.stringify({ sub: 'synthetic-reviewer', tenant_id: 'synthetic-tenant', exp: 9999999999 }))}.synthetic`
// A fresh document has no credentials. Override auth accessors explicitly, including refresh.
for (const [method, value] of Object.entries({
  getUser: () => ({ sub: 'synthetic-reviewer', name: 'Test', email: '', roles: ['admin'], scopes: [], exp: 9999999999 }), getAccessToken: () => syntheticToken, isAuthenticated: () => true,
  canRefresh: () => false, hasScope: () => false, hasRole: (role: string) => role === 'admin',
  getFreshAccessToken: async () => syntheticToken,
  login: () => { throw new Error('Synthetic visual fixture cannot authenticate') },
  logout: () => { throw new Error('Synthetic visual fixture cannot authenticate') },
  handleCallback: () => { throw new Error('Synthetic visual fixture cannot authenticate') },
})) Object.defineProperty(auth, method, { value })

Object.defineProperty(apiClient, 'get', { value: async (url: string) => {
  if (url === '/api/v1/portal/kundenkonten') return { data: [] }
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

beginPortalInspection()
usePortalKonto.getState().waehle({ customer_id: 'synthetic-customer', customer_number: 'TEST', name: 'Synthetischer Testbetrieb', rolle: 'intern', rechte: [] })

const client = new QueryClient({ defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } } })
const rootRoute = createRootRoute({ component: Outlet })
const route = createRoute({ getParentRoute: () => rootRoute, path: '/portal', component: CustomerPortalLayout })
const content = createRoute({ getParentRoute: () => route, path: '/', component: () => (
  <section className="rounded-lg border border-border bg-card p-4 text-foreground"><h1>Portal-Prüfansicht</h1><p>Synthetischer Inhalt zur Prüfung des Portalrahmens. Keine fachliche Buchung.</p></section>
) })
const router = createRouter({ routeTree: rootRoute.addChildren([route.addChildren([content])]), history: createMemoryHistory({ initialEntries: ['/portal?preview=customer'] }) })
const container = document.getElementById('root')
if (!container) throw new Error('Harness braucht #root')
createRoot(container).render(<QueryClientProvider client={client}><RouterProvider router={router} /></QueryClientProvider>)
