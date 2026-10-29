import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, renderHook, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { ReactNode } from 'react'
import DebitorenPage from '@/pages/fibu/debitoren'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { evaluateListExperience, formatListAggregate } from '@/components/mask-builder/runtime/list-experience'
import { useDebitorenOP } from '@/lib/api/fibu'
import definitionFixture from '../../fixtures/fibu-debitoren-builder-contract.json'

const testState = vi.hoisted(() => ({ get: vi.fn(), navigate: vi.fn(), failRows: false, currencyMismatch: false }))

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
  saveUserOverlay: vi.fn(), deleteUserOverlay: vi.fn(),
}))

const definition = definitionFixture as ScreenDefinition

function row(index: number): Record<string, unknown> {
  const last = index === 127
  return {
    id: String(index), rechnungsnr: `INV-${String(index).padStart(3, '0')}`,
    kunde_name: `CUSTOMER-${String(index).padStart(3, '0')}`, konto_nr: `D-${index}`,
    rechnungsdatum: '2026-10-01', faelligkeit: '2026-10-10', op_betrag: 20,
    offen: last ? '12.34' : '0.10', mahn_stufe: 0, ueberfaellig: last,
    waehrung: testState.currencyMismatch && index === 1 ? 'USD' : 'EUR',
  }
}

function setup() {
  const rows = Array.from({ length: 127 }, (_, index) => row(index + 1))
  testState.get.mockImplementation(async (url: string) => {
    if (url === '/api/v1/masks/fibu__debitoren-liste/screen-definition') return { data: definition }
    if (url.startsWith('/api/v1/masks/fibu%2Fdebitoren-liste/data/list?')) {
      if (testState.failRows) throw new Error('Open-Items nicht erreichbar')
      const query = new URLSearchParams(url.split('?')[1])
      const limit = Number(query.get('limit') ?? 100)
      const offset = query.has('offset') ? Number(query.get('offset')) : (Number(query.get('page') ?? 1) - 1) * limit
      return { data: { data: { items: rows.slice(offset, offset + limit), total: rows.length } } }
    }
    throw new Error(`Unexpected read: ${url}`)
  })
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  render(<QueryClientProvider client={client}><DebitorenPage /></QueryClientProvider>)
}

describe('Studio Debitoren OP list', () => {
  beforeEach(() => { vi.clearAllMocks(); testState.failRows = false; testState.currencyMismatch = false })
  afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks() })

  it('uses the full runtime for multipage search, exact EUR KPI, filtered CSV and navigation', async () => {
    let downloaded: Blob | undefined
    vi.stubGlobal('URL', { ...URL, createObjectURL: vi.fn((blob: Blob) => { downloaded = blob; return 'blob:test' }), revokeObjectURL: vi.fn() })
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined)
    const pushState = vi.spyOn(window.history, 'pushState')
    setup()

    await waitFor(() => expect(testState.get.mock.calls.length).toBeGreaterThan(1))
    expect(await screen.findByText('Seite 1 / 3')).toBeTruthy()
    expect(screen.getByText('24,94', { exact: false })).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    expect(await screen.findByText('Seite 2 / 3')).toBeTruthy()

    fireEvent.change(screen.getByTestId('search-list'), { target: { value: 'CUSTOMER-127' } })
    expect(await screen.findAllByText('INV-127')).toHaveLength(2)
    expect(screen.getByText('1 überfällige Rechnung(en)!')).toBeTruthy()
    expect(screen.queryByText('INV-001')).toBeNull()
    expect(within(screen.getByTestId('selected-record-panel')).getByText(/12,34.*€/)).toBeTruthy()

    fireEvent.click(screen.getByRole('button', { name: 'CSV-Export' }))
    await waitFor(() => expect(downloaded).toBeDefined())
    const csv = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(String(reader.result))
      reader.onerror = () => reject(reader.error)
      reader.readAsText(downloaded!)
    })
    expect(csv.split('\n')).toHaveLength(2)
    expect(csv).toContain('INV-127')
    expect(csv).not.toContain('INV-126')
    expect(csv.split('\n')[0].split(';')).toHaveLength(9)

    fireEvent.click(screen.getByRole('button', { name: 'In Vollansicht öffnen' }))
    expect(pushState).toHaveBeenCalledWith(null, '', '/finance/ar-open-item/127')
    fireEvent.click(screen.getByRole('button', { name: 'Zurück zur OP-Verwaltung' }))
    expect(testState.navigate).toHaveBeenCalledWith('/fibu/op-verwaltung')
    expect(screen.queryByRole('button', { name: /Neuer Debitor|Neu/ })).toBeNull()
  })

  it('shows a load error rather than an empty-list success state', async () => {
    testState.failRows = true
    setup()
    expect(await screen.findByTestId('table-load-error-list')).toBeTruthy()
    expect(screen.getByTestId('table-load-error-list').textContent).toContain('Tabelle „Debitoren OP“ konnte nicht geladen werden.')
  })

  it('keeps the table visible when one KPI would combine currencies', async () => {
    testState.currencyMismatch = true
    setup()
    expect(await screen.findByText('INV-001')).toBeTruthy()
    expect(await screen.findByText('Listenkennzahlen konnten nicht sicher berechnet werden. Bitte Währung und Datenbasis prüfen.')).toBeTruthy()
    expect(screen.getByTestId('table-list')).toBeTruthy()
  })

  it('formats currency by each row currency and blocks cross-currency totals', () => {
    const aggregate = definition.listExperience.aggregates[1]
    expect(formatListAggregate(aggregate, 12.34, 'EUR')).toContain('12,34')
    expect(formatListAggregate(aggregate, 12.34, 'USD')).toContain('12,34')
    expect(formatListAggregate(aggregate, 12.34, 'USD')).toContain('$')
    expect(() => evaluateListExperience(definition.listExperience, [
      { offen: '12.34', waehrung: 'EUR' }, { offen: '1.00', waehrung: 'USD' },
    ])).toThrow('Währungsübergreifende Summe ist gesperrt.')
  })

  it('maps the compatibility hook from the real open-item response contract', async () => {
    testState.get.mockImplementationOnce(async (url: string) => {
      expect(url).toBe('/api/v1/finance/open-items?konto_typ=debitoren&only_open=true&limit=5000&offset=0')
      return { data: { items: [{
        id: 'op-1', rechnungsnr: 'R-1', kunde_name: 'Kunde 1', konto_nr: 'D-100',
        rechnungsdatum: '2026-10-01', faelligkeit: '2026-10-12', op_betrag: '80.00',
        offen: '42.50', ueberfaellig: true, mahn_stufe: 2, waehrung: 'USD',
      }], total: 1 } }
    })
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const wrapper = ({ children }: { children: ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>
    const { result } = renderHook(() => useDebitorenOP(), { wrapper })
    await waitFor(() => expect(result.current.data?.[0]?.rechnungsnr).toBe('R-1'))
    expect(result.current.data?.[0]).toMatchObject({
      kunde: 'Kunde 1', kundennr: 'D-100', datum: '2026-10-01', faelligkeit: '2026-10-12',
      betrag: 80, offen: 42.5, ueberfaellig: true, mahnStufe: 2, waehrung: 'USD',
    })
  })
})
