import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import Rationsoptimierung from '@/components/mask-builder/specialized/feed/ration-optimization-surface'
import type { OptimizationResult } from '@/lib/api/rations-optimization'

const api = vi.hoisted(() => ({ feeds: vi.fn(), demo: vi.fn(), optimize: vi.fn(), group: vi.fn(), readiness: vi.fn(), draft: vi.fn(), transition: vi.fn() }))
vi.mock('@/components/mask-builder/specialized/intake/domain-data', () => ({
  useDomainIdentity: () => ({ tenantId: 'test-tenant', actor: 'test-actor' }),
}))

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

describe('Neuberechnung in der Werkbank', () => {
  it('ignoriert ungueltige und unveraenderte Leistungswerte und berechnet gueltige Werte neu', async () => {
    await calculate()
    const field = screen.getByRole('spinbutton', { name: /Leistungsniveau kg ECM/ })
    for (const value of ['0', '-5', '38']) {
      fireEvent.change(field, { target: { value } })
      fireEvent.blur(field)
    }
    expect(api.optimize).toHaveBeenCalledTimes(1)
    fireEvent.change(field, { target: { value: '42' } })
    fireEvent.blur(field)
    await waitFor(() => expect(api.optimize).toHaveBeenCalledTimes(2))
    expect(api.optimize.mock.calls[1][0]).toMatchObject({ milk_kg_day: 42 })
  })
  it('zeigt einen Solverfehler und erlaubt eine erneute Berechnung', async () => {
    await calculate()
    api.optimize.mockRejectedValueOnce(new Error('Solver nicht erreichbar'))
    const field = screen.getByRole('spinbutton', { name: /Leistungsniveau kg ECM/ })
    fireEvent.change(field, { target: { value: '42' } })
    fireEvent.blur(field)
    expect(await screen.findByText('Solver nicht erreichbar')).toBeTruthy()
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Review & Freigabe', exact: true }))
    expect((screen.getByRole('button', { name: 'Zur Pruefung einreichen' }) as HTMLButtonElement).disabled).toBe(true)
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Rations-Workbench', exact: true }))
    const retry = screen.getByRole('spinbutton', { name: /Leistungsniveau kg ECM/ })
    fireEvent.change(retry, { target: { value: '43' } })
    fireEvent.blur(retry)
    await waitFor(() => expect(api.optimize).toHaveBeenCalledTimes(3))
    await waitFor(() => expect(screen.queryByText('Solver nicht erreichbar')).toBeNull())
    expect(api.optimize.mock.calls[2][0]).toMatchObject({ milk_kg_day: 43 })
  })
  it('verhindert die Einreichung vor Blur und verwirft verspaetete Solverantworten', async () => {
    await calculate()
    let resolveOld!: (value: OptimizationResult) => void
    api.optimize.mockImplementationOnce(() => new Promise<OptimizationResult>(resolve => { resolveOld = resolve }))
    const field = screen.getByRole('spinbutton', { name: /Leistungsniveau kg ECM/ })
    fireEvent.change(field, { target: { value: '42' } })
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Review & Freigabe', exact: true }))
    expect((screen.getByRole('button', { name: 'Zur Pruefung einreichen' }) as HTMLButtonElement).disabled).toBe(true)
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Rations-Workbench', exact: true }))
    const next = screen.getByRole('spinbutton', { name: /Leistungsniveau kg ECM/ })
    fireEvent.change(next, { target: { value: '42' } })
    fireEvent.blur(next)
    await waitFor(() => expect(api.optimize).toHaveBeenCalledTimes(2))
    const newer = screen.getByRole('spinbutton', { name: /Leistungsniveau kg ECM/ })
    fireEvent.change(newer, { target: { value: '43' } })
    fireEvent.blur(newer)
    await waitFor(() => expect(api.optimize).toHaveBeenCalledTimes(3))
    await act(async () => { resolveOld({ ...result(), status: 'infeasible' }) })
    fireEvent.click(within(screen.getByRole('navigation')).getByRole('button', { name: 'Review & Freigabe', exact: true }))
    expect((screen.getByRole('button', { name: 'Zur Pruefung einreichen' }) as HTMLButtonElement).disabled).toBe(false)
  })
})



