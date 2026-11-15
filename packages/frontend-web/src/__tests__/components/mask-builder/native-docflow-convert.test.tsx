import conversionAction from '../../fixtures/docflow-sales-order-conversion.json'
import type { ScreenActionDefinition } from '@/components/mask-builder/schema'
import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, expect, it, vi } from 'vitest'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

const mocks = vi.hoisted(() => ({ get: vi.fn(), execute: vi.fn(), refetch: vi.fn() }))
const action = conversionAction as ScreenActionDefinition
const schema = { id: 'beleg/sales-order', title: 'Auftrag', adapter: { temporary: false }, actions: [action],
  documentVariant: { variantId: 'sales_order' } }
const options = { source_doc_id: 'doc-1', source_doc_type: 'sales_order', target_doc_type: 'sales_delivery', version: 4,
  items: [
    { source_item_id: 'item-1', line_number: 1, article_number: 'W-1', description: 'Weizen', unit: 't', remaining_quantity: 6 },
    { source_item_id: 'item-2', line_number: 2, article_number: 'R-2', description: 'Raps', unit: 'kg', remaining_quantity: 2 },
  ] }
vi.mock('@tanstack/react-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/features/mask-pilot/use-mask-pilot-state', () => ({ useMaskPilotState: () => ({ onTabChange: vi.fn() }) }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: schema }) }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => ['belege.bearbeiten'] }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: mocks.get, post: vi.fn().mockResolvedValue({}) },
  getAxiosErrorMessage: (error: unknown) => error instanceof Error ? error.message : String(error) }))
vi.mock('@/components/mask-builder', () => ({
  useUniversalMaskRuntime: () => ({ plan: {}, entityData: { belegart: 'sales_order', version: 4, aktion_umwandeln_sales_delivery: true },
    tableRows: {}, tableQueryStates: {}, tableTotals: {}, messages: [], lookupBindings: {},
    setTableQuery: vi.fn(), updateUserOverlay: vi.fn(), resetUserOverlay: vi.fn(), refetch: mocks.refetch }),
  useHumanActionDispatch: () => ({ executeAction: mocks.execute }),
  UniversalMaskRenderer: ({ onAction, messages }: { onAction: (key: string, payload: object) => void; messages: Array<{ key: string; message: string }> }) =>
    <><button onClick={() => onAction(action.key, { quantities_by_source_item_id: [{ source_item_id: 'paged-only' }] })}>Lieferschein erstellen</button>{messages.map(message => <p key={message.key}>{message.message}</p>)}</>,
}))
const client = () => new QueryClient({ defaultOptions: { queries: { retry: false } } })
function view(entityId = 'doc-1') {
  return <QueryClientProvider client={client()}><UniversalNativeDetailPage screenId="beleg/sales-order" entityId={entityId} /></QueryClientProvider>
}
beforeEach(() => {
  vi.clearAllMocks()
  mocks.get.mockResolvedValue({ data: options })
  mocks.execute.mockResolvedValue({ success: true, proposedChanges: ['Lieferschein aus Positionen erstellen'] })
})
async function openConversion() {
  fireEvent.click(screen.getByRole('button', { name: 'Lieferschein erstellen' }))
  const dialog = await screen.findByRole('dialog')
  expect(mocks.get).toHaveBeenCalledWith('/api/v1/docflow/doc-1/conversion-options?target_doc_type=sales_delivery')
  return dialog
}

it('zeigt vollstaendige Restmengen und sendet 4 von 6 mit unveraenderter Version in Vorschau und Ausfuehrung', async () => {
  render(view())
  const dialog = await openConversion()
  expect(within(dialog).getByLabelText('Einheit, Zeile 1')).toHaveValue('t')
  expect(within(dialog).getByLabelText('Restmenge, Zeile 1')).toHaveValue('6')
  expect(within(dialog).getByLabelText('Artikel, Zeile 2')).toHaveValue('R-2')
  expect(within(dialog).getByLabelText('Uebernahmemenge, Zeile 2')).toHaveValue(0)
  fireEvent.change(within(dialog).getByLabelText('Uebernahmemenge, Zeile 1'), { target: { value: '4' } })
  fireEvent.click(within(dialog).getByRole('button', { name: 'Weiter' }))
  const preview = await screen.findByRole('dialog', { name: /Vorschau/ })
  const expectedPayload = { quantities_by_source_item_id: [
    { ...options.items[0], quantity: 4 }, { ...options.items[1], quantity: 0 },
  ] }
  expect(mocks.execute).toHaveBeenCalledTimes(1)
  expect(mocks.execute.mock.calls[0][0]).toEqual({ actionKey: action.key, entityId: 'doc-1', expectedVersion: 4, mode: 'dryRun', payload: expectedPayload, bindingSnapshot: JSON.stringify(action.commandBinding) })
  fireEvent.click(within(preview).getByRole('button', { name: 'Ausführen' }))
  await waitFor(() => expect(mocks.execute).toHaveBeenCalledTimes(2))
  expect(mocks.execute.mock.calls[1][0]).toEqual({ actionKey: action.key, entityId: 'doc-1', expectedVersion: 4, mode: 'execute', payload: expectedPayload, bindingSnapshot: JSON.stringify(action.commandBinding), approvalId: undefined, auditReason: undefined })
})

it('erhaelt die Eingaben nach abgelehnter Vorschau und fuehrt nichts aus', async () => {
  mocks.execute.mockResolvedValue({ success: false, error: 'Restmenge nicht mehr verfuegbar' })
  render(view())
  const dialog = await openConversion()
  fireEvent.change(within(dialog).getByLabelText('Uebernahmemenge, Zeile 1'), { target: { value: '4' } })
  fireEvent.click(within(dialog).getByRole('button', { name: 'Weiter' }))
  expect((await screen.findAllByText('Restmenge nicht mehr verfuegbar')).length).toBeGreaterThan(0)
  expect(screen.getByLabelText('Uebernahmemenge, Zeile 1')).toHaveValue(4)
  expect(mocks.execute).toHaveBeenCalledTimes(1)
  expect(mocks.execute.mock.calls[0][0].mode).toBe('dryRun')
})

it('oeffnet keine Positionsauswahl fuer veraltete Optionen', async () => {
  mocks.get.mockResolvedValue({ data: { ...options, version: 3 } })
  render(view())
  fireEvent.click(screen.getByRole('button', { name: 'Lieferschein erstellen' }))
  expect(await screen.findByText(/Positionsauswahl ist unvollstaendig oder veraltet/)).toBeVisible()
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  expect(mocks.execute).not.toHaveBeenCalled()
})

it('verwirft spaete Antwort nach Navigation und doppelte Klicks', async () => {
  let resolve!: (value: unknown) => void
  mocks.get.mockReturnValue(new Promise(done => { resolve = done }))
  const page = render(view())
  const button = screen.getByRole('button', { name: 'Lieferschein erstellen' })
  fireEvent.click(button); fireEvent.click(button)
  expect(mocks.get).toHaveBeenCalledTimes(1)
  page.rerender(view('doc-2'))
  await act(async () => { resolve({ data: options }) })
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  expect(mocks.execute).not.toHaveBeenCalled()
})
