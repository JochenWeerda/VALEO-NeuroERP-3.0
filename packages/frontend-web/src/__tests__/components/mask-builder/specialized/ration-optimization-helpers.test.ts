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
import type { FeedIngredient, GrundfutterAnalyse, UploadedCompoundFeed } from '@/lib/api/rations-optimization'

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

  it('übernimmt relaxation_policy, policy_profile sowie Fix/Unfix/Remove', () => {
    const withPolicy = applyRationPatch(baseWizard() as never, {
      relaxation_policy: 'relaxed',
      policy_profile: 'herd_a',
      set_feed_min_fm: {},
    })
    expect(withPolicy.relaxationPolicy).toBe('relaxed')
    expect(withPolicy.policyProfile).toBe('herd_a')

    const fixed = applyRationPatch(baseWizard() as never, {
      fix_feed_fm: { f1: 7, bad: Number.NaN, zero: 0 },
      add_feed_ids: ['f2'],
    })
    expect(fixed.feedMinFm?.f1).toBe(7)
    expect(fixed.feedMaxFm.f1).toBe(7)
    expect(fixed.selectedFeedIds.has('f2')).toBe(true)

    const unfixed = applyRationPatch(fixed as never, { unfix_feed_ids: ['f1'] })
    expect(unfixed.feedMinFm?.f1).toBeUndefined()
    expect(unfixed.feedMaxFm.f1).toBeUndefined()

    const removed = applyRationPatch(
      { ...fixed, feedMinFm: { f1: 7, f2: 1 }, feedMaxFm: { f1: 7, f2: 9 }, selectedFeedIds: new Set(['f1', 'f2']) } as never,
      { remove_feed_ids: ['f2'], set_feed_min_fm: { f3: 0, f4: 5 } },
    )
    expect(removed.selectedFeedIds.has('f2')).toBe(false)
    expect(removed.feedMinFm?.f2).toBeUndefined()
    expect(removed.feedMinFm?.f3).toBe(0)
    expect(removed.feedMinFm?.f4).toBe(5)

    const nullProfile = applyRationPatch(baseWizard() as never, { policy_profile: null })
    expect(nullProfile.policyProfile).toBeNull()
  })

  it('behandelt fehlende Milch-EP-Felder als 0', () => {
    expect(
      getMilkEpExcessKg({
        forage_only: {},
        supplemented: { milk_from_protein_kg: 12, milk_from_energy_kg: 10 },
      }),
    ).toEqual({ ist: 0, neu: 2 })
    expect(
      getMilkEpExcessKg({
        forage_only: { milk_from_protein_kg: 5 },
        supplemented: {},
      }),
    ).toEqual({ ist: 5, neu: 0 })
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
    const gfa = {
      id: 'gfa-1',
      tenant_id: 't1',
      bezeichnung: 'Gras',
      trockensubstanz_os: 40,
      me_gfe2023_ts: 10,
      sidp_ts: 80,
      andfom_ts: 40,
      gesamtzucker_ts: 4,
      rohfett_ts: 3,
      calcium_ts: 0.5,
      phosphor_ts: 0.3,
      natrium_ts: 0.1,
    } as GrundfutterAnalyse
    const wd = { ...baseWizard(), compoundFeeds: [doc], customFeeds: [gfa] }
    const dm = buildFeedDmById(base, wd as never)
    expect(dm.get('base-1')).toBe(0.35)
    expect(dm.get('c1')).toBe(0.9)
    expect(dm.get('gfa_gfa-1')).toBe(0.4)
    const lookup = buildFeedLookupMap(base, wd as never)
    expect(lookup.get('c1')?.name).toBe('Kraft')
    expect(lookup.get('gfa_gfa-1')?.name).toBe('Gras')
    expect(buildFeedLookupMap(base, null).size).toBe(1)
  })
})
