import { useEffect } from 'react'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, expect, it, vi } from 'vitest'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const state = vi.hoisted(() => ({ request: vi.fn(), print: vi.fn(), toast: vi.fn(), navigate: vi.fn(), rows: [] as Record<string, unknown>[], permissions: ['sales.offer.import'], definition: {} as ScreenDefinition }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: state.definition }) }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => state.permissions }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => state.navigate }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: state.toast }) }))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => true }))
vi.mock('@/hooks/useKeyboardShortcuts', () => ({ buildCoreMaskShortcuts: () => [], useKeyboardShortcuts: () => undefined }))
vi.mock('@/lib/export-utils', () => ({ exportToCSV: vi.fn(), printTable: state.print }))
vi.mock('@/lib/api-client', () => ({ apiClient: { request: state.request, get: vi.fn() }, getAxiosErrorMessage: (e: Error) => e.message }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ onAction, onListData }: { onAction: (key: string, payload: object) => void; onListData: (rows: object[]) => void }) => {
    useEffect(() => { onListData(state.rows) }, [onListData])
    return <><button onClick={() => onAction('import_csv', {})}>Import starten</button><button onClick={() => onAction('print', {})}>Druck starten</button></>
  },
}))
const csv = 'offer_number;subject;customer_id;total_amount;currency\nANG-7;Saatgut;C-1;12.50;EUR'
beforeEach(() => {
  vi.clearAllMocks()
  state.permissions = ['sales.offer.import']
  state.rows = [{ offer_number: 'ANG-7', subject: 'Saatgut' }]
  state.definition = {
    schemaVersion: 1, id: 'sales/angebote-liste', domain: 'sales', mode: 'list', title: 'Angebote',
    listExperience: { searchFields: ['offer_number'], aggregates: [], export: { filenamePrefix: 'Angebote_', delimiter: ';', columns: [{key:'offer_number',label:'Angebot'}] } },
    actions: [
      { key: 'print', label: 'Drucken', localEffect: 'print' },
      { key: 'import_csv', label: 'CSV importieren', permission: 'sales.offer.import', commandEndpoint: '/api/v1/sales/offers/actions/import-csv', method: 'POST', requiresConfirmation: true,
        inputFields: [{key:'csv_content',label:'CSV-Datei',type:'file',required:true,fileContent:{encoding:'utf-8',accept:'.csv',maxBytes:1048576}}] },
    ],
  } as ScreenDefinition
})
function mount() {
  return render(<QueryClientProvider client={new QueryClient()}><NativeListPage screenId="sales/angebote-liste" /></QueryClientProvider>)
}
it('prints the loaded filtered rows and declared columns without fetching another data set', () => {
  mount()
  fireEvent.click(screen.getByRole('button', {name:'Druck starten'}))
  expect(state.print).toHaveBeenCalledWith(state.rows, 'Angebote', [{key:'offer_number',label:'Angebot'}])
  expect(state.request).not.toHaveBeenCalled()
})
it('reports an empty print view instead of printing stale or invented data', () => {
  state.rows=[]
  mount()
  fireEvent.click(screen.getByRole('button', {name:'Druck starten'}))
  expect(state.print).not.toHaveBeenCalled()
  expect(state.toast).toHaveBeenCalledWith(expect.objectContaining({variant:'destructive'}))
})
it('reads CSV contents, requires confirmation and preserves the same retry key after a failed command', async () => {
  state.request.mockRejectedValueOnce(new Error('Verbindung unterbrochen')).mockResolvedValueOnce({data:{success:true,summary:'1 Angebot importiert'}})
  mount()
  fireEvent.click(screen.getByRole('button', {name:'Import starten'}))
  const file = new File([csv], 'angebote.csv', {type:'text/csv'})
  Object.defineProperty(file, 'arrayBuffer', {value: async () => new TextEncoder().encode(csv).buffer})
  fireEvent.change(screen.getByLabelText('CSV-Datei'), {target:{files:[file]}})
  await waitFor(() => expect(screen.getByLabelText('Dateivorschau')).toHaveTextContent('ANG-7'))
  fireEvent.click(screen.getByRole('button', {name:'Weiter'}))
  expect(state.request).not.toHaveBeenCalled()
  fireEvent.click(screen.getByRole('button', {name:'CSV importieren'}))
  await waitFor(() => expect(state.toast).toHaveBeenCalledWith(expect.objectContaining({variant:'destructive'})))
  expect(screen.getByRole('dialog')).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', {name:'CSV importieren'}))
  await waitFor(() => expect(state.request).toHaveBeenCalledTimes(2))
  const [first, retry] = state.request.mock.calls.map(call => call[0])
  expect(first).toMatchObject({url:'/api/v1/sales/offers/actions/import-csv',method:'POST',data:{csv_content:csv}})
  expect(first.data._idempotencyKey).toBeTruthy()
  expect(retry.data).toEqual(first.data)
  await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
})
it('does not open the import command without its declared permission', () => {
  state.permissions=[]
  mount()
  fireEvent.click(screen.getByRole('button', {name:'Import starten'}))
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  expect(state.request).not.toHaveBeenCalled()
})
