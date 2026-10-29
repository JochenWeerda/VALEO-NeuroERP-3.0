import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import definitionJson from './contract-audit-studio.fixture.json'
import FrmKontraktProtokoll from '@/pages/kontrakte/FrmKontraktProtokoll'

const definition = definitionJson as ScreenDefinition
const fixture = vi.hoisted(() => ({ get: vi.fn(), search: '', params: {} as Record<string, string> }))
vi.mock('@/app/routing/typed-router', () => ({ useParams: () => fixture.params, useSearchParams: () => [new URLSearchParams(fixture.search), vi.fn()], useNavigate: () => vi.fn(), useLocation: () => ({ pathname: '/', search: '', hash: '', state: {}, key: 'test' }), Link: ({ children }: { children: React.ReactNode }) => children }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: definition, isLoading: false }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: fixture.get } }))
vi.mock('@/lib/api/ux-overlays', () => ({ useUserScreenOverlay: () => ({ data: undefined, isLoading: false, refetch: vi.fn() }), overlayKeys: {}, saveUserOverlay: vi.fn(), deleteUserOverlay: vi.fn() }))
vi.mock('@/components/mask-builder/runtime/useFlowSpineCatalogRuntime', () => ({ useFlowSpineCatalogRuntime: () => ({}) }))
const rows = [
  { audit_id: 'a', changed_at: '2025-01-02T10:30:00Z', changed_by: 'Anna', field_name: 'Preis', old_value: null, new_value: '42', action: 'UPDATE' },
  { audit_id: 'b', changed_at: '2025-02-02T10:30:00Z', changed_by: 'Bernd', field_name: 'Preis', old_value: '7', new_value: '8', action: 'UPDATE' },
  { audit_id: 'c', changed_at: '2025-03-02T10:30:00Z', changed_by: 'Anna', field_name: 'Menge', old_value: '2', new_value: '3', action: 'UPDATE' },
]
function show(contractId?: string) { const client = new QueryClient({ defaultOptions: { queries: { retry: false } } }); return render(<QueryClientProvider client={client}><FrmKontraktProtokoll contractId={contractId} /></QueryClientProvider>) }
beforeEach(() => {
  fixture.search = ''; fixture.params = {}
  fixture.get.mockImplementation(async (url: string) => { const page = new URL(url, 'http://local').searchParams.get('page'); return { data: { data: { items: page === '1' ? rows.slice(0, 2) : rows.slice(2), total: rows.length } } } })
})
afterEach(() => { cleanup(); vi.resetAllMocks() })
describe('Kontraktprotokoll: Python definition and real renderer', () => {
  it('shows all six columns, dates and nulls, and combines filters over all fetched pages', async () => {
    show('contract one')
    await screen.findByText('Bernd')
    expect(screen.getByText('Menge')).toBeTruthy()
    for (const label of ['Wann', 'Benutzer', 'Feld', 'Alt', 'Neu', 'Aktion']) expect(screen.getByText(label)).toBeTruthy()
    expect(screen.getByText(new Date(rows[0].changed_at).toLocaleString('de-DE'))).toBeTruthy()
    expect(screen.getAllByText('–').length).toBeGreaterThan(0)
    expect(fixture.get).toHaveBeenCalledTimes(2)
    expect(fixture.get.mock.calls[0][0]).toContain('entity_id=contract+one')
    fireEvent.change(screen.getByLabelText('Filter Feld'), { target: { value: 'PRE' } })
    fireEvent.change(screen.getByLabelText('Filter Benutzer'), { target: { value: 'anna' } })
    expect(screen.getByText('Anna')).toBeTruthy()
    expect(screen.queryByText('Bernd')).toBeNull()
    expect(screen.queryByText('Menge')).toBeNull()
  })
  it('uses standalone query context', async () => { fixture.search = 'contractId=query-contract'; show(); await screen.findByText('Bernd'); expect(fixture.get.mock.calls[0][0]).toContain('entity_id=query-contract') })
  it('blocks a standalone route without context', () => { show(); expect(screen.getByRole('status').textContent).toContain('Vorgang'); expect(fixture.get).not.toHaveBeenCalled() })
})
