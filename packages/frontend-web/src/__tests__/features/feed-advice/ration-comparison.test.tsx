import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { RationComparison } from '@/features/feed-advice/RationComparison'

const compareRationVersionsMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api/feeding-ration-editor', async (importOriginal) => ({
  ...(await importOriginal<Record<string, unknown>>()),
  compareRationVersions: compareRationVersionsMock,
}))

const comparison = {
  group_id: 'g-1',
  requirement_profile_id: 'p-1',
  base: { version_id: 'v-1', ration_id: 'r-1', totals: { dm_kg: 13, cost_eur: 3.1, me_mj: 140 } },
  variant: { version_id: 'v-2', ration_id: 'r-1', totals: { dm_kg: 12.2, cost_eur: 2.9, me_mj: 138 } },
  component_diff: [
    { feed_id: 'f-gras', name: 'Grassilage', base_kg_fm: 20, variant_kg_fm: 16, delta_kg_fm: -4, change: 'changed' },
    { feed_id: 'f-mais', name: 'Maissilage', base_kg_fm: 18, variant_kg_fm: null, delta_kg_fm: null, change: 'removed' },
    { feed_id: 'f-soja', name: 'Sojaschrot', base_kg_fm: null, variant_kg_fm: 2, delta_kg_fm: null, change: 'added' },
  ],
  metric_diff: [
    { metric: 'cost_eur', label: 'Kosten', base: 3.1, variant: 2.9, delta: -0.2 },
    { metric: 'me_mj', label: 'Energie (ME)', base: 140, variant: 138, delta: -2 },
  ],
  base_findings: [{ code: 'energy_deficit', severity: 'high', metric: 'me_mj', actual: 140, target: 210, message: 'Basis: Energie-Unterdeckung.' }],
  variant_findings: [],
}

describe('RationComparison', () => {
  beforeEach(() => {
    compareRationVersionsMock.mockReset()
    compareRationVersionsMock.mockResolvedValue(comparison)
  })

  it('stellt Komponenten-Diff mit hinzugefuegt/entfernt und Deltas dar (nie 0 fuer unbekannt)', async () => {
    render(<RationComparison baseVersionId="v-1" variantVersionId="v-2" />)

    expect(await screen.findByText('Grassilage')).toBeInTheDocument()
    const removedRow = screen.getByText('Maissilage').closest('tr') as HTMLElement
    expect(removedRow).toHaveTextContent('Entfernt')
    expect(removedRow).not.toHaveTextContent('0,0')
    const addedRow = screen.getByText('Sojaschrot').closest('tr') as HTMLElement
    expect(addedRow).toHaveTextContent('Neu')

    expect(screen.getByText(/Basis: Energie-Unterdeckung/)).toBeInTheDocument()
    expect(screen.getByText(/Keine Befunde/)).toBeInTheDocument()
    // Kennzahlen-Diff mit Delta
    expect(screen.getByTestId('metric-diff')).toHaveTextContent('Kosten')
  })

  it('zeigt Fehler handlungsorientiert', async () => {
    compareRationVersionsMock.mockRejectedValueOnce(new Error('409'))
    render(<RationComparison baseVersionId="v-1" variantVersionId="v-x" />)
    expect(await screen.findByRole('alert')).toHaveTextContent(/Vergleich konnte nicht geladen werden/)
  })
})
