import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import CreditNoteEditorPage from '@/pages/sales/credit-note-editor'

const mocks = vi.hoisted(() => ({
  liste: vi.fn(),
  laden: vi.fn(),
  schluessel: vi.fn(),
  vorschau: vi.fn(),
  speichern: vi.fn(),
  buchen: vi.fn(),
  vorschlaege: vi.fn(),
  freigeben: vi.fn(),
  ablehnen: vi.fn(),
  toast: { success: vi.fn(), error: vi.fn() },
}))
vi.mock('@/lib/api/gutschrift', () => ({
  listeGutschriften: mocks.liste,
  ladeGutschrift: mocks.laden,
  listeSteuerschluessel: mocks.schluessel,
  steuerVorschau: mocks.vorschau,
  speichereGutschrift: mocks.speichern,
  bucheGutschrift: mocks.buchen,
  listeBuchungsvorschlaege: mocks.vorschlaege,
  gibVorschlagFrei: mocks.freigeben,
  lehneVorschlagAb: mocks.ablehnen,
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

const SCHLUESSEL = [
  { id: 'a', code: '2', bezeichnung: 'Umsatzsteuer 7 %', steuersatz: 7, credit_account: '1771', revenue_account: '8300' },
  { id: 'b', code: '3', bezeichnung: 'Umsatzsteuer 19 %', steuersatz: 19, credit_account: '1776', revenue_account: '8400' },
  { id: 'c', code: '9', bezeichnung: 'Vorsteuer 19 %', steuersatz: 19, debit_account: '1576' },
]
const ENTWURF = {
  id: 'gs-1', credit_note_number: 'GS-1', customer_id: 'K-100', customer_name: 'Hof Janssen', invoice_reference: 'RE-7',
  reason: 'Retoure', correction_type: 'rechnungskorrektur', total_amount: 1190, net_amount: 1000, tax_amount: 190,
  status: 'draft', lines: [{ description: 'Weizen', quantity: 2, unit_price: 500, tax_code: '3' }],
}

const VORSCHLAG = {
  proposal_id: 'v-1', credit_note_id: 'gs-1', credit_note_number: 'GS-1', netto: 1000, steuer: 190, brutto: 1190,
  approval_status: 'pending', vorgeschlagen_von: 'agent-7', gebucht: false,
}

function zeichnen(): void {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(<QueryClientProvider client={client}><CreditNoteEditorPage /></QueryClientProvider>)
}

async function erfassePosition(mitSchluessel: boolean): Promise<void> {
  fireEvent.change(screen.getByLabelText(/^Position: Bezeichnung/), { target: { value: 'Weizen' } })
  fireEvent.change(screen.getByLabelText(/^Position: Menge/), { target: { value: '2' } })
  fireEvent.change(screen.getByLabelText(/^Position: Einzelpreis netto/), { target: { value: '500' } })
  if (mitSchluessel) {
    fireEvent.change(screen.getByLabelText(/^Position: Steuerschlüssel/), { target: { value: '3' } })
  }
  fireEvent.click(screen.getByTestId('action-position'))
}

beforeEach(() => {
  vi.clearAllMocks()
  mocks.liste.mockResolvedValue([])
  mocks.vorschlaege.mockResolvedValue([])
  mocks.schluessel.mockResolvedValue(SCHLUESSEL)
  mocks.vorschau.mockResolvedValue({
    geklaert: true, netto: 1000, steuer: 190, brutto: 1190,
    gruppen: [{ tax_code: '3', satz: 19, netto: 1000, steuer: 190, brutto: 1190 }],
  })
})

// Die Maske kommt aus der Screen Definition sales/gutschrift. Sie hat kein Prozentfeld:
// Die Umsatzsteuer kommt aus dem Steuerschluessel, gerechnet wird auf dem Server.
describe('Gutschrift', () => {
  it('bietet Steuerschluessel statt eines Prozentfelds und waehlt keinen vor', async () => {
    zeichnen()
    const auswahl = await screen.findByLabelText(/^Position: Steuerschlüssel/)
    await waitFor(() => expect(within(auswahl).getByRole('option', { name: '3 – Umsatzsteuer 19 % (19 %)' })).toBeInTheDocument())
    // Verkaufsbeleg: kein reiner Vorsteuerschluessel in der Auswahl.
    expect(within(auswahl).queryByRole('option', { name: /Vorsteuer/ })).toBeNull()
    expect(auswahl).toHaveValue('')
    expect(screen.queryByLabelText(/Steuersatz|MwSt|%$/)).toBeNull()
  })

  it('laesst den Server rechnen und zeigt Netto, Umsatzsteuer und Brutto', async () => {
    zeichnen()
    await screen.findByLabelText(/^Position: Steuerschlüssel/)
    await waitFor(() => expect(mocks.schluessel).toHaveBeenCalled())
    await erfassePosition(true)
    await waitFor(() => expect(mocks.vorschau).toHaveBeenCalledWith([
      { description: 'Weizen', quantity: 2, unit_price: 500, tax_code: '3' },
    ]))
    // Positionsliste nennt den Schluessel, der Steuerausweis kommt vom Server.
    expect((await screen.findAllByText('3 – Umsatzsteuer 19 %')).length).toBeGreaterThan(0)
    expect(screen.getAllByText('190,00 €').length).toBeGreaterThan(0)
    expect(screen.getAllByText('1.190,00 €').length).toBeGreaterThan(0)
  })

  it('nimmt ohne Steuerschluessel keinen Satz an und zeigt den Pruefgrund', async () => {
    mocks.vorschau.mockResolvedValue({
      geklaert: false, pruefgrund: 'Position 1 hat keinen Steuerschlüssel.', netto: 1000, steuer: null, brutto: null, gruppen: [],
    })
    zeichnen()
    await screen.findByLabelText(/^Position: Steuerschlüssel/)
    await erfassePosition(false)
    await waitFor(() => expect(mocks.vorschau).toHaveBeenCalledWith([
      { description: 'Weizen', quantity: 2, unit_price: 500, tax_code: null },
    ]))
    expect(await screen.findByText(/Position 1 hat keinen Steuerschlüssel\./)).toBeInTheDocument()
    expect(screen.getAllByText('offen').length).toBeGreaterThanOrEqual(2)
  })

  it('speichert ueber den Kommando-Weg mit Steuerschluessel und ohne Steuersatz', async () => {
    mocks.speichern.mockResolvedValue({ actionKey: 'speichern', mode: 'execute', success: true, summary: 'gespeichert' })
    mocks.laden.mockResolvedValue(ENTWURF)
    zeichnen()
    await screen.findByLabelText(/^Position: Steuerschlüssel/)
    fireEvent.change(screen.getByLabelText(/^Gutschriftnummer/), { target: { value: 'GS-1' } })
    fireEvent.change(screen.getByLabelText(/^Kunde \(Nr\.\)/), { target: { value: 'K-100' } })
    fireEvent.change(screen.getByLabelText(/^Grund/), { target: { value: 'Retoure' } })
    await erfassePosition(true)
    mocks.liste.mockResolvedValue([ENTWURF])
    fireEvent.click(screen.getByTestId('action-speichern'))
    await waitFor(() => expect(mocks.speichern).toHaveBeenCalledTimes(1))
    const [daten, auftrag] = mocks.speichern.mock.calls[0]
    expect(daten).toMatchObject({
      credit_note_number: 'GS-1', customer_id: 'K-100', reason: 'Retoure', correction_type: 'rechnungskorrektur',
      lines: [{ description: 'Weizen', quantity: 2, unit_price: 500, tax_code: '3' }],
    })
    expect(daten.lines[0]).not.toHaveProperty('tax_rate')
    expect(auftrag).toBe('gutschrift-speichern-GS-1')
  })

  it('buchen fragt nach und zeigt den Pruefgrund, wenn die Buchung ablehnt', async () => {
    mocks.liste.mockResolvedValue([ENTWURF])
    mocks.laden.mockResolvedValue(ENTWURF)
    mocks.buchen.mockResolvedValue({
      actionKey: 'buchen', mode: 'execute', success: false,
      error: 'Gutschrift nicht gebucht, bitte prüfen: Konto 8400 fehlt im Kontenplan.',
    })
    zeichnen()
    fireEvent.click(await screen.findByTestId('row-action-laden'))
    await waitFor(() => expect(screen.getByTestId('action-buchen')).not.toBeDisabled())
    fireEvent.click(screen.getByTestId('action-buchen'))
    expect(mocks.buchen).not.toHaveBeenCalled()
    const dialog = await screen.findByRole('alertdialog')
    fireEvent.click(within(dialog).getByRole('button', { name: 'Buchen' }))
    await waitFor(() => expect(mocks.buchen).toHaveBeenCalledWith('gs-1', 'gutschrift-buchen-gs-1'))
    await waitFor(() => expect(mocks.toast.error).toHaveBeenCalledWith('Nicht gebucht', {
      description: 'Gutschrift nicht gebucht, bitte prüfen: Konto 8400 fehlt im Kontenplan. Die Gutschrift bleibt Entwurf.',
    }))
    expect(await screen.findByText(/Gutschrift nicht gebucht, bitte prüfen: Konto 8400 fehlt im Kontenplan\./)).toBeInTheDocument()
  })

  // Ein Agent bucht nicht selbst: Er schlaegt vor, ein Mensch prueft in dieser Maske und gibt frei.
  it('laesst den Vorschlag eines Agenten erst nach dem Oeffnen der Gutschrift freigeben', async () => {
    mocks.liste.mockResolvedValue([ENTWURF])
    mocks.laden.mockResolvedValue(ENTWURF)
    mocks.vorschlaege.mockResolvedValue([VORSCHLAG])
    mocks.freigeben.mockResolvedValue({ actionKey: 'vorschlag_freigeben', mode: 'execute', success: true, summary: 'freigegeben' })
    zeichnen()
    expect(await screen.findByText('agent-7')).toBeInTheDocument()
    expect(screen.getByText('Wartet auf Prüfung')).toBeInTheDocument()
    // Ohne geoeffnete Gutschrift gibt es nichts freizugeben.
    expect(screen.getByTestId('action-vorschlag_freigeben')).toBeDisabled()
    fireEvent.click(screen.getByTestId('row-action-pruefen'))
    await waitFor(() => expect(mocks.laden).toHaveBeenCalledWith('gs-1'))
    await waitFor(() => expect(screen.getByTestId('action-vorschlag_freigeben')).not.toBeDisabled())
    fireEvent.click(screen.getByTestId('action-vorschlag_freigeben'))
    expect(mocks.freigeben).not.toHaveBeenCalled()
    const dialog = await screen.findByRole('alertdialog')
    expect(within(dialog).getByText(/Die Freigabe selbst bucht nicht/)).toBeInTheDocument()
    fireEvent.click(within(dialog).getByRole('button', { name: 'Freigeben' }))
    await waitFor(() => expect(mocks.freigeben).toHaveBeenCalledWith('v-1'))
    expect(mocks.buchen).not.toHaveBeenCalled()
  })

  it('lehnt einen Vorschlag nur mit Grund ab', async () => {
    mocks.liste.mockResolvedValue([ENTWURF])
    mocks.laden.mockResolvedValue(ENTWURF)
    mocks.vorschlaege.mockResolvedValue([VORSCHLAG])
    mocks.ablehnen.mockResolvedValue({ actionKey: 'vorschlag_ablehnen', mode: 'execute', success: true, summary: 'abgelehnt' })
    zeichnen()
    fireEvent.click(await screen.findByTestId('row-action-pruefen'))
    await waitFor(() => expect(screen.getByTestId('action-vorschlag_ablehnen')).not.toBeDisabled())
    fireEvent.click(screen.getByTestId('action-vorschlag_ablehnen'))
    fireEvent.change(await screen.findByLabelText(/Grund der Ablehnung/), { target: { value: 'Menge stimmt nicht' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await waitFor(() => expect(mocks.ablehnen).toHaveBeenCalledWith('v-1', 'Menge stimmt nicht'))
  })
})
