import { describe, it, expect } from 'vitest'
import { scaleRationItems, type RationItem } from '@/lib/api/rations-optimization'

/**
 * RATION-WB-20: Die Live-Vorschau skaliert ausschliesslich linear. Sie ist kein
 * Evaluator (Skill §10.2) — hier wird nur geprueft, dass die Arithmetik stimmt
 * und dass fehlende Beitragsfelder nicht still zu 0 werden (Skill §10.3).
 */

const items: RationItem[] = [
  { feed_id: 'maissilage', name: 'Maissilage', kgfm: 22, kgdm: 7.04, unit_cost: 0.05, total_cost: 1.1, me_mj: 71.8, sidp_g: 457.6, cp_g: 528 },
  { feed_id: 'rapsschrot', name: 'Rapsschrot', kgfm: 1.6, kgdm: 1.44, unit_cost: 0.32, total_cost: 0.512, me_mj: 15.84, sidp_g: 295.2, cp_g: 504 },
]

describe('scaleRationItems (RATION-WB-20)', () => {
  it('scales mass, nutrient contributions and cost linearly', () => {
    const out = scaleRationItems(items, { maissilage: 33 })
    const mais = out.find((i) => i.feed_id === 'maissilage')!

    expect(mais.kgfm).toBe(33)
    expect(mais.kgdm).toBeCloseTo(10.56, 6)
    expect(mais.me_mj).toBeCloseTo(107.7, 6)
    expect(mais.sidp_g).toBeCloseTo(686.4, 6)
    expect(mais.total_cost).toBeCloseTo(1.65, 6)
  })

  it('leaves untouched items identical', () => {
    const out = scaleRationItems(items, { maissilage: 33 })
    expect(out.find((i) => i.feed_id === 'rapsschrot')).toEqual(items[1])
  })

  it('scales to zero without producing NaN', () => {
    const out = scaleRationItems(items, { maissilage: 0 })
    const mais = out.find((i) => i.feed_id === 'maissilage')!

    expect(mais.kgdm).toBe(0)
    expect(mais.me_mj).toBe(0)
    expect(mais.total_cost).toBe(0)
  })

  it('keeps missing contribution fields undefined instead of defaulting to 0', () => {
    const sparse: RationItem[] = [
      { feed_id: 'heu', name: 'Heu', kgfm: 2, kgdm: 1.8, unit_cost: 0.2, total_cost: 0.4 },
    ]
    const out = scaleRationItems(sparse, { heu: 4 })

    expect(out[0].kgdm).toBeCloseTo(3.6, 6)
    expect(out[0].me_mj).toBeUndefined()
    expect(out[0].sidp_g).toBeUndefined()
    expect(out[0].cp_g).toBeUndefined()
  })

  it('cannot scale an item whose original amount is zero (no density derivable)', () => {
    const zero: RationItem[] = [
      { feed_id: 'x', name: 'X', kgfm: 0, kgdm: 0, unit_cost: 0, total_cost: 0, me_mj: 0 },
    ]
    const out = scaleRationItems(zero, { x: 5 })

    // Ohne Ausgangsmenge gibt es keine ableitbare Dichte — Position bleibt unveraendert,
    // die autoritative Neuberechnung liefert den echten Wert.
    expect(out[0]).toEqual(zero[0])
  })

  it('ignores overrides for unknown feed ids and invalid numbers', () => {
    expect(scaleRationItems(items, { unbekannt: 5 })).toEqual(items)
    expect(scaleRationItems(items, { maissilage: Number.NaN })).toEqual(items)
    expect(scaleRationItems(items, { maissilage: -3 })).toEqual(items)
  })

  it('returns the same array reference semantics for an empty override set', () => {
    expect(scaleRationItems(items, {})).toEqual(items)
  })
})
