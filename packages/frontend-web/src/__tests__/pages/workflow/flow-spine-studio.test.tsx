import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import FlowSpineStudioPage from '@/pages/workflow/flow-spine-studio'
import i18n, { initI18n } from '@/i18n/config'
import { compileRenderPlan } from '@/components/mask-builder/render-plan/schema-compiler'
import catalogDefinition from '../../fixtures/flow-spine-catalog-studio.json'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
const transport = vi.hoisted(() => ({ get: vi.fn(), navigate: vi.fn() }))
vi.mock('@/app/routing/typed-router', async () => ({ ...await vi.importActual('@/app/routing/typed-router'), useNavigate: () => transport.navigate }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: transport.get } }))
const definition: ScreenDefinition = { ...catalogDefinition, flowSpineCatalog: { enabled: true, warmWorkspaces: false } }

const process = { key: 'order-to-cash', label: 'Auftrag bis Zahlung', route_path: '/workflow/flow-spine-order-to-cash', summary: 'Vertrieb und Zahlung.', domain: 'sales' }
let response: unknown
let unavailable = false
beforeAll(async () => { await initI18n(); i18n.addResourceBundle('en', 'translation', { catalog: 'Catalog' }) })
beforeEach(() => {
 vi.clearAllMocks(); response = { processes: [process] }; unavailable = false
 Object.defineProperty(i18n, 'resolvedLanguage', { value: 'de', configurable: true })
 transport.get.mockImplementation(async (url: string) => {
  if (url.includes('/screen-definition')) return { data: definition }
  if (url.includes('/ux/overlays/')) return { data: { overlay: {} } }
  if (url.includes('/catalog?')) { if (unavailable) throw new Error('synthetic failure'); return { data: response } }
  throw new Error('Unexpected HTTP read: ' + url)
 })
})
function mount() { return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><MemoryRouter><FlowSpineStudioPage /></MemoryRouter></QueryClientProvider>) }
describe('Studio process catalog with real compiler and runtime', () => {
 it('loads localized catalog fields and navigates', async () => {
  mount(); const button = await screen.findByRole('button', { name: /Auftrag bis Zahlung/ })
  expect(screen.getByRole('heading', { name: 'Flow Spine Studio', level: 1 })).toBeInTheDocument()
  expect(screen.getByText('sales')).toBeInTheDocument(); expect(screen.getByText('Vertrieb und Zahlung.')).toBeInTheDocument()
  expect(screen.getByText(/1 Prozesse verfügbar/)).toBeInTheDocument()
  expect(transport.get).toHaveBeenCalledWith('/api/v1/process/flow-spines/catalog?lang=de')
  fireEvent.click(button); expect(transport.navigate).toHaveBeenCalledWith(process.route_path)
 })
 it('shows genuine empty data', async () => { response = { processes: [] }; mount(); expect(await screen.findByText('Keine Prozesse verfügbar.')).toBeInTheDocument() })
 it('reports errors and retries', async () => {
  unavailable = true; mount(); expect(await screen.findByText('Prozesskatalog nicht verfügbar.')).toBeInTheDocument()
  unavailable = false; fireEvent.click(screen.getByRole('button', { name: 'Erneut versuchen' })); expect(await screen.findByText(process.label)).toBeInTheDocument()
 })
 it('rejects arbitrary URLs from catalog data', async () => {
  response = { processes: [{ ...process, route_path: 'https://invalid.example' }] }; mount()
  expect(await screen.findByRole('button', { name: /Auftrag bis Zahlung/ })).toBeDisabled(); expect(transport.navigate).not.toHaveBeenCalled()
 })
 it('separates language changes in cache', async () => {
  mount(); await screen.findByText(process.label)
  await act(async () => { await i18n.changeLanguage('en') })
  await waitFor(() => expect(transport.get).toHaveBeenCalledWith('/api/v1/process/flow-spines/catalog?lang=en'))
 })
 it('validates metadata before caching', () => {
  const context = { screenId: definition.id, schemaVersion: 1, auth: { permissions: [] } }
  const first = compileRenderPlan(definition, context)
  const second = compileRenderPlan({ ...definition, flowSpineCatalog: { enabled: true, warmWorkspaces: true } }, context)
  expect(first.flowSpineCatalog?.warmWorkspaces).toBe(false); expect(second.flowSpineCatalog?.warmWorkspaces).toBe(true)
  expect(() => compileRenderPlan({ ...definition, flowSpineCatalog: { enabled: true, warmWorkspaces: true, endpoint: 'bad' } } as unknown as ScreenDefinition, context)).toThrow('Invalid process catalog contract')
 })
})
