import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import DebitorenPage from '@/pages/fibu/debitoren'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import definitionFixture from '../../fixtures/fibu-debitoren-builder-contract.json'

const testState = vi.hoisted(() => ({ get: vi.fn(), navigate: vi.fn() }))

// Exercise the real ScreenDefinition/runtime/table path; only transport and app context are replaced.
vi.mock('@/lib/api-client', () => ({
  apiClient: { get: testState.get, request: vi.fn() },
  getAxiosErrorMessage: (error: Error) => error.message,
}))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => testState.navigate }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { id: 'test-user', roles: [], scopes: [] } }) }))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => false }))
vi.mock('@/hooks/useKeyboardShortcuts', () => ({ buildCoreMaskShortcuts: () => [], useKeyboardShortcuts: () => undefined }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api/ux-overlays', () => ({
  overlayKeys: { screen: (id: string) => ['overlays', id] },
  useUserScreenOverlay: () => ({ data: { overlay: {}, schema_version: 1 } }),
  saveUserOverlay: vi.fn(),
  deleteUserOverlay: vi.fn(),
}))

const definition = definitionFixture as ScreenDefinition
const openItems = [
  {
    id: 'op-schmidt', rechnungsnr: 'RE-2025-0123', kunde_name: 'Agrar Schmidt GmbH', konto_nr: '10001',
    rechnungsdatum: '2025-03-01', faelligkeit: '2025-03-15', op_betrag: '1250.00', offen: '1250.00',
    mahn_stufe: 1, ueberfaellig: true, waehrung: 'EUR',
  },
  {
    id: 'op-meyer', rechnungsnr: 'RE-2025-0456', kunde_name: 'Meyer Landhandel', konto_nr: '20002',
    rechnungsdatum: '2025-04-01', faelligkeit: '2025-04-15', op_betrag: '80.00', offen: '42.50',
    mahn_stufe: 0, ueberfaellig: false, waehrung: 'EUR',
  },
]

function renderPage() {
  testState.get.mockImplementation(async (url: string) => {
    if (url === '/api/v1/masks/fibu__debitoren-liste/screen-definition') return { data: definition }
    if (url.startsWith('/api/v1/masks/fibu%2Fdebitoren-liste/data/list?')) {
      const params = new URLSearchParams(url.split('?')[1])
      const limit = Number(params.get('limit') ?? 100)
      const offset = Number(params.get('offset') ?? 0)
      return { data: { data: { items: openItems.slice(offset, offset + limit), total: openItems.length } } }
    }
    throw new Error(`Unexpected HTTP read: ${url}`)
  })
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(<QueryClientProvider client={client}><DebitorenPage /></QueryClientProvider>)
}

describe('DebitorenPage native OP list', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('renders the canonical open-item list and its business heading', async () => {
    renderPage()

    expect(await screen.findByRole('heading', { name: 'Debitoren OP' })).toBeTruthy()
    expect(screen.getByText('Offene Posten Debitoren')).toBeTruthy()
    expect(await screen.findByText('RE-2025-0123')).toBeTruthy()
    const table = screen.getByTestId('table-list')
    expect(within(table).getByText('Agrar Schmidt GmbH')).toBeTruthy()
    expect(within(table).getByText('10001')).toBeTruthy()
    expect(within(table).getByText('Ja')).toBeTruthy()
    expect(within(table).getAllByText('EUR')).toHaveLength(2)
  })

  it('searches canonical customer, account and invoice fields, including no matches', async () => {
    renderPage()
    expect(await screen.findByText('RE-2025-0123')).toBeTruthy()
    const search = screen.getByTestId('search-list')
    const table = screen.getByTestId('table-list')

    fireEvent.change(search, { target: { value: 'Schmidt' } })
    expect(await within(table).findByText('RE-2025-0123')).toBeTruthy()
    expect(within(table).queryByText('RE-2025-0456')).toBeNull()

    fireEvent.change(search, { target: { value: '20002' } })
    expect(await within(table).findByText('RE-2025-0456')).toBeTruthy()
    expect(within(table).queryByText('RE-2025-0123')).toBeNull()

    fireEvent.change(search, { target: { value: 'RE-2025-0123' } })
    expect(await within(table).findByText('RE-2025-0123')).toBeTruthy()
    expect(within(table).queryByText('RE-2025-0456')).toBeNull()

    fireEvent.change(search, { target: { value: 'kein Treffer' } })
    await waitFor(() => expect(within(table).queryByText('RE-2025-0123')).toBeNull())
    expect(within(table).queryByText('RE-2025-0456')).toBeNull()
  })

  it('shows count, EUR total, overdue and dunning KPIs from the real aggregate contract', async () => {
    renderPage()
    const summary = within(await screen.findByRole('region', { name: 'Listenübersicht' }))
    expect(summary.getByText('Offene Posten')).toBeTruthy()
    expect(summary.getByText('Gesamt offen')).toBeTruthy()
    expect(summary.getByText('Überfällig')).toBeTruthy()
    expect(summary.getByText('In Mahnung')).toBeTruthy()
    expect(summary.getByText('2', { selector: 'dd' })).toBeTruthy()
    expect(summary.getByText(/1\.292,50\s*€/)).toBeTruthy()
    expect(screen.getByText('1 überfällige Rechnung(en)!')).toBeTruthy()
    expect(summary.getAllByText('1', { selector: 'dd' })).toHaveLength(2)
  })

  it('renders the canonical DTO values, not legacy-shaped mock properties', async () => {
    renderPage()
    const table = await screen.findByTestId('table-list')
    expect(within(table).getByText('RE-2025-0123')).toBeTruthy()
    expect(within(table).getByText('Agrar Schmidt GmbH')).toBeTruthy()
    expect(within(table).getAllByText(/1\.250,00\s*€/)).toHaveLength(2)
    expect(within(table).getByText('Ja')).toBeTruthy()
  })
})
