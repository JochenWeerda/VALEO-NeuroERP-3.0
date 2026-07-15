import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { FeedControllingTrends } from '@/features/feed-advice/FeedControllingTrends'
import type { ControllingSeriesPoint } from '@/lib/api/feed-controlling'

const fetchFeedingGroupsMock = vi.hoisted(() => vi.fn())
const fetchControllingSeriesMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api/rations-lifecycle', () => ({
  fetchFeedingGroups: fetchFeedingGroupsMock,
}))

vi.mock('@/lib/api/feed-controlling', () => ({
  fetchControllingSeries: fetchControllingSeriesMock,
}))

const groups = [
  { id: 'g-1', name: 'Hochleistung', animal_count: 120, feeding_system: 'TMR', active: true },
  { id: 'g-2', name: 'Trockensteher', animal_count: 40, feeding_system: 'TMR', active: true },
]

function point(overrides: Partial<ControllingSeriesPoint>): ControllingSeriesPoint {
  return {
    group_id: 'g-1',
    group_name: 'Hochleistung',
    observation_date: '2026-07-10',
    actual_dmi_kg_cow: 22.5,
    target_dmi_kg_cow: 23,
    actual_cost_eur_cow: 7.8,
    target_cost_eur_cow: 7.5,
    actual_milk_kg_cow: 34,
    actual_ecm_kg_cow: 33.1,
    nitrogen_efficiency_pct: 29.4,
    actual_methane_kg_cow: null,
    target_methane_kg_cow: 0.42,
    methane_estimated: false,
    ...overrides,
  }
}

describe('FeedControllingTrends', () => {
  beforeEach(() => {
    fetchFeedingGroupsMock.mockReset()
    fetchControllingSeriesMock.mockReset()
    fetchFeedingGroupsMock.mockResolvedValue(groups)
  })

  it('rendert Soll-Ist-Trendcharts und Gruppen-Benchmark aus der Tagesreihe', async () => {
    fetchControllingSeriesMock.mockResolvedValue([
      point({ observation_date: '2026-07-10' }),
      point({ observation_date: '2026-07-11', actual_dmi_kg_cow: 21.9 }),
      point({ group_id: 'g-2', group_name: 'Trockensteher', observation_date: '2026-07-10', actual_dmi_kg_cow: 13.2 }),
    ])

    render(<FeedControllingTrends />)

    expect(await screen.findByRole('heading', { name: 'TM-Aufnahme (kg/Kuh)' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Futterkosten (EUR/Kuh/Tag)' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Milch-N-Effizienz (%)' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Methan (kg/Kuh/Tag)' })).toBeInTheDocument()

    // Soll-Linien sind als rezessive Referenz beschriftet
    expect(screen.getAllByText('Soll (aktive Ration)').length).toBeGreaterThanOrEqual(2)

    // Benchmark listet beide Gruppen mit Periodenmittel (TM-Aufnahme)
    const benchmark = screen.getByRole('region', { name: 'Gruppen-Benchmark' })
    expect(benchmark).toHaveTextContent('Hochleistung')
    expect(benchmark).toHaveTextContent('Trockensteher')
    expect(benchmark).toHaveTextContent('13,2 kg/Kuh')

    // Methan-Ist ist ueberall null -> keine Schaetz-Notiz
    expect(screen.queryByTestId('methane-estimated-note')).not.toBeInTheDocument()
  })

  it('kennzeichnet geschaetzte Methanwerte und filtert nach Gruppe', async () => {
    fetchControllingSeriesMock.mockResolvedValue([
      point({ actual_methane_kg_cow: 0.45, methane_estimated: true }),
    ])

    render(<FeedControllingTrends />)

    expect(await screen.findByTestId('methane-estimated-note')).toBeInTheDocument()

    fetchControllingSeriesMock.mockResolvedValue([point({})])
    await userEvent.selectOptions(screen.getByLabelText('Tiergruppe'), 'g-1')

    await waitFor(() => {
      expect(fetchControllingSeriesMock).toHaveBeenLastCalledWith(
        expect.objectContaining({ groupId: 'g-1' }),
      )
    })
  })

  it('zeigt Leerzustand mit Handlungsaufforderung und Fehlerzustand mit erneutem Laden', async () => {
    fetchControllingSeriesMock.mockResolvedValueOnce([])
    render(<FeedControllingTrends />)
    expect(await screen.findByRole('status')).toHaveTextContent('noch keine Tageswerte')

    fetchControllingSeriesMock.mockRejectedValueOnce(new Error('kaputt'))
    await userEvent.click(screen.getByRole('button', { name: '90 Tage' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Trenddaten konnten nicht geladen werden.')

    fetchControllingSeriesMock.mockResolvedValueOnce([point({})])
    await userEvent.click(screen.getByRole('button', { name: 'Erneut laden' }))
    expect(await screen.findByRole('heading', { name: 'TM-Aufnahme (kg/Kuh)' })).toBeInTheDocument()
  })
})
