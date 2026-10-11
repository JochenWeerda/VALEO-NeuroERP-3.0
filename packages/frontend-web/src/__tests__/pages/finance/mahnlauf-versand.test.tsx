import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import MahnlaufPage from '@/pages/finance/mahnlauf'

const mocks = vi.hoisted(() => ({ get: vi.fn(), put: vi.fn(), post: vi.fn(), toast: vi.fn() }))

vi.mock('@/lib/api-client', () => ({ apiClient: { get: mocks.get, put: mocks.put, post: mocks.post } }))
vi.mock('@/hooks/use-toast', () => ({ toast: mocks.toast }))

const OFFEN = {
  id: 'm-1', stufe: 1, datum: '2026-10-01', offen: 1250, gebuehr: 5, zinsen: 3.7, gesamt: 1258.7, frist: '2026-10-15',
  status: 'offen', rechnungsnr: 'RE-1001', partner: 'Hof Janssen', versand_art: null, empfaenger: null, versendet_am: null,
}
const VERSENDET = {
  ...OFFEN, id: 'm-2', rechnungsnr: 'RE-1002', status: 'sent', versand_art: 'email', empfaenger: 'hof@landwirt.example',
  versendet_am: '2026-10-02',
}

function zeichnen(): void {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(<QueryClientProvider client={client}><MahnlaufPage /></QueryClientProvider>)
}

beforeEach(() => {
  vi.clearAllMocks()
  mocks.get.mockImplementation((url: string) =>
    Promise.resolve({ data: { items: url.endsWith('/notices') ? [OFFEN, VERSENDET] : [] } }))
})

// Bis 08.10.2026 setzte "Mahnung senden" nur den Status. Die Liste zeigt jetzt, wie und an
// wen eine Mahnung ging, und bietet den Versand nur fuer unversendete an.
describe('Mahnlauf: erzeugte Mahnungen versenden', () => {
  it('zeigt den Versandweg und bietet den Versand nur fuer offene Mahnungen an', async () => {
    zeichnen()
    expect(await screen.findByText('RE-1001')).toBeInTheDocument()
    expect(screen.getByText('E-Mail an hof@landwirt.example')).toBeInTheDocument()
    expect(screen.getByText('Versendet')).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: /per E-Mail senden/ })).toHaveLength(1)
    expect(screen.getByRole('button', { name: 'Mahnung zu RE-1001 per E-Mail senden' })).toBeEnabled()
  })

  it('sendet per E-Mail ueber den Versandweg des Servers und meldet den Erfolg', async () => {
    mocks.put.mockResolvedValue({ data: { status: 'sent' } })
    zeichnen()
    fireEvent.click(await screen.findByRole('button', { name: 'Mahnung zu RE-1001 per E-Mail senden' }))
    await waitFor(() => expect(mocks.put).toHaveBeenCalledTimes(1))
    expect(mocks.put).toHaveBeenCalledWith('/api/v1/finance/dunning/m-1/send', null, { params: { versand_art: 'email' } })
    await waitFor(() => expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Mahnung versendet' })))
  })

  it('haelt den Postversand fest', async () => {
    mocks.put.mockResolvedValue({ data: { status: 'sent' } })
    zeichnen()
    fireEvent.click(await screen.findByRole('button', { name: 'Postversand der Mahnung zu RE-1001 festhalten' }))
    await waitFor(() => expect(mocks.put).toHaveBeenCalledWith(
      '/api/v1/finance/dunning/m-1/send', null, { params: { versand_art: 'post' } }))
    await waitFor(() => expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Postversand festgehalten' })))
  })

  it('zeigt den Grund, wenn nichts hinausging, und gibt den Knopf wieder frei', async () => {
    mocks.put.mockRejectedValue({ response: { data: { detail: 'Beim Kunden ist keine E-Mail-Adresse hinterlegt' } } })
    zeichnen()
    const knopf = await screen.findByRole('button', { name: 'Mahnung zu RE-1001 per E-Mail senden' })
    fireEvent.click(knopf)
    await waitFor(() => expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({
      title: 'Mahnung nicht versendet', description: 'Beim Kunden ist keine E-Mail-Adresse hinterlegt', variant: 'destructive',
    })))
    await waitFor(() => expect(knopf).toBeEnabled())
  })

  it('sperrt waehrend des Versands gegen den Doppelklick', async () => {
    let fertig: (wert: unknown) => void = () => undefined
    mocks.put.mockReturnValue(new Promise((aufloesen) => { fertig = aufloesen }))
    zeichnen()
    const knopf = await screen.findByRole('button', { name: 'Mahnung zu RE-1001 per E-Mail senden' })
    fireEvent.click(knopf)
    await waitFor(() => expect(knopf).toBeDisabled())
    fireEvent.click(knopf)
    expect(mocks.put).toHaveBeenCalledTimes(1)
    fertig({ data: { status: 'sent' } })
    await waitFor(() => expect(knopf).toBeEnabled())
  })
})
