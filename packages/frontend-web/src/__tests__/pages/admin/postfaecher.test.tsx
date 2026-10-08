import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import AdminPostfaecherPage from '@/pages/admin/postfaecher'

const mocks = vi.hoisted(() => ({
  liste: vi.fn(),
  speichern: vi.fn(),
  testen: vi.fn(),
  entfernen: vi.fn(),
  google: vi.fn(),
  toast: { success: vi.fn(), error: vi.fn() },
}))
vi.mock('@/lib/api/postfaecher', () => ({
  listePostfaecher: mocks.liste,
  speicherePostfach: mocks.speichern,
  testePostfach: mocks.testen,
  entfernePostfach: mocks.entfernen,
  starteGoogleAnmeldung: mocks.google,
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
vi.mock('@/lib/api/admin', () => ({
  useRollen: () => ({ data: [
    { id: 'FINANCE_ADMIN', name: 'Finanzleitung', beschreibung: '', benutzer: 1, rechte: 3 },
    { id: 'FINANCE_BEARBEITEN', name: 'Finanzbuchhaltung', beschreibung: '', benutzer: 2, rechte: 2 },
  ] }),
}))

const FIBU = {
  id: 'p-fibu', kennung: 'fibu', anbieter: 'ionos', anmeldung: 'passwort', absender_email: 'fibu@haus.example',
  smtp_host: 'smtp.ionos.de', smtp_port: 587, sicherheit: 'starttls', ist_standard: false, verwendungen: ['fibu'],
  rollen: ['FINANCE_ADMIN'], benutzer_freigabe: [], hat_geheimnis: true, status: 'geprueft',
}

function zeichnen(): void {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(<QueryClientProvider client={client}><AdminPostfaecherPage /></QueryClientProvider>)
}

beforeEach(() => {
  vi.clearAllMocks()
  mocks.liste.mockResolvedValue([FIBU])
})

// Die Maske kommt aus der Screen Definition admin/postfaecher; das Passwort ist
// ein verdecktes Feld, das nie einen gespeicherten Wert zeigt.
describe('Postfächer', () => {
  it('zeichnet Liste und Felder aus der Screen Definition, Passwort verdeckt', async () => {
    zeichnen()
    expect(await screen.findByText('fibu@haus.example')).toBeInTheDocument()
    expect(screen.getByLabelText(/^Passwort/)).toHaveAttribute('type', 'password')
    expect(screen.getByText('FINANCE_ADMIN')).toBeInTheDocument()
  })

  it('bearbeiten lädt das Postfach ohne Passwort, speichern schickt Listen', async () => {
    mocks.speichern.mockResolvedValue({ ...FIBU, rollen: ['FINANCE_ADMIN', 'FINANCE_BEARBEITEN'] })
    zeichnen()
    await screen.findByText('fibu@haus.example')
    fireEvent.click(screen.getByTestId('row-action-bearbeiten'))
    await waitFor(() => expect(screen.getByLabelText(/^Kennung/)).toHaveValue('fibu'))
    expect(screen.getByLabelText(/^Passwort/)).toHaveValue('')
    // Rollen und Verwendung sind Mehrfachauswahlen aus dem Mask Builder.
    expect(screen.getByRole('checkbox', { name: 'Finanzleitung' })).toBeChecked()
    expect(screen.getByRole('checkbox', { name: 'Finanzbuchhaltung (Rechnungen, Mahnungen)' })).toBeChecked()
    fireEvent.click(screen.getByRole('checkbox', { name: 'Finanzbuchhaltung' }))
    fireEvent.click(screen.getByTestId('action-speichern'))
    await waitFor(() => expect(mocks.speichern).toHaveBeenCalledTimes(1))
    const [daten, id] = mocks.speichern.mock.calls[0]
    expect(id).toBe('p-fibu')
    expect(daten).toMatchObject({ kennung: 'fibu', rollen: ['FINANCE_ADMIN', 'FINANCE_BEARBEITEN'], verwendungen: ['fibu'], passwort: null })
  })

  it('entfernen fragt nach und entfernt erst dann', async () => {
    mocks.entfernen.mockResolvedValue(undefined)
    zeichnen()
    await screen.findByText('fibu@haus.example')
    fireEvent.click(screen.getByTestId('row-action-entfernen'))
    expect(mocks.entfernen).not.toHaveBeenCalled()
    const dialog = await screen.findByRole('alertdialog')
    fireEvent.click(within(dialog).getByRole('button', { name: 'Entfernen' }))
    await waitFor(() => expect(mocks.entfernen).toHaveBeenCalledWith('p-fibu'))
  })

  it('Testmail fragt den Empfänger und meldet den Fehler des Servers', async () => {
    mocks.testen.mockRejectedValue(new Error('535 Authentication failed'))
    zeichnen()
    await screen.findByText('fibu@haus.example')
    fireEvent.click(screen.getByTestId('row-action-bearbeiten'))
    await waitFor(() => expect(screen.getByTestId('action-testen')).not.toBeDisabled())
    fireEvent.click(screen.getByTestId('action-testen'))
    fireEvent.change(await screen.findByLabelText(/Empfänger/), { target: { value: 'pruefer@haus.example' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await waitFor(() => expect(mocks.testen).toHaveBeenCalledWith('p-fibu', 'pruefer@haus.example'))
    await waitFor(() => expect(mocks.toast.error).toHaveBeenCalledWith('Testmail nicht versendet',
      { description: '535 Authentication failed' }))
  })
})
