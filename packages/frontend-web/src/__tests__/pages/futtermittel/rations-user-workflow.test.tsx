import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import Rationsoptimierung from '@/pages/futtermittel/rationsoptimierung'
import type { OptimizationResult } from '@/lib/api/rations-optimization'

const api = vi.hoisted(() => ({ feeds: vi.fn(), demo: vi.fn(), optimize: vi.fn(), group: vi.fn(), readiness: vi.fn(), draft: vi.fn(), transition: vi.fn() }))
vi.mock('@/lib/api/rations-optimization', async importOriginal => ({
  ...await importOriginal<typeof import('@/lib/api/rations-optimization')>(),
  fetchFeeds: api.feeds, optimizeDemo: api.demo, optimizeFromProfile: api.optimize,
  fetchDlgInfo: vi.fn(async () => ({})), fetchFeedingControlLogs: vi.fn(async () => []),
}))
vi.mock('@/lib/api/rations-lifecycle', () => ({
  ensureFeedingGroup: api.group, evaluateFeedReadiness: api.readiness,
  createRationDraft: api.draft, transitionRationVersion: api.transition,
}))

function result(): OptimizationResult {
  return { status: 'optimal', total_cost_eur_day: 5.25,
    ration_items: [{ feed_id: 'mais', name: 'Synthetische Maissilage', kgfm: 20, kgdm: 7, unit_cost: 0.2, total_cost: 4 }],
    nutrient_supply: { dmi_kg: 22, me_mj: 220, sidp_g: 2100, andfom_g: 4000, starch_g: 2500, sugar_g: 900, fat_g: 500, ca_g: 100, p_g: 80, na_g: 40, forage_share_pct: 65 },
    constraint_report: [], warnings: ['Synthetischer Pruefhinweis'],
  }
}
function mount() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity }, mutations: { retry: false } } })
  return render(<QueryClientProvider client={client}><Rationsoptimierung /></QueryClientProvider>)
}
async function demo() {
  mount()
  await waitFor(() => expect(api.feeds).toHaveBeenCalledOnce())
  vi.useFakeTimers()
  fireEvent.click(screen.getByRole('button', { name: 'Demo starten' }))
  await act(async () => { await vi.advanceTimersByTimeAsync(5000) })
  vi.useRealTimers()
  await waitFor(() => expect(api.demo).toHaveBeenCalledOnce())
  await screen.findByText('Synthetische Maissilage')
}
async function calculate() {
  mount()
  await waitFor(() => expect(api.feeds).toHaveBeenCalledOnce())
  fireEvent.click(screen.getByRole('button', { name: 'Neue Ration', exact: true }))
  fireEvent.click(screen.getByRole('button', { name: 'Weiter', exact: true }))
  fireEvent.click(screen.getByRole('button', { name: 'Weiter', exact: true }))
  fireEvent.click(screen.getByRole('button', { name: 'Optimierung starten', exact: true }))
  await waitFor(() => expect(api.optimize).toHaveBeenCalledOnce())
  await screen.findByText('Synthetische Maissilage')
}
beforeEach(() => {
  vi.clearAllMocks()
  localStorage.clear()
  api.feeds.mockResolvedValue([])
  api.demo.mockResolvedValue(result())
  api.optimize.mockResolvedValue(result())
})
afterEach(() => { cleanup(); vi.useRealTimers() })

describe('Rationsberatung aus Sicht des Bearbeiters', () => {
  it('sperrt Ergebnisansichten vor Berechnung und erlaubt Abbruch des Wizards', async () => {
    mount()
    expect((within(screen.getByRole('navigation')).getByRole('button', { name: 'Diagnose', exact: true }) as HTMLButtonElement).disabled).toBe(true)
    expect((within(screen.getByRole('navigation')).getByRole('button', { name: 'Review & Freigabe', exact: true }) as HTMLButtonElement).disabled).toBe(true)
    fireEvent.click(screen.getByRole('button', { name: 'Neue Ration', exact: true }))
    expect(screen.getByText('Leistungsziel')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Abbrechen', exact: true }))
    expect(screen.getByRole('button', { name: 'Demo starten' })).toBeTruthy()
    expect(api.optimize).not.toHaveBeenCalled()
    expect(api.draft).not.toHaveBeenCalled()
  })

  it('zeigt Solverantwort, Diagnose und Review ohne Demo-Geschaeftswirkung', async () => {
    await demo()
    expect(screen.getAllByText('Synthetischer Pruefhinweis').length).toBeGreaterThan(0)
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Diagnose', exact: true }))
    expect(screen.getAllByText(/Tierwohl/).length).toBeGreaterThan(0)
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Review & Freigabe', exact: true }))
    const submit = screen.getByRole('button', { name: 'Zur Pruefung einreichen' }) as HTMLButtonElement
    expect(submit.disabled).toBe(true)
    fireEvent.click(submit)
    expect(api.group).not.toHaveBeenCalled()
    expect(api.draft).not.toHaveBeenCalled()
    expect(api.transition).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Zurücksetzen', exact: true }))
    expect((within(screen.getByRole('navigation')).getByRole('button', { name: 'Diagnose', exact: true }) as HTMLButtonElement).disabled).toBe(true)
  })

  it('reicht eine eigene optimale Beratung ein und zeigt einen Speicherfehler ohne Freigabe', async () => {
    api.group.mockResolvedValue({ id: 'synthetic-group', name: 'Testgruppe', animal_count: 80 })
    api.readiness.mockResolvedValue({ ready: true })
    api.draft.mockRejectedValue(new Error('Synthetischer Speicherfehler'))
    await calculate()
    expect(api.demo).not.toHaveBeenCalled()
    expect(api.optimize.mock.calls[0][0]).toMatchObject({ breed: 'Holstein', milk_kg_day: 38, feeding_type: 'TMR' })
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Review & Freigabe', exact: true }))
    const submit = screen.getByRole('button', { name: 'Zur Pruefung einreichen' }) as HTMLButtonElement
    expect(submit.disabled).toBe(false)
    fireEvent.click(submit)
    await waitFor(() => expect(api.draft).toHaveBeenCalledOnce())
    expect(api.readiness).toHaveBeenCalledWith({ mobile: expect.objectContaining({
      group: { id: 'synthetic-group', name: 'Testgruppe', count: 80 },
      components: [{ feed_id: 'mais', name: 'Synthetische Maissilage', soll_kg: 1600 }],
    }) })
    expect(api.draft).toHaveBeenCalledWith(expect.objectContaining({ group_id: 'synthetic-group', source: 'solver',
      snapshot: expect.objectContaining({ schema_version: 1, optimization_result: result() }),
    }))
    expect(api.transition).not.toHaveBeenCalled()
    expect(await screen.findByRole('alert')).toHaveTextContent('Synthetischer Speicherfehler')
  })

  it('verhindert Einreichung bei nicht loesbarem Solverergebnis', async () => {
    api.optimize.mockResolvedValue({ ...result(), status: 'infeasible' })
    await calculate()
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Review & Freigabe', exact: true }))
    const submit = screen.getByRole('button', { name: 'Zur Pruefung einreichen' }) as HTMLButtonElement
    expect(submit.disabled).toBe(true)
    fireEvent.click(submit)
    expect(api.group).not.toHaveBeenCalled()
    expect(api.draft).not.toHaveBeenCalled()
  })

  it('beginnt nach einer Demo eine eigene Beratung ohne einreichbare alte Ergebnisse', async () => {
    await demo()
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Neue Ration', exact: true }))
    expect((within(screen.getByRole('navigation')).getByRole('button', { name: 'Review & Freigabe', exact: true }) as HTMLButtonElement).disabled).toBe(true)
    fireEvent.click(screen.getByRole('button', { name: 'Weiter', exact: true }))
    fireEvent.click(screen.getByRole('button', { name: 'Weiter', exact: true }))
    fireEvent.click(screen.getByRole('button', { name: 'Optimierung starten', exact: true }))
    await waitFor(() => expect(api.optimize).toHaveBeenCalledOnce())
    await screen.findByText('Synthetische Maissilage')
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Review & Freigabe', exact: true }))
    expect((screen.getByRole('button', { name: 'Zur Pruefung einreichen' }) as HTMLButtonElement).disabled).toBe(false)
    expect(api.draft).not.toHaveBeenCalled()
  })

  it.each([0, -1, 1.5, Number.NaN, Number.POSITIVE_INFINITY])('verwirft ungueltige bestaetigte Tieranzahl %s vor Folgeauftraegen', async count => {
    api.group.mockResolvedValue({ id: 'synthetic-group', name: 'Testgruppe', animal_count: count })
    await calculate()
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Review & Freigabe', exact: true }))
    fireEvent.click(screen.getByRole('button', { name: 'Zur Pruefung einreichen' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('keine gültige Tieranzahl')
    expect(api.readiness).not.toHaveBeenCalled()
    expect(api.draft).not.toHaveBeenCalled()
    expect(api.transition).not.toHaveBeenCalled()
  })

  it('sendet den bestaetigten Versionsbezug nur zur fachlichen Pruefung und zeigt deren Ablehnung', async () => {
    api.group.mockResolvedValue({ id: 'synthetic-group', name: 'Testgruppe', animal_count: 58 })
    api.readiness.mockResolvedValue({ ready: true })
    api.draft.mockResolvedValue({ id: 'synthetic-ration', latest_version_id: 'synthetic-version' })
    api.transition.mockRejectedValue(new Error('Vier-Augen-Pruefung erforderlich'))
    await calculate()
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Review & Freigabe', exact: true }))
    fireEvent.click(screen.getByRole('button', { name: 'Zur Pruefung einreichen' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Vier-Augen-Pruefung erforderlich')
    expect(api.transition).toHaveBeenCalledExactlyOnceWith({ versionId: 'synthetic-version', expectedStatus: 'draft', targetStatus: 'in_review', reason: 'Vom Ersteller zur fachlichen Pruefung eingereicht.' })
  })
})
