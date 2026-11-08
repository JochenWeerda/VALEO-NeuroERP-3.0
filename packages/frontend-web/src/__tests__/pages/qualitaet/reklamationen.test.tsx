import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import ReklamationenPage from '@/pages/qualitaet/reklamationen'
import definition from '../../fixtures/complaint-studio.json'

const transport = vi.hoisted(() => ({ get: vi.fn(), request: vi.fn(), navigate: vi.fn(), checkpoint: vi.fn(), toast: vi.fn() }))
vi.mock('@/app/routing/typed-router', async () => ({ ...await vi.importActual('@/app/routing/typed-router'), useNavigate: () => transport.navigate }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: transport.get, request: transport.request }, getAxiosErrorMessage: (e: Error) => e.message }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { id: 'synthetic-user', roles: ['admin'], scopes: [] } }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: transport.toast }) }))
vi.mock('@/lib/api/flow-spines', async () => ({ ...await vi.importActual('@/lib/api/flow-spines'), saveFlowSpineResumeCheckpoint: transport.checkpoint }))
const rows = [
  { id: 'rek-1', nummer: 'REK-001', kunde: 'Agrar Mueller', artikel: 'Weizen', grund: 'Feuchte', datum: '2026-03-20', prioritaet: 'hoch', status: 'neu' },
  { id: 'rek-2', nummer: 'REK-002', kunde: 'Landhandel Nord', artikel: 'Gerste', grund: 'Besatz', datum: '2026-03-19', prioritaet: null, status: 'in-bearbeitung' },
]
beforeEach(() => {
  vi.restoreAllMocks(); vi.clearAllMocks()
  Object.defineProperty(window, 'innerWidth', { value: 1440, configurable: true })
  transport.checkpoint.mockResolvedValue({})
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({ width: 1440, height: 600, top: 0, left: 0, right: 1440, bottom: 600, x: 0, y: 0, toJSON: () => ({}) })
  transport.get.mockImplementation(async (url: string) => {
    if (url.includes('/screen-definition')) return { data: definition }
    if (url.includes('/ux/overlays/')) return { data: { screen_id: definition.id, overlay: {} } }
    if (url.includes('/data/list')) return { data: { data: { items: rows, total: rows.length } } }
    if (url.startsWith('/api/v1/qualitaet/reklamationen')) return { data: rows }
    throw new Error(`Unexpected HTTP read: ${url}`)
  })
})
function mount(query = '') {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
    <MemoryRouter initialEntries={['/qualitaet/reklamationen' + query]}><ReklamationenPage /></MemoryRouter>
  </QueryClientProvider>)
}
const context = '?workflowProcess=complaint-to-resolution&workflowInstanceId=instance-1&workflowCase=CASE-1'

describe('Studio ReklamationenPage', () => {
  it('zeigt Reklamationsliste und Suchfeld durch die echte Runtime', async () => {
    mount()
    expect(await screen.findByText('REK-001')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Reklamationen', level: 1 })).toBeInTheDocument()
    expect(screen.getByLabelText('Suche in Reklamationen')).toBeInTheDocument()
    expect(screen.getByText('Ohne Prioritätsangabe').nextElementSibling).toHaveTextContent('1')
    expect(screen.getAllByTestId('screen-qualitaet/reklamationen-liste').some(element => element.dataset.runtime === 'native-cockpit')).toBe(true)
  })
  it('filtert Reklamationen und Kennzahlen nach den deklarierten Fachfeldern', async () => {
    mount(); await screen.findByText('REK-001')
    fireEvent.change(screen.getByLabelText('Suche in Reklamationen'), { target: { value: 'Landhandel Nord' } })
    await waitFor(() => expect(screen.queryByText('REK-001')).not.toBeInTheDocument())
    expect(screen.getByText('REK-002')).toBeInTheDocument()
    expect(screen.getByText('Bearbeitung läuft')).toBeInTheDocument()
    expect(screen.queryByText('1 neue Reklamation(en)')).not.toBeInTheDocument()
  })
  it('speichert den Checkpoint vor Navigation und sperrt wiederholte Klicks', async () => {
    let finish!: () => void
    transport.checkpoint.mockImplementation(() => new Promise<void>(resolve => { finish = resolve }))
    mount(context); await screen.findByText('REK-001')
    const create = screen.getByRole('button', { name: 'Neue Reklamation' })
    fireEvent.click(create); fireEvent.click(create)
    await waitFor(() => expect(transport.checkpoint).toHaveBeenCalledTimes(1))
    expect(transport.navigate).not.toHaveBeenCalled()
    expect(transport.checkpoint.mock.calls[0][2]).toMatchObject({ resume_node_id: 'complaint', resume_payload: { screen: 'complaint-create', workflowCase: 'CASE-1' } })
    finish()
    await waitFor(() => expect(transport.navigate).toHaveBeenCalledWith(expect.stringContaining('/qualitaet/reklamation/neu?workflowProcess=')))
  })
  it('bleibt bei Checkpointfehler auf der Maske und erlaubt einen erneuten Versuch', async () => {
    transport.checkpoint.mockRejectedValueOnce(new Error('unavailable'))
    mount(context); await screen.findByText('REK-001')
    fireEvent.click(screen.getByRole('button', { name: 'Neue Reklamation' }))
    await waitFor(() => expect(transport.toast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' })))
    expect(transport.navigate).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Neue Reklamation' }))
    await waitFor(() => expect(transport.navigate).toHaveBeenCalledTimes(1))
  })
  it('übernimmt Workflowkontext beim Öffnen einer Zeile', async () => {
    mount(context); await screen.findByText('REK-001')
    fireEvent.click(screen.getByText('REK-001'))
    await waitFor(() => expect(transport.navigate).toHaveBeenCalledWith(expect.stringContaining('/qualitaet/reklamation/rek-1?workflowProcess=')))
    expect(transport.checkpoint.mock.calls[0][2].resume_payload.screen).toBe('complaint-detail')
  })
  it('fokussiert die Suche per Tastatur und legt per zentralem Kürzel neu an', async () => {
    mount(); await screen.findByText('REK-001')
    fireEvent.keyDown(window, { key: 'f', ctrlKey: true })
    expect(screen.getByLabelText('Suche in Reklamationen')).toHaveFocus()
    fireEvent.blur(screen.getByLabelText('Suche in Reklamationen'))
    fireEvent.keyDown(window, { key: 'n', ctrlKey: true })
    await waitFor(() => expect(transport.navigate).toHaveBeenCalledWith('/qualitaet/reklamation/neu'))
  })
  it('exportiert nur die gefilterten Fälle ohne unbemerkten erneuten Datenabruf', async () => {
    mount(); await screen.findByText('REK-001')
    fireEvent.change(screen.getByLabelText('Suche in Reklamationen'), { target: { value: 'Landhandel Nord' } })
    await screen.findByText('Bearbeitung läuft')
    const objectURL = vi.fn((_blob: Blob) => 'blob:synthetic-export')
    Object.defineProperty(URL, 'createObjectURL', { value: objectURL, configurable: true })
    Object.defineProperty(URL, 'revokeObjectURL', { value: vi.fn(), configurable: true })
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
    const reads = transport.get.mock.calls.length
    fireEvent.click(screen.getByRole('button', { name: 'CSV-Export' }))
    await waitFor(() => expect(objectURL).toHaveBeenCalledTimes(1))
    const blob = objectURL.mock.calls[0][0]
    const csv = await new Promise<string>(resolve => { const reader = new FileReader(); reader.onload = () => resolve(String(reader.result)); reader.readAsText(blob) })
    expect(csv).toContain('REK-002')
    expect(csv).not.toContain('REK-001')
    expect(csv).toContain('"Nummer";"Lieferant";"Artikel";"Grund";"Datum";"Prioritaet";"Status"')
    expect(transport.get).toHaveBeenCalledTimes(reads)
  })
  it('bleibt auf Touch-Geräten bedienbar und blendet die Tastaturhilfe aus', async () => {
    Object.defineProperty(window, 'innerWidth', { value: 600, configurable: true })
    mount(); await screen.findByText('REK-001')
    expect(screen.queryByLabelText('Keyboard Shortcuts')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Neue Reklamation' }))
    await waitFor(() => expect(transport.navigate).toHaveBeenCalledWith('/qualitaet/reklamation/neu'))
  })
  it('zeigt einen Quellfehler statt eines erfundenen leeren Erfolgs', async () => {
    const original = transport.get.getMockImplementation()!
    transport.get.mockImplementation((url: string) => url.includes('/data/list') ? Promise.reject(new Error('private DB details')) : original(url))
    mount()
    expect((await screen.findAllByText(/konnte nicht geladen werden/)).length).toBeGreaterThan(0)
    expect(screen.queryByText('Kein Fall mit Status Neu oder In Bearbeitung')).not.toBeInTheDocument()
    expect(screen.queryByText('private DB details')).not.toBeInTheDocument()
  })

})
