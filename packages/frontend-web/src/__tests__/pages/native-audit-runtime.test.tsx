import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { NativeAuditListPage } from '@/components/mask-builder/NativeAuditListPage'

const fixture = vi.hoisted(() => ({ get: vi.fn(), rows: [] as Record<string, unknown>[] }))
const definition = {
  id: 'audit/test', schemaVersion: 1, domain: 'test', mode: 'list', title: 'Audit',
  layout: { floorplan: 'worklist', density: 'compact', contextRail: 'none', tableProfile: 'audit' },
  dataSources: [{ key: 'list', endpoint: '/api/v1/contracts/{entity_id}/audit' }], actions: [],
  tables: [{ key: 'list', label: 'Audit', dataSourceKey: 'list', serverPagination: false, pageSize: 50, columns: [
    { key: 'field_name', label: 'Feld', filterable: true }, { key: 'changed_by', label: 'Benutzer', filterable: true },
    { key: 'old_value', label: 'Alt', filterable: false },
  ] }],
}
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: definition, isLoading: false }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: fixture.get } }))
vi.mock('@/lib/api/ux-overlays', () => ({ useUserScreenOverlay: () => ({ data: undefined, isLoading: false, refetch: vi.fn() }), overlayKeys: {}, saveUserOverlay: vi.fn(), deleteUserOverlay: vi.fn() }))
vi.mock('@/components/mask-builder/runtime/useFlowSpineCatalogRuntime', () => ({ useFlowSpineCatalogRuntime: () => ({}) }))
vi.mock('@/components/mask-builder/UniversalMaskRenderer', () => ({ UniversalMaskRenderer: ({ tables, messages }: { tables: Record<string, Record<string, unknown>[]>; messages: { message: string }[] }) => <div>{messages.map(m => <p role="alert" key={m.message}>{m.message}</p>)}{tables.list?.map((row, i) => <p key={i}>{String(row.field_name)}:{String(row.changed_by)}:{String(row.old_value)}</p>)}</div> }))
function show(id?: string) { const client = new QueryClient({ defaultOptions: { queries: { retry: false } } }); return render(<QueryClientProvider client={client}><NativeAuditListPage screenId="audit/test" entityId={id} /></QueryClientProvider>) }
afterEach(() => { cleanup(); vi.resetAllMocks() })
describe('context-bound audit runtime', () => {
  it('blocks missing context without transport', () => { show(); expect(screen.getByRole('status').textContent).toContain('Vorgang'); expect(fixture.get).not.toHaveBeenCalled() })
  it('loads all projected pages and combines the declared filters', async () => {
    fixture.get.mockImplementation(async (url: string) => { const page = new URL(url, 'http://local').searchParams.get('page'); return { data: { data: { items: page === '1' ? [{ field_name: 'Preis', changed_by: 'Anna', old_value: null }] : [{ field_name: 'Menge', changed_by: 'Anna', old_value: '1' }], total: 2 } } } })
    show('C 1')
    await screen.findByText('Preis:Anna:null')
    expect(fixture.get.mock.calls[0][0]).toContain('entity_id=C+1')
    expect(fixture.get).toHaveBeenCalledTimes(2)
    fireEvent.change(screen.getByLabelText('Filter Feld'), { target: { value: 'PRE' } })
    fireEvent.change(screen.getByLabelText('Filter Benutzer'), { target: { value: 'anna' } })
    expect(screen.getByText('Preis:Anna:null')).toBeTruthy()
    expect(screen.queryByText('Menge:Anna:1')).toBeNull()
  })
  it('shows access failures rather than an empty audit', async () => {
    fixture.get.mockRejectedValue(new Error('404'))
    show('other-tenant')
    await waitFor(() => expect(screen.getByRole('alert').textContent).toContain('konnte nicht geladen'))
  })
})
