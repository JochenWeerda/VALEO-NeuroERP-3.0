import { describe, expect, it } from 'vitest'
import {
  applyRationPatch,
  buildFeedDmById,
  buildFeedLookupMap,
  compoundFeedToDisplayFeed,
  deriveObjectiveStrategy,
  epBalanceWithinGuidance,
  getMilkEpExcessKg,
  limitDisplayToFm,
  limitFmToDisplay,
} from '@/components/mask-builder/specialized/feed/ration-optimization-surface'
import type { FeedIngredient, UploadedCompoundFeed } from '@/lib/api/rations-optimization'

const weights = (partial: Partial<Record<string, number>> = {}) => ({
  cost: 50,
  performance: 50,
  rumen: 50,
  health: 50,
  simplicity: 50,
  ...partial,
})

const baseWizard = () => ({
  group: { id: 'g1', name: 'G', count: 1, bodyMass: 600, lactationDays: 100, lactationNumber: 2, location: 'Stall' },
  milkYield: 30,
  fatPercent: 4,
  proteinPercent: 3.4,
  dmiTarget: 24,
  feedingType: 'tmr' as const,
  mode: 'Kosten minimieren' as const,
  selectedFeedIds: new Set<string>(['f1']),
  customFeeds: [] as never[],
  compoundFeeds: [] as UploadedCompoundFeed[],
  feedMaxFm: { f1: 10 },
  feedMinFm: { f1: 1 },
  fanMode: 'standard' as const,
  fanReference: 0,
  relaxationPolicy: 'strict' as const,
  seasonProfile: null,
  policyProfile: null,
})

const compoundDoc = (overrides: Partial<UploadedCompoundFeed> = {}): UploadedCompoundFeed => ({
  product_name: 'KF-Mix',
  source_filename: 'mix.pdf',
  source_type: 'pdf',
  declared_analysis: {},
  composition: [],
  warnings: [],
  raw_text_preview: '',
  optimizer_feed: {},
  gfe2023_estimate: {
    basis: 'estimate',
    match_coverage_pct: 80,
    me_fan1_mj_kgdm: 11.5,
    sidp_g_kgdm: 90,
    andfom_g_kgdm: 180,
    starch_g_kgdm: 220,
    sugar_g_kgdm: 40,
    fat_g_kgdm: 30,
  },
  ...overrides,
})

describe('ration-optimization helpers (new-code coverage)', () => {
  it('berechnet Milch-EP-Überschuss und Guidance-Schwelle', () => {
    const excess = getMilkEpExcessKg({
      forage_only: { milk_from_energy_kg: 28, milk_from_protein_kg: 31 },
      supplemented: { milk_from_energy_kg: 32, milk_from_protein_kg: 33 },
    })
    expect(excess).toEqual({ ist: 3, neu: 1 })
    expect(epBalanceWithinGuidance(2)).toBe(true)
    expect(epBalanceWithinGuidance(2.1)).toBe(false)
  })

  it('leitet objective_strategy aus Modus und Prioritäten ab', () => {
    expect(deriveObjectiveStrategy('Kosten minimieren', weights({ cost: 80, simplicity: 40, rumen: 10, performance: 10, health: 10 }))).toBe('cost_only')
    expect(deriveObjectiveStrategy('Tiergesundheit', weights())).toBe('balance_only')
    expect(deriveObjectiveStrategy('Leistung absichern', weights({ cost: 40 }))).toBe('balance_only')
    expect(deriveObjectiveStrategy('IOFC maximieren', weights({ cost: 70, rumen: 20, performance: 20, health: 20 }))).toBe('balance_then_cost')
  })

  it('setzt Min/Max-FM-Grenzen und verwirft ungültige Werte', () => {
    const next = applyRationPatch(baseWizard() as never, {
      set_feed_min_fm: { f1: 2, bad: Number.NaN, neg: -1 },
      set_feed_max_fm: { f1: 12, bad: Number.NaN },
    })
    expect(next.feedMinFm?.f1).toBe(2)
    expect(next.feedMinFm?.bad).toBeUndefined()
    expect(next.feedMaxFm.f1).toBe(12)
  })

  it('rechnet FM/TM-Grenzen in beide Richtungen', () => {
    expect(limitFmToDisplay(undefined, 0.4, 'FM')).toBe('')
    expect(limitFmToDisplay(10, 0.4, 'TM')).toBe(4)
    expect(limitFmToDisplay(10, 0.4, 'FM')).toBe(10)
    expect(limitDisplayToFm(4, 0.4, 'TM')).toBe(10)
    expect(limitDisplayToFm(4, 0.4, 'FM')).toBe(4)
    expect(limitDisplayToFm(4, 0, 'TM')).toBe(4)
  })

  it('mappt Compound-Feed und baut DM-/Lookup-Maps', () => {
    const doc = compoundDoc({
      optimizer_feed: { id: 'c1', name: 'Kraft', group: 'KF', dm_frac: 0.9, price: 0.4, me: 12, sidp: 95, ndf: 170, st: 200, zu: 35, xl: 28, ca: 1, p: 2, na: 0.5, min_kg: 0, max_kg: 6 },
    })
    const mapped = compoundFeedToDisplayFeed(doc)
    expect(mapped.id).toBe('c1')
    expect(mapped._compoundId).toBe('c1')
    expect(mapped.dm_frac).toBe(0.9)

    const fallback = compoundFeedToDisplayFeed(compoundDoc())
    expect(fallback.id).toBe('compound_KF-Mix')
    expect(fallback.me_mj_kgdm).toBe(11.5)

    const base: FeedIngredient[] = [{
      id: 'base-1', name: 'Mais', group: 'GF', dm_frac: 0.35, price_eur_kgdm: 0.2,
      me_mj_kgdm: 11, sidp_g_kgdm: 80, andfom_g_kgdm: 400, starch_g_kgdm: 300,
      sugar_g_kgdm: 20, fat_g_kgdm: 25, ca_g_kgdm: 1, p_g_kgdm: 2, na_g_kgdm: 0.3,
      min_kgdm: 0, max_kgdm: 20, active: true,
    }]
    const wd = { ...baseWizard(), compoundFeeds: [doc] }
    const dm = buildFeedDmById(base, wd as never)
    expect(dm.get('base-1')).toBe(0.35)
    expect(dm.get('c1')).toBe(0.9)
    const lookup = buildFeedLookupMap(base, wd as never)
    expect(lookup.get('c1')?.name).toBe('Kraft')
    expect(buildFeedLookupMap(base, null).size).toBe(1)
  })
})
