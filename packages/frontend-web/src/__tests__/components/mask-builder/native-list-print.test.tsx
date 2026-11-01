import { useEffect } from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, expect, it, vi } from 'vitest'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const state = vi.hoisted(() => ({
  print: vi.fn(), toast: vi.fn(), request: vi.fn(), get: vi.fn(),
  rows: [] as Record<string, unknown>[], permissions: ['list.print'],
  definition: {} as ScreenDefinition,
}))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: state.definition }) }))
vi.mock('@/lib/export-utils', () => ({ exportToCSV: vi.fn(), printTable: state.print }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: state.toast }) }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => state.permissions }))
vi.mock('@/lib/api-client', () => ({ apiClient: { request: state.request, get: state.get }, getAxiosErrorMessage: (e: Error) => e.message }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ onAction, onListData }: {
    onAction: (key: string, payload: object) => void
    onListData?: (rows: Record<string, unknown>[]) => void
  }) => {
    useEffect(() => { onListData?.(state.rows) }, [onListData])
    return <button onClick={() => onAction('print', {})}>Liste drucken</button>
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
  state.print.mockReset()
  state.permissions = ['list.print']
  state.rows = [{ name: 'Gefiltert A', secret: 'intern' }, { name: 'Gefiltert B', secret: 'intern' }]
  state.definition = {
    schemaVersion: 1, id: 'test/print-list', domain: 'sales', mode: 'list', title: 'Angebote',
    actions: [{ key: 'print', label: 'Drucken', localEffect: 'print', permission: 'list.print' }],
    listExperience: { searchFields: ['name'], aggregates: [],
      export: { filenamePrefix: 'offers', delimiter: ';', columns: [{ key: 'name', label: 'Name' }] } },
  } as ScreenDefinition
})
function mount() {
  render(<QueryClientProvider client={new QueryClient()}><NativeListPage screenId="test/print-list" /></QueryClientProvider>)
  fireEvent.click(screen.getByRole('button', { name: 'Liste drucken' }))
}
it('prints the complete filtered result with declared columns without reading or writing data', () => {
  mount()
  expect(state.print).toHaveBeenCalledWith(state.rows, 'Angebote', [{ key: 'name', label: 'Name' }])
  expect(state.get).not.toHaveBeenCalled()
  expect(state.request).not.toHaveBeenCalled()
})
it('refuses empty results', () => {
  state.rows = []
  mount()
  expect(state.print).not.toHaveBeenCalled()
  expect(state.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Keine Daten' }))
})
it('refuses undeclared data without an unfiltered fallback', () => {
  delete state.definition.listExperience
  mount()
  expect(state.print).not.toHaveBeenCalled()
  expect(state.get).not.toHaveBeenCalled()
  expect(state.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Druck nicht verfügbar' }))
})
it('checks the action permission before printing', () => {
  state.permissions = []
  mount()
  expect(state.print).not.toHaveBeenCalled()
})
it('reports print failures without executing a command', () => {
  state.print.mockImplementation(() => { throw new Error('Druckfenster nicht verfügbar') })
  mount()
  expect(state.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Druck fehlgeschlagen', variant: 'destructive' }))
  expect(state.request).not.toHaveBeenCalled()
})
it('preserves the command contract for document print actions', () => {
  state.definition.actions = [{ key: 'print', label: 'Drucken', localEffect: 'print',
    permission: 'list.print', commandEndpoint: '/api/v1/documents/print' }]
  mount()
  expect(state.print).not.toHaveBeenCalled()
  expect(screen.getByRole('dialog')).toBeInTheDocument()
  expect(state.request).not.toHaveBeenCalled()
})
