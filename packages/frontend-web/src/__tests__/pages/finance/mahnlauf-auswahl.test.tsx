import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import MahnlaufPage from '@/pages/finance/mahnlauf'

const mocks = vi.hoisted(() => ({ get: vi.fn(), put: vi.fn(), post: vi.fn(), toast: vi.fn() }))

vi.mock('@/lib/api-client', () => ({ apiClient: { get: mocks.get, put: mocks.put, post: mocks.post } }))
vi.mock('@/hooks/use-toast', () => ({ toast: mocks.toast }))

const kandidat = (nr: string | null, partner: string, opId: string) => ({
  op_id: opId, rechnungsnr: nr, partner, faelligkeit: '2026-09-01', tage_ueberfaellig: 40, offen: 1250,
  aktuelle_stufe: 0, naechste_stufe: 1, dunning_fee: 5, interest: 3.7, total_amount: 1258.7,
})
const JANSSEN = kandidat('RE-1001', 'Hof Janssen', 'op-1')
const HARMS = kandidat('RE-1002', 'Hof Harms', 'op-2')
const OHNE_NUMMER = kandidat(null, 'Hof Poppinga', 'op-3')

function zeichnen(kandidaten: unknown[]): void {
  mocks.get.mockImplementation((url: string) =>
    Promise.resolve({ data: { items: url.endsWith('/candidates') ? kandidaten : [] } }))
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(<QueryClientProvider client={client}><MahnlaufPage /></QueryClientProvider>)
}

const haken = (nr: string, partner: string) =>
  screen.findByRole('checkbox', { name: `${nr} von ${partner} in diesem Lauf mahnen` })

beforeEach(() => {
  vi.clearAllMocks()
  mocks.post.mockResolvedValue({ data: { ok: true, erzeugt: 1 } })
})

// Bis zum 11.10.2026 gab es zwei Mahnlaeufe: einen mit Versand und ohne Auswahl, einen mit
// Auswahl und ohne Versand. Es gibt jetzt einen; wer einen Posten auslaesst, nimmt den Haken heraus.
describe('Mahnlauf: Posten auslassen', () => {
  it('waehlt jeden Kandidaten vor und startet ohne Abwahl den Gesamtlauf', async () => {
    zeichnen([JANSSEN, HARMS])
    expect(await haken('RE-1001', 'Hof Janssen')).toBeChecked()
    expect(await haken('RE-1002', 'Hof Harms')).toBeChecked()
    fireEvent.click(screen.getByRole('button', { name: 'Mahnlauf ausführen (2)' }))
    await waitFor(() => expect(mocks.post).toHaveBeenCalledWith('/api/v1/finance/mahnlauf/run', {}))
  })

  it('mahnt nach einer Abwahl genau die uebrigen Rechnungen', async () => {
    zeichnen([JANSSEN, HARMS])
    fireEvent.click(await haken('RE-1002', 'Hof Harms'))
    fireEvent.click(screen.getByRole('button', { name: 'Mahnlauf ausführen (1 von 2)' }))
    await waitFor(() => expect(mocks.post).toHaveBeenCalledWith(
      '/api/v1/finance/mahnlauf/run', { rechnungsnrn: ['RE-1001'] }))
    await waitFor(() => expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Mahnlauf abgeschlossen' })))
  })

  it('sendet keinen Bediener — wer mahnt, sagt die Anmeldung', async () => {
    zeichnen([JANSSEN, HARMS])
    fireEvent.click(await haken('RE-1002', 'Hof Harms'))
    fireEvent.click(screen.getByRole('button', { name: /Mahnlauf ausführen/ }))
    await waitFor(() => expect(mocks.post).toHaveBeenCalledTimes(1))
    expect(mocks.post.mock.calls[0][1]).not.toHaveProperty('bediener')
  })

  it('startet nichts, wenn alles abgewaehlt ist', async () => {
    zeichnen([JANSSEN])
    fireEvent.click(await haken('RE-1001', 'Hof Janssen'))
    const knopf = screen.getByRole('button', { name: 'Mahnlauf ausführen (0 von 1)' })
    expect(knopf).toBeDisabled()
    fireEvent.click(knopf)
    expect(mocks.post).not.toHaveBeenCalled()
  })

  it('haelt einen Posten ohne Rechnungsnummer aus der Teilmenge heraus und sagt es', async () => {
    zeichnen([JANSSEN, HARMS, OHNE_NUMMER])
    expect(await screen.findByRole('checkbox', { name: 'Posten von Hof Poppinga in diesem Lauf mahnen' })).toBeDisabled()
    fireEvent.click(await haken('RE-1002', 'Hof Harms'))
    fireEvent.click(screen.getByRole('button', { name: 'Mahnlauf ausführen (2 von 3)' }))
    await waitFor(() => expect(mocks.post).toHaveBeenCalledWith(
      '/api/v1/finance/mahnlauf/run', { rechnungsnrn: ['RE-1001'] }))
    await waitFor(() => expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({
      description: expect.stringContaining('1 Posten ohne Rechnungsnummer nicht enthalten'),
    })))
  })

  it('startet keinen Gesamtlauf, wenn nur ein Posten ohne Rechnungsnummer uebrig ist', async () => {
    zeichnen([JANSSEN, OHNE_NUMMER])
    fireEvent.click(await haken('RE-1001', 'Hof Janssen'))
    fireEvent.click(screen.getByRole('button', { name: 'Mahnlauf ausführen (1 von 2)' }))
    await waitFor(() => expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({
      title: 'Mahnlauf nicht gestartet', variant: 'destructive',
    })))
    expect(mocks.post).not.toHaveBeenCalled()
  })

  it('waehlt nach dem Lauf wieder alles vor', async () => {
    zeichnen([JANSSEN, HARMS])
    fireEvent.click(await haken('RE-1002', 'Hof Harms'))
    fireEvent.click(screen.getByRole('button', { name: 'Mahnlauf ausführen (1 von 2)' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Mahnlauf ausführen (2)' })).toBeInTheDocument())
  })
})

describe('Es gibt einen Mahnlauf', () => {
  const lesen = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

  it('fuehrt jeden Mahnlauf-Weg auf dieselbe Seite', () => {
    const { aliases } = JSON.parse(lesen('../../../app/route-aliases.json')) as { aliases: Array<{ module: string; path: string }> }
    const ziel = (pfad: string) => aliases.filter((e) => e.path === pfad).map((e) => e.module)
    for (const pfad of ['finance/mahnlauf', 'finance/mahnwesen', 'finance/dunning', 'mahnwesen/mahnlauf']) {
      expect(ziel(pfad), pfad).toEqual(['@/pages/finance/mahnlauf'])
    }
    expect(() => lesen('../../../pages/mahnwesen/mahnlauf.tsx')).toThrow()
    expect(lesen('../../../app/routing/route-tree.gen.tsx')).not.toContain('@/pages/mahnwesen/mahnlauf')
  })
})
