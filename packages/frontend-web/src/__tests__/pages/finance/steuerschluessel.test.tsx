import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import SteuerschluesselPage from '@/pages/finance/steuerschluessel'

const mocks = vi.hoisted(() => ({
  liste: vi.fn(),
  speichern: vi.fn(),
  konten: vi.fn(),
  toast: { success: vi.fn(), error: vi.fn() },
}))
vi.mock('@/lib/api/steuerschluessel', () => ({
  listeSteuerschluessel: mocks.liste,
  speichereSteuerschluessel: mocks.speichern,
  ladeKontenvorschlaege: mocks.konten,
}))
vi.mock('sonner', () => ({ toast: mocks.toast }))
vi.mock('@/app/routing/typed-router', () => ({
  useNavigate: () => vi.fn(),
  useParams: () => ({}),
  useBlocker: () => ({ state: 'unblocked', proceed: vi.fn(), reset: vi.fn() }),
}))
vi.mock('@/lib/api-client', () => ({
  apiClient: { get: vi.fn() },
  getAxiosErrorMessage: (e: unknown) => String((e as Error).message),
}))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => false }))

const GRUND = {
  intracom: false, export: false, reverse_charge: false, par_24_ustg: false, active: true, gueltig_von: '2021-01-01',
}
const SCHLUESSEL = [
  { ...GRUND, id: 'a', code: '3', bezeichnung: 'Umsatzsteuer 19 %', steuersatz: '19.00', credit_account: '1776',
    revenue_account: '8400', verwendung: 'Verkauf' },
  { ...GRUND, id: 'b', code: '24', bezeichnung: 'Durchschnittssatz 7,8 %', steuersatz: '7.80', credit_account: '1771',
    par_24_ustg: true, verwendung: 'Bucht nicht automatisch: Für Steuerschlüssel 24 ist kein Erlöskonto hinterlegt.' },
]

function zeichnen(): void {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(<QueryClientProvider client={client}><SteuerschluesselPage /></QueryClientProvider>)
}

function trage(feld: RegExp, wert: string): void {
  fireEvent.change(screen.getByLabelText(feld), { target: { value: wert } })
}

beforeEach(() => {
  vi.clearAllMocks()
  mocks.liste.mockResolvedValue(SCHLUESSEL)
  mocks.konten.mockImplementation(async (satz: string) => ({
    credit_account: [
      { account_number: '1776', account_name: 'Umsatzsteuer 19 %', grund: satz === '19' ? 'passt zum Satz 19 %' : 'nach Bezeichnung' },
      { account_number: '1771', account_name: 'Umsatzsteuer 7 %', grund: 'nach Bezeichnung' },
    ],
    debit_account: [{ account_number: '1576', account_name: 'Abziehbare Vorsteuer 19 %', grund: 'nach Bezeichnung' }],
    revenue_account: [
      { account_number: '8400', account_name: 'Erlöse 19 % USt', grund: null },
      { account_number: '8300', account_name: 'Erlöse 7 % USt', grund: null },
    ],
    expense_account: [{ account_number: '3400', account_name: 'Wareneingang 19 % Vorsteuer', grund: 'nach Bezeichnung' }],
  }))
})

// Die Maske kommt aus der Screen Definition finance/steuerschluessel. Aus den Schluesseln nehmen alle
// Belege Satz und Konten — deshalb belegt die Maske nichts vor.
describe('Steuerschlüssel', () => {
  it('belegt weder Satz noch Konten vor und kennt Erloeskonto und Paragraf 24', async () => {
    zeichnen()
    expect(await screen.findByLabelText(/^Steuersatz in %/)).toHaveValue(null)
    expect(screen.getByLabelText(/^Umsatzsteuerkonto/)).toHaveValue('')
    expect(screen.getByLabelText(/^Erlöskonto/)).toHaveValue('')
    expect(screen.getByLabelText(/^Vorsteuerkonto/)).toHaveValue('')
    // Das Gegenstueck zum Erloeskonto fuer Eingangsbelege.
    expect(screen.getByLabelText(/^Aufwandskonto/)).toHaveValue('')
    expect(screen.getByLabelText(/^Gültig von/)).toHaveValue('')
    expect(screen.getByLabelText(/§ 24 UStG/)).toBeInTheDocument()
  })

  it('bietet Konten aus dem Kontenplan an, reiht nach dem Satz und waehlt keines vor', async () => {
    zeichnen()
    const ust = await screen.findByLabelText(/^Umsatzsteuerkonto/)
    await waitFor(() => expect(within(ust).getByRole('option', { name: '1776 – Umsatzsteuer 19 %' })).toBeInTheDocument())
    expect(mocks.konten).toHaveBeenCalledWith('')
    trage(/^Steuersatz in %/, '19')
    await waitFor(() => expect(mocks.konten).toHaveBeenCalledWith('19'))
    await waitFor(() => expect(
      within(ust).getByRole('option', { name: '1776 – Umsatzsteuer 19 % (Vorschlag: passt zum Satz 19 %)' })).toBeInTheDocument())
    // Vorgeschlagen, nicht gewaehlt.
    expect(ust).toHaveValue('')
    expect(screen.getByLabelText(/^Erlöskonto/)).toHaveValue('')
    // Je Feld nur seine Konten: kein Erloeskonto unter den Umsatzsteuerkonten.
    expect(within(ust).queryByRole('option', { name: /8400/ })).toBeNull()
  })

  it('zeigt ein hinterlegtes Konto, das der Kontenplan nicht mehr anbietet', async () => {
    mocks.liste.mockResolvedValue([{ ...SCHLUESSEL[0], revenue_account: '8999' }])
    zeichnen()
    fireEvent.click(await screen.findByTestId('row-action-bearbeiten'))
    const erloes = screen.getByLabelText(/^Erlöskonto/)
    await waitFor(() => expect(erloes).toHaveValue('8999'))
    expect(within(erloes).getByRole('option', { name: /^8999 – nicht im Kontenplan/ })).toBeInTheDocument()
  })

  it('zeigt je Schluessel, wofuer er bucht oder warum nicht', async () => {
    zeichnen()
    expect(await screen.findByText('Verkauf')).toBeInTheDocument()
    expect(screen.getByText(/kein Erlöskonto hinterlegt/)).toBeInTheDocument()
    expect(screen.getByText('§ 24 UStG')).toBeInTheDocument()
    expect(screen.getByText('7,8 %')).toBeInTheDocument()
  })

  it('speichert ohne Steuersatz nicht und fragt den Server nicht', async () => {
    zeichnen()
    await screen.findByText('Verkauf')
    trage(/^Schlüssel/, '5')
    trage(/^Bezeichnung/, 'Umsatzsteuer 19 % (Dienstleistung)')
    trage(/^Gültig von/, '2021-01-01')
    fireEvent.click(screen.getByTestId('action-speichern'))
    await waitFor(() => expect(mocks.toast.error).toHaveBeenCalledWith('Steuerschlüssel unvollständig', expect.anything()))
    expect(screen.queryByRole('alertdialog')).toBeNull()
    expect(mocks.speichern).not.toHaveBeenCalled()
  })

  it('legt nach Rueckfrage an und schickt leere Konten als leer', async () => {
    mocks.speichern.mockResolvedValue({ actionKey: 'speichern', mode: 'execute', success: true, summary: 'angelegt' })
    zeichnen()
    await screen.findByText('Verkauf')
    trage(/^Schlüssel/, '5')
    trage(/^Bezeichnung/, 'Steuerfrei')
    trage(/^Steuersatz in %/, '0')
    trage(/^Erlöskonto/, '8400')
    trage(/^Gültig von/, '2021-01-01')
    fireEvent.click(screen.getByTestId('action-speichern'))
    expect(mocks.speichern).not.toHaveBeenCalled()
    const dialog = await screen.findByRole('alertdialog')
    expect(within(dialog).getByText('Steuerschlüssel 5 anlegen?')).toBeInTheDocument()
    fireEvent.click(within(dialog).getByRole('button', { name: 'Speichern' }))
    await waitFor(() => expect(mocks.speichern).toHaveBeenCalledTimes(1))
    const [daten, auftrag] = mocks.speichern.mock.calls[0]
    expect(daten).toMatchObject({
      code: '5', bezeichnung: 'Steuerfrei', steuersatz: '0', revenue_account: '8400', credit_account: null,
      debit_account: null, expense_account: null, par_24_ustg: false, reverse_charge: false, active: true, gueltig_von: '2021-01-01',
    })
    expect(auftrag).toMatch(/^steuerschluessel-speichern-/)
    await waitFor(() => expect(mocks.toast.success).toHaveBeenCalledWith('Steuerschlüssel gespeichert', expect.anything()))
  })

  it('laedt einen Schluessel zum Bearbeiten, sperrt den Schluessel und sagt, dass geaendert wird', async () => {
    mocks.speichern.mockResolvedValue({ actionKey: 'speichern', mode: 'execute', success: true, summary: 'geändert' })
    zeichnen()
    await screen.findByText('Verkauf')
    fireEvent.click(screen.getAllByTestId('row-action-bearbeiten')[1])
    await waitFor(() => expect(screen.getByLabelText(/^Schlüssel/)).toHaveValue('24'))
    expect(screen.getByLabelText(/^Schlüssel/)).toHaveAttribute('readonly')
    expect(screen.getByLabelText(/^Steuersatz in %/)).toHaveValue(7.8)
    trage(/^Erlöskonto/, '8300')
    fireEvent.click(screen.getByTestId('action-speichern'))
    const dialog = await screen.findByRole('alertdialog')
    expect(within(dialog).getByText('Steuerschlüssel 24 ändern?')).toBeInTheDocument()
    fireEvent.click(within(dialog).getByRole('button', { name: 'Speichern' }))
    await waitFor(() => expect(mocks.speichern).toHaveBeenCalledTimes(1))
    expect(mocks.speichern.mock.calls[0][0]).toMatchObject({
      code: '24', steuersatz: '7.8', credit_account: '1771', revenue_account: '8300', par_24_ustg: true,
    })
  })

  it('nennt den Grund, wenn der Server ablehnt', async () => {
    mocks.speichern.mockResolvedValue({
      actionKey: 'speichern', mode: 'execute', success: false,
      validationErrors: [{ field: 'revenue_account', message: 'Erlöskonto 8999 steht nicht im Kontenplan.', severity: 'blocking' }],
    })
    zeichnen()
    await screen.findByText('Verkauf')
    fireEvent.click(screen.getAllByTestId('row-action-bearbeiten')[0])
    await waitFor(() => expect(screen.getByLabelText(/^Schlüssel/)).toHaveValue('3'))
    trage(/^Erlöskonto/, '8999')
    fireEvent.click(screen.getByTestId('action-speichern'))
    fireEvent.click(within(await screen.findByRole('alertdialog')).getByRole('button', { name: 'Speichern' }))
    await waitFor(() => expect(mocks.toast.error).toHaveBeenCalledWith(
      'Steuerschlüssel nicht gespeichert', { description: 'Erlöskonto 8999 steht nicht im Kontenplan.' }))
    expect(mocks.toast.success).not.toHaveBeenCalled()
  })
})
