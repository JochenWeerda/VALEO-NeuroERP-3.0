import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, expect, it, vi } from 'vitest'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const { request, get, navigate, csv, toast } = vi.hoisted(() => ({
  request: vi.fn(), get: vi.fn(), navigate: vi.fn(), csv: vi.fn(), toast: vi.fn(),
}))
const definition: ScreenDefinition = {
  schemaVersion: 1, id: 'einkauf/anfragen', domain: 'einkauf', mode: 'list', title: 'Anfragen',
  dataSources: [{ key: 'list', endpoint: '/api/v1/einkauf/anfragen' }],
  actions: [
    { key: 'neu', label: 'Neue Anfrage', navigationRoute: '/einkauf/anfrage-erfassung', localEffect: 'navigation' },
    { key: 'export', label: 'CSV-Export', localEffect: 'download' },
  ],
  tables: [{ key: 'list', label: 'Anfragen', dataSourceKey: 'list',
    columns: [{ key: 'anfrageNummer', label: 'Anfrage-Nr.' }, { key: 'status', label: 'Status' }],
    rowActions: [{ key: 'loeschen', label: 'Loeschen', dangerLevel: 'high', permission: 'einkauf.anfrage.loeschen',
      commandEndpoint: '/api/v1/einkauf/anfragen/{entity_id}/actions/loeschen', method: 'POST',
      requiresConfirmation: true, auditReasonRequired: true }] }],
} as ScreenDefinition

vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: definition }) }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => [] }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => navigate }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast }) }))
vi.mock('@/lib/export-utils', () => ({ exportToCSV: csv }))
vi.mock('@/lib/api-client', () => ({ apiClient: { request, get }, getAxiosErrorMessage: (e: Error) => e.message }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ onAction }: { onAction: (key: string, payload: object) => void }) => (
    <div>
      <button onClick={() => onAction('neu', {})}>Neu</button>
      <button onClick={() => onAction('export', {})}>Export</button>
      <button onClick={() => onAction('loeschen', { id: 'A-1' })}>Zeile loeschen</button>
    </div>
  ),
}))

beforeEach(() => { vi.clearAllMocks() })
function mount() {
  render(<QueryClientProvider client={new QueryClient()}><NativeListPage screenId="einkauf/anfragen" /></QueryClientProvider>)
}

it('navigiert ueber die deklarierte Route und exportiert mit den Spalten der Definition', async () => {
  get.mockResolvedValue({ data: [{ anfrageNummer: 'A-1', status: 'OFFEN' }] })
  mount()
  fireEvent.click(screen.getByRole('button', { name: 'Neu' }))
  expect(navigate).toHaveBeenCalledWith('/einkauf/anfrage-erfassung')
  fireEvent.click(screen.getByRole('button', { name: 'Export' }))
  await waitFor(() => expect(csv).toHaveBeenCalledTimes(1))
  expect(get).toHaveBeenCalledWith('/api/v1/einkauf/anfragen')
  expect(csv.mock.calls[0][2]).toEqual([{ key: 'anfrageNummer', label: 'Anfrage-Nr.' }, { key: 'status', label: 'Status' }])
})

it('ruft den Kommandoweg erst mit Begruendung und meldet eine Ablehnung', async () => {
  request.mockResolvedValue({ data: { success: false, error: 'Aktion im Status FREIGEGEBEN nicht moeglich.' } })
  mount()
  fireEvent.click(screen.getByRole('button', { name: 'Zeile loeschen' }))
  const knopf = await screen.findByRole('button', { name: 'Loeschen' })
  expect(knopf).toBeDisabled()
  fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Doppelt erfasst' } })
  fireEvent.click(knopf)
  await waitFor(() => expect(request).toHaveBeenCalledTimes(1))
  expect(request.mock.calls[0][0]).toMatchObject({ url: '/api/v1/einkauf/anfragen/A-1/actions/loeschen',
    data: { _auditReason: 'Doppelt erfasst' } })
  await waitFor(() => expect(toast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' })))
})

it('blendet Zeilenaktionen ohne Recht im Plan aus', () => {
  const ohne = compileRenderPlanFromScreenDefinition(definition, { permissions: [] })
  const mit = compileRenderPlanFromScreenDefinition(definition, { permissions: ['einkauf.anfrage.loeschen'] })
  expect(ohne.tablesByKey.list.rowActions).toEqual([])
  expect(mit.tablesByKey.list.rowActions?.map(a => a.key)).toEqual(['loeschen'])
})

it('wertet die 2xx-Antwort eines Fachwegs ohne Umschlag als Erfolg', async () => {
  request.mockResolvedValue({ data: { id: 'A-1', status: 'ENTWURF' } })
  mount()
  fireEvent.click(screen.getByRole('button', { name: 'Zeile loeschen' }))
  fireEvent.change(await screen.findByRole('textbox'), { target: { value: 'Doppelt erfasst' } })
  fireEvent.click(screen.getByRole('button', { name: 'Loeschen' }))
  await waitFor(() => expect(toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Loeschen' })))
  expect(toast).not.toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' }))
})
