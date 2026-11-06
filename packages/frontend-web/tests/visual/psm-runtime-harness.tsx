/** Isolated visual fixture: the production page and canonical definition, no real session or API. */
import React from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createMemoryHistory, createRootRoute, createRoute, createRouter, Outlet, RouterProvider } from '@tanstack/react-router'
import { NativeListPage } from '../../src/components/mask-builder/NativeListPage'
import type { ScreenDefinition } from '../../src/components/mask-builder/schema'
import { apiClient } from '../../src/lib/api-client'
import '../../src/index.css'

declare global {
  interface Window { __PSM_VISUAL_SCHEMA__: ScreenDefinition }
}

const schema = window.__PSM_VISUAL_SCHEMA__
if (schema.id !== 'compliance/zulassungen-liste' || schema.adapter?.type !== 'native') {
  throw new Error('Canonical native PSM definition required')
}

const rows = [
  { id: 'visual-1', artikelnummer: 'PSM-VIS-001', name: 'Synthetisches Mittel mit längerer Bezeichnung für die Zulassungsübersicht', wirkstoff: 'Prüfstoff A', mittel_typ: 'Testmittel', bvl_nummer: 'VIS-001', zulassung_ablauf: '2099-12-31T00:00:00+01:00', ist_aktiv: true },
  { id: 'visual-2', artikelnummer: 'PSM-VIS-002', name: 'Synthetisches inaktives Mittel', wirkstoff: 'Prüfstoff B', mittel_typ: 'Testmittel', bvl_nummer: 'VIS-002', zulassung_ablauf: '2020-01-01T00:00:00+01:00', ist_aktiv: false },
  { id: 'visual-3', artikelnummer: 'PSM-VIS-003', name: 'Synthetisches Mittel mit unbekanntem Aktivwert', wirkstoff: 'Prüfstoff C', mittel_typ: 'Testmittel', bvl_nummer: 'VIS-003', zulassung_ablauf: '2099-01-01T00:00:00+01:00', ist_aktiv: null },
]

// Only this test document replaces the HTTP adapter. No credentials or business API are used.
Object.defineProperty(apiClient, 'get', { value: async (url: string) => {
  if (url.includes('/screen-definition')) return { data: schema }
  if (url.includes('/ux/overlays/')) return { data: { screen_id: schema.id, schema_version: schema.schemaVersion, overlay: {} } }
  if (url.includes('/masks/') && url.includes('/data/')) {
    return { data: { data: { items: rows, total: rows.length } } }
  }
  throw new Error(`Unexpected visual-fixture read: ${url}`)
} })
for (const method of ['post', 'put', 'patch', 'delete']) {
  Object.defineProperty(apiClient, method, { value: () => { throw new Error('Visual fixture never writes') } })
}

const client = new QueryClient({ defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } } })
const rootRoute = createRootRoute({ component: Outlet })
const route = createRoute({ getParentRoute: () => rootRoute, path: '/', component: () => (
  <main className="min-h-screen bg-background text-foreground">
    <p className="border-b px-4 py-2 text-sm">Synthetische Komponentenprüfung · keine Anmeldung oder Buchung</p>
    <NativeListPage screenId={schema.id} testId="visual-psm" />
  </main>
) })
const router = createRouter({ routeTree: rootRoute.addChildren([route]), history: createMemoryHistory({ initialEntries: ['/'] }) })
createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={client}><RouterProvider router={router} /></QueryClientProvider>,
)
