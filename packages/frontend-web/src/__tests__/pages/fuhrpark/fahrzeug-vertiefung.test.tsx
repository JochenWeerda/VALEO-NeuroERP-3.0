import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import FahrzeugVertiefungPage from '@/pages/fuhrpark/fahrzeug-vertiefung-legacy'

const api = vi.hoisted(() => ({
  toast: vi.fn(),
  getHistorie: vi.fn(),
  changeStatus: vi.fn(),
  listSchaeden: vi.fn(),
  createSchaden: vi.fn(),
  listBussgeld: vi.fn(),
  createBussgeld: vi.fn(),
  wartung: vi.fn(),
  leasing: vi.fn(),
}))

vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: api.toast }) }))
const updateSchadenMock = vi.hoisted(() => vi.fn())
const updateBussgeldMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api/fuhrpark', () => ({
  getFahrzeugStatusHistorie: (...args: unknown[]) => api.getHistorie(...args),
  changeFahrzeugStatus: (...args: unknown[]) => api.changeStatus(...args),
  listFahrzeugSchaeden: (...args: unknown[]) => api.listSchaeden(...args),
  createFahrzeugSchaden: (...args: unknown[]) => api.createSchaden(...args),
  updateFahrzeugSchaden: (...args: unknown[]) => updateSchadenMock(...args),
  listFahrzeugBussgeld: (...args: unknown[]) => api.listBussgeld(...args),
  createFahrzeugBussgeld: (...args: unknown[]) => api.createBussgeld(...args),
  updateFahrzeugBussgeld: (...args: unknown[]) => updateBussgeldMock(...args),
  getFahrzeugWartungVorhersage: (...args: unknown[]) => api.wartung(...args),
  leasingRueckgabe: (...args: unknown[]) => api.leasing(...args),
}))

function renderPage() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(
    <QueryClientProvider client={qc}>
      <FahrzeugVertiefungPage />
    </QueryClientProvider>,
  )
}

describe('FahrzeugVertiefungPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    api.getHistorie.mockResolvedValue([
      { id: 'h1', von_status: 'verfuegbar', zu_status: 'unterwegs', grund: 'Tour', km_stand: 100, timestamp: '2026-11-01T10:00:00Z' },
    ])
    api.listSchaeden.mockResolvedValue([])
    api.listBussgeld.mockResolvedValue([])
    api.wartung.mockResolvedValue({ naechste_wartung_km: 5000, risiko: 'niedrig' })
    api.changeStatus.mockResolvedValue({})
    api.createSchaden.mockResolvedValue({})
    api.createBussgeld.mockResolvedValue({})
    api.leasing.mockResolvedValue({})
    updateSchadenMock.mockReset()
    updateBussgeldMock.mockReset()
    updateSchadenMock.mockResolvedValue({})
    updateBussgeldMock.mockResolvedValue({})
  })

  it('laedt Statushistorie nach Fahrzeug-ID und wechselt Status', async () => {
    renderPage()
    fireEvent.change(screen.getByPlaceholderText('z. B. F-ABC12345'), { target: { value: 'FZ-1' } })
    await waitFor(() => expect(api.getHistorie).toHaveBeenCalledWith('FZ-1'))
    const statusSelect = screen.getByDisplayValue('Verfügbar')
    fireEvent.change(statusSelect, { target: { value: 'wartung' } })
    fireEvent.change(screen.getByPlaceholderText('z. B. TÜV fällig'), { target: { value: 'Inspektion' } })
    fireEvent.click(screen.getByRole('button', { name: 'Status wechseln' }))
    await waitFor(() =>
      expect(api.changeStatus).toHaveBeenCalledWith(
        'FZ-1',
        expect.objectContaining({ zu_status: 'wartung', grund: 'Inspektion' }),
      ),
    )
    expect(api.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Status geändert' }))
  })

  it('zeigt Statushistorie-Zeilen nach Laden', async () => {
    renderPage()
    fireEvent.change(screen.getByPlaceholderText('z. B. F-ABC12345'), { target: { value: 'FZ-2' } })
    expect(await screen.findByText('Tour')).toBeTruthy()
    expect(screen.getAllByText('Unterwegs').length).toBeGreaterThan(0)
    expect(screen.getByText(/100\s*km/)).toBeTruthy()
  })

  it('laedt Wartungsvorhersage und Bußgelder in den Tabs', async () => {
    const user = userEvent.setup()
    api.wartung.mockResolvedValue({
      aktueller_km_stand: 12000,
      tuev_faellig_in_tagen: 40,
      asu_faellig_in_tagen: 20,
      inspektion_faellig_in_tagen: null,
      vorhersagen_nach_km: [
        { terminart: 'Ölwechsel', intervall_km: 15000, faellig_in_km: 3000, faellig_bei_km: 15000, dringend: false },
      ],
    })
    api.listBussgeld.mockResolvedValue([
      { id: 'bg-1', datum: '2026-10-01T00:00:00Z', betrag_eur: 60, status: 'offen', tatbestand: 'Tempo' },
    ])
    renderPage()
    fireEvent.change(screen.getByPlaceholderText('z. B. F-ABC12345'), { target: { value: 'FZ-9' } })
    await user.click(screen.getByRole('tab', { name: 'Wartungsvorhersage' }))
    await waitFor(() => expect(api.wartung).toHaveBeenCalledWith('FZ-9'))
    expect(await screen.findByText('12.000')).toBeTruthy()
    await user.click(screen.getByRole('tab', { name: 'Bußgelder' }))
    await waitFor(() => expect(api.listBussgeld).toHaveBeenCalledWith('FZ-9'))
    fireEvent.change(screen.getByPlaceholderText(/Überladung/i), { target: { value: 'Zu schnell' } })
    fireEvent.change(screen.getByPlaceholderText('395.00'), { target: { value: '80' } })
    fireEvent.click(screen.getByRole('button', { name: 'Bußgeld anlegen' }))
    await waitFor(() =>
      expect(api.createBussgeld).toHaveBeenCalledWith(
        'FZ-9',
        expect.objectContaining({ tatbestand: 'Zu schnell', betrag_eur: 80 }),
      ),
    )
  })

  it('legt Schadensfall im Tab an', async () => {
    const user = userEvent.setup()
    renderPage()
    fireEvent.change(screen.getByPlaceholderText('z. B. F-ABC12345'), { target: { value: 'FZ-10' } })
    await user.click(screen.getByRole('tab', { name: 'Schadensfälle' }))
    expect(await screen.findByText('Neuen Schadensfall anlegen')).toBeTruthy()
    fireEvent.change(screen.getByPlaceholderText('z. B. Autobahn A7, km 123'), { target: { value: 'Hof' } })
    fireEvent.change(screen.getByPlaceholderText('Kurzbeschreibung des Schadensereignisses'), { target: { value: 'Delle' } })
    fireEvent.click(screen.getByRole('button', { name: 'Schadensfall anlegen' }))
    await waitFor(() =>
      expect(api.createSchaden).toHaveBeenCalledWith(
        'FZ-10',
        expect.objectContaining({ ort: 'Hof', beschreibung: 'Delle' }),
      ),
    )
  })

  it('meldet Fehler bei fehlgeschlagenem Statuswechsel', async () => {
    api.changeStatus.mockRejectedValue(new Error('boom'))
    renderPage()
    fireEvent.change(screen.getByPlaceholderText('z. B. F-ABC12345'), { target: { value: 'FZ-3' } })
    await waitFor(() => expect(api.getHistorie).toHaveBeenCalled())
    fireEvent.click(screen.getByRole('button', { name: 'Status wechseln' }))
    await waitFor(() =>
      expect(api.toast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' })),
    )
  })

  it('leitet Leasing-Rueckgabe ein und meldet Fehler', async () => {
    const user = userEvent.setup()
    api.leasing.mockResolvedValue({ rueckgabe_protokoll: { status: 'ok', km: 45000 } })
    renderPage()
    fireEvent.change(screen.getByPlaceholderText('z. B. F-ABC12345'), { target: { value: 'FZ-LR' } })
    await user.click(screen.getByRole('tab', { name: 'Leasing-Rückgabe' }))
    expect(await screen.findByRole('button', { name: 'Leasing-Rückgabe einleiten' })).toBeTruthy()
    fireEvent.change(screen.getByPlaceholderText('z. B. 145000'), { target: { value: '45000' } })
    fireEvent.change(screen.getByPlaceholderText(/leichte Kratzer/i), { target: { value: 'ok' } })
    fireEvent.click(screen.getByRole('button', { name: 'Leasing-Rückgabe einleiten' }))
    await waitFor(() =>
      expect(api.leasing).toHaveBeenCalledWith(
        'FZ-LR',
        expect.objectContaining({ km_stand_bei_rueckgabe: 45000, zustand_bemerkung: 'ok' }),
      ),
    )
    expect(api.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Leasing-Rückgabe eingeleitet' }))
    expect(await screen.findByText(/Rückgabe protokolliert/)).toBeTruthy()

    api.leasing.mockRejectedValueOnce(new Error('lr-fail'))
    fireEvent.click(screen.getByRole('button', { name: 'Leasing-Rückgabe einleiten' }))
    await waitFor(() =>
      expect(api.toast).toHaveBeenCalledWith(expect.objectContaining({ description: 'lr-fail' })),
    )
  })

  it('schliesst Schadensfall ab und markiert Bussgeld als bezahlt', async () => {
    const user = userEvent.setup()
    api.listSchaeden.mockResolvedValue([
      {
        id: 'sch-1',
        datum: '2026-10-01T00:00:00Z',
        ort: 'Hof',
        beschreibung: 'Delle',
        status: 'offen',
        schadenhoehe_eur: 100,
        versicherung_gemeldet: false,
      },
    ])
    api.listBussgeld.mockResolvedValue([
      { id: 'bg-2', datum: '2026-10-02T00:00:00Z', betrag_eur: 40, status: 'offen', tatbestand: 'Parken', ort: 'Ort' },
    ])
    renderPage()
    fireEvent.change(screen.getByPlaceholderText('z. B. F-ABC12345'), { target: { value: 'FZ-PAY' } })
    await user.click(screen.getByRole('tab', { name: 'Schadensfälle' }))
    expect(await screen.findByText('Hof')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Abschließen' }))
    await waitFor(() =>
      expect(updateSchadenMock).toHaveBeenCalledWith(
        'FZ-PAY',
        'sch-1',
        expect.objectContaining({ status: 'abgeschlossen' }),
      ),
    )
    expect(api.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Schadensfall abgeschlossen' }))

    await user.click(screen.getByRole('tab', { name: 'Bußgelder' }))
    expect(await screen.findByText('Parken')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Bezahlt' }))
    await waitFor(() =>
      expect(updateBussgeldMock).toHaveBeenCalledWith(
        'FZ-PAY',
        'bg-2',
        expect.objectContaining({ status: 'bezahlt' }),
      ),
    )
    expect(api.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Als bezahlt markiert' }))
  })

  it('meldet Fehler beim Anlegen von Schaden und Bussgeld', async () => {
    const user = userEvent.setup()
    api.createSchaden.mockRejectedValueOnce(new Error('s-fail'))
    api.createBussgeld.mockRejectedValueOnce(new Error('b-fail'))
    renderPage()
    fireEvent.change(screen.getByPlaceholderText('z. B. F-ABC12345'), { target: { value: 'FZ-ERR' } })
    await user.click(screen.getByRole('tab', { name: 'Schadensfälle' }))
    fireEvent.change(screen.getByPlaceholderText('z. B. Autobahn A7, km 123'), { target: { value: 'Hof' } })
    fireEvent.change(screen.getByPlaceholderText('Kurzbeschreibung des Schadensereignisses'), { target: { value: 'Delle' } })
    fireEvent.click(screen.getByRole('button', { name: 'Schadensfall anlegen' }))
    await waitFor(() =>
      expect(api.toast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' })),
    )

    await user.click(screen.getByRole('tab', { name: 'Bußgelder' }))
    fireEvent.change(screen.getByPlaceholderText(/Überladung/i), { target: { value: 'Parken' } })
    fireEvent.change(screen.getByPlaceholderText('395.00'), { target: { value: '35' } })
    fireEvent.click(screen.getByRole('button', { name: 'Bußgeld anlegen' }))
    await waitFor(() =>
      expect(api.toast).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Fehler', description: expect.stringMatching(/Bußgeld/i) }),
      ),
    )
  })
})
