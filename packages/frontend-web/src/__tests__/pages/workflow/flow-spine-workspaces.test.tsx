import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest'
import { initI18n } from '@/i18n/config'
import { MemoryRouter } from '@/app/routing/test-router'
import Order from '@/pages/workflow/flow-spine-order-to-cash'
import Procure from '@/pages/workflow/flow-spine-procure-to-pay'
import Inventory from '@/pages/workflow/flow-spine-inventory-to-settlement'
import Harvest from '@/pages/workflow/flow-spine-harvest-to-settlement'
import Contract from '@/pages/workflow/flow-spine-contract-to-settlement'
import Complaint from '@/pages/workflow/flow-spine-complaint-to-resolution'
import Service from '@/pages/workflow/flow-spine-service-to-customer'
import Finance from '@/pages/workflow/flow-spine-finance-to-close'
import Compliance from '@/pages/workflow/flow-spine-compliance-to-report'
import definitions from '../../fixtures/flow-spine-workspaces-studio.json'

const transport = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), navigate: vi.fn(), toast: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: transport.get, post: transport.post } }))
vi.mock('@/hooks/use-toast', () => ({ toast: transport.toast }))
vi.mock('@/app/routing/typed-router', async () => ({ ...await vi.importActual('@/app/routing/typed-router'), useNavigate: () => transport.navigate }))

const cases = [
  ['order-to-cash', Order, 'Auftragsprozess', 'Lieferung', 'In Zustellung', 'Supply Chain Alert'],
  ['procure-to-pay', Procure, 'Beschaffungsprozess', 'Bestellung', 'PO-2026-188', 'ETA bedroht Skonto-Fenster'],
  ['inventory-to-settlement', Inventory, 'Inventory-to-Settlement', 'Kommissionierung', '85% erledigt', 'Welle 2 benoetigt Eingriff'],
  ['harvest-to-settlement', Harvest, 'Harvest-to-Settlement', 'Trocknung', 'Kapazitaet', 'Trocknungskapazitaet an Grenze'],
  ['contract-to-settlement', Contract, 'Contract-to-Settlement', 'Annahme', 'ANH-551', 'Annahme sauber verknuepft'],
  ['complaint-to-resolution', Complaint, 'Complaint-to-Resolution', 'Reklamation', 'Prioritaet hoch', 'Kulanzpfad empfohlen'],
  ['service-to-customer', Service, 'Service-to-Customer', 'Einsatz', 'Vor Ort', 'Kunde informiert'],
  ['finance-to-close', Finance, 'Finance-to-Close', 'Abstimmung', '3 Konten offen', 'Abstimmungsabweichung erkannt'],
  ['compliance-to-report', Compliance, 'Compliance-to-Report', 'Aggregation', 'In Arbeit', 'Aggregation laeuft'],
] as const

function payload(key: string, title: string, node: string, metric: string, insight: string, apiPath = '/api/v1/action') {
  return {
    process_key: key, title, subtitle: 'Prozess', instance_label: 'Vorgang', breadcrumb: [], mode: 'Flow', user_role: 'Fachrolle',
    left_navigation: { processes: [{ key, label: title, route_path: `/workflow/flow-spine-${key}`, active: true }], favorites: [], recent_items: [], role_switches: [] },
    badges: [], focus_node_id: 'step',
    nodes: [{ id: 'step', label: node, status: 'active', icon: 'Package', metric, submetric: 'Heute', timestamp: '2026-03-24T10:00:00Z', insight,
      detail_rows: [{ label: 'Vorgangsstand', value: metric }], kpis: [], documents: [],
      actions: [{ label: 'Aktion ausfuehren', href: '/sales/delivery', variant: 'primary', api_path: apiPath }],
      agent: { headline: insight, message: 'Hinweis', reasons: [], actions: [] } }],
    right_panel: { resources: [], linked_modules: [], domain: 'workflow' }, footer_cards: [],
  }
}

function mount(testCase: typeof cases[number], apiPath = '/api/v1/action') {
  const [key, Page, title, node, metric, insight] = testCase
  const definition = definitions[key]
  transport.get.mockImplementation(async (url: string) => {
    if (url.includes('/screen-definition')) return { data: definition }
    if (url.includes('/ux/overlays/')) return { data: { overlay: {} } }
    if (url.includes('/instances')) return { data: { instances: [], total: 0 } }
    if (url.includes(`/flow-spines/${key}?`)) return { data: payload(key, title, node, metric, insight, apiPath) }
    throw new Error(`Unexpected GET ${url}`)
  })
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  render(<QueryClientProvider client={client}><MemoryRouter><Page /></MemoryRouter></QueryClientProvider>)
}

beforeAll(async () => {
  await initI18n()
  vi.stubGlobal('EventSource', class { addEventListener() {} removeEventListener() {} close() {} })
})
beforeEach(() => { vi.clearAllMocks() })

describe('Studio Flow-Spine Prozessraeume', () => {
  it.each(cases)('%s laedt seinen Prozess und zeigt Schritt, Status und Hinweis', async (key, Page, title, node, metric, insight) => {
    mount([key, Page, title, node, metric, insight] as typeof cases[number])
    expect(await screen.findByRole('heading', { name: title, level: 1 }, { timeout: 10000 })).toBeInTheDocument()
    expect(transport.get).toHaveBeenCalledWith(`/api/v1/process/flow-spines/${key}?lang=de`)
    expect(screen.getAllByText(node).length).toBeGreaterThan(0)
    expect(screen.getAllByText(metric).length).toBeGreaterThan(0)
    expect(screen.getAllByText(insight).length).toBeGreaterThan(0)
    expect(screen.getAllByText('ACTIVE').length).toBeGreaterThan(0)
  })

  it.each([403, 409])('bleibt bei HTTP %s im Prozess und meldet keinen Erfolg', async (status) => {
    transport.post.mockRejectedValueOnce(Object.assign(new Error(`HTTP ${status}`), { response: { status } }))
    mount(cases[0])
    await userEvent.click(await screen.findByRole('button', { name: 'Aktion ausfuehren' }))
    await waitFor(() => expect(transport.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Fehler', variant: 'destructive' })))
    expect(transport.post).toHaveBeenCalledWith('/api/v1/action', {})
    expect(transport.navigate).not.toHaveBeenCalledWith('/sales/delivery')
    expect(transport.toast).not.toHaveBeenCalledWith(expect.objectContaining({ title: 'Aktion ausgeführt' }))
  })

  it('navigiert nach erfolgreicher Aktion', async () => {
    transport.post.mockResolvedValueOnce({ data: {} })
    mount(cases[0])
    await userEvent.click(await screen.findByRole('button', { name: 'Aktion ausfuehren' }))
    await waitFor(() => expect(transport.navigate).toHaveBeenCalledWith('/sales/delivery'))
    expect(transport.post).toHaveBeenCalledWith('/api/v1/action', {})
  })

  it('navigiert bei reinem Link ohne Schreibaufruf', async () => {
    mount(cases[0], '')
    await userEvent.click(await screen.findByRole('button', { name: 'Aktion ausfuehren' }))
    expect(transport.navigate).toHaveBeenCalledWith('/sales/delivery')
    expect(transport.post).not.toHaveBeenCalled()
  })
})
