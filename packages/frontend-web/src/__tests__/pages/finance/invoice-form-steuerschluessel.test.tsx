import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import FinanceInvoiceFormPage from '@/pages/finance/invoice-form'

const mocks = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), toast: vi.fn(), navigate: vi.fn() }))
vi.mock('@/lib/api-client', () => ({
  apiClient: { get: mocks.get, post: mocks.post },
  getAxiosErrorMessage: (e: unknown) => String((e as Error).message),
}))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: mocks.toast }) }))
vi.mock('@/app/routing/typed-router', () => ({
  useNavigate: () => mocks.navigate,
  useParams: () => ({}),
  useLocation: () => ({ pathname: '/finance/invoices/new', search: '' }),
  Link: ({ children }: { children: unknown }) => children,
}))
vi.mock('@/components/app/ModuleToolbar', () => ({ ModuleToolbar: () => null }))

const VERKAUF = [
  { code: '2', bezeichnung: 'Umsatzsteuer 7 %', steuersatz: '7.00' },
  { code: '3', bezeichnung: 'Umsatzsteuer 19 %', steuersatz: '19.00' },
]

function zeichnen(): void {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(<QueryClientProvider client={client}><FinanceInvoiceFormPage /></QueryClientProvider>)
}

beforeEach(() => {
  vi.clearAllMocks()
  mocks.get.mockImplementation(async (weg: string) =>
    weg.includes('/tax-keys/auswahl') ? { data: VERKAUF } : { data: { items: [] } })
  mocks.post.mockResolvedValue({ data: { ok: true } })
})

// Bis zum 13.10.2026 hatte die Position ein Feld „MwSt %“, vorbelegt mit 19.
describe('Ausgangsrechnung: Steuerschluessel statt Prozentfeld', () => {
  it('hat kein Prozentfeld und belegt keinen Steuerschluessel vor', async () => {
    zeichnen()
    fireEvent.click(screen.getByRole('button', { name: /Position hinzufügen/ }))
    const feld = await screen.findByLabelText('Steuerschlüssel Position 1')
    await waitFor(() => expect(within(feld).getByRole('option', { name: '3 – Umsatzsteuer 19 % (19 %)' })).toBeInTheDocument())
    expect(feld).toHaveValue('')
    expect(screen.queryByText('MwSt %')).toBeNull()
    // Ohne Schluessel steht keine Steuer und kein Brutto da.
    expect(screen.getAllByText('offen').length).toBeGreaterThanOrEqual(2)
    expect(screen.getByText(/Mindestens eine Position hat keinen Steuerschlüssel/)).toBeInTheDocument()
  })

  it('zeigt die Steuer aus dem gewaehlten Schluessel', async () => {
    zeichnen()
    fireEvent.click(screen.getByRole('button', { name: /Position hinzufügen/ }))
    const feld = await screen.findByLabelText('Steuerschlüssel Position 1')
    await waitFor(() => expect(within(feld).getAllByRole('option').length).toBeGreaterThan(2))
    fireEvent.change(screen.getByPlaceholderText('Beschreibung'), { target: { value: 'Weizen' } })
    const zahlen = screen.getAllByRole('spinbutton')
    fireEvent.change(zahlen[0], { target: { value: '2' } })
    fireEvent.change(zahlen[1], { target: { value: '100' } })
    fireEvent.change(feld, { target: { value: '2' } })
    await waitFor(() => expect(screen.getByText('14.00 €')).toBeInTheDocument())
    expect(screen.getByText('214.00 €')).toBeInTheDocument()
    expect(screen.queryByText(/Mindestens eine Position hat keinen Steuerschlüssel/)).toBeNull()
  })
})
