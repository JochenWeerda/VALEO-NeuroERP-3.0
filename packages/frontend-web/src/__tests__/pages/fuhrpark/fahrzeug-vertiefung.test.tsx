import { fireEvent, render, screen, waitFor } from '@testing-library/react'
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
vi.mock('@/lib/api/fuhrpark', () => ({
  getFahrzeugStatusHistorie: (...args: unknown[]) => api.getHistorie(...args),
  changeFahrzeugStatus: (...args: unknown[]) => api.changeStatus(...args),
  listFahrzeugSchaeden: (...args: unknown[]) => api.listSchaeden(...args),
  createFahrzeugSchaden: (...args: unknown[]) => api.createSchaden(...args),
  updateFahrzeugSchaden: vi.fn(),
  listFahrzeugBussgeld: (...args: unknown[]) => api.listBussgeld(...args),
  createFahrzeugBussgeld: (...args: unknown[]) => api.createBussgeld(...args),
  updateFahrzeugBussgeld: vi.fn(),
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
})
