import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, expect, it, vi } from 'vitest'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

const mocks = vi.hoisted(() => ({ get: vi.fn(), execute: vi.fn(), refetch: vi.fn() }))
const action = { key: 'bearbeiten', label: 'Beleg bearbeiten', permission: 'belege.bearbeiten',
  enabledWhen: 'aktion_bearbeiten', method: 'PUT', commandEndpoint: '/api/v1/docflow/{entity_id}',
  commandBinding: { adapter: 'docflow.v1', command: 'update', preview: false },
  inputFields: [{ key: 'source_ref', label: 'Referenz', type: 'text' },
    { key: 'items', label: 'Positionen', type: 'table', rowFields: [
      { key: 'article_number', label: 'Artikel', type: 'text', required: true },
      { key: 'quantity', label: 'Menge', type: 'number', required: true },
    ], tableEditing: { allowAdd: true, allowDelete: true } }] }
const schema = { id: 'beleg/sales-offer', title: 'Angebot', adapter: { temporary: false }, actions: [action] }
const document = { id: 'doc-1', doc_type: 'sales_offer', version: 4, status: 'draft', currency: 'EUR',
  document_date: '2026-10-17', source_ref: 'old reference', items: [
    { article_number: 'SYNTHETIC', quantity: 12.5, unit: 't', unit_price: 220, charge: 'SYNTH-CHARGE', batch_id: 'SYNTH-BATCH' }] }
vi.mock('@tanstack/react-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/features/mask-pilot/use-mask-pilot-state', () => ({ useMaskPilotState: () => ({ onTabChange: vi.fn() }) }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: schema }) }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => ['belege.bearbeiten', 'belege.preise'] }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: mocks.get, post: vi.fn().mockResolvedValue({}) },
  getAxiosErrorMessage: (error: unknown) => error instanceof Error ? error.message : String(error) }))
vi.mock('@/components/mask-builder', () => ({
  useUniversalMaskRuntime: () => ({ plan: {}, entityData: { belegart: 'sales_offer', version: 4, aktion_bearbeiten: true },
    tableRows: {}, tableQueryStates: {}, tableTotals: {}, messages: [], lookupBindings: {},
    setTableQuery: vi.fn(), updateUserOverlay: vi.fn(), resetUserOverlay: vi.fn(), refetch: mocks.refetch }),
  useHumanActionDispatch: () => ({ executeAction: mocks.execute }),
  UniversalMaskRenderer: ({ onAction }: { onAction: (key: string, payload: object) => void }) =>
    <button onClick={() => onAction('bearbeiten', { items: [{ article_number: 'PAGED-INCOMPLETE' }] })}>Beleg bearbeiten</button>,
}))
const client = () => new QueryClient({ defaultOptions: { queries: { retry: false } } })
function view(entityId = 'doc-1') {
  return <QueryClientProvider client={client()}><UniversalNativeDetailPage screenId="beleg/sales-offer" entityId={entityId} /></QueryClientProvider>
}
beforeEach(() => {
  vi.clearAllMocks()
  mocks.get.mockResolvedValue({ data: document })
  mocks.execute.mockResolvedValue({ success: true })
})
it('preloads the complete canonical document and submits edited rows with hidden metadata and explicit cleared reference', async () => {
  render(view())
  fireEvent.click(screen.getByRole('button', { name: 'Beleg bearbeiten' }))
  await screen.findByRole('dialog')
  expect(mocks.get).toHaveBeenCalledWith('/api/v1/docflow/doc-1')
  expect(screen.getByLabelText('Artikel, Zeile 1')).toHaveValue('SYNTHETIC')
  fireEvent.change(screen.getByLabelText('Menge, Zeile 1'), { target: { value: '15' } })
  fireEvent.change(screen.getByLabelText('Referenz'), { target: { value: '' } })
  fireEvent.click(screen.getByRole('button', { name: 'Entwurf speichern' }))
  await waitFor(() => expect(mocks.execute).toHaveBeenCalledTimes(1))
  expect(mocks.execute.mock.calls[0][0]).toMatchObject({ expectedVersion: 4, mode: 'execute',
    payload: { source_ref: '', items: [{ quantity: 15, unit_price: 220, charge: 'SYNTH-CHARGE', batch_id: 'SYNTH-BATCH' }] } })
})
it('does not open an old document after navigation and ignores a duplicate preload click', async () => {
  let resolve!: (value: unknown) => void
  mocks.get.mockReturnValue(new Promise(done => { resolve = done }))
  const page = render(view())
  const button = screen.getByRole('button', { name: 'Beleg bearbeiten' })
  fireEvent.click(button)
  fireEvent.click(button)
  expect(mocks.get).toHaveBeenCalledTimes(1)
  page.rerender(view('doc-2'))
  await act(async () => { resolve({ data: document }) })
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  expect(mocks.execute).not.toHaveBeenCalled()
})

it('keeps edited rows after a failed save and repeats the same version and payload', async () => {
  mocks.execute.mockResolvedValueOnce({ success: false, error: 'Transport unklar' }).mockResolvedValueOnce({ success: true })
  render(view())
  fireEvent.click(screen.getByRole('button', { name: 'Beleg bearbeiten' }))
  await screen.findByRole('dialog')
  fireEvent.change(screen.getByLabelText('Menge, Zeile 1'), { target: { value: '17' } })
  fireEvent.click(screen.getByRole('button', { name: 'Entwurf speichern' }))
  await screen.findByRole('dialog')
  expect(screen.getByLabelText('Menge, Zeile 1')).toHaveValue(17)
  expect(screen.getAllByText('Transport unklar').length).toBeGreaterThan(0)
  fireEvent.click(screen.getByRole('button', { name: 'Entwurf speichern' }))
  await waitFor(() => expect(mocks.execute).toHaveBeenCalledTimes(2))
  expect(mocks.execute.mock.calls[1][0]).toEqual(mocks.execute.mock.calls[0][0])
})
