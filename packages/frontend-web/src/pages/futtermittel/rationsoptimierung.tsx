/**
 * Rationsoptimierung — KLARAGRI Design
 *
 * Design: nutriopt-ai (Google AI Studio) — adaptiert für VALEO NeuroERP
 * Backend: /api/v1/agrar/rations-optimization (GfE-2023, HiGHS-Solver)
 *
 * Views: dashboard → wizard → workbench → review
 */

import { useState, useEffect, useMemo, useRef, useCallback } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  ArrowRight,
  ArrowLeft,
  Calculator,
  Check,
  ChevronRight,
  FileText,
  Filter,
  HelpCircle,
  Loader2,
  Plus,
  RotateCcw,
  Search,
  Sparkles,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  AlertCircle,
  Send,
  Copy,
  Play,
  X as XIcon,
  ChevronLeft,
  ChevronRight as ChevronRightIcon,
  Zap,
  Database,
  RefreshCw,
  FlaskConical,
} from 'lucide-react'
import {
  fetchFeeds,
  optimizeFromProfile,
  optimizeDemo,
  uploadCompoundFeedDocument,
  getRationsApiErrorMessage,
  fetchDlgInfo,
  triggerDlgRefresh,
  fetchGrundfutterAnalysen,
  gfaToDisplayFeed,
  FAN_DEFAULTS,
  FAN_REFERENCE_PRESETS,
  defaultFeedingSystemConfig,
  type CowProfile,
  type FeedIngredient,
  type OptimizationResult,
  type DlgIndicators,
  type GrundfutterAnalyse,
  type UploadedCompoundFeed,
  type FeedingMode,
  type PastureRiskPayload,
  type FanMode,
  type RelaxationPolicy,
  type SeasonProfile,
  type PolicyProfile,
  type FanCalibrationPayload,
  type ConstraintStatusItem,
  type PenaltySummary,
  type ConcentrateCallUp,
  type RationBlocks,
  type MixingProtocol,
  type RationAdjustmentApplyPatch,
  type RationAdjustmentSuggestion,
  type ObjectiveStrategy,
} from '@/lib/api/rations-optimization'

// ---------------------------------------------------------------------------
// Design Tokens (nutriopt-ai Palette)
// ---------------------------------------------------------------------------
const C = {
  dark: '#1B3022',
  accent: '#88B04B',
  bg: '#F0F2F5',
  card: '#FFFFFF',
  border: '#D1D5DB',
  muted: '#6B7280',
  aiBg: '#E0F2FE',
  aiBorder: '#BAE6FD',
  aiText: '#0369A1',
  deltaBg: '#FFFBEB',
  deltaBorder: '#FEF3C7',
  deltaText: '#92400E',
  activeBg: '#F0F7ED',
  error: '#DC2626',
  success: '#059669',
  warn: '#D97706',
} as const

/** Beratungs-Orientierung: max. Mehr-Menge „Milch aus Protein“ vs. „Milch aus Energie“ (kg Milch ≈ l). */
const MILK_EP_BALANCE_MAX_PROTEIN_EXCESS_KG = 2

type ForagePerformancePayload = NonNullable<OptimizationResult['forage_performance']>

function getMilkEpExcessKg(fp: ForagePerformancePayload): { ist: number; neu: number } {
  const fo = fp.forage_only
  const sup = fp.supplemented
  const eIst = Number(fo.milk_from_energy_kg ?? 0)
  const pIst = Number(fo.milk_from_protein_kg ?? 0)
  const eNeu = Number(sup.milk_from_energy_kg ?? 0)
  const pNeu = Number(sup.milk_from_protein_kg ?? 0)
  return {
    ist: Math.max(0, pIst - eIst),
    neu: Math.max(0, pNeu - eNeu),
  }
}

function epBalanceWithinGuidance(excessKg: number): boolean {
  return excessKg <= MILK_EP_BALANCE_MAX_PROTEIN_EXCESS_KG + 1e-6
}

// ---------------------------------------------------------------------------
// Static Data
// ---------------------------------------------------------------------------

type CowGroup = {
  id: string
  name: string
  count: number
  bodyMass: number
  lactationDays: number
  lactationNumber: number
  location: string
}

const GROUPS: CowGroup[] = [
  { id: 'g1', name: 'Hochleistung Nordstall', count: 58, bodyMass: 670, lactationDays: 110, lactationNumber: 2.4, location: 'Nordstall' },
  { id: 'g2', name: 'Frischmelker', count: 22, bodyMass: 650, lactationDays: 20, lactationNumber: 2.1, location: 'Südabteil' },
  { id: 'g3', name: 'Trockensteher', count: 15, bodyMass: 720, lactationDays: 0, lactationNumber: 3.2, location: 'Außenbereich' },
]

type OptMode = 'Kosten minimieren' | 'IOFC maximieren' | 'Leistung absichern' | 'Tiergesundheit'

/** Relative Gewichtung der Zielkriterien (0–100), UI / spätere Solver-Anbindung */
type PriorityWeights = {
  cost: number
  performance: number
  rumen: number
  health: number
  simplicity: number
}

const DEFAULT_PRIORITY_WEIGHTS: PriorityWeights = {
  cost: 80,
  performance: 60,
  rumen: 70,
  health: 65,
  simplicity: 40,
}

const PRIORITY_SLIDER_ROWS: { key: keyof PriorityWeights; label: string }[] = [
  { key: 'cost', label: 'Kosten (Wirtschaftlichkeit)' },
  { key: 'performance', label: 'Leistung (Milch kg)' },
  { key: 'rumen', label: 'Pansensicherheit (Struktur)' },
  { key: 'health', label: 'Tiergesundheit (Proxys)' },
  { key: 'simplicity', label: 'Einfachheit (Management)' },
]

/** Schritt 3: Grenzwerte (TM-Band wirkt im Solver; übrige Felder werden dokumentiert / Folge-LP). */
type WizardHardBounds = {
  dmiMinKg: number
  dmiMaxKg: number
  meMinMjPerKgDm: number
  starchMaxPctTm: number
  andfomMinPctTm: number
  andfomGfMinPctTm: number
}

type WizardSoftGoals = {
  minimizeSoya: boolean
  minimizeDeviationFromBaseline: boolean
  maximizeNEfficiencyRmd: boolean
  preferHomegrown: boolean
}

const DEFAULT_WIZARD_HARD_BOUNDS: WizardHardBounds = {
  dmiMinKg: 23.5,
  dmiMaxKg: 25.5,
  meMinMjPerKgDm: 11.3,
  starchMaxPctTm: 26,
  andfomMinPctTm: 30,
  andfomGfMinPctTm: 20,
}

const DEFAULT_WIZARD_SOFT_GOALS: WizardSoftGoals = {
  minimizeSoya: true,
  minimizeDeviationFromBaseline: true,
  maximizeNEfficiencyRmd: false,
  preferHomegrown: false,
}

/** Prioritäten-Schieberegler → Solver-Stufe (`objective_strategy`). */
function deriveObjectiveStrategy(mode: OptMode, w: PriorityWeights): ObjectiveStrategy {
  const balanceSignal = w.rumen + w.performance + w.health
  const costSignal = w.cost + w.simplicity * 0.5
  if (mode === 'Kosten minimieren' && w.cost >= 72 && costSignal > balanceSignal + 25) {
    return 'cost_only'
  }
  if (
    mode === 'Tiergesundheit'
    || mode === 'Leistung absichern'
    || (balanceSignal > costSignal + 35 && w.cost < 62)
  ) {
    return 'balance_only'
  }
  return 'balance_then_cost'
}

type WizardData = {
  group: CowGroup
  milkYield: number
  fatPercent: number
  proteinPercent: number
  dmiTarget: number
  feedingType: FeedingMode
  mode: OptMode
  selectedFeedIds: Set<string>
  customFeeds: GrundfutterAnalyse[]
  compoundFeeds: UploadedCompoundFeed[]
  feedMaxFm: Record<string, number>  // feed_id → max kg FM/Tag (0 = unbegrenzt)
  /** Min kg FM/Tag je Feed; fehlend/leer = keine Untergrenze */
  feedMinFm?: Record<string, number>
  // FAN-MODE-V1 (GfE 2023): Bewertungsmodus + Solver-Relaxation (Spec §4/§6/§8)
  fanMode: FanMode
  fanReference: number              // nur relevant bei fanMode === 'reference'
  relaxationPolicy: RelaxationPolicy
  seasonProfile: SeasonProfile | null
  // DLG 01|2025 Tab. 13-15: optionale Leistungs-/Physiologiestufe.
  // null = Backend-Auto-Mapping aus Fuetterungstyp/Saison.
  policyProfile: PolicyProfile | null
  /** Schritt 3: Prioritäts-Gewichte (0–100), Schieberegler */
  priorityWeights?: PriorityWeights
  wizardHardBounds?: WizardHardBounds
  wizardSoftGoals?: WizardSoftGoals
}

function applyRationPatch(wd: WizardData, patch: RationAdjustmentApplyPatch): WizardData {
  const next: WizardData = { ...wd }
  if (patch.relaxation_policy != null) next.relaxationPolicy = patch.relaxation_policy
  if (patch.policy_profile !== undefined) next.policyProfile = patch.policy_profile
  if (patch.add_feed_ids?.length) {
    const s = new Set(next.selectedFeedIds)
    for (const id of patch.add_feed_ids) s.add(id)
    next.selectedFeedIds = s
  }
  return next
}

function patchHasSolverKeys(patch: RationAdjustmentApplyPatch): boolean {
  return (
    patch.relaxation_policy != null
    || patch.policy_profile !== undefined
    || (patch.add_feed_ids?.length ?? 0) > 0
  )
}

// localStorage-Key für persistierte Feed-Auswahl
const LS_FEED_SELECTION = 'rations_feed_selection_v1'

interface PersistedFeedSelection {
  selectedFeedIds: string[]
  customFeedIds: string[]  // GFA-ids (müssen beim Laden neu abgefragt werden)
  feedMaxFm: Record<string, number>
  feedMinFm: Record<string, number>
  savedAt: string
}

const QUICK_ACTIONS = [
  { label: 'Neue Ration erstellen', intent: 'wizard' },
  { label: 'Kosten senken', intent: 'wizard' },
  { label: 'Mehr Milchleistung', intent: 'wizard' },
  { label: 'Frischmelker', intent: 'wizard' },
  { label: 'Trockensteher', intent: 'wizard' },
  { label: 'Azidose-Risiko prüfen', intent: 'wizard' },
]

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(' ')
}

function fmt(v: number | null | undefined, d = 2) {
  if (v == null || isNaN(v as number)) return '–'
  return (v as number).toLocaleString('de-DE', { minimumFractionDigits: d, maximumFractionDigits: d })
}

function card(extra = '') {
  return `bg-white border border-[${C.border}] rounded-[6px] p-3 shadow-[0_1px_3px_rgba(0,0,0,0.05)] ${extra}`
}

function compoundFeedToDisplayFeed(doc: UploadedCompoundFeed): FeedIngredient & {
  _isCustom: boolean
  _compoundId: string
  _docName: string
} {
  const optimizerFeed = doc.optimizer_feed as Record<string, unknown>
  return {
    id: String(optimizerFeed.id ?? `compound_${doc.product_name}`),
    name: String(optimizerFeed.name ?? doc.product_name),
    group: String(optimizerFeed.group ?? 'Kraftfutter/Betrieb'),
    dm_frac: Number(optimizerFeed.dm_frac ?? 0.88),
    price_eur_kgdm: Number(optimizerFeed.price ?? 0.38),
    me_mj_kgdm: Number(optimizerFeed.me ?? doc.gfe2023_estimate.me_fan1_mj_kgdm ?? 0),
    sidp_g_kgdm: Number(optimizerFeed.sidp ?? doc.gfe2023_estimate.sidp_g_kgdm ?? 0),
    andfom_g_kgdm: Number(optimizerFeed.ndf ?? doc.gfe2023_estimate.andfom_g_kgdm ?? 0),
    starch_g_kgdm: Number(optimizerFeed.st ?? doc.gfe2023_estimate.starch_g_kgdm ?? 0),
    sugar_g_kgdm: Number(optimizerFeed.zu ?? doc.gfe2023_estimate.sugar_g_kgdm ?? 0),
    fat_g_kgdm: Number(optimizerFeed.xl ?? doc.gfe2023_estimate.fat_g_kgdm ?? 0),
    ca_g_kgdm: Number(optimizerFeed.ca ?? 0),
    p_g_kgdm: Number(optimizerFeed.p ?? 0),
    na_g_kgdm: Number(optimizerFeed.na ?? 0),
    min_kgdm: Number(optimizerFeed.min_kg ?? 0),
    max_kgdm: Number(optimizerFeed.max_kg ?? 8),
    active: true,
    _isCustom: true,
    _compoundId: String(optimizerFeed.id ?? `compound_${doc.product_name}`),
    _docName: doc.source_filename,
  }
}

function buildFeedDmById(baseFeeds: FeedIngredient[], wd: WizardData): Map<string, number> {
  const m = new Map<string, number>()
  for (const f of baseFeeds) m.set(f.id, f.dm_frac)
  for (const gfa of wd.customFeeds ?? []) {
    const d = gfaToDisplayFeed(gfa)
    m.set(d.id, d.dm_frac)
  }
  for (const doc of wd.compoundFeeds ?? []) {
    const d = compoundFeedToDisplayFeed(doc)
    m.set(d.id, d.dm_frac)
  }
  return m
}

/** DLG + Betriebsanalysen + Lieferschein-Rezepturen: gleiche Keys wie `ration_items[].feed_id` für ME/sidP-Spalten. */
function buildFeedLookupMap(baseFeeds: FeedIngredient[], wd: WizardData | null): Map<string, FeedIngredient> {
  const m = new Map<string, FeedIngredient>()
  for (const f of baseFeeds) m.set(f.id, f)
  if (!wd) return m
  for (const gfa of wd.customFeeds ?? []) {
    const d = gfaToDisplayFeed(gfa)
    m.set(d.id, d)
  }
  for (const doc of wd.compoundFeeds ?? []) {
    const d = compoundFeedToDisplayFeed(doc)
    m.set(d.id, d)
  }
  return m
}

type AmpelState = 'ok' | 'warn' | 'error'

function ampelDot(state: AmpelState) {
  const col = state === 'ok' ? C.success : state === 'warn' ? C.warn : C.error
  return <span className="inline-block h-3 w-3 rounded-full" style={{ backgroundColor: col }} />
}

function RationBlocksPanel({
  blocks,
  compact = false,
}: {
  blocks: RationBlocks | null | undefined
  compact?: boolean
}) {
  if (!blocks) return null
  const fs = blocks.feeding_system
  const blk = (label: string, b: RationBlocks['tmr_block']) => (
    <div className="rounded-lg border px-3 py-2" style={{ borderColor: C.border }}>
      <div className="text-[10px] uppercase font-bold" style={{ color: C.muted }}>{label}</div>
      <div className="text-sm font-bold" style={{ color: C.dark }}>{fmt(b.dmi_kg, 2)} kg TM</div>
      <div className="text-[10px]" style={{ color: C.muted }}>{fmt(b.dmi_share_pct, 0)} % der Ration</div>
    </div>
  )

  return (
    <div className={card(compact ? 'space-y-3' : 'space-y-4')}>
      <div>
        <p className="text-[11px] uppercase font-bold tracking-[0.5px]" style={{ color: C.muted }}>
          Fütterungssystem & Blöcke
        </p>
        <p className="text-sm font-semibold" style={{ color: C.dark }}>
          {fs.system ?? '–'} · {fs.concentrate_distribution ?? '–'}
        </p>
        {fs.auto_promoted_from_tmr && (
          <p className="text-[11px] mt-1 px-2 py-1 rounded border" style={{ background: '#FFFBEB', borderColor: C.deltaBorder, color: C.deltaText }}>
            Automatisch von TMR auf PMR+Weide angehoben: Weide liegt in der Lösung, wird nicht im Mischwagen geführt.
          </p>
        )}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
        {blk('TMR / Mischwagen', blocks.tmr_block)}
        {blk('Weide', blocks.pasture_block)}
        {blk('Kraftfutter gestaffelt', blocks.concentrate_staged_block)}
      </div>
    </div>
  )
}

function ForagePerformancePanel({
  result,
  compact = false,
}: {
  result: OptimizationResult | null
  compact?: boolean
}) {
  const performance = result?.forage_performance
  if (!performance) return null

  const epEx = getMilkEpExcessKg(performance)
  const epIstOk = epBalanceWithinGuidance(epEx.ist)
  const epNeuOk = epBalanceWithinGuidance(epEx.neu)

  const rows = [
    {
      label: 'Milch aus Energie Grundfutter',
      ist: `${fmt(performance.forage_only.milk_from_energy_kg, 1)} kg`,
      soll: `${fmt(performance.target_milk_kg, 1)} kg`,
      neu: `${fmt(performance.supplemented.milk_from_energy_kg, 1)} kg`,
    },
    {
      label: 'Milch aus Protein Grundfutter',
      ist: `${fmt(performance.forage_only.milk_from_protein_kg, 1)} kg`,
      soll: `${fmt(performance.target_milk_kg, 1)} kg`,
      neu: `${fmt(performance.supplemented.milk_from_protein_kg, 1)} kg`,
    },
    {
      label: 'Limitierende Milchmenge',
      ist: `${fmt(performance.forage_only.limiting_milk_kg, 1)} kg`,
      soll: `${fmt(performance.target_milk_kg, 1)} kg`,
      neu: `${fmt(performance.supplemented.limiting_milk_kg, 1)} kg`,
    },
  ]

  return (
    <div className={card(compact ? 'space-y-3' : 'space-y-4')}>
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-[11px] uppercase font-bold tracking-[0.5px]" style={{ color: C.muted }}>
            Grundfutterleistung {performance.feeding_type}
          </p>
          <p className="text-sm font-semibold" style={{ color: C.dark }}>
            IST = nur Grobfutter; Ziel (Profil) = gewünschte Leistung; NEU = nach Modell-Kraftfutter und Verdrängung
          </p>
        </div>
        <div className="text-right text-xs" style={{ color: C.muted }}>
          <div>Kraftfutter: {fmt(performance.supplemented.concentrate_dmi_kg, 2)} kg TM</div>
          <div>Verdrängung: {fmt(performance.supplemented.forage_displacement_dmi_kg, 2)} kg TM</div>
        </div>
      </div>

      {!compact && (
        <div className="rounded-lg border px-3 py-2.5 text-[11px] leading-relaxed space-y-1.5" style={{ borderColor: C.border, background: '#F8FAFC', color: C.muted }}>
          <p>
            <span className="font-semibold" style={{ color: C.dark }}>Priorität:</span>{' '}
            Zuerst fachliche und tiergesundheitliche Grenzen (GfE/DLG, Aufnahme, Struktur). Wirtschaftliche Optimierung nur innerhalb dieser Grenzen — niedrigere Kosten ersetzen keine sichere Fütterung.
          </p>
          <p>
            <span className="font-semibold" style={{ color: C.dark }}>Ausgewogene Ration:</span>{' '}
            „Milch aus Energie“ und „Milch aus Protein“ sollten ähnlich liegen. Orientierung: Mehrleistung auf Protein-Seite höchstens{' '}
            <span className="font-mono font-semibold" style={{ color: C.dark }}>{MILK_EP_BALANCE_MAX_PROTEIN_EXCESS_KG} kg</span>{' '}
            (≈{' '}
            <span className="font-mono font-semibold" style={{ color: C.dark }}>{MILK_EP_BALANCE_MAX_PROTEIN_EXCESS_KG} l</span>
            ) über der Energie-Seite; darüber bitte bewerten.
          </p>
        </div>
      )}

      {compact && (
        <p className="text-[10px] leading-snug" style={{ color: C.muted }}>
          E/P-Abgleich: Überhang Protein vs. Energie max. {MILK_EP_BALANCE_MAX_PROTEIN_EXCESS_KG} kg (≈ l). Ziel-Spalte = Profil-Leistung.
        </p>
      )}

      <div className="grid gap-2">
        <div className="grid grid-cols-[1.7fr_0.8fr_0.8fr_0.8fr] gap-2 px-1 text-[10px] font-bold uppercase tracking-wide" style={{ color: C.muted }}>
          <span>Kennzahl</span>
          <span className="text-right">IST</span>
          <span className="text-right">Ziel (Profil)</span>
          <span className="text-right">NEU</span>
        </div>
        {rows.map((row) => (
          <div key={row.label} className="grid grid-cols-[1.7fr_0.8fr_0.8fr_0.8fr] gap-2 rounded-lg border px-3 py-2 text-xs" style={{ borderColor: C.border, background: '#F9FAFB' }}>
            <div className="font-semibold" style={{ color: C.dark }}>{row.label}</div>
            <div className="text-right" style={{ color: C.muted }}>{row.ist}</div>
            <div className="text-right" style={{ color: C.deltaText }}>{row.soll}</div>
            <div className="text-right font-bold" style={{ color: C.accent }}>{row.neu}</div>
          </div>
        ))}
        <div
          className="grid grid-cols-[1.7fr_0.8fr_0.8fr_0.8fr] gap-2 rounded-lg border px-3 py-2 text-xs"
          style={{
            borderColor: epIstOk && epNeuOk ? C.border : C.deltaBorder,
            background: epIstOk && epNeuOk ? '#F0FDF4' : C.deltaBg,
          }}
        >
          <div className="font-semibold" style={{ color: C.dark }}>
            Mehr „Milch aus Protein“ vs. „Milch aus Energie“
            <span className="block font-normal text-[10px] font-mono mt-0.5" style={{ color: C.muted }}>
              Orientierung ≤ {MILK_EP_BALANCE_MAX_PROTEIN_EXCESS_KG} kg (≈ l)
            </span>
          </div>
          <div className="text-right font-mono" style={{ color: epIstOk ? C.success : C.deltaText }}>
            {fmt(epEx.ist, 1)} kg{!epIstOk ? ' ⚠' : ''}
          </div>
          <div className="text-right font-mono" style={{ color: C.muted }}>≤ {MILK_EP_BALANCE_MAX_PROTEIN_EXCESS_KG}</div>
          <div className="text-right font-bold font-mono" style={{ color: epNeuOk ? C.accent : C.deltaText }}>
            {fmt(epEx.neu, 1)} kg{!epNeuOk ? ' ⚠' : ''}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        <div className="rounded-lg border px-3 py-2" style={{ borderColor: C.border }}>
          <div style={{ color: C.muted }}>Grundfutter TM</div>
          <div className="font-bold" style={{ color: C.dark }}>{fmt(performance.forage_only.forage_dmi_kg, 2)} kg</div>
        </div>
        <div className="rounded-lg border px-3 py-2" style={{ borderColor: C.border }}>
          <div style={{ color: C.muted }}>Gesamt-TM nach Ergänzung</div>
          <div className="font-bold" style={{ color: C.dark }}>{fmt(performance.supplemented.total_dmi_kg, 2)} kg</div>
        </div>
        <div className="rounded-lg border px-3 py-2" style={{ borderColor: C.border }}>
          <div style={{ color: C.muted }}>Verdrängungsfaktor</div>
          <div className="font-bold" style={{ color: C.dark }}>{fmt(performance.supplemented.forage_displacement_factor, 2)}</div>
        </div>
      </div>
    </div>
  )
}

function RationWarningAdjustmentsPanel({
  result,
  wizardData,
  isOptimizing,
  onApplySuggestion,
  onGoWizard,
  onReoptimizeSame,
}: {
  result: OptimizationResult | null
  wizardData: WizardData | null
  isOptimizing: boolean
  onApplySuggestion: (patch: RationAdjustmentApplyPatch) => void
  onGoWizard: () => void
  onReoptimizeSame: () => void
}) {
  if (!result) return null
  const warn = result.warnings ?? []
  const raw = result.ration_adjustment_suggestions
  const suggestions: RationAdjustmentSuggestion[] =
    raw && raw.length > 0
      ? raw
      : warn.length > 0
        ? [
            {
              id: 'fallback_wizard',
              title: 'Eigene Anpassung im Assistenten',
              detail:
                'Backend liefert noch keine strukturierten Vorschläge: bitte Futtermittel, Grenzen und Relaxation im Assistenten prüfen und erneut optimieren.',
              apply_patch: {},
            },
          ]
        : []

  if (warn.length === 0 && suggestions.length === 0) return null

  return (
    <div
      className="p-3 rounded-lg border text-[12px] space-y-3"
      style={{ background: C.deltaBg, borderColor: C.deltaBorder, color: C.deltaText }}
    >
      <div className="text-[11px] font-bold uppercase tracking-wider">Hinweise &amp; Rationsanpassung</div>
      <p className="text-[10px] leading-snug opacity-90">
        Vorschlag übernehmen wendet den Patch an und startet die Optimierung erneut. Eigene Anpassung öffnet den Assistenten.
        {wizardData ? ' Ohne Änderung erneut rechnen ist nur sinnvoll nach manuellen Schritten.' : ' Ohne Assistenten-Daten (z. B. reine Demo) zuerst „Neue Ration“ oder Demo mit Profil nutzen.'}
      </p>
      {warn.length > 0 && (
        <ul className="space-y-1">
          {warn.map((w, i) => (
            <li key={i} className="flex items-start gap-1.5">
              <AlertTriangle size={12} className="mt-0.5 flex-shrink-0" />
              <span>{w}</span>
            </li>
          ))}
        </ul>
      )}
      {suggestions.length > 0 && (
        <div className="space-y-2 border-t pt-2" style={{ borderColor: C.deltaBorder }}>
          <div className="text-[10px] font-bold uppercase" style={{ color: C.muted }}>
            Vorschläge zur Anpassung
          </div>
          {suggestions.map((s) => {
            const hasPatch = patchHasSolverKeys(s.apply_patch)
            return (
              <div
                key={s.id}
                className="rounded-md border p-2 space-y-2"
                style={{ borderColor: C.deltaBorder, background: 'rgba(255,255,255,0.65)' }}
              >
                <div className="font-semibold" style={{ color: C.dark }}>
                  {s.title}
                </div>
                <div className="text-[11px] leading-snug" style={{ color: '#374151' }}>
                  {s.detail}
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    disabled={isOptimizing}
                    onClick={() => {
                      if (!wizardData) {
                        onGoWizard()
                        return
                      }
                      if (hasPatch) onApplySuggestion(s.apply_patch)
                      else onGoWizard()
                    }}
                    className="px-3 py-1.5 rounded text-xs font-bold text-white disabled:opacity-40"
                    style={{ background: C.accent }}
                  >
                    {!wizardData
                      ? 'Zum Assistenten'
                      : hasPatch
                        ? 'Vorschlag übernehmen & neu optimieren'
                        : 'Zum Assistenten (manuell anpassen)'}
                  </button>
                  <button
                    type="button"
                    disabled={isOptimizing}
                    onClick={onGoWizard}
                    className="px-3 py-1.5 rounded text-xs font-semibold border transition-colors hover:bg-white/80"
                    style={{ borderColor: C.border, color: C.dark }}
                  >
                    Eigene Anpassung
                  </button>
                  {wizardData && (
                    <button
                      type="button"
                      disabled={isOptimizing}
                      onClick={onReoptimizeSame}
                      className="px-3 py-1.5 rounded text-xs font-semibold border transition-colors hover:bg-white/80"
                      style={{ borderColor: C.border, color: C.dark }}
                    >
                      Nur erneut optimieren
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function PastureRiskPanel({
  risk,
  compact = false,
}: {
  risk: PastureRiskPayload | null | undefined
  compact?: boolean
}) {
  if (!risk?.active) return null

  const kMg = risk.pasture_k_mg_ratio
  const kMgState: AmpelState =
    kMg == null ? 'warn' : kMg <= 4 ? 'ok' : kMg <= 6 ? 'warn' : 'error'
  const cp = risk.pasture_cp_g_kgdm
  const cpState: AmpelState =
    cp == null ? 'warn' : cp <= 200 ? 'ok' : cp <= 230 ? 'warn' : 'error'
  const mgSup = risk.mg_supplement_dmi_kg
  const mgSupState: AmpelState = mgSup >= 0.05 ? 'ok' : mgSup > 0 ? 'warn' : 'error'

  return (
    <div className={card(compact ? 'space-y-3' : 'space-y-4')}>
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-[11px] uppercase font-bold tracking-[0.5px]" style={{ color: C.muted }}>
            Weide-Risiko &amp; Milch aus Weide/Grassilage
          </p>
          <p className="text-sm font-semibold" style={{ color: C.dark }}>
            {risk.feeding_type} · DLG-Merkblatt 417/443 · GfE-Workshop 2023
          </p>
        </div>
        <div className="text-right text-xs" style={{ color: C.muted }}>
          <div>Weide TM: {fmt(risk.pasture_dmi_kg, 2)} kg</div>
          <div>Grassilage TM: {fmt(risk.grass_silage_dmi_kg, 2)} kg</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        <div className="rounded-lg border px-3 py-2 flex items-start gap-2" style={{ borderColor: C.border }}>
          {ampelDot(kMgState)}
          <div>
            <div style={{ color: C.muted }}>K:Mg-Verhaeltnis Weide</div>
            <div className="font-bold" style={{ color: C.dark }}>{kMg == null ? '–' : fmt(kMg, 2)}</div>
            <div style={{ color: C.muted }}>Ziel {risk.pasture_k_mg_ratio_ziel}</div>
          </div>
        </div>
        <div className="rounded-lg border px-3 py-2 flex items-start gap-2" style={{ borderColor: C.border }}>
          {ampelDot(cpState)}
          <div>
            <div style={{ color: C.muted }}>Rohprotein Weide</div>
            <div className="font-bold" style={{ color: C.dark }}>{cp == null ? '–' : `${fmt(cp, 0)} g/kg TM`}</div>
            <div style={{ color: C.muted }}>Ziel &lt;= 200 (kritisch &gt; 230)</div>
          </div>
        </div>
        <div className="rounded-lg border px-3 py-2 flex items-start gap-2" style={{ borderColor: C.border }}>
          {ampelDot(mgSupState)}
          <div>
            <div style={{ color: C.muted }}>Mg/Na-Weidemineral</div>
            <div className="font-bold" style={{ color: C.dark }}>{fmt(risk.mg_supplement_dmi_kg, 3)} kg TM</div>
            <div style={{ color: C.muted }}>{risk.mg_supplement_ziel}</div>
          </div>
        </div>
      </div>

      <div className="grid gap-2">
        {[
          { label: 'Milch aus Weide', ms: risk.milk_from_pasture },
          { label: 'Milch aus Grassilage', ms: risk.milk_from_grass_silage },
          { label: 'Milch aus Weide + Grassilage', ms: risk.milk_from_pasture_plus_grass_silage },
        ].map((row) => (
          <div
            key={row.label}
            className="grid grid-cols-[1.6fr_1fr_1fr_1fr] gap-2 rounded-lg border px-3 py-2 text-xs"
            style={{ borderColor: C.border, background: '#F9FAFB' }}
          >
            <div className="font-semibold" style={{ color: C.dark }}>{row.label}</div>
            <div className="text-right" style={{ color: C.muted }}>
              Energie {row.ms == null ? '–' : `${fmt(row.ms.milk_from_energy_kg, 1)} kg`}
            </div>
            <div className="text-right" style={{ color: C.muted }}>
              Protein {row.ms == null ? '–' : `${fmt(row.ms.milk_from_protein_kg, 1)} kg`}
            </div>
            <div className="text-right font-bold" style={{ color: C.accent }}>
              Limit {row.ms == null ? '–' : `${fmt(row.ms.limiting_milk_kg, 1)} kg`}
            </div>
          </div>
        ))}
      </div>

      {risk.warnings.length > 0 && (
        <div className="space-y-1.5">
          {risk.warnings.map((w, idx) => (
            <div
              key={idx}
              className="flex gap-2 text-xs rounded border px-3 py-2"
              style={{ background: C.deltaBg, borderColor: C.deltaBorder, color: C.deltaText }}
            >
              <AlertTriangle size={14} className="mt-[2px] shrink-0" />
              <span>{w}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Slice 2 (2026-04-23): Konzentrat-Futterabruf-Staffel
// ---------------------------------------------------------------------------
//
// Zeigt eine lineare / stueckweise lineare Staffel oberhalb der Basisleistung
// aus Grobfutter/Weide. 0,45-0,50 kg Konzentrat (FM) je kg Zusatzmilch.
// Einzelgabe-Limit + empfohlenes Tagesmax + 1,5x-Sicherheitsnetz sichtbar.
function ConcentrateCallUpPanel({
  callUp,
  compact = false,
}: {
  callUp: ConcentrateCallUp | null | undefined
  compact?: boolean
}) {
  if (!callUp) return null
  const distributionLabels: Record<string, string> = {
    transponder: 'Transponder (Abrufstation)',
    ams: 'AMS (Melkroboter)',
    milkparlor: 'Melkstand',
    included_in_tmr: 'Im TMR enthalten',
  }
  const dist = callUp.basis.concentrate_distribution
  const distLabel = distributionLabels[dist] ?? dist

  return (
    <div className={card(compact ? 'space-y-3' : 'space-y-4')}>
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-[11px] uppercase font-bold tracking-[0.5px]" style={{ color: C.muted }}>
            Futterabruf-Staffel Konzentrat
          </p>
          <p className="text-sm font-semibold" style={{ color: C.dark }}>
            Leistungsabhaengige Konzentratgabe ({distLabel})
          </p>
          <p className="text-[11px]" style={{ color: C.muted }}>
            Basis: Milch aus Grobfutter = {fmt(callUp.basis.milk_from_forage_kg, 1)} kg; Ziel =
            {' '}{fmt(callUp.basis.target_milk_kg, 1)} kg; Band{' '}
            {fmt(callUp.basis.kg_conc_per_additional_milk_low, 2)}-
            {fmt(callUp.basis.kg_conc_per_additional_milk_high, 2)} kg FM/kg Zusatzmilch.
          </p>
        </div>
        <div className="text-right text-[11px]" style={{ color: C.muted }}>
          {callUp.basis.concentrate_max_per_serving_kg_fm != null && (
            <div>Einzelgabe max: {fmt(callUp.basis.concentrate_max_per_serving_kg_fm, 1)} kg FM</div>
          )}
          {callUp.basis.concentrate_max_per_day_kg_fm != null && (
            <div>Tagesmax: {fmt(callUp.basis.concentrate_max_per_day_kg_fm, 1)} kg FM</div>
          )}
          {callUp.basis.hard_safety_daily_cap_kg_fm != null && (
            <div style={{ color: C.error }}>
              Hart (1,5x): {fmt(callUp.basis.hard_safety_daily_cap_kg_fm, 1)} kg FM
            </div>
          )}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-[11px]">
          <thead>
            <tr style={{ background: '#F9FAFB' }}>
              {['Milch (kg/d)', 'Zusatzmilch', 'Konz. low', 'Konz. mid', 'Konz. high', 'je Abruf', 'Status'].map((h) => (
                <th
                  key={h}
                  className="py-2 px-2 border-b text-[10px] font-semibold text-[#4B5563] text-right first:text-left"
                  style={{ borderColor: C.border }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {callUp.rows.map((r) => {
              const status: AmpelState = r.exceeds_hard_safety_limit
                ? 'error'
                : r.exceeds_per_serving_limit || r.exceeds_recommended_daily_limit
                ? 'warn'
                : 'ok'
              return (
                <tr key={r.milk_kg_day} className="border-b" style={{ borderColor: '#F3F4F6' }}>
                  <td className="p-2 font-medium" style={{ color: C.dark }}>
                    {fmt(r.milk_kg_day, 1)}
                  </td>
                  <td className="p-2 text-right font-mono">{fmt(r.additional_milk_kg, 1)}</td>
                  <td className="p-2 text-right font-mono">{fmt(r.concentrate_kg_fm_day_low, 2)}</td>
                  <td className="p-2 text-right font-mono font-bold">
                    {fmt(r.concentrate_kg_fm_day_mid, 2)}
                  </td>
                  <td className="p-2 text-right font-mono">{fmt(r.concentrate_kg_fm_day_high, 2)}</td>
                  <td className="p-2 text-right font-mono">{fmt(r.per_serving_kg_fm, 2)}</td>
                  <td className="p-2 text-right">{ampelDot(status)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {callUp.warnings.length > 0 && (
        <div className="space-y-2">
          {callUp.warnings.map((w, i) => (
            <div
              key={i}
              className="flex gap-2 text-xs rounded border px-3 py-2"
              style={{ background: C.deltaBg, borderColor: C.deltaBorder, color: C.deltaText }}
            >
              <AlertTriangle size={14} className="mt-[2px] shrink-0" />
              <span>{w}</span>
            </div>
          ))}
        </div>
      )}

      <p className="text-[10px] italic" style={{ color: C.muted }}>
        Praxisrichtwert 0,45-0,50 kg Konzentrat je kg Zusatzmilch (entspricht ~1 l
        Konzentrat / 2 l Milch). Keine KI-Bildwerte. Annahme TM-Gehalt
        Konzentrat: {fmt(callUp.basis.assumed_concentrate_dm_frac * 100, 0)} %.
      </p>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Slice 3 (2026-04-23): Misch- und Fuetterungsprotokoll (TMR/PMR)
// ---------------------------------------------------------------------------
//
// Zeigt das Mischprotokoll fuer den Futtertisch-Anteil (TMR-Block):
// - Reihenfolge: Grobfutter (struktur) -> Silagen -> Saftfutter/CoP -> KF/Mineral -> Wasser
// - Wasser-Zugabe zur Ziel-TM-Homogenitaet (typisch Ziel-TM 38-42 % fuer PMR)
// - Uebermenge (Futterrest): Praxisfaktor ~+5 % je Mischung, als Orientierung
function MixingProtocolPanel({
  protocol,
  compact = false,
}: {
  protocol: MixingProtocol | null | undefined
  compact?: boolean
}) {
  if (!protocol || protocol.steps.length === 0) return null

  return (
    <div className={card(compact ? 'space-y-3' : 'space-y-4')}>
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-[11px] uppercase font-bold tracking-[0.5px]" style={{ color: C.muted }}>
            Mischprotokoll (TMR-Mischmasse)
          </p>
          <p className="text-sm font-semibold" style={{ color: C.dark }}>
            Reihenfolge Mischwagen, Wasserzugabe, Uebermenge
          </p>
          <p className="text-[11px]" style={{ color: C.muted }}>
            System: {protocol.basis.feeding_system}; TMR-Block: {fmt(protocol.totals.tmr_kgfm_without_water, 1)} kg FM /{' '}
            {fmt(protocol.totals.tmr_kgdm, 1)} kg TM.
          </p>
          {protocol.excluded_pasture && protocol.excluded_pasture.kgdm > 0.001 && (
            <p className="text-[11px] mt-1 font-medium" style={{ color: C.deltaText }}>
              Nicht im Mischwagen: Weide gesamt {fmt(protocol.excluded_pasture.kgdm, 2)} kg TM
              {protocol.excluded_pasture.items?.length
                ? ` (${protocol.excluded_pasture.items.map((i) => i.name).join(', ')})`
                : ''}
              .
            </p>
          )}
        </div>
        <div className="text-right text-[11px]" style={{ color: C.muted }}>
          <div>Ziel-TM Mischung: ~{fmt(protocol.basis.target_dm_frac * 100, 0)} %</div>
          <div>Wasser: +{fmt(protocol.water_addition_kg_fm, 1)} kg FM</div>
          <div>Uebermenge (+{fmt(protocol.basis.overfill_pct, 0)} %): {fmt(protocol.overfill_kg_fm, 1)} kg FM</div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-[11px]">
          <thead>
            <tr style={{ background: '#F9FAFB' }}>
              {['Schritt', 'Gruppe', 'Futtermittel', 'kg FM', 'kg TM', 'Anteil'].map((h) => (
                <th
                  key={h}
                  className="py-2 px-2 border-b text-[10px] font-semibold text-[#4B5563] text-right first:text-left"
                  style={{ borderColor: C.border }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {protocol.steps.map((item) => (
              <tr key={item.feed_id ?? item.name} className="border-b" style={{ borderColor: '#F3F4F6' }}>
                <td className="p-2 font-medium" style={{ color: C.dark }}>
                  {item.step}
                </td>
                <td className="p-2 text-xs" style={{ color: C.muted }}>
                  {item.group_label}
                </td>
                <td className="p-2 font-medium" style={{ color: C.dark }}>
                  {item.name}
                </td>
                <td className="p-2 text-right font-mono">{fmt(item.kgfm, 1)}</td>
                <td className="p-2 text-right font-mono">{fmt(item.kgdm, 2)}</td>
                <td className="p-2 text-right font-mono">{fmt(item.share_fm_pct, 1)}%</td>
              </tr>
            ))}
            <tr style={{ background: '#F9FAFB' }} className="font-semibold">
              <td className="p-2" style={{ color: C.dark }}>
                +
              </td>
              <td className="p-2 text-xs" style={{ color: C.muted }}>
                Wasser (Homogenitaet)
              </td>
              <td className="p-2" style={{ color: C.dark }}>
                Wasser zur Ziel-TM {fmt(protocol.basis.target_dm_frac * 100, 0)} %
              </td>
              <td className="p-2 text-right font-mono">{fmt(protocol.water_addition_kg_fm, 1)}</td>
              <td className="p-2 text-right font-mono">0,00</td>
              <td className="p-2 text-right font-mono">–</td>
            </tr>
          </tbody>
          <tfoot>
            <tr className="font-bold" style={{ background: '#F9FAFB' }}>
              <td className="p-2" style={{ color: C.dark }} colSpan={3}>
                Mischung gesamt (je Kuh · Tag)
              </td>
              <td className="p-2 text-right font-mono">
                {fmt(protocol.totals.tmr_kgfm_with_water, 1)}
              </td>
              <td className="p-2 text-right font-mono">{fmt(protocol.totals.tmr_kgdm, 2)}</td>
              <td className="p-2 text-right font-mono">100%</td>
            </tr>
          </tfoot>
        </table>
      </div>

      {protocol.warnings.length > 0 && (
        <div className="space-y-2">
          {protocol.warnings.map((w, i) => (
            <div
              key={i}
              className="flex gap-2 text-xs rounded border px-3 py-2"
              style={{ background: C.deltaBg, borderColor: C.deltaBorder, color: C.deltaText }}
            >
              <AlertTriangle size={14} className="mt-[2px] shrink-0" />
              <span>{w}</span>
            </div>
          ))}
        </div>
      )}

      <p className="text-[10px] italic" style={{ color: C.muted }}>
        Reihenfolge und Wasserzugabe sind Praxis-Richtwerte (Vertikalmischer:
        Strukturfutter zuerst, Mineral/Konzentrat zuletzt; Wasser zur
        Ziel-TM 38-42 %). Uebermenge +{fmt(protocol.basis.overfill_pct, 0)} %
        fuer Futterrest/Transportverlust. Bitte betriebsspezifisch anpassen.
      </p>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatusBar({ result }: { result: OptimizationResult | null }) {
  return (
    <footer
      className="h-[30px] border-t flex items-center gap-5 px-5 text-[11px]"
      style={{ background: '#F9FAFB', borderColor: C.border, color: C.muted }}
    >
      <span className="font-semibold" style={{ color: C.dark }}>
        Status: {result ? (result.status === 'optimal' ? 'Solver-Feasible ✓' : result.status) : 'Bereit'}
      </span>
      <span className="w-[1px] h-3 bg-[#D1D5DB]" />
      <span>Warnungen: {result?.warnings?.length ?? 0}</span>
      <span className="flex-1 text-right">GfE-2023 · HiGHS-Solver</span>
    </footer>
  )
}

// ---------------------------------------------------------------------------
// Demo Scenarios
// ---------------------------------------------------------------------------

const DEMO_SCENARIOS = [
  {
    id: 'hochleistung',
    label: 'Hochleistung',
    emoji: '🐄',
    farm: 'Musterbetrieb Schwarzwald GbR',
    group: '58 Kühe · Hochleistung Nordstall',
    profile: {
      breed: 'Deutsche Holstein',
      body_weight_kg: 675,
      milk_kg_day: 38,
      milk_fat_pct: 4.1,
      milk_protein_pct: 3.4,
      lactation_stage_days: 110,
      parity: 2,
    },
    chatSeed: [
      { role: 'ai' as const, text: '🌱 Demo-Modus aktiv — Musterbetrieb Schwarzwald GbR, 58 Hochleistungskühe.' },
      { role: 'user' as const, text: 'Kann ich Soja durch Raps ersetzen?' },
      { role: 'ai' as const, text: 'Ja, Rapsextraktionsschrot (RES) kann Soja ersetzen. RES liefert ~190 g sidP/kg TM vs. Soja ~250 g/kg TM — Sie brauchen ca. 30% mehr Menge. Empfehlung: max. 2,5 kg TM/d RES, Methionin-Versorgung über sidMet prüfen (Ziel-Verhältnis sidLys:sidMet = 3:1).' },
      { role: 'user' as const, text: 'Warum ist der Pansen-pH bei 6.18?' },
      { role: 'ai' as const, text: 'Der simulierte pH 6.18 liegt im Grenzbereich (Ziel ≥ 6.2). Ursache: peNDF knapp unter Minimum. Empfehlung: 0.5 kg Stroh oder Heu ergänzen — hebt pH auf ~6.28 und verbessert Strukturindex.' },
    ],
  },
  {
    id: 'frischmelker',
    label: 'Frischmelker',
    emoji: '🍼',
    farm: 'Musterbetrieb Schwarzwald GbR',
    group: '22 Kühe · Frischmelker (Laktationstag 14–45)',
    profile: {
      breed: 'Deutsche Holstein',
      body_weight_kg: 650,
      milk_kg_day: 32,
      milk_fat_pct: 4.4,
      milk_protein_pct: 3.2,
      lactation_stage_days: 21,
      parity: 2,
    },
    chatSeed: [
      { role: 'ai' as const, text: '🍼 Demo-Modus — Frischmelkerration Laktationstag 14–45. Kritische Phase: NEB-Risiko, Ketose-Prophylaxe.' },
      { role: 'user' as const, text: 'Wie beugen wir Ketose vor?' },
      { role: 'ai' as const, text: 'Frischmelker befinden sich typisch in negativer Energiebilanz (NEB). Diese Ration priorisiert: (1) ME-Dichte ≥ 11.5 MJ/kg TM via Maissilage + Körnermais, (2) pabKH ≤ 200 g/kg TM für Pansengesundheit, (3) Propylenglykol-Zulage 200 ml/d in ersten 2 Wochen empfohlen. Propionat-Bildung fördert Gluconeogenese.' },
    ],
  },
  {
    id: 'trockensteher',
    label: 'Trockensteher',
    emoji: '💤',
    farm: 'Musterbetrieb Schwarzwald GbR',
    group: '15 Kühe · Trockensteher (Laktationstag 0)',
    profile: {
      breed: 'Deutsche Holstein',
      body_weight_kg: 720,
      milk_kg_day: 0,
      milk_fat_pct: 4.0,
      milk_protein_pct: 3.4,
      lactation_stage_days: 0,
      parity: 3,
    },
    chatSeed: [
      { role: 'ai' as const, text: '💤 Demo-Modus — Trockenstehration (close-up). Ziel: Kalbiervorbereitung, DCAB, Mg-Versorgung.' },
      { role: 'user' as const, text: 'Wie stelle ich DCAB ein?' },
      { role: 'ai' as const, text: 'DCAB (Dietary Cation-Anion Balance) für Trockensteher: Ziel −100 bis −150 meq/kg TM (GfE-Workshop 2023). Grasreiches Futter hat DCAB +300–400 — stark kationenüberschüssig. Anpassung: Anionenergänzer (Ca-Sulfat, CaCl₂) gezielt einsetzen. Kontrolle: Harn-pH < 6.5 indiziert erfolgreiche Ansäuerung.' },
    ],
  },
]

// ---------------------------------------------------------------------------
// Demo Overlay (Lade-Animation)
// ---------------------------------------------------------------------------

function DemoLoadingOverlay({ scenario, onDone }: { scenario: typeof DEMO_SCENARIOS[0]; onDone: () => void }) {
  const [phase, setPhase] = useState(0)
  const steps = [
    { label: `Betrieb wird geladen …`, sub: scenario.farm },
    { label: 'DLG-Futterdatenbank 2025 …', sub: '164 Futtermittel · GfE-2023-Werte' },
    { label: 'LP-Solver läuft …', sub: 'HiGHS-Optimizer · Kostenminimum' },
    { label: 'pH-Simulation …', sub: 'Zebeli/Schwarz 2023 · peNDF-Lookup' },
  ]

  useEffect(() => {
    let t: ReturnType<typeof setTimeout>
    const advance = (i: number) => {
      if (i >= steps.length) { onDone(); return }
      setPhase(i)
      t = setTimeout(() => advance(i + 1), i === 2 ? 1600 : 700)
    }
    advance(0)
    return () => clearTimeout(t)
  }, [])  // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="fixed inset-0 z-[200] flex flex-col items-center justify-center" style={{ background: 'rgba(27,48,34,0.97)' }}>
      <div className="text-center space-y-6 max-w-md px-8">
        <div className="text-5xl mb-2">{scenario.emoji}</div>
        <h2 className="text-2xl font-bold text-white tracking-tight">{scenario.farm}</h2>
        <p className="text-sm opacity-60 text-white">{scenario.group}</p>
        <div className="space-y-3 mt-6">
          {steps.map((s, i) => (
            <div
              key={i}
              className="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-500"
              style={{
                background: i < phase ? 'rgba(136,176,75,0.15)' : i === phase ? 'rgba(255,255,255,0.08)' : 'transparent',
                opacity: i <= phase ? 1 : 0.25,
              }}
            >
              <div className="w-5 h-5 flex-shrink-0 flex items-center justify-center">
                {i < phase
                  ? <Check size={14} className="text-green-400" />
                  : i === phase
                  ? <Loader2 size={14} className="text-white animate-spin" />
                  : <div className="w-2 h-2 rounded-full bg-white opacity-30" />
                }
              </div>
              <div className="text-left">
                <div className="text-sm font-semibold text-white">{s.label}</div>
                <div className="text-[11px] opacity-50 text-white">{s.sub}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Demo Banner + Tour
// ---------------------------------------------------------------------------

const TOUR_STEPS = [
  { target: 'kpi-bar',      title: '① Kennzahlen auf einen Blick', body: 'Kosten, ME-Dichte, sidP, Stärke, Grundfutteranteil und Strukturindex — alles live aus dem Solver.' },
  { target: 'feed-table',   title: '② Ration & Futtermittel-Mix', body: 'Jede Zeile ist ein Futtermittel im optimierten Plan — mit kg TM/d, FM, Kosten und Nährstoffbeitrag.' },
  { target: 'dlg-panel',    title: '③ DLG / GfE-Workshop 2023', body: 'Ampel für alle Schlüsselindikatoren: peNDF, Pansen-pH-Simulation, Strukturindex, RMD, pabKH.' },
  { target: 'ai-copilot',   title: '④ AI-Copilot', body: 'Stellen Sie Fragen zur Ration — der Copilot erklärt Warnungen, schlägt Alternativen vor und berechnet Umbau-Szenarien.' },
]

function DemoBanner({
  scenario,
  scenarioIdx,
  tourStep,
  onScenario,
  onNextTour,
  onPrevTour,
  onExit,
}: {
  scenario: typeof DEMO_SCENARIOS[0]
  scenarioIdx: number
  tourStep: number | null
  onScenario: (idx: number) => void
  onNextTour: () => void
  onPrevTour: () => void
  onExit: () => void
}) {
  return (
    <div
      className="sticky z-30 flex items-center gap-4 px-5 py-2 text-sm font-semibold shadow-md"
      style={{ top: 90, background: '#B8860B', color: 'white' }}
    >
      <Zap size={14} className="flex-shrink-0" />
      <span className="font-bold uppercase tracking-widest text-[11px] opacity-80">Demo-Modus</span>
      <span className="opacity-60">·</span>
      <span className="opacity-90 font-normal truncate hidden sm:block">{scenario.farm} · {scenario.group}</span>

      {/* Scenario switcher */}
      <div className="flex items-center gap-1 ml-auto">
        {DEMO_SCENARIOS.map((s, i) => (
          <button
            key={s.id}
            onClick={() => onScenario(i)}
            className="px-3 py-1 rounded text-[11px] font-bold transition-all"
            style={{ background: i === scenarioIdx ? 'rgba(255,255,255,0.25)' : 'rgba(255,255,255,0.08)' }}
          >
            {s.emoji} {s.label}
          </button>
        ))}
      </div>

      {/* Tour nav */}
      {tourStep !== null && (
        <div className="flex items-center gap-2 bg-white bg-opacity-15 rounded-lg px-3 py-1.5 ml-3">
          <button onClick={onPrevTour} disabled={tourStep === 0}><ChevronLeft size={12} /></button>
          <span className="text-[11px] font-bold opacity-90">{TOUR_STEPS[tourStep].title}</span>
          <button onClick={onNextTour} disabled={tourStep === TOUR_STEPS.length - 1}><ChevronRightIcon size={12} /></button>
        </div>
      )}

      <button
        onClick={onExit}
        className="ml-2 opacity-70 hover:opacity-100 transition-opacity flex items-center gap-1 text-[11px]"
      >
        <XIcon size={12} /> Demo beenden
      </button>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Tour Tooltip
// ---------------------------------------------------------------------------

function TourTooltip({ step, onNext, onClose }: { step: typeof TOUR_STEPS[0]; onNext: () => void; onClose: () => void }) {
  return (
    <div
      className="fixed z-[100] bottom-20 left-1/2 -translate-x-1/2 max-w-sm w-full rounded-xl shadow-2xl p-4 text-sm"
      style={{ background: C.dark, color: 'white' }}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="font-bold text-[13px] mb-1" style={{ color: C.accent }}>{step.title}</div>
          <p className="text-[12px] opacity-80 leading-relaxed">{step.body}</p>
        </div>
        <button onClick={onClose} className="opacity-50 hover:opacity-100 mt-0.5"><XIcon size={14} /></button>
      </div>
      <div className="flex justify-between items-center mt-3 pt-3 border-t border-white border-opacity-10">
        <div className="flex gap-1">
          {TOUR_STEPS.map((_, i) => (
            <div key={i} className="w-1.5 h-1.5 rounded-full" style={{ background: i === TOUR_STEPS.indexOf(step) ? C.accent : 'rgba(255,255,255,0.3)' }} />
          ))}
        </div>
        <button
          onClick={onNext}
          className="px-3 py-1 rounded text-[11px] font-bold transition-all"
          style={{ background: C.accent }}
        >
          {TOUR_STEPS.indexOf(step) < TOUR_STEPS.length - 1 ? 'Weiter →' : 'Tour beenden'}
        </button>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// VIEW: Dashboard
// ---------------------------------------------------------------------------

function Dashboard({ onStart, onDemo }: { onStart: () => void; onDemo: () => void }) {
  const [aiPrompt, setAiPrompt] = useState('')

  return (
    <div className="p-10 space-y-10 max-w-[1200px] mx-auto w-full">
      {/* Hero */}
      <section className="bg-white p-10 rounded-xl border shadow-sm space-y-8" style={{ borderColor: C.border }}>
        <div className="space-y-3">
          <h1 className="text-3xl font-bold tracking-tight" style={{ color: C.dark }}>
            Willkommen bei KLAR<span style={{ color: C.accent }}>AGRI</span>
          </h1>
          <p className="text-lg max-w-2xl" style={{ color: C.muted }}>
            Optimieren Sie Ihre Milchviehfütterung. Kosten senken, Leistung steigern und Tiergesundheit sichern mit GfE-2023-basierter Präzisionsoptimierung.
          </p>
        </div>

        <div className="flex flex-wrap gap-4">
          <button
            onClick={onStart}
            className="px-8 py-3 text-base font-bold rounded-lg text-white transition-opacity hover:opacity-90"
            style={{ background: C.dark }}
          >
            Neue Ration erstellen
          </button>
          <button
            onClick={onDemo}
            className="px-8 py-3 text-base font-semibold rounded-lg border transition-all hover:shadow-md flex items-center gap-2"
            style={{ borderColor: '#B8860B', color: '#B8860B', background: '#FFFBEB' }}
          >
            <Play size={16} /> Demo starten
          </button>
        </div>

        {/* AI Quick Start */}
        <div className="p-6 rounded-lg border space-y-4" style={{ background: C.aiBg, borderColor: C.aiBorder }}>
          <div className="flex items-center gap-2 font-bold text-xs uppercase tracking-widest" style={{ color: C.aiText }}>
            <Sparkles size={16} /> AI-Schnellstart
          </div>
          <div className="flex gap-4">
            <input
              type="text"
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && aiPrompt.trim() && onStart()}
              placeholder='"Baue eine günstigere Ration für 38 kg Milch, gleiche Struktur, weniger Soja..."'
              className="flex-1 bg-white border rounded-md px-4 py-3 text-sm outline-none focus:border-sky-400 transition-colors"
              style={{ borderColor: C.aiBorder }}
            />
            <button
              onClick={onStart}
              className="px-6 font-bold text-sm rounded-md text-white whitespace-nowrap transition-opacity hover:opacity-90"
              style={{ background: C.accent }}
            >
              Mit AI starten
            </button>
          </div>
        </div>
      </section>

      {/* Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Quick Actions */}
        <div className="space-y-4">
          <h2 className="text-sm font-bold uppercase tracking-widest px-1" style={{ color: C.muted }}>Schnellzugriff</h2>
          <div className="grid grid-cols-1 gap-3">
            {QUICK_ACTIONS.map((a) => (
              <button
                key={a.label}
                onClick={onStart}
                className="flex items-center justify-between p-4 rounded-lg border text-sm font-semibold transition-all shadow-sm hover:shadow-md bg-white"
                style={{ borderColor: C.border, color: C.dark }}
              >
                {a.label}
                <ChevronRight size={16} style={{ opacity: 0.4 }} />
              </button>
            ))}
          </div>
        </div>

        {/* Recent */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-sm font-bold uppercase tracking-widest px-1" style={{ color: C.muted }}>Letzte Projekte</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { name: 'Hochleistung Sep', group: 'Hochleistung Nordstall', milk: 38, cost: 6.42, status: 'Entwurf' },
              { name: 'Frischmelker 08/2026', group: 'Frischmelker', milk: 32, cost: 5.88, status: 'Freigegeben' },
            ].map((r) => (
              <div
                key={r.name}
                onClick={onStart}
                className="bg-white p-5 rounded-lg border shadow-sm cursor-pointer group transition-all hover:shadow-md"
                style={{ borderColor: C.border }}
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-bold group-hover:text-[#88B04B] transition-colors" style={{ color: C.dark }}>{r.name}</h3>
                  <span className="text-[10px] font-bold uppercase bg-slate-50 px-1.5 py-0.5 rounded border" style={{ color: C.muted, borderColor: C.border }}>
                    {r.status}
                  </span>
                </div>
                <div className="space-y-1.5 pt-2 border-t text-[11px]" style={{ borderColor: '#F3F4F6' }}>
                  <div className="flex justify-between"><span style={{ color: C.muted }}>Gruppe:</span><span className="font-semibold">{r.group}</span></div>
                  <div className="flex justify-between"><span style={{ color: C.muted }}>Ziel-Milch:</span><span className="font-semibold">{r.milk} kg</span></div>
                </div>
                <div className="mt-4 flex items-center justify-between text-[11px] font-bold border-t pt-3" style={{ borderColor: '#F3F4F6', color: C.dark }}>
                  <span>{fmt(r.cost)} €/Kuh/Tag</span>
                  <span className="flex items-center gap-1" style={{ color: C.accent }}>Öffnen <ChevronRight size={10} /></span>
                </div>
              </div>
            ))}
            <div
              onClick={onStart}
              className="bg-slate-50 p-5 rounded-lg border-2 border-dashed flex flex-col items-center justify-center cursor-pointer min-h-[160px] transition-all hover:bg-white"
              style={{ borderColor: C.border }}
            >
              <Plus size={24} className="mb-2 opacity-40" />
              <span className="font-bold text-xs uppercase tracking-widest" style={{ color: C.muted }}>Neue Vorlage</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Grundfutter-Analyse Picker (Modal)
// ---------------------------------------------------------------------------

function GfaPickerModal({
  alreadyAdded,
  onAdd,
  onClose,
}: {
  alreadyAdded: string[]
  onAdd: (analyse: GrundfutterAnalyse) => void
  onClose: () => void
}) {
  const { data, isLoading } = useQuery({
    queryKey: ['gfa-list-picker'],
    queryFn: () => fetchGrundfutterAnalysen({ limit: 100 }),
  })
  const [q, setQ] = useState('')
  const analysen = data?.items ?? []
  const filtered = analysen.filter((a) =>
    a.bezeichnung.toLowerCase().includes(q.toLowerCase()) ||
    (a.probenart ?? '').toLowerCase().includes(q.toLowerCase()) ||
    (a.probe_nr ?? '').toLowerCase().includes(q.toLowerCase())
  )

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.4)' }}>
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col overflow-hidden">
        <div className="px-6 py-4 border-b flex items-center justify-between" style={{ borderColor: C.border }}>
          <div>
            <h3 className="font-bold text-base" style={{ color: C.dark }}>Betriebseigene Grundfutteranalyse hinzufügen</h3>
            <p className="text-xs mt-0.5" style={{ color: C.muted }}>LUFA-Analysen aus dem Grundfutteranalysen-Modul importieren</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 transition-colors">
            <XIcon size={20} />
          </button>
        </div>
        <div className="px-4 py-3 border-b" style={{ borderColor: C.border }}>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={15} />
            <input
              autoFocus
              type="text"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Bezeichnung, Probenart oder Probe-Nr. suchen…"
              className="w-full border rounded-lg pl-9 pr-4 py-2 text-sm outline-none focus:ring-2 focus:ring-[#88B04B]"
              style={{ borderColor: C.border }}
            />
          </div>
        </div>
        <div className="flex-1 overflow-auto">
          {isLoading && (
            <div className="flex items-center justify-center py-16 gap-2 text-sm" style={{ color: C.muted }}>
              <Loader2 size={16} className="animate-spin" /> Lade Analysen…
            </div>
          )}
          {!isLoading && filtered.length === 0 && (
            <div className="py-12 text-center text-sm" style={{ color: C.muted }}>
              Keine Grundfutteranalysen gefunden.{' '}
              <a href="/futtermittel/grundfutteranalysen" className="underline" style={{ color: C.accent }}>
                Jetzt anlegen →
              </a>
            </div>
          )}
          {filtered.map((a) => {
            const already = alreadyAdded.includes(a.id)
            return (
              <div
                key={a.id}
                className="px-6 py-4 border-b flex items-center gap-4 hover:bg-slate-50 transition-colors"
                style={{ borderColor: '#F3F4F6' }}
              >
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-sm truncate" style={{ color: C.dark }}>{a.bezeichnung}</div>
                  <div className="text-xs mt-0.5 flex items-center gap-3" style={{ color: C.muted }}>
                    <span>{a.probenart ?? '–'}</span>
                    {a.probe_nr && <span>Probe {a.probe_nr}</span>}
                    {a.erntetermin && <span>Ernte {a.erntetermin}</span>}
                    {a.labor && <span style={{ color: C.accent }}>{a.labor}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-4 text-xs font-mono shrink-0" style={{ color: C.muted }}>
                  {a.me_gfe2023_ts != null && <span>ME {a.me_gfe2023_ts.toFixed(1)}</span>}
                  {a.nel_ts != null && <span>NEL {a.nel_ts.toFixed(1)}</span>}
                  {a.rohprotein_ts != null && <span>XP {a.rohprotein_ts.toFixed(1)}%</span>}
                  {a.trockensubstanz_os != null && <span>TM {a.trockensubstanz_os.toFixed(0)}%</span>}
                </div>
                <button
                  disabled={already}
                  onClick={() => { onAdd(a); onClose() }}
                  className="px-3 py-1.5 rounded-lg text-xs font-bold transition-all"
                  style={already
                    ? { background: '#F3F4F6', color: C.muted, cursor: 'default' }
                    : { background: C.dark, color: '#fff' }
                  }
                >
                  {already ? 'Hinzugefügt' : 'Hinzufügen'}
                </button>
              </div>
            )
          })}
        </div>
        <div className="px-6 py-3 border-t text-xs" style={{ borderColor: C.border, color: C.muted }}>
          {filtered.length} Analysen gefunden · Werte werden automatisch auf g/kg TM umgerechnet
        </div>
      </div>
    </div>
  )
}


// ---------------------------------------------------------------------------
// VIEW: Wizard (3 Steps)
// ---------------------------------------------------------------------------

function Wizard({
  feeds,
  feedsLoading,
  resumeFrom,
  initialStep = 1,
  onComplete,
  onCancel,
}: {
  feeds: FeedIngredient[]
  feedsLoading: boolean
  resumeFrom?: WizardData | null
  initialStep?: number
  onComplete: (data: WizardData) => void
  onCancel: () => void
}) {
  const [step, setStep] = useState(() => initialStep)
  const [group, setGroup] = useState<CowGroup>(() => resumeFrom?.group ?? GROUPS[0])
  const [milkYield, setMilkYield] = useState(() => resumeFrom?.milkYield ?? 38.0)
  const [fatPercent, setFatPercent] = useState(() => resumeFrom?.fatPercent ?? 4.1)
  const [proteinPercent, setProteinPercent] = useState(() => resumeFrom?.proteinPercent ?? 3.5)
  const [dmiTarget, setDmiTarget] = useState(() => resumeFrom?.dmiTarget ?? 24.0)
  const [feedingType, setFeedingType] = useState<FeedingMode>(() => resumeFrom?.feedingType ?? 'TMR')
  const [mode, setMode] = useState<OptMode>(() => resumeFrom?.mode ?? 'Kosten minimieren')
  const [fanMode, setFanMode] = useState<FanMode>(() => resumeFrom?.fanMode ?? FAN_DEFAULTS.mode)
  const [fanReference, setFanReference] = useState<number>(() => resumeFrom?.fanReference ?? FAN_REFERENCE_PRESETS[1]) // 3.0 als mittlerer Preset
  const [relaxationPolicy, setRelaxationPolicy] = useState<RelaxationPolicy>(() => resumeFrom?.relaxationPolicy ?? FAN_DEFAULTS.relaxation_policy)
  const [seasonProfile, setSeasonProfile] = useState<SeasonProfile | null>(() => resumeFrom?.seasonProfile ?? null)
  // DLG 01|2025 Tab. 13-15: optionale Leistungs-/Physiologiestufen-Auswahl.
  // Leer = Auto-Mapping aus Fuetterungstyp/Saison (pmr_pasture_spring etc.).
  const [policyProfile, setPolicyProfile] = useState<PolicyProfile | null>(() => resumeFrom?.policyProfile ?? null)
  const [priorityWeights, setPriorityWeights] = useState<PriorityWeights>(() => ({
    ...DEFAULT_PRIORITY_WEIGHTS,
    ...resumeFrom?.priorityWeights,
  }))
  const [wizardHardBounds, setWizardHardBounds] = useState<WizardHardBounds>(() => ({
    ...DEFAULT_WIZARD_HARD_BOUNDS,
    ...resumeFrom?.wizardHardBounds,
  }))
  const [wizardSoftGoals, setWizardSoftGoals] = useState<WizardSoftGoals>(() => ({
    ...DEFAULT_WIZARD_SOFT_GOALS,
    ...resumeFrom?.wizardSoftGoals,
  }))
  const [showFanAdvanced, setShowFanAdvanced] = useState(false)
  const [selectedFeedIds, setSelectedFeedIds] = useState<Set<string>>(() =>
    resumeFrom ? new Set(resumeFrom.selectedFeedIds) : new Set(),
  )
  const [feedMaxFm, setFeedMaxFm] = useState<Record<string, number>>(() => ({ ...resumeFrom?.feedMaxFm }))
  const [feedMinFm, setFeedMinFm] = useState<Record<string, number>>(() => ({ ...resumeFrom?.feedMinFm }))
  const [searchQuery, setSearchQuery] = useState('')
  const [customFeeds, setCustomFeeds] = useState<GrundfutterAnalyse[]>(() => [...(resumeFrom?.customFeeds ?? [])])
  const [compoundFeeds, setCompoundFeeds] = useState<UploadedCompoundFeed[]>(() => [...(resumeFrom?.compoundFeeds ?? [])])
  const [showGfaPicker, setShowGfaPicker] = useState(false)
  const [restoredFromStorage, setRestoredFromStorage] = useState(() => !!resumeFrom)
  const compoundUploadRef = useRef<HTMLInputElement | null>(null)

  // Beim ersten Laden: gespeicherte Auswahl aus localStorage wiederherstellen (nicht bei Nachoptimierung / Resume)
  useEffect(() => {
    if (feeds.length === 0 || restoredFromStorage) return
    if (resumeFrom) {
      setRestoredFromStorage(true)
      return
    }
    setRestoredFromStorage(true)
    try {
      const raw = localStorage.getItem(LS_FEED_SELECTION)
      if (raw) {
        const saved: PersistedFeedSelection = JSON.parse(raw)
        const validIds = new Set(feeds.map((f) => f.id))
        const restored = saved.selectedFeedIds.filter((id) => validIds.has(id) || id.startsWith('gfa_'))
        if (restored.length > 0) {
          setSelectedFeedIds(new Set(restored))
          setFeedMaxFm(saved.feedMaxFm ?? {})
          setFeedMinFm(saved.feedMinFm ?? {})
          return
        }
      }
    } catch { /* ignore */ }
    // Fallback: alle DLG-Feeds aktivieren
    setSelectedFeedIds(new Set(feeds.map((f) => f.id)))
  }, [feeds, restoredFromStorage, resumeFrom])

  // Auswahl in localStorage speichern (debounced via effect)
  useEffect(() => {
    if (selectedFeedIds.size === 0) return
    try {
      const payload: PersistedFeedSelection = {
        selectedFeedIds: [...selectedFeedIds],
        customFeedIds: customFeeds.map((c) => c.id),
        feedMaxFm,
        feedMinFm,
        savedAt: new Date().toISOString(),
      }
      localStorage.setItem(LS_FEED_SELECTION, JSON.stringify(payload))
    } catch { /* ignore */ }
  }, [selectedFeedIds, customFeeds, feedMaxFm, feedMinFm])

  // Custom feeds (betriebseigen) immer oben, dann DLG alphabetisch
  const allDisplayFeeds = useMemo(() => {
    const custom = customFeeds.map(gfaToDisplayFeed)
    const compounds = compoundFeeds.map(compoundFeedToDisplayFeed)
    return [...custom, ...compounds, ...feeds]
  }, [feeds, customFeeds, compoundFeeds])

  const filteredFeeds = useMemo(
    () => allDisplayFeeds.filter((f) => f.name.toLowerCase().includes(searchQuery.toLowerCase())),
    [allDisplayFeeds, searchQuery],
  )

  const { data: dlgInfo } = useQuery({ queryKey: ['dlg-info'], queryFn: fetchDlgInfo, staleTime: 60_000 })
  const dlgRefreshMut = useMutation({ mutationFn: triggerDlgRefresh })

  const stepLabel = step === 1 ? 'Gruppe & Ziel' : step === 2 ? 'Futtermittel & Analysen' : 'Restriktionen & Prioritäten'

  function handleComplete() {
    onComplete({
      group, milkYield, fatPercent, proteinPercent, dmiTarget, feedingType, mode,
      selectedFeedIds, customFeeds, compoundFeeds, feedMaxFm, feedMinFm,
      fanMode, fanReference, relaxationPolicy, seasonProfile, policyProfile,
      priorityWeights,
      wizardHardBounds,
      wizardSoftGoals,
    })
  }

  const compoundUploadMut = useMutation({
    mutationFn: uploadCompoundFeedDocument,
    onSuccess: (uploaded) => {
      setCompoundFeeds((prev) => {
        const next = prev.filter((item) => item.product_name !== uploaded.parsed.product_name)
        return [...next, uploaded.parsed]
      })
      const optimizerFeed = uploaded.parsed.optimizer_feed as Record<string, unknown>
      const compoundId = String(optimizerFeed.id ?? '')
      if (compoundId) {
        setSelectedFeedIds((prev) => new Set([...prev, compoundId]))
      }
    },
  })

  const inputCls = 'w-full border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-[#88B04B] transition-all'
  const labelCls = 'text-xs font-semibold text-slate-500 block mb-1'

  return (
    <div className="flex-1 p-6 flex flex-col max-w-6xl mx-auto w-full space-y-6" style={{ background: C.bg }}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight" style={{ color: C.dark }}>Neue Ration erstellen</h2>
          <p className="text-sm" style={{ color: C.muted }}>Schritt {step} von 3: {stepLabel}</p>
        </div>
        <div className="flex gap-2">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className="h-2 w-12 rounded-full transition-all duration-300"
              style={{ background: step >= s ? C.dark : '#D1D5DB' }}
            />
          ))}
        </div>
      </div>

      {/* Card */}
      <div className="flex-1 bg-white rounded-lg border shadow-sm overflow-hidden flex flex-col" style={{ borderColor: C.border }}>
        {/* Step 1: Group & Goal */}
        {step === 1 && (
          <div className="flex-1 grid grid-cols-1 lg:grid-cols-2">
            <div className="p-8 border-r border-slate-100 space-y-8">
              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Tiergruppe</h3>
                <div className="space-y-1.5">
                  <label className={labelCls}>Gruppe</label>
                  <select
                    value={group.id}
                    onChange={(e) => setGroup(GROUPS.find((g) => g.id === e.target.value) ?? GROUPS[0])}
                    className={inputCls}
                    style={{ borderColor: C.border, background: '#F9FAFB' }}
                  >
                    {GROUPS.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: 'Anzahl Kühe', val: group.count },
                    { label: 'Körpermasse (kg)', val: group.bodyMass },
                    { label: 'Laktationstage', val: group.lactationDays },
                    { label: 'Laktation Nr.', val: group.lactationNumber },
                  ].map((row) => (
                    <div key={row.label} className="space-y-1.5">
                      <label className={labelCls}>{row.label}</label>
                      <input type="number" value={row.val} readOnly className={cn(inputCls, 'bg-slate-50')} style={{ borderColor: C.border }} />
                    </div>
                  ))}
                </div>
              </div>
              {/* AI hint */}
              <div className="p-4 rounded-lg border space-y-2" style={{ background: C.activeBg, borderColor: C.accent }}>
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider" style={{ color: C.dark }}>
                  <Sparkles size={14} /> AI-Hinweise
                </div>
                <p className="text-xs leading-relaxed" style={{ color: C.dark }}>
                  Laktationstag {group.lactationDays}: TM-Aufnahme {dmiTarget} kg ist plausibel.
                  Ziel-Milch {milkYield} kg liegt im optimalen Bereich für diese Gruppe.
                </p>
              </div>
            </div>

            <div className="p-8 bg-slate-50/50 space-y-6">
              <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">Leistungsziel</h3>
              <div className="space-y-2">
                <label className={labelCls}>Optimierungs-Modus</label>
                <div className="flex flex-col gap-2">
                  {(['Kosten minimieren', 'IOFC maximieren', 'Leistung absichern', 'Tiergesundheit'] as OptMode[]).map((m) => (
                    <button
                      key={m}
                      type="button"
                      onClick={() => setMode(m)}
                      className={cn(
                        'px-3 py-2.5 rounded-lg text-xs font-bold border transition-all text-left',
                        mode === m ? 'text-white shadow-sm' : 'bg-white hover:border-[#88B04B]',
                      )}
                      style={{
                        background: mode === m ? C.dark : undefined,
                        borderColor: mode === m ? C.dark : C.border,
                        color: mode === m ? '#fff' : C.muted,
                      }}
                    >
                      {m}
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: 'Ziel-Milch (kg)', val: milkYield, setter: setMilkYield, step: 1 },
                  { label: 'TM-Aufnahme (kg)', val: dmiTarget, setter: setDmiTarget, step: 0.5 },
                  { label: 'Fett (%)', val: fatPercent, setter: setFatPercent, step: 0.1 },
                  { label: 'Eiweiß (%)', val: proteinPercent, setter: setProteinPercent, step: 0.1 },
                ].map((field) => (
                  <div key={field.label} className="space-y-1.5">
                    <label className={labelCls}>{field.label}</label>
                    <input
                      type="number"
                      step={field.step}
                      value={field.val}
                      onChange={(e) => field.setter(parseFloat(e.target.value) || 0)}
                      className={inputCls}
                      style={{ borderColor: C.border }}
                    />
                  </div>
                ))}
              </div>
              <div className="space-y-1.5">
                <label className={labelCls}>Fütterungssystem</label>
                <div className="flex gap-2">
                  {([
                    { key: 'TMR', label: 'TMR', hint: 'Totalmischration' },
                    { key: 'PMR', label: 'PMR', hint: 'Partielle Mischration' },
                    { key: 'PMR+Weide', label: 'PMR + Weide', hint: 'PMR mit Ganztagsweide/Frischgras' },
                  ] as const).map((opt) => (
                    <button
                      key={opt.key}
                      type="button"
                      onClick={() => {
                        setFeedingType(opt.key)
                        if (opt.key === 'PMR+Weide') {
                          setShowFanAdvanced(true)
                          if (!seasonProfile) setSeasonProfile('spring_mid')
                        }
                      }}
                      title={opt.hint}
                      className="flex-1 py-2 rounded-lg text-xs font-bold border transition-all"
                      style={{
                        background: feedingType === opt.key ? C.dark : '#fff',
                        borderColor: feedingType === opt.key ? C.dark : C.border,
                        color: feedingType === opt.key ? '#fff' : C.muted,
                      }}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
                {feedingType === 'PMR+Weide' && (
                  <div
                    className="text-[11px] leading-tight mt-1 px-2 py-1.5 rounded border space-y-1"
                    style={{ background: '#F0F7ED', borderColor: C.accent, color: C.dark }}
                  >
                    <div>
                      Weide-/Frischgrasaufnahme wird separat bilanziert (DLG 417/443).
                      Weidemineral Mg/Na wird automatisch als Sicherheitsbaustein gefuehrt.
                    </div>
                    {seasonProfile?.startsWith('spring') && (
                      <div className="font-semibold">
                        Aktives Profil: <span className="font-mono">pmr_pasture_spring</span> (saisonale
                        Fruehjahrsweide mit K/Mg-Risiko-Korridoren).
                      </div>
                    )}
                    {seasonProfile?.startsWith('summer') && (
                      <div className="font-semibold">
                        Aktives Profil: <span className="font-mono">pmr_pasture_summer</span> –
                        Hitzestress-Korridor: reduzierte TM-Aufnahme (-3 % bis -12 %), erhoehter
                        Na-Bedarf, Pansenpuffer NaHCO3 als Pflichtbaustein.
                      </div>
                    )}
                    {seasonProfile === 'autumn' && (
                      <div className="font-semibold">
                        Aktives Profil: <span className="font-mono">pmr_pasture_autumn</span> –
                        stickstoffreicher Grasaufwuchs: CP-Dichte-Obergrenze 175 g/kg TM
                        (Harnstoffschutz), aNDFomGF-Boost fuer Strukturstuetzung.
                      </div>
                    )}
                    {!seasonProfile && (
                      <div style={{ color: C.muted }}>
                        Hinweis: Bitte Saison unter &quot;mehr Optionen&quot; setzen, damit das richtige
                        Weideprofil aktiv wird.
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* FAN-MODE-V1: Bewertungsmodus (GfE 2023) --------------------------- */}
              <div className="space-y-2 pt-3 border-t" style={{ borderColor: C.border }}>
                <div className="flex items-center justify-between">
                  <label className={labelCls}>Bewertungsmodus (GfE 2023)</label>
                  <button
                    type="button"
                    onClick={() => setShowFanAdvanced((v) => !v)}
                    className="text-[11px] font-semibold underline-offset-2 hover:underline"
                    style={{ color: C.muted }}
                  >
                    {showFanAdvanced ? 'weniger' : 'mehr Optionen'}
                  </button>
                </div>
                <div className="flex gap-2">
                  {([
                    { key: 'auto_iterative', label: 'Auto-iterativ', hint: 'Default: Fixpunkt-Iteration bei |dFANi|<=0.05 (V1)' },
                    { key: 'reference', label: 'Referenz', hint: 'Feste FAN-Stufe zur Bewertung (2.5 / 3.0 / 3.5)' },
                    { key: 'evaluation_only', label: 'Nur Bewertung', hint: 'Keine FAN-abhaengige Anpassung der Futterwerte' },
                  ] as const).map((opt) => (
                    <button
                      key={opt.key}
                      type="button"
                      onClick={() => setFanMode(opt.key)}
                      title={opt.hint}
                      className="flex-1 py-1.5 rounded-lg text-[11px] font-bold border transition-all"
                      style={{
                        background: fanMode === opt.key ? C.dark : '#fff',
                        borderColor: fanMode === opt.key ? C.dark : C.border,
                        color: fanMode === opt.key ? '#fff' : C.muted,
                      }}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
                {fanMode === 'reference' && (
                  <div className="flex gap-2 items-center">
                    {FAN_REFERENCE_PRESETS.map((preset) => (
                      <button
                        key={preset}
                        type="button"
                        onClick={() => setFanReference(preset)}
                        className="px-2.5 py-1 rounded text-[11px] font-semibold border transition-all"
                        style={{
                          background: Math.abs(fanReference - preset) < 1e-6 ? C.accent : '#fff',
                          borderColor: Math.abs(fanReference - preset) < 1e-6 ? C.accent : C.border,
                          color: Math.abs(fanReference - preset) < 1e-6 ? '#fff' : C.dark,
                        }}
                      >
                        FAN {preset.toFixed(1)}
                      </button>
                    ))}
                    <input
                      type="number"
                      step={0.1}
                      min={1}
                      max={5}
                      value={fanReference}
                      onChange={(e) => setFanReference(parseFloat(e.target.value) || 3.0)}
                      className="w-20 px-2 py-1 rounded border text-[11px]"
                      style={{ borderColor: C.border }}
                    />
                  </div>
                )}
                {showFanAdvanced && (
                  <div className="space-y-2 pt-2">
                    <div>
                      <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 block mb-1">
                        Relaxation (weiche Grenzen)
                      </label>
                      <div className="flex gap-2">
                        {([
                          { key: 'strict', label: 'Strict', hint: 'Fast alles hart. Nur fuer Gutachten/Debug.' },
                          { key: 'standard', label: 'Standard', hint: 'Sicherheit hart, Balance weich (Default).' },
                          { key: 'soft', label: 'Soft', hint: 'Breitere Toleranzen, z.B. schwieriges Fruehjahr.' },
                        ] as const).map((opt) => (
                          <button
                            key={opt.key}
                            type="button"
                            onClick={() => setRelaxationPolicy(opt.key)}
                            title={opt.hint}
                            className="flex-1 py-1.5 rounded text-[11px] font-semibold border transition-all"
                            style={{
                              background: relaxationPolicy === opt.key ? C.dark : '#fff',
                              borderColor: relaxationPolicy === opt.key ? C.dark : C.border,
                              color: relaxationPolicy === opt.key ? '#fff' : C.muted,
                            }}
                          >
                            {opt.label}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 block mb-1">
                        Weide-/Saisonprofil
                      </label>
                      <select
                        value={seasonProfile ?? ''}
                        onChange={(e) => setSeasonProfile((e.target.value || null) as SeasonProfile | null)}
                        className={cn(inputCls, 'text-[12px] py-1.5')}
                        style={{ borderColor: C.border }}
                      >
                        <option value="">— nicht gesetzt —</option>
                        <option value="spring_young">Fruehjahr (jung)</option>
                        <option value="spring_mid">Fruehjahr (mittel)</option>
                        <option value="spring_late">Fruehjahr (spaet)</option>
                        <option value="summer_young">Sommer (jung)</option>
                        <option value="summer_mid">Sommer (mittel)</option>
                        <option value="summer_late">Sommer (spaet)</option>
                        <option value="autumn">Herbst</option>
                        <option value="winter">Winter</option>
                      </select>
                    </div>
                    {/* DLG 01|2025 Tab. 13-15: Leistungs-/Physiologiestufe */}
                    <div>
                      <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 block mb-1">
                        Leistungsstufe (DLG 01|2025 Tab. 13-15)
                      </label>
                      <select
                        value={policyProfile ?? ''}
                        onChange={(e) => setPolicyProfile((e.target.value || null) as PolicyProfile | null)}
                        className={cn(inputCls, 'text-[12px] py-1.5')}
                        style={{ borderColor: C.border }}
                        title="Bindet die Ration an DLG-Referenzkorridore fuer ME/CP/sidP/pabKH/aNDFomGF+CoP. Leer = Auto-Mapping aus Fuetterungstyp + Saison."
                      >
                        <option value="">— Auto (aus Fuetterungstyp/Saison) —</option>
                        <optgroup label="TMR Laktation">
                          <option value="tmr_fresh_lactation">Frischmelker (0-60 LT)</option>
                          <option value="tmr_high_yield">Hochleistung (≥ 35 kg)</option>
                          <option value="tmr_mid_yield">Mittellaktation (25-34 kg)</option>
                          <option value="tmr_late_lactation">Altmelker (&lt; 25 kg)</option>
                        </optgroup>
                        <optgroup label="TMR Trockenphase">
                          <option value="tmr_transit">Transit / Anfuetterung</option>
                          <option value="tmr_dry_cow">Trockensteher</option>
                        </optgroup>
                        <optgroup label="Saisonale PMR-Profile">
                          <option value="tmr_standard">TMR Standard</option>
                          <option value="pmr_standard">PMR Standard</option>
                          <option value="pmr_pasture_spring">PMR + Weide Fruehjahr</option>
                          <option value="pmr_pasture_summer">PMR + Weide Sommer</option>
                          <option value="pmr_pasture_autumn">PMR + Weide Herbst</option>
                        </optgroup>
                      </select>
                      <div className="text-[10px] mt-1" style={{ color: C.muted }}>
                        Bei Auswahl greift die DLG-01|2025-Bandauswertung als
                        <em> weiche </em> Constraint (Klasse B, relaxation-policy-skaliert).
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Feeds */}
        {step === 2 && (
          <div className="flex-1 flex flex-col" style={{ minHeight: 500 }}>

            {/* DLG Info-Bar */}
            {dlgInfo && (
              <div
                className="px-4 py-2 flex items-center gap-3 text-xs border-b"
                style={{
                  background: dlgInfo.needs_update ? '#FFFBEB' : '#F0F9F4',
                  borderColor: dlgInfo.needs_update ? '#FEF3C7' : '#D1FAE5',
                  color: dlgInfo.needs_update ? '#92400E' : '#065F46',
                }}
              >
                <Database size={13} />
                <span>
                  <strong>DLG-Futterwerttabellen:</strong> {dlgInfo.feed_count} Einträge
                  {dlgInfo.last_update ? ` · Stand ${dlgInfo.last_update}` : ' · Fallback-Datensatz'}
                  {dlgInfo.needs_update && ' · Aktualisierung empfohlen'}
                </span>
                <button
                  onClick={() => dlgRefreshMut.mutate()}
                  disabled={dlgRefreshMut.isPending}
                  className="ml-auto flex items-center gap-1 px-2 py-0.5 rounded border text-xs font-semibold hover:bg-white transition-all"
                  style={{ borderColor: 'currentColor', opacity: dlgRefreshMut.isPending ? 0.5 : 1 }}
                >
                  <RefreshCw size={11} className={dlgRefreshMut.isPending ? 'animate-spin' : ''} />
                  Aktualisieren
                </button>
              </div>
            )}

            {/* Toolbar */}
            <div className="p-4 border-b flex items-center justify-between gap-4 flex-wrap" style={{ borderColor: C.border }}>
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Futtermittel suchen..."
                  className="w-full border rounded-lg pl-10 pr-4 py-2 text-sm outline-none focus:ring-2 focus:ring-[#88B04B]"
                  style={{ borderColor: C.border }}
                />
              </div>
              <div className="flex items-center gap-2 text-sm font-medium" style={{ color: C.muted }}>
                {feedsLoading ? <Loader2 size={16} className="animate-spin" /> : null}
                {selectedFeedIds.size} / {allDisplayFeeds.length} ausgewählt
                {customFeeds.length > 0 && (
                  <span className="ml-1 text-xs px-1.5 py-0.5 rounded font-bold" style={{ background: '#EEF2FF', color: '#4338CA' }}>
                    +{customFeeds.length} Betrieb
                  </span>
                )}
                {compoundFeeds.length > 0 && (
                  <span className="ml-1 text-xs px-1.5 py-0.5 rounded font-bold" style={{ background: '#ECFDF5', color: '#047857' }}>
                    +{compoundFeeds.length} Kraftfutter
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  className="text-xs px-3 py-1.5 border rounded-lg hover:bg-slate-50 flex items-center gap-1.5 font-semibold"
                  style={{ borderColor: C.accent, color: C.accent }}
                  onClick={() => setShowGfaPicker(true)}
                >
                  <FlaskConical size={13} />
                  Betriebsanalyse hinzufügen
                </button>
                <button
                  className="text-xs px-3 py-1.5 border rounded-lg hover:bg-slate-50 flex items-center gap-1.5 font-semibold"
                  style={{ borderColor: '#0F766E', color: '#0F766E' }}
                  onClick={() => compoundUploadRef.current?.click()}
                  disabled={compoundUploadMut.isPending}
                >
                  {compoundUploadMut.isPending ? <Loader2 size={13} className="animate-spin" /> : <FileText size={13} />}
                  Lieferschein / Rezeptur hochladen
                </button>
                <button className="text-xs px-3 py-1.5 border rounded-lg hover:bg-slate-50" style={{ borderColor: C.border }} onClick={() => setSelectedFeedIds(new Set(allDisplayFeeds.map((f) => f.id)))}>Alle</button>
                <button className="text-xs px-3 py-1.5 border rounded-lg hover:bg-slate-50" style={{ borderColor: C.border }} onClick={() => setSelectedFeedIds(new Set())}>Keine</button>
              </div>
              <input
                ref={compoundUploadRef}
                type="file"
                accept=".pdf,image/*"
                data-testid="rations-compound-upload-input"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) compoundUploadMut.mutate(file)
                  e.currentTarget.value = ''
                }}
              />
            </div>

            {(compoundUploadMut.isError || compoundFeeds.length > 0) && (
              <div className="px-4 py-3 border-b space-y-2" style={{ borderColor: C.border, background: '#F8FAFC' }}>
                {compoundUploadMut.isError && (
                  <div className="text-xs flex items-start gap-2" style={{ color: C.error }}>
                    <AlertCircle size={14} className="mt-0.5 shrink-0" />
                    <span>{getRationsApiErrorMessage(compoundUploadMut.error, 'Dokument konnte nicht verarbeitet werden.')}</span>
                  </div>
                )}
                {compoundFeeds.map((doc) => {
                  const compoundId = String((doc.optimizer_feed as Record<string, unknown>).id ?? '')
                  return (
                    <div key={compoundId} className="rounded-lg border bg-white px-3 py-2 flex items-start gap-3" style={{ borderColor: '#DCE7E4' }}>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <div className="text-sm font-semibold" style={{ color: C.dark }}>{doc.product_name}</div>
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ background: '#ECFDF5', color: '#047857' }}>
                            Match {fmt(doc.gfe2023_estimate.match_coverage_pct, 0)}%
                          </span>
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ background: '#EEF2FF', color: '#4338CA' }}>
                            {doc.source_type === 'image_ocr' ? 'Foto/OCR' : 'PDF'}
                          </span>
                        </div>
                        <div className="text-xs mt-1 flex flex-wrap gap-x-4 gap-y-1" style={{ color: C.muted }}>
                          <span>ME {fmt(doc.gfe2023_estimate.me_fan1_mj_kgdm, 2)} MJ</span>
                          <span>sidP {fmt(doc.gfe2023_estimate.sidp_g_kgdm, 0)} g/kg TM</span>
                          <span>NEL alt {fmt(doc.declared_analysis.nel_mj_kg, 1)} MJ</span>
                          <span>XP {fmt(doc.declared_analysis.crude_protein_pct, 1)}%</span>
                          <span>Datei {doc.source_filename}</span>
                        </div>
                        {doc.warnings.length > 0 && (
                          <div className="mt-1 text-[11px]" style={{ color: '#92400E' }}>
                            {doc.warnings[0]}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => {
                          setCompoundFeeds((prev) => prev.filter((item) => item.product_name !== doc.product_name))
                          setFeedMaxFm((prev) => { const n = { ...prev }; delete n[compoundId]; return n })
                          setFeedMinFm((prev) => { const n = { ...prev }; delete n[compoundId]; return n })
                          setSelectedFeedIds((prev) => {
                            const next = new Set(prev)
                            next.delete(compoundId)
                            return next
                          })
                        }}
                        className="text-slate-300 hover:text-red-400 transition-colors"
                      >
                        <XIcon size={12} />
                      </button>
                    </div>
                  )
                })}
                <div className="text-[11px]" style={{ color: C.muted }}>
                  Uploads liefern eine Alt-/Neu-System-Brücke aus Deklaration und DLG-Match. Foto-Uploads werden per OCR ausgelesen und sollten fachlich gegengeprüft werden.
                </div>
              </div>
            )}

            {/* Feed-Tabelle */}
            <div className="flex-1 overflow-auto">
              <table className="w-full text-left border-collapse">
                <thead className="sticky top-0 z-10" style={{ background: '#F9FAFB' }}>
                  <tr>
                    <th className="px-4 py-3 border-b text-xs font-semibold w-10" style={{ borderColor: C.border, color: '#4B5563' }} />
                    <th className="px-4 py-3 border-b text-xs font-semibold" style={{ borderColor: C.border, color: '#4B5563' }}>Futtermittel</th>
                    <th className="px-4 py-3 border-b text-xs font-semibold" style={{ borderColor: C.border, color: '#4B5563' }}>Kategorie</th>
                    <th className="px-4 py-3 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }}>TM %</th>
                    <th className="px-4 py-3 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }}>ME</th>
                    <th className="px-4 py-3 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }}>sidP</th>
                    <th className="px-4 py-3 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }}>Stärke</th>
                    <th className="px-4 py-3 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }}>€/kg TM</th>
                    <th className="px-4 py-3 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }} title="Mindestverzehr in kg Frischmasse/Tag (leer = keine Untergrenze).">Min FM kg/d</th>
                    <th className="px-4 py-3 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }} title="Max. Verzehrsgrenze in kg Frischmasse/Tag (0 = unbegrenzt). Sinnvoll bei saisonal begrenzten Vorräten.">Max FM kg/d</th>
                    <th className="px-4 py-3 border-b text-xs font-semibold w-8" style={{ borderColor: C.border }} />
                  </tr>
                </thead>
                <tbody>
                  {filteredFeeds.map((f) => {
                    const checked = selectedFeedIds.has(f.id)
                    const isCustom = '_isCustom' in f && (f as { _isCustom?: boolean })._isCustom
                    return (
                      <tr
                        key={f.id}
                        onClick={() => {
                          const next = new Set(selectedFeedIds)
                          if (checked) next.delete(f.id)
                          else next.add(f.id)
                          setSelectedFeedIds(next)
                        }}
                        className="cursor-pointer border-b transition-colors hover:bg-slate-50"
                        style={{ background: checked ? C.activeBg : undefined, borderColor: '#F3F4F6' }}
                      >
                        <td className="px-4 py-3">
                          <div
                            className="w-4 h-4 rounded border flex items-center justify-center transition-all"
                            style={{ background: checked ? C.accent : '#fff', borderColor: checked ? C.accent : C.border }}
                          >
                            {checked && <Check size={10} strokeWidth={4} color="#fff" />}
                          </div>
                        </td>
                        <td className="px-4 py-3 font-bold text-sm" style={{ color: C.dark }}>
                          <span>{f.name}</span>
                          {isCustom && (
                            <span className="ml-2 text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ background: '#EEF2FF', color: '#4338CA' }}>
                              Betrieb
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-xs" style={{ color: C.muted }}>{f.group}</td>
                        <td className="px-4 py-3 text-right font-mono text-xs">{fmt(f.dm_frac * 100, 1)}</td>
                        <td className="px-4 py-3 text-right font-mono text-xs">{fmt(f.me_mj_kgdm, 1)}</td>
                        <td className="px-4 py-3 text-right font-mono text-xs">{fmt(f.sidp_g_kgdm, 0)}</td>
                        <td className="px-4 py-3 text-right font-mono text-xs">{fmt(f.starch_g_kgdm, 0)}</td>
                        <td className="px-4 py-3 text-right font-mono text-xs font-bold">{fmt(f.price_eur_kgdm, 3)}</td>
                        <td className="px-4 py-3 text-right" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="number"
                            min={0}
                            step={0.5}
                            value={feedMinFm[f.id] ?? ''}
                            onChange={(e) => {
                              const v = parseFloat(e.target.value)
                              setFeedMinFm((prev) => {
                                const next = { ...prev }
                                if (isNaN(v) || v <= 0) delete next[f.id]
                                else next[f.id] = v
                                return next
                              })
                            }}
                            placeholder="—"
                            className="w-16 border rounded px-2 py-0.5 text-xs text-right outline-none focus:ring-1 focus:ring-[#88B04B]"
                            style={{ borderColor: feedMinFm[f.id] ? C.accent : C.border }}
                            title="Min. kg Frischmasse/Tag (leer = keine Untergrenze)"
                          />
                        </td>
                        <td className="px-4 py-3 text-right" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="number"
                            min={0}
                            step={0.5}
                            value={feedMaxFm[f.id] ?? ''}
                            onChange={(e) => {
                              const v = parseFloat(e.target.value)
                              setFeedMaxFm((prev) => {
                                const next = { ...prev }
                                if (isNaN(v) || v <= 0) delete next[f.id]
                                else next[f.id] = v
                                return next
                              })
                            }}
                            placeholder="∞"
                            className="w-16 border rounded px-2 py-0.5 text-xs text-right outline-none focus:ring-1 focus:ring-[#88B04B]"
                            style={{ borderColor: feedMaxFm[f.id] ? C.accent : C.border }}
                            title="Max. kg Frischmasse/Tag (leer = unbegrenzt)"
                          />
                        </td>
                        <td className="px-4 py-3">
                          {isCustom && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                const analyseId = (f as { _analyseId?: string })._analyseId
                                const compoundId = (f as { _compoundId?: string })._compoundId
                                if (analyseId) {
                                  setCustomFeeds((prev) => prev.filter((cf) => cf.id !== analyseId))
                                }
                                if (compoundId) {
                                  setCompoundFeeds((prev) =>
                                    prev.filter((cf) => String((cf.optimizer_feed as Record<string, unknown>).id ?? '') !== compoundId)
                                  )
                                }
                                setFeedMaxFm((prev) => { const n = { ...prev }; delete n[f.id]; return n })
                                setFeedMinFm((prev) => { const n = { ...prev }; delete n[f.id]; return n })
                                setSelectedFeedIds((prev) => { const next = new Set(prev); next.delete(f.id); return next })
                              }}
                              className="text-slate-300 hover:text-red-400 transition-colors"
                            >
                              <XIcon size={12} />
                            </button>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                  {filteredFeeds.length === 0 && (
                    <tr>
                      <td colSpan={11} className="py-10 text-center text-sm" style={{ color: C.muted }}>
                        Keine Futtermittel gefunden
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Grundfutter-Analyse Picker Modal */}
            {showGfaPicker && (
              <GfaPickerModal
                alreadyAdded={customFeeds.map((cf) => cf.id)}
                onAdd={(analyse) => {
                  setCustomFeeds((prev) => [...prev, analyse])
                  setSelectedFeedIds((prev) => new Set([...prev, `gfa_${analyse.id}`]))
                }}
                onClose={() => setShowGfaPicker(false)}
              />
            )}
          </div>
        )}

        {/* Step 3: Restrictions */}
        {step === 3 && (
          <div className="flex-1 p-8 grid grid-cols-1 lg:grid-cols-2 gap-12 overflow-auto">
            <div className="space-y-8">
              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-widest" style={{ color: C.accent }}>Harte Grenzen</h3>
                <p className="text-xs" style={{ color: C.muted }}>
                  TM-Band und die übrigen Grenzwerte gehen an den Solver (TM min/max sowie Mindest-/Höchst-Dichten für ME, Stärke und aNDFom auf Gesamtration-Basis; aNDFom GF min schärft die Struktur-Untergrenze).
                </p>
                <div className="space-y-4">
                  <div className="flex items-center justify-between gap-4">
                    <span className="text-sm font-medium text-slate-700">TM-Aufnahme (kg/Tag)</span>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        step={0.1}
                        value={wizardHardBounds.dmiMinKg}
                        onChange={(e) => {
                          const v = Number(e.target.value)
                          if (!Number.isFinite(v)) return
                          setWizardHardBounds((prev) => ({ ...prev, dmiMinKg: v }))
                        }}
                        className="w-16 border rounded px-2 py-1 text-sm text-center"
                        style={{ borderColor: C.border }}
                        aria-label="TM-Aufnahme Minimum kg pro Tag"
                      />
                      <span style={{ color: C.muted }}>–</span>
                      <input
                        type="number"
                        step={0.1}
                        value={wizardHardBounds.dmiMaxKg}
                        onChange={(e) => {
                          const v = Number(e.target.value)
                          if (!Number.isFinite(v)) return
                          setWizardHardBounds((prev) => ({ ...prev, dmiMaxKg: v }))
                        }}
                        className="w-16 border rounded px-2 py-1 text-sm text-center"
                        style={{ borderColor: C.border }}
                        aria-label="TM-Aufnahme Maximum kg pro Tag"
                      />
                    </div>
                  </div>
                  {([
                    { label: 'ME min (MJ/kg TM)', field: 'meMinMjPerKgDm' as const },
                    { label: 'Stärke max (% d. TM)', field: 'starchMaxPctTm' as const },
                    { label: 'aNDFom min (% d. TM)', field: 'andfomMinPctTm' as const },
                    { label: 'aNDFom GF min (% d. TM)', field: 'andfomGfMinPctTm' as const },
                  ]).map((row) => (
                    <div key={row.field} className="flex items-center justify-between gap-4">
                      <span className="text-sm font-medium text-slate-700">{row.label}</span>
                      <input
                        type="number"
                        step={0.1}
                        value={wizardHardBounds[row.field]}
                        onChange={(e) => {
                          const v = Number(e.target.value)
                          if (!Number.isFinite(v)) return
                          setWizardHardBounds((prev) => ({ ...prev, [row.field]: v }))
                        }}
                        className="w-16 border rounded px-2 py-1 text-sm text-center"
                        style={{ borderColor: C.border }}
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-widest" style={{ color: C.accent }}>Weiche Ziele</h3>
                <div className="space-y-2">
                  {([
                    { key: 'minimizeSoya' as const, label: 'Sojaanteil minimieren' },
                    { key: 'minimizeDeviationFromBaseline' as const, label: 'Änderungen zur Ist-Ration gering halten' },
                    { key: 'maximizeNEfficiencyRmd' as const, label: 'N-Effizienz maximieren (RMD)' },
                    { key: 'preferHomegrown' as const, label: 'Hofeigene Komponenten bevorzugen' },
                  ]).map((item) => (
                    <label key={item.key} className="flex items-center gap-3 p-3 bg-slate-50 border border-slate-100 rounded-xl cursor-pointer hover:bg-white transition-colors">
                      <input
                        type="checkbox"
                        checked={wizardSoftGoals[item.key]}
                        onChange={(e) => {
                          setWizardSoftGoals((prev) => ({ ...prev, [item.key]: e.target.checked }))
                        }}
                        className="w-4 h-4 rounded"
                        style={{ accentColor: C.accent }}
                      />
                      <span className="text-sm text-slate-700">{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="space-y-8">
              <div className="space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-widest" style={{ color: C.accent }}>Prioritäten</h3>
                <p className="text-xs" style={{ color: C.muted }}>
                  Gewichtung per Schieberegler (0–100). Aus den Werten wird eine Solver-Stufe abgeleitet (
                  <span className="font-semibold text-slate-600">{deriveObjectiveStrategy(mode, priorityWeights)}</span>
                  ); Details werden zusätzlich unter <code className="text-[11px]">policy_overrides.wizard_priorities</code> mitgeschickt.
                </p>
                {PRIORITY_SLIDER_ROWS.map(({ key, label }) => {
                  const val = priorityWeights[key]
                  return (
                    <div key={key} className="space-y-2">
                      <div className="flex justify-between items-center text-sm gap-3">
                        <span className="font-medium text-slate-700">{label}</span>
                        <span className="font-bold tabular-nums shrink-0 min-w-[3rem] text-right" style={{ color: C.accent }}>{val}%</span>
                      </div>
                      <input
                        type="range"
                        min={0}
                        max={100}
                        step={1}
                        value={val}
                        onChange={(e) => {
                          const n = Number(e.target.value)
                          setPriorityWeights((prev) => ({ ...prev, [key]: Number.isFinite(n) ? n : prev[key] }))
                        }}
                        className="w-full h-2 rounded-full appearance-none cursor-pointer bg-slate-100
                          [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4
                          [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-white
                          [&::-webkit-slider-thumb]:shadow [&::-webkit-slider-thumb]:bg-[#88B04B]
                          [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:border-2
                          [&::-moz-range-thumb]:border-white [&::-moz-range-thumb]:shadow-sm [&::-moz-range-thumb]:bg-[#88B04B]"
                        style={{ accentColor: C.accent }}
                        aria-label={`${label}: ${val} Prozent`}
                      />
                      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden -mt-1 pointer-events-none">
                        <div className="h-full rounded-full transition-[width] duration-75" style={{ width: `${val}%`, background: C.accent }} />
                      </div>
                    </div>
                  )
                })}
              </div>

              <div className="p-6 rounded-2xl text-white space-y-4" style={{ background: '#1B3022' }}>
                <div className="flex items-center gap-2 font-bold text-sm uppercase tracking-widest" style={{ color: C.accent }}>
                  <Sparkles size={16} /> AI-Vorschau
                </div>
                <p className="text-sm text-slate-300">
                  Basierend auf {selectedFeedIds.size} ausgewählten Futtermitteln und aktuellen Preisen kann eine optimale Ration berechnet werden.
                </p>
                <div className="flex items-center gap-2 text-xs font-bold" style={{ color: C.accent }}>
                  <Calculator size={14} /> Solver: GfE-2023 LP (HiGHS)
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer Nav */}
        <div className="h-20 border-t bg-white px-8 flex items-center justify-between sticky bottom-0" style={{ borderColor: C.border }}>
          <button
            onClick={step === 1 ? onCancel : () => setStep((s) => s - 1)}
            className="px-6 py-2.5 border font-bold rounded-xl hover:bg-slate-50 transition-all flex items-center gap-2"
            style={{ borderColor: C.border, color: '#374151' }}
          >
            <ArrowLeft size={18} /> {step === 1 ? 'Abbrechen' : 'Zurück'}
          </button>
          <button
            onClick={step === 3 ? handleComplete : () => setStep((s) => s + 1)}
            className="px-8 py-2.5 font-bold rounded-xl text-white shadow-lg transition-all hover:opacity-90 flex items-center gap-2"
            style={{ background: C.accent }}
          >
            {step === 3 ? 'Optimierung starten' : 'Weiter'} <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// FAN-MODE-V1 Panels: Bewertung + Constraint-Status
// ---------------------------------------------------------------------------

function FanCalibrationPanel({
  fan,
  policyProfile,
  seasonProfile,
  relaxationPolicy,
}: {
  fan: FanCalibrationPayload
  policyProfile?: string
  seasonProfile?: SeasonProfile | null
  relaxationPolicy?: RelaxationPolicy
}) {
  const mode = fan.mode
  const ref = fan.fani_final ?? fan.reference
  const converged = fan.converged
  const warnTol = fan.tolerance_warn ?? 0.1
  const lastDelta = fan.iterations?.length > 0
    ? Math.abs(fan.iterations[fan.iterations.length - 1]?.delta ?? 0)
    : 0
  const warnOpen = converged === true && lastDelta > warnTol
  const fallbackCount = fan.feeds_fallback ?? 0
  const totalCount = (fan.feeds_exact ?? 0) + (fan.feeds_mapped ?? 0) + (fan.feeds_fallback ?? 0)

  const modeLabel = mode === 'auto_iterative' ? 'Auto-iterativ' : mode === 'reference' ? 'Referenz' : 'Nur Bewertung'
  const badgeColor = converged === false ? C.error : converged === true ? C.success : C.muted

  return (
    <div className={card()}>
      <div className="flex items-center justify-between mb-2">
        <div className="text-[11px] uppercase font-bold tracking-[0.5px]" style={{ color: C.muted }}>
          FAN-Kalibrierung (GfE 2023)
        </div>
        <span
          className="text-[10px] font-bold px-2 py-0.5 rounded border"
          style={{ background: '#F9FAFB', borderColor: badgeColor, color: badgeColor }}
        >
          bewertet bei FAN {ref != null ? ref.toFixed(2) : '–'}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-1.5 text-[11px]">
        <div className="flex justify-between"><span style={{ color: C.muted }}>Modus</span><span className="font-semibold">{modeLabel}</span></div>
        <div className="flex justify-between"><span style={{ color: C.muted }}>Iterationen</span><span className="font-semibold">{fan.iteration_count ?? fan.iterations?.length ?? 0}</span></div>
        <div className="flex justify-between"><span style={{ color: C.muted }}>Toleranz</span><span className="font-mono">{fan.tolerance?.toFixed(3)}</span></div>
        <div className="flex justify-between">
          <span style={{ color: C.muted }}>Konvergiert</span>
          <span className="font-semibold" style={{ color: badgeColor }}>
            {converged === true ? 'ja' : converged === false ? 'nein' : '–'}
          </span>
        </div>
        {totalCount > 0 && (
          <div className="col-span-2 flex justify-between pt-1 border-t" style={{ borderColor: '#F3F4F6' }}>
            <span style={{ color: C.muted }}>Futterwert-Quelle</span>
            <span className="font-mono">
              {fan.feeds_exact ?? 0} exakt · {fan.feeds_mapped ?? 0} gemappt · {fallbackCount} fallback
            </span>
          </div>
        )}
        {(policyProfile || seasonProfile || relaxationPolicy) && (
          <div className="col-span-2 flex justify-between pt-1 border-t" style={{ borderColor: '#F3F4F6' }}>
            <span style={{ color: C.muted }}>Policy</span>
            <span className="font-mono text-[10px]">
              {policyProfile ?? '–'}
              {seasonProfile ? ` · ${seasonProfile}` : ''}
              {relaxationPolicy ? ` · ${relaxationPolicy}` : ''}
            </span>
          </div>
        )}
      </div>
      {warnOpen && (
        <div className="mt-2 text-[10px] px-2 py-1 rounded" style={{ background: C.deltaBg, borderColor: C.deltaBorder, color: C.deltaText }}>
          Hinweis: letzte Iteration hatte |dFANi|={lastDelta.toFixed(3)} (&gt; {warnTol.toFixed(2)}). Ergebnis weiter stabil, aber pruefen.
        </div>
      )}
      {fan.fallback_warning && (
        <div className="mt-2 text-[10px] px-2 py-1 rounded" style={{ background: '#FEF2F2', borderColor: '#FECACA', color: C.error }}>
          {fan.fallback_warning}
        </div>
      )}
      {fan.iterations && fan.iterations.length > 1 && (
        <details className="mt-2">
          <summary className="text-[10px] cursor-pointer" style={{ color: C.muted }}>
            Iterationsverlauf anzeigen
          </summary>
          <div className="mt-1 text-[10px] font-mono space-y-0.5">
            {fan.iterations.map((it, i) => (
              <div key={i} className="flex justify-between">
                <span>#{it.i + 1}</span>
                <span>FAN_in={it.fan_in.toFixed(2)} → FAN_out={it.fan_out?.toFixed?.(2) ?? '–'} (Δ={it.delta?.toFixed?.(3) ?? '–'})</span>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}

function ConstraintStatusPanel({
  items,
  summary,
}: {
  items: ConstraintStatusItem[]
  summary?: PenaltySummary
}) {
  const hardViolations = items.filter((it) => it.status === 'hard_violated')
  const softViolations = items.filter((it) => it.status === 'violated')
  const ok = items.filter((it) => it.status === 'ok')
  const totalPenalty = summary?.total ?? items.reduce((s, it) => s + (it.penalty_cost ?? 0), 0)

  return (
    <div className={card()}>
      <div className="flex items-center justify-between mb-2">
        <div className="text-[11px] uppercase font-bold tracking-[0.5px]" style={{ color: C.muted }}>
          Constraint-Status
        </div>
        <div className="text-[10px]" style={{ color: C.muted }}>
          {ok.length} OK · {softViolations.length} weich · {hardViolations.length} hart
        </div>
      </div>
      <div className="space-y-1 max-h-52 overflow-y-auto pr-1">
        {items.map((it, i) => {
          const color =
            it.status === 'hard_violated' ? C.error :
            it.status === 'violated' ? C.warn :
            C.success
          const klass = it.class ? ` · Klasse ${it.class}` : ''
          return (
            <div
              key={i}
              className="flex justify-between items-center text-[11px] py-1 border-b"
              style={{ borderColor: '#F3F4F6' }}
            >
              <span className="flex items-center gap-1.5">
                <span className="inline-block h-2 w-2 rounded-full" style={{ background: color }} />
                <span className="font-medium">{it.name}</span>
                <span className="text-[9px]" style={{ color: C.muted }}>
                  {it.kind}{klass}
                </span>
              </span>
              <span className="font-mono">
                {typeof it.actual === 'number' ? it.actual.toFixed(it.unit?.includes('g') ? 0 : 2) : '–'}
                <span className="opacity-60"> / {typeof it.target === 'number' ? it.target.toFixed(it.unit?.includes('g') ? 0 : 2) : '–'}</span>
                {it.unit ? <span className="text-[9px] ml-1" style={{ color: C.muted }}>{it.unit}</span> : null}
              </span>
            </div>
          )
        })}
      </div>
      {totalPenalty > 0 && (
        <div className="mt-2 pt-1 border-t" style={{ borderColor: '#F3F4F6' }}>
          <div className="flex justify-between text-[11px]">
            <span style={{ color: C.muted }}>Summe Strafkosten</span>
            <span className="font-semibold font-mono">{totalPenalty.toFixed(2)}</span>
          </div>
          {summary?.by_class && (
            <div className="flex justify-between text-[10px] mt-0.5 font-mono" style={{ color: C.muted }}>
              <span>Klassen A / B / C</span>
              <span>
                {summary.by_class.A.toFixed(2)} · {summary.by_class.B.toFixed(2)} · {summary.by_class.C.toFixed(2)}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// VIEW: Workbench (3-column)
// ---------------------------------------------------------------------------

function Workbench({
  feeds,
  wizardData,
  result,
  isOptimizing,
  error,
  onOptimize,
  onDemo,
  onReset,
  onGoReview,
  onGoWizard,
  onApplySuggestionPatch,
  chatSeed,
  tourStep,
  onTourNext: _onTourNext,
}: {
  feeds: FeedIngredient[]
  wizardData: WizardData | null
  result: OptimizationResult | null
  isOptimizing: boolean
  error: string | null
  onOptimize: () => void
  onDemo: () => void
  onReset: () => void
  onGoReview: () => void
  onGoWizard: () => void
  onApplySuggestionPatch: (patch: RationAdjustmentApplyPatch) => void
  chatSeed?: { role: 'ai' | 'user'; text: string }[]
  tourStep?: number | null
  onTourNext?: () => void
}) {
  const [activeVariant, setActiveVariant] = useState('Entwurf A')
  const [aiMessage, setAiMessage] = useState('')
  const defaultChat = chatSeed && chatSeed.length > 0
    ? chatSeed
    : [{ role: 'ai' as const, text: 'Guten Tag! Starten Sie die Optimierung oder beschreiben Sie Ihr Ziel.' }]
  const [chatLog, setChatLog] = useState<{ role: 'ai' | 'user'; text: string }[]>(defaultChat)

  const feedById = useMemo(() => buildFeedLookupMap(feeds, wizardData), [feeds, wizardData])

  const rationItems = result?.ration_items.filter((r) => r.kgdm > 0.001) ?? []
  const rationNameDupCounts = useMemo(() => {
    const m = new Map<string, number>()
    const items = result?.ration_items.filter((r) => r.kgdm > 0.001) ?? []
    for (const r of items) {
      m.set(r.name, (m.get(r.name) ?? 0) + 1)
    }
    return m
  }, [result?.ration_items])
  const totalKgdm = rationItems.reduce((s, r) => s + r.kgdm, 0)
  const totalCost = rationItems.reduce((s, r) => s + r.total_cost, 0)

  // Tour highlight: ring around active panel
  const TOUR_TARGETS = ['kpi-bar', 'feed-table', 'dlg-panel', 'ai-copilot']
  function tourRing(target: string): React.CSSProperties {
    const idx = TOUR_TARGETS.indexOf(target)
    return tourStep === idx ? { outline: `2.5px solid ${C.accent}`, outlineOffset: '2px' } : {}
  }

  const maeKg = (result?.forage_performance as any)?.supplemented?.milk_from_energy_kg as number | undefined
  const mapKg = (result?.forage_performance as any)?.supplemented?.milk_from_protein_kg as number | undefined
  const maeMapDiff = (maeKg != null && mapKg != null) ? Math.abs(maeKg - mapKg) : null
  const maeMapStatus: 'success' | 'warn' | 'error' =
    maeMapDiff == null ? 'warn' : maeMapDiff <= 2 ? 'success' : maeMapDiff <= 5 ? 'warn' : 'error'

  const kpis = result
    ? [
        { label: 'Kosten', value: fmt(result.total_cost_eur_day ?? 0), unit: '€/Kuh', status: 'success' as const },
        { label: 'ME (MJ/kg)', value: fmt(result.nutrient_supply.me_mj / (result.nutrient_supply.dmi_kg || 1), 2), unit: 'MJ/kg TM', status: 'success' as const },
        { label: 'sidP (g/d)', value: fmt(result.nutrient_supply.sidp_g, 0), unit: 'g/Tag', status: 'success' as const },
        {
          label: 'MaE / MaP',
          value: maeKg != null && mapKg != null ? `${fmt(maeKg, 1)} / ${fmt(mapKg, 1)}` : '–',
          unit: 'kg Milch',
          status: maeMapStatus,
          title: `Milch aus Energie: ${fmt(maeKg, 1)} kg · Milch aus Protein: ${fmt(mapKg, 1)} kg · Differenz ${fmt(maeMapDiff, 1)} kg (Ziel ≤2 kg)`,
        },
        { label: 'Stärke', value: fmt(((result.nutrient_supply.staerke_g ?? result.nutrient_supply.starch_g ?? 0) / (result.nutrient_supply.dmi_kg || 1) / 10), 1), unit: '%TM', status: 'success' as const },
        { label: 'GF-Anteil', value: fmt(result.nutrient_supply.forage_share_pct, 1), unit: '%', status: result.nutrient_supply.forage_share_pct >= 55 ? 'success' as const : 'warn' as const },
        { label: 'Struktur-SI', value: result.dlg_indicators?.strukturindex != null ? fmt(result.dlg_indicators.strukturindex, 0) : '–', unit: '', status: (result.dlg_indicators?.strukturindex_erfuellt ? 'success' : 'error') as 'success' | 'error' },
      ]
    : []

  const dlg = result?.dlg_indicators

  function handleAiSend() {
    if (!aiMessage.trim()) return
    setChatLog((prev) => [...prev, { role: 'user', text: aiMessage }])
    const msg = aiMessage.toLowerCase()
    let response = 'Verarbeite Ihre Anfrage...'
    if (msg.includes('warum') || msg.includes('rot') || msg.includes('fehler')) {
      response = result?.warnings?.length
        ? `Aktuelle Warnungen: ${result.warnings.slice(0, 2).join(' | ')}`
        : 'Keine kritischen Probleme gefunden. Die Ration ist pansensicher.'
    } else if (msg.includes('kosten') || msg.includes('günstig') || msg.includes('spar')) {
      response = `Aktuell ${fmt(result?.total_cost_eur_day ?? 0)} €/Kuh/Tag. Durch Reduzierung von Kraftfutter und Erhöhung von Grundfutter können weitere Einsparungen erzielt werden.`
    } else if (msg.includes('soja')) {
      response = 'Sojaschrot kann durch Rapsschrot oder DDGS ersetzt werden bei ähnlichem sidP-Niveau. Starten Sie eine neue Optimierung mit Soja deaktiviert.'
    } else if (msg.includes('struktur') || msg.includes('pansen')) {
      response = result?.dlg_indicators
        ? `Strukturindex: ${result.dlg_indicators.strukturindex ?? '–'} (Ziel ≥ 50). aNDFomGF: ${result.dlg_indicators.andfom_gf_kgdm} g/kg TM.`
        : 'Starten Sie zuerst eine Optimierung.'
    } else {
      response = 'Tipp: Fragen Sie nach "Kosten senken", "Soja ersetzen", "Strukturindex" oder "Warum ist die Ration nicht optimal?"'
    }
    setAiMessage('')
    setTimeout(() => setChatLog((prev) => [...prev, { role: 'ai', text: response }]), 400)
  }

  return (
    <div
      className="grid h-[calc(100vh-120px)] p-[15px] gap-[15px]"
      style={{ gridTemplateColumns: '220px 1fr 280px', background: C.bg }}
    >
      {/* ── Linke Sidebar ── */}
      <aside className="flex flex-col gap-[15px]">
        <div className={card()}>
          <div className="text-[11px] uppercase font-bold mb-2.5 tracking-[0.5px]" style={{ color: C.muted }}>Varianten</div>
          {[
            { name: 'Ist-Ration', price: '–' },
            { name: 'Entwurf A', price: result ? `${fmt(result.total_cost_eur_day ?? 0)} €` : '…' },
            { name: 'Entwurf B', price: '–' },
          ].map((v) => (
            <div
              key={v.name}
              onClick={() => setActiveVariant(v.name)}
              className="p-2 rounded text-[13px] mb-1 cursor-pointer flex justify-between border transition-all"
              style={{
                background: activeVariant === v.name ? C.activeBg : undefined,
                borderColor: activeVariant === v.name ? C.accent : 'transparent',
                color: activeVariant === v.name ? C.dark : C.muted,
                fontWeight: activeVariant === v.name ? 600 : undefined,
              }}
            >
              <span>{v.name}</span>
              <span style={{ opacity: 0.7 }}>{v.price}</span>
            </div>
          ))}
        </div>

        <div className={card()}>
          <div className="text-[11px] uppercase font-bold mb-2.5 tracking-[0.5px]" style={{ color: C.muted }}>Gruppeninfo</div>
          {[
            { label: 'Kühe', val: wizardData?.group.count ?? '–' },
            { label: 'Ziel-Milch', val: wizardData ? `${wizardData.milkYield} kg` : '–' },
            { label: 'KM', val: wizardData ? `${wizardData.group.bodyMass} kg` : '–' },
            { label: 'TM-Aufnahme', val: result ? `${fmt(result.nutrient_supply.dmi_kg, 1)} kg` : '–' },
            { label: 'Bewertung', val: wizardData ? (
              wizardData.fanMode === 'auto_iterative' ? 'Auto-iterativ' :
              wizardData.fanMode === 'reference' ? `FAN ${wizardData.fanReference.toFixed(1)}` :
              'Nur Bewertung'
            ) : '–' },
          ].map((row) => (
            <div key={row.label} className="flex justify-between text-[12px] py-1 border-b" style={{ borderColor: '#F3F4F6' }}>
              <span style={{ color: C.muted }}>{row.label}</span>
              <span className="font-bold">{row.val}</span>
            </div>
          ))}
        </div>

        <button
          className="w-full py-2 text-sm font-semibold rounded-lg border transition-colors hover:bg-slate-50"
          style={{ borderColor: C.border, color: C.dark }}
          onClick={onGoReview}
          disabled={!result}
        >
          → Review & Freigabe
        </button>
      </aside>

      {/* ── Mitte: Rationstabelle ── */}
      <main className="flex flex-col gap-[15px]">
        {/* Toolbar */}
        <div className="flex gap-[10px] flex-wrap">
          <button
            onClick={onOptimize}
            disabled={isOptimizing}
            className="px-4 py-2 rounded text-sm font-bold text-white flex items-center gap-2 transition-opacity hover:opacity-90"
            style={{ background: C.accent }}
          >
            {isOptimizing ? <Loader2 size={14} className="animate-spin" /> : <Calculator size={14} />}
            Optimieren
          </button>
          <button onClick={onDemo} disabled={isOptimizing} className="px-4 py-2 rounded text-sm font-semibold border transition-colors hover:bg-slate-50" style={{ borderColor: C.border }}>
            Demo
          </button>
          <button onClick={onReset} className="px-4 py-2 rounded text-sm font-semibold border transition-colors hover:bg-slate-50" style={{ borderColor: C.border }}>
            <RotateCcw size={14} />
          </button>
          <div className="flex-grow" />
          <button
            onClick={onGoReview}
            disabled={!result}
            className="px-4 py-2 rounded text-sm font-bold text-white flex items-center gap-2 transition-opacity hover:opacity-90 disabled:opacity-40"
            style={{ background: C.dark }}
          >
            Review <ArrowRight size={14} />
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="p-3 rounded-lg border text-sm flex items-start gap-2" style={{ background: '#FEF2F2', borderColor: '#FECACA', color: C.error }}>
            <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Table */}
        <div id="feed-table" className={cn(card('flex-grow overflow-hidden p-0'))} style={tourRing('feed-table')}>
          {isOptimizing ? (
            <div className="flex items-center justify-center h-full gap-3" style={{ color: C.muted }}>
              <Loader2 size={24} className="animate-spin" />
              <span className="text-sm font-medium">Optimierung läuft…</span>
            </div>
          ) : (
            <table className="w-full text-[12px]">
              <thead>
                <tr style={{ background: '#F9FAFB' }}>
                  {['Futtermittel', 'kg FM', 'kg TM', '% TM', 'ME (MJ)', 'sidP (g)', '€/Tag'].map((h) => (
                    <th key={h} className="py-2.5 px-2 border-b text-xs font-semibold text-[#4B5563] text-right first:text-left" style={{ borderColor: C.border }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rationItems.map((item) => {
                  const feed = feedById.get(item.feed_id)
                  const anteil = totalKgdm > 0 ? (item.kgdm / totalKgdm) * 100 : 0
                  const meBeitrag = feed ? item.kgdm * feed.me_mj_kgdm : 0
                  const sidpBeitrag = feed ? item.kgdm * feed.sidp_g_kgdm : 0
                  const dupName = (rationNameDupCounts.get(item.name) ?? 0) > 1
                  return (
                    <tr key={item.feed_id} className="border-b transition-colors hover:bg-slate-50 cursor-pointer" style={{ borderColor: '#F3F4F6' }}>
                      <td className="p-2 font-medium" style={{ color: C.dark }} title={dupName ? item.feed_id : undefined}>
                        {item.name}
                        {dupName ? (
                          <span className="text-slate-400 font-normal text-[11px] ml-1">({item.feed_id})</span>
                        ) : null}
                      </td>
                      <td className="p-2 text-right font-mono text-xs">{fmt(item.kgfm, 1)}</td>
                      <td className="p-2 text-right font-mono text-xs">{fmt(item.kgdm, 2)}</td>
                      <td className="p-2 text-right font-mono text-xs">{fmt(anteil, 1)}%</td>
                      <td className="p-2 text-right font-mono text-xs">{fmt(meBeitrag, 1)}</td>
                      <td className="p-2 text-right font-mono text-xs">{fmt(sidpBeitrag, 0)}</td>
                      <td className="p-2 text-right font-mono text-xs font-bold">{fmt(item.total_cost, 2)}</td>
                    </tr>
                  )
                })}
                {rationItems.length === 0 && (
                  <tr>
                    <td colSpan={7} className="py-16 text-center text-sm" style={{ color: C.muted }}>
                      Starten Sie die Optimierung oder laden Sie die Demo
                    </td>
                  </tr>
                )}
              </tbody>
              {rationItems.length > 0 && (
                <tfoot>
                  <tr className="font-bold" style={{ background: '#F9FAFB' }}>
                    <td className="p-2 text-sm" style={{ color: C.dark }}>Gesamt</td>
                    <td className="p-2 text-right font-mono text-xs">{fmt(rationItems.reduce((s, r) => s + r.kgfm, 0), 1)}</td>
                    <td className="p-2 text-right font-mono text-xs">{fmt(totalKgdm, 2)}</td>
                    <td className="p-2 text-right font-mono text-xs">100%</td>
                    <td className="p-2 text-right font-mono text-xs">{fmt(result?.nutrient_supply.me_mj ?? 0, 1)}</td>
                    <td className="p-2 text-right font-mono text-xs">{fmt(result?.nutrient_supply.sidp_g ?? 0, 0)}</td>
                    <td className="p-2 text-right font-mono text-xs">{fmt(totalCost, 2)}</td>
                  </tr>
                </tfoot>
              )}
            </table>
          )}
        </div>

        <RationWarningAdjustmentsPanel
          result={result}
          wizardData={wizardData}
          isOptimizing={isOptimizing}
          onApplySuggestion={onApplySuggestionPatch}
          onGoWizard={onGoWizard}
          onReoptimizeSame={onOptimize}
        />

        <RationBlocksPanel blocks={result?.ration_blocks ?? null} compact />
        <ForagePerformancePanel result={result} compact />
        <PastureRiskPanel risk={result?.pasture_risk ?? null} compact />
        {/* Slice 2: Konzentrat-Futterabruf-Staffel (nur gestaffelte Verteilungen). */}
        <ConcentrateCallUpPanel callUp={result?.concentrate_call_up ?? null} compact />
        {/* Slice 3: Misch- und Fuetterungsprotokoll (TMR-Mischmasse). */}
        <MixingProtocolPanel protocol={result?.mixing_protocol ?? null} compact />
      </main>

      {/* ── Rechte Spalte: KPI + AI ── */}
      <aside className="flex flex-col gap-[15px]">
        {/* KPI */}
        <div id="kpi-bar" className={card()} style={tourRing('kpi-bar')}>
          <div className="text-[11px] uppercase font-bold mb-2.5 tracking-[0.5px]" style={{ color: C.muted }}>KPI Status</div>
          <div className="grid grid-cols-2 gap-2">
            {kpis.map((kpi, i) => (
              <div key={i} className="border p-2 rounded text-center" style={{ background: '#F9FAFB', borderColor: C.border }} title={(kpi as any).title}>
                <div className="text-[10px] uppercase mb-1" style={{ color: C.muted }}>{kpi.label}</div>
                <div className="text-[15px] font-bold">{kpi.value}</div>
                <div
                  className="text-[10px] uppercase font-bold"
                  style={{ color: kpi.status === 'success' ? C.success : kpi.status === 'warn' ? C.warn : C.error }}
                >
                  {kpi.status === 'success' ? '✓ OK' : kpi.status === 'warn' ? '⚠ Grenze' : '✗ Fehlt'} {kpi.unit}
                </div>
              </div>
            ))}
            {kpis.length === 0 && (
              <div className="col-span-2 py-6 text-center text-xs" style={{ color: C.muted }}>Noch keine Ergebnisse</div>
            )}
          </div>
        </div>

        {/* FAN-Kalibrierung (GfE 2023) ---------------------------------------- */}
        {result?.fan_calibration && (
          <FanCalibrationPanel
            fan={result.fan_calibration}
            policyProfile={result.active_policy_profile}
            seasonProfile={result.season_profile ?? wizardData?.seasonProfile ?? null}
            relaxationPolicy={result.relaxation_policy}
          />
        )}

        {/* Constraint-Status: hart / weich mit Klasse A/B/C -------------------- */}
        {result?.constraint_status && result.constraint_status.length > 0 && (
          <ConstraintStatusPanel
            items={result.constraint_status}
            summary={result.penalty_summary}
          />
        )}

        {/* DLG Strukturkontrolle (kompakt).
            Reihenfolge spiegelt die Priorisierung nach DLG 01|2023 wider:
            Strukturindex + aNDFomGF sind die PRIMAEREN Planungsgroessen,
            peNDF ist eine KONTROLL-/VALIDIERUNGSGROESSE (darunter gruppiert). */}
        {dlg && (
          <div id="dlg-panel" className={card()} style={tourRing('dlg-panel')}>
            <div className="text-[11px] uppercase font-bold mb-2 tracking-[0.5px]" style={{ color: C.muted }}>DLG 01|25 / GfE-Workshop 2023</div>
            <div className="text-[10px] font-semibold uppercase tracking-[0.4px] mb-1" style={{ color: C.muted }}>
              Planung (primaer)
            </div>
            {[
              { label: 'Strukturindex', val: dlg.strukturindex != null ? `${fmt(dlg.strukturindex, 0)}` : '–', ok: dlg.strukturindex_erfuellt },
              {
                label: 'aNDFomGF',
                val: dlg.andfom_gf_starch_uplift != null && dlg.andfom_gf_base != null
                  ? `${fmt(dlg.andfom_gf_kgdm, 0)} g/kg TM (Ziel ${fmt(dlg.andfom_gf_base, 0)}+${fmt(dlg.andfom_gf_starch_uplift, 0)})`
                  : `${fmt(dlg.andfom_gf_kgdm, 0)} g/kg TM`,
                ok: dlg.andfom_gf_kgdm >= 200,
              },
              // DLG 01|25 Kap. 8.2: aNDFomGF + strukturwirksame Co-Produkte ist die
              // aktuell empfohlene Planungsgroesse (binaere Kaskade 200/280).
              ...(dlg.andfom_gf_cop_kgdm != null
                ? [{
                    label: 'aNDFomGF+CoP',
                    val: dlg.andfom_gf_cop_target_kgdm != null
                      ? `${fmt(dlg.andfom_gf_cop_kgdm, 0)} / ≥${fmt(dlg.andfom_gf_cop_target_kgdm, 0)} g/kg TM`
                      : `${fmt(dlg.andfom_gf_cop_kgdm, 0)} g/kg TM`,
                    ok: dlg.andfom_gf_cop_target_kgdm != null
                      ? dlg.andfom_gf_cop_kgdm >= dlg.andfom_gf_cop_target_kgdm
                      : null,
                  }]
                : []),
              { label: 'pabKH', val: `${fmt(dlg.pabkh_kgdm, 0)} g/kg TM`, ok: dlg.pabkh_kgdm <= 210 },
              { label: 'RMD', val: dlg.rmd_gn_kgdm != null ? `${fmt(dlg.rmd_gn_kgdm, 2)} g N/kg TM` : '–', ok: dlg.rmd_gn_kgdm != null ? (dlg.rmd_gn_kgdm >= -1 && dlg.rmd_gn_kgdm <= 0.5) : null },
            ].map((row) => (
              <div key={row.label} className="flex justify-between items-center text-[11px] py-1 border-b" style={{ borderColor: '#F3F4F6' }}>
                <span className="flex items-center gap-1.5">
                  <span className="inline-block h-2 w-2 rounded-full" style={{ background: row.ok === null ? '#94a3b8' : row.ok ? C.success : C.error }} />
                  {row.label}
                </span>
                <span className="font-mono font-medium">{row.val}</span>
              </div>
            ))}

            <div className="text-[10px] font-semibold uppercase tracking-[0.4px] mt-2 mb-1" style={{ color: C.muted }}>
              Kontrolle / Validierung (DLG 01|2023)
            </div>
            {/* peNDF-Status-Zeile: peNDF-Modell im kalibrierten Bereich oder Fallback. */}
            {dlg.pendf_model_status && (
              <div className="flex items-start gap-1.5 text-[10px] mb-1" style={{ color: C.muted }}>
                <span
                  className="inline-block h-2 w-2 rounded-full mt-0.5"
                  style={{ background: dlg.pendf_model_calibrated === false ? '#f59e0b' : '#94a3b8' }}
                />
                <span>{dlg.pendf_model_status}</span>
              </div>
            )}
            {[
              {
                label: 'peNDF (Kontrolle)',
                val: dlg.pendf_kgdm != null
                  ? `${fmt(dlg.pendf_kgdm, 0)} / ${fmt(dlg.pendf_min_kgdm ?? 0, 0)} g/kg TM`
                  : '–',
                ok: dlg.pendf_model_calibrated === false ? null : (dlg.pendf_erfuellt ?? null),
              },
              {
                label: 'Pansen-pH (sim.)',
                val: dlg.ph_predicted != null
                  ? (dlg.ph_formula_applicable === false
                      ? `${fmt(dlg.ph_predicted, 2)} (Formel ausserhalb Validitaetsbereich)`
                      : `${fmt(dlg.ph_predicted, 2)}`)
                  : '–',
                ok: dlg.ph_formula_applicable === false ? null : (dlg.ph_ok ?? null),
              },
              // DLG 01|25 Kap. 8.4: Fermentationsindex Kohlenhydrate (FIKH),
              // Ziel >= 50 %. Neutrale Ampel wenn keine NDFD-Werte verfuegbar.
              ...(dlg.fikh_pct !== undefined
                ? [{
                    label: 'FIKH',
                    val: dlg.fikh_pct != null
                      ? `${fmt(dlg.fikh_pct, 0)} % (Ziel ≥ 50)`
                      : (dlg.fikh_diagnose ? `– (${dlg.fikh_diagnose})` : '–'),
                    ok: dlg.fikh_pct != null ? (dlg.fikh_erfuellt ?? null) : null,
                  }]
                : []),
            ].map((row) => (
              <div key={row.label} className="flex justify-between items-center text-[11px] py-1 border-b" style={{ borderColor: '#F3F4F6' }}>
                <span className="flex items-center gap-1.5">
                  <span className="inline-block h-2 w-2 rounded-full" style={{ background: row.ok === null ? '#94a3b8' : row.ok ? C.success : C.error }} />
                  {row.label}
                </span>
                <span className="font-mono font-medium">{row.val}</span>
              </div>
            ))}
          </div>
        )}

        {/* DLG 01|2025-Policy-Profil-Auswertung (Tab. 13-15 Bandchecks) ------
            Zeigt die Leistungsstufen-Korridore des aktiven Profils und welche
            weichen Bandchecks verletzt sind. Penalty fliesst in Klasse B ein. */}
        {result?.policy_profile_evaluation && (
          <div className={card()}>
            <div className="flex items-center justify-between mb-2">
              <div className="text-[11px] uppercase font-bold tracking-[0.5px]" style={{ color: C.muted }}>
                Leistungsstufen-Check (DLG 01|2025)
              </div>
              <span
                className="text-[10px] font-bold px-2 py-0.5 rounded border"
                style={{
                  background: '#F9FAFB',
                  borderColor: result.policy_profile_evaluation.violation_count === 0 ? C.success : '#f59e0b',
                  color: result.policy_profile_evaluation.violation_count === 0 ? C.success : '#b45309',
                }}
              >
              {result.policy_profile_evaluation.violation_count === 0
                ? 'alle Baender im Korridor'
                : `${result.policy_profile_evaluation.violation_count} Abweichung(en)`}
              </span>
            </div>
            <div className="text-[11px] mb-2" style={{ color: C.muted }}>
              Profil: <span className="font-semibold">{result.policy_profile_evaluation.label ?? result.active_policy_profile}</span>
              {' · '}
              Strafe gesamt (Klasse B):{' '}
              <span className="font-mono">{(result.policy_profile_evaluation.penalty_total ?? 0).toFixed(2)}</span>
              {result.policy_profile_lp_mode === 'stage2_cost_plus_policy_slack' && (
                <span
                  className="ml-2 text-[10px] font-bold px-1.5 py-0.5 rounded border"
                  title="Die Policy-Baender sind als native Slack-Variablen im LP gebunden. Der Solver minimiert Kosten und Korridor-Abweichung gemeinsam."
                  style={{ background: '#ECFDF5', borderColor: C.success, color: C.success }}
                >
                  LP-Slack aktiv
                </span>
              )}
              {result.concentrate_max_lp_slack_kg != null && result.concentrate_max_lp_slack_kg > 0 && (
                <span
                  className="ml-2 text-[10px] font-bold px-1.5 py-0.5 rounded border"
                  title="Empfohlenes Konzentrat-Tagesmaximum wurde im Stage-2-LP mit einer Slack-Variable weich überschritten."
                  style={{ background: '#FFFBEB', borderColor: C.deltaBorder, color: C.deltaText }}
                >
                  KF-Tagesmax-Slack {fmt(result.concentrate_max_lp_slack_kg, 3)} kg TM
                </span>
              )}
            </div>
            <div className="space-y-0.5">
              {result.policy_profile_evaluation.bands.map((band) => {
                const dotBg = band.status === 'ok' ? C.success : '#f59e0b'
                const range = (band.target_min != null || band.target_max != null)
                  ? `${band.target_min != null ? fmt(band.target_min, 1) : '–'} … ${band.target_max != null ? fmt(band.target_max, 1) : '–'}`
                  : fmt(band.target, 1)
                return (
                  <div key={band.name} className="flex justify-between items-center text-[11px] py-1 border-b" style={{ borderColor: '#F3F4F6' }}>
                    <span className="flex items-center gap-1.5">
                      <span className="inline-block h-2 w-2 rounded-full" style={{ background: dotBg }} />
                      {band.name.replace(/^DLG-Policy:\s*/, '')}
                    </span>
                    <span className="font-mono text-[10px]">
                      {fmt(band.actual, 1)} {band.unit}
                      {' · Ziel '}
                      {range} {band.unit}
                      {band.status !== 'ok' && (
                        <span className="ml-1" style={{ color: '#b45309' }}>
                          (dev {fmt(band.deviation_norm ?? 0, 2)})
                        </span>
                      )}
                    </span>
                  </div>
                )
              })}
            </div>
            {/* LP-Slack-Details: welche Baender hat der Solver selbst relaxiert? */}
            {Array.isArray(result.policy_profile_lp_slacks) && result.policy_profile_lp_slacks.length > 0 && (
              <div className="mt-3 pt-2 border-t" style={{ borderColor: '#E5E7EB' }}>
                <div className="text-[10px] uppercase font-bold tracking-[0.5px] mb-1" style={{ color: C.muted }}>
                  LP-Solver-Slacks (aktive Korridor-Verletzungen)
                </div>
                {(() => {
                  const active = (result.policy_profile_lp_slacks ?? []).filter((s) => s.active)
                  if (active.length === 0) {
                    return (
                      <div className="text-[11px]" style={{ color: C.muted }}>
                        keine – alle Slacks sind 0 (Korridore eingehalten).
                      </div>
                    )
                  }
                  return (
                    <div className="space-y-0.5">
                      {active.map((s) => (
                        <div key={s.name} className="flex justify-between text-[11px] font-mono">
                          <span>{s.name.replace(/^DLG-Policy:\s*/, '')}</span>
                          <span>
                            slack {fmt(s.slack_value, 2)} {s.unit}
                            {' · '}Penalty {fmt(s.penalty_cost, 2)}
                          </span>
                        </div>
                      ))}
                      <div className="flex justify-between text-[11px] font-mono pt-1 border-t" style={{ borderColor: '#F3F4F6' }}>
                        <span className="font-semibold">Summe LP-Penalty</span>
                        <span>{fmt(result.policy_profile_lp_total_penalty ?? 0, 2)}</span>
                      </div>
                    </div>
                  )
                })()}
              </div>
            )}
          </div>
        )}

        {/* SARA-Safety-Reopt-Badge: nur sichtbar, wenn der Azidose-Schutz-Loop
            greifen musste. Zeigt, welche Constraints verschaerft wurden und ob
            das Problem geloest werden konnte. */}
        {result?.sara_safety_reopt?.triggered && (
          <div
            className={card()}
            style={{
              borderColor: result.sara_safety_reopt.resolved ? '#f59e0b' : '#dc2626',
              background: result.sara_safety_reopt.resolved ? '#fffbeb' : '#fef2f2',
            }}
          >
            <div className="flex items-center gap-2 mb-2">
              <span
                className="inline-block h-2.5 w-2.5 rounded-full"
                style={{ background: result.sara_safety_reopt.resolved ? '#f59e0b' : '#dc2626' }}
              />
              <div className="text-[11px] uppercase font-bold tracking-[0.5px]">
                SARA-Safety-Reopt {result.sara_safety_reopt.resolved ? 'aktiv (geloest)' : 'aktiv (ungeloest)'}
              </div>
            </div>
            {result.sara_safety_reopt.reason && (
              <div className="text-[11px] mb-2" style={{ color: C.muted }}>
                Ausloeser: {result.sara_safety_reopt.reason}
              </div>
            )}
            {(result.sara_safety_reopt.actions ?? []).length > 0 && (
              <ul className="text-[11px] list-disc pl-4 mb-2 space-y-0.5">
                {(result.sara_safety_reopt.actions ?? []).map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            )}
            {result.sara_safety_reopt.metrics_before && result.sara_safety_reopt.metrics_after && (
              <div className="grid grid-cols-2 gap-1 text-[11px] font-mono">
                <div className="font-semibold">vorher</div>
                <div className="font-semibold">nachher</div>
                <div>pH {result.sara_safety_reopt.metrics_before.ph_predicted ?? '–'}</div>
                <div>pH {result.sara_safety_reopt.metrics_after.ph_predicted ?? '–'}</div>
                <div>peNDF {result.sara_safety_reopt.metrics_before.pendf_kgdm ?? '–'}</div>
                <div>peNDF {result.sara_safety_reopt.metrics_after.pendf_kgdm ?? '–'}</div>
                <div>pabKH {result.sara_safety_reopt.metrics_before.pabkh_kgdm ?? '–'}</div>
                <div>pabKH {result.sara_safety_reopt.metrics_after.pabkh_kgdm ?? '–'}</div>
              </div>
            )}
            {result.sara_safety_reopt.resolution_note && (
              <div className="text-[11px] mt-2" style={{ color: C.muted }}>
                {result.sara_safety_reopt.resolution_note}
              </div>
            )}
          </div>
        )}

        {/* AI Copilot */}
        <div
          id="ai-copilot"
          className="flex flex-col flex-grow p-3 rounded-lg border"
          style={{ background: C.aiBg, borderColor: C.aiBorder, ...tourRing('ai-copilot') }}
        >
          <div className="text-[11px] uppercase font-bold mb-2.5 tracking-[0.5px]" style={{ color: C.aiText }}>AI-Copilot</div>
          <div className="flex-grow overflow-y-auto pr-1 flex flex-col gap-2 max-h-48">
            {chatLog.map((msg, i) => (
              <div
                key={i}
                className="p-2 rounded text-[12px] border-l-[3px] shadow-sm leading-relaxed"
                style={{
                  background: '#fff',
                  borderColor: msg.role === 'ai' ? '#0EA5E9' : C.accent,
                }}
              >
                {msg.text}
              </div>
            ))}
          </div>
          <div className="mt-2 flex gap-1">
            <input
              type="text"
              value={aiMessage}
              onChange={(e) => setAiMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAiSend()}
              placeholder="Frage den Copiloten…"
              className="flex-1 p-2 rounded border text-[12px] outline-none focus:border-sky-400 transition-all"
              style={{ borderColor: C.aiBorder }}
            />
            <button
              onClick={handleAiSend}
              className="p-2 rounded text-white transition-opacity hover:opacity-90"
              style={{ background: C.aiText }}
            >
              <Send size={14} />
            </button>
          </div>
          {/* Quick prompts */}
          <div className="mt-2 flex flex-wrap gap-1">
            {['Warum rot?', 'Kosten senken', 'Soja ersetzen', 'Strukturindex'].map((p) => (
              <button
                key={p}
                onClick={() => { setAiMessage(p); }}
                className="text-[10px] px-2 py-0.5 rounded border transition-colors hover:bg-white"
                style={{ borderColor: C.aiBorder, color: C.aiText }}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </aside>
    </div>
  )
}

// ---------------------------------------------------------------------------
// VIEW: Review & Freigabe
// ---------------------------------------------------------------------------

function Review({
  wizardData,
  result,
  onBack,
  onFinalize,
  isOptimizing,
  onGoWizard,
  onApplySuggestionPatch,
  onReoptimize,
}: {
  wizardData: WizardData | null
  result: OptimizationResult | null
  onBack: () => void
  onFinalize: () => void
  isOptimizing: boolean
  onGoWizard: () => void
  onApplySuggestionPatch: (patch: RationAdjustmentApplyPatch) => void
  onReoptimize: () => void
}) {
  const comparison = result
    ? [
        { label: 'Kosten/Kuh/Tag', ist: '–', neu: `${fmt(result.total_cost_eur_day ?? 0)} €`, delta: null },
        { label: 'ME (MJ/Tag)', ist: '–', neu: fmt(result.nutrient_supply.me_mj, 1), delta: null },
        { label: 'sidP (g/Tag)', ist: '–', neu: fmt(result.nutrient_supply.sidp_g, 0), delta: null },
        { label: 'GF-Anteil', ist: '–', neu: `${fmt(result.nutrient_supply.forage_share_pct, 1)} %`, delta: null },
        { label: 'Strukturindex', ist: '–', neu: result.dlg_indicators?.strukturindex != null ? fmt(result.dlg_indicators.strukturindex, 0) : '–', delta: null },
      ]
    : []

  const fpReview = result?.forage_performance
  let epReview: { ist: number; neu: number } | null = null
  const forageComparison = fpReview
    ? (() => {
        const ex = getMilkEpExcessKg(fpReview)
        epReview = ex
        return [
          {
            label: 'Milch aus Energie',
            ist: `${fmt(fpReview.forage_only.milk_from_energy_kg, 1)} kg`,
            soll: `${fmt(fpReview.target_milk_kg, 1)} kg`,
            neu: `${fmt(fpReview.supplemented.milk_from_energy_kg, 1)} kg`,
          },
          {
            label: 'Milch aus Protein',
            ist: `${fmt(fpReview.forage_only.milk_from_protein_kg, 1)} kg`,
            soll: `${fmt(fpReview.target_milk_kg, 1)} kg`,
            neu: `${fmt(fpReview.supplemented.milk_from_protein_kg, 1)} kg`,
          },
          {
            label: 'Limitierende Milchmenge',
            ist: `${fmt(fpReview.forage_only.limiting_milk_kg, 1)} kg`,
            soll: `${fmt(fpReview.target_milk_kg, 1)} kg`,
            neu: `${fmt(fpReview.supplemented.limiting_milk_kg, 1)} kg`,
          },
          {
            label: `Mehr „Milch aus Protein“ vs. Energie (max. ${MILK_EP_BALANCE_MAX_PROTEIN_EXCESS_KG} kg ≈ l)`,
            ist: `${fmt(ex.ist, 1)} kg`,
            soll: `≤ ${MILK_EP_BALANCE_MAX_PROTEIN_EXCESS_KG} kg`,
            neu: `${fmt(ex.neu, 1)} kg`,
          },
        ]
      })()
    : []

  const changeLog = result?.ration_items.filter((r) => r.kgdm > 0.001).slice(0, 5) ?? []

  return (
    <div className="flex-1 p-8 max-w-5xl mx-auto w-full space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight" style={{ color: C.dark }}>Review & Freigabe</h2>
          <p className="text-sm" style={{ color: C.muted }}>Prüfen Sie die optimierte Ration vor dem Export.</p>
        </div>
        {result?.status === 'optimal' && (
          <div
            className="px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest border flex items-center gap-2"
            style={{ background: C.activeBg, color: C.dark, borderColor: C.accent }}
          >
            <Sparkles size={14} /> Solver: Optimal
          </div>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className={card('space-y-2')}>
          <p className="text-[11px] uppercase font-bold tracking-[0.5px]" style={{ color: C.muted }}>Gruppe</p>
          <p className="text-lg font-bold" style={{ color: C.dark }}>{wizardData?.group.name ?? '–'}</p>
          <p className="text-xs" style={{ color: C.muted }}>{wizardData?.group.count} Kühe · {wizardData?.group.location}</p>
        </div>
        <div className={card('space-y-2')}>
          <p className="text-[11px] uppercase font-bold tracking-[0.5px]" style={{ color: C.muted }}>Primärziel</p>
          <p className="text-lg font-bold" style={{ color: C.dark }}>{wizardData?.mode ?? '–'}</p>
          <p className="text-xs" style={{ color: C.muted }}>{wizardData?.milkYield} kg Ziel-Milch · {wizardData?.feedingType}</p>
        </div>
        <div className="p-5 rounded-lg text-white shadow-md space-y-2" style={{ background: C.dark }}>
          <p className="text-[10px] font-bold opacity-70 uppercase tracking-widest">Futterkosten/Kuh/Tag</p>
          <p className="text-2xl font-black">{result ? `${fmt(result.total_cost_eur_day ?? 0)} €` : '–'}</p>
          {result?.total_cost_eur_100kg_milk && (
            <p className="text-[11px] opacity-80">{fmt(result.total_cost_eur_100kg_milk)} € / 100 kg Milch</p>
          )}
        </div>
      </div>

      {/* KPI Comparison */}
      <div className={card('overflow-hidden p-0')}>
        <div className="px-5 py-3 border-b flex justify-between font-bold text-[11px] uppercase tracking-widest" style={{ background: '#F9FAFB', borderColor: C.border, color: C.muted }}>
          <span>Kennzahl-Vergleich</span>
          <span>Ergebnisse</span>
        </div>
        <table className="w-full text-left border-collapse text-[12px]">
          <thead>
            <tr>
              <th className="px-4 py-2.5 border-b text-xs font-semibold" style={{ borderColor: C.border, color: '#4B5563' }}>Kennzahl</th>
              <th className="px-4 py-2.5 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }}>IST</th>
              <th className="px-4 py-2.5 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }}>NEU</th>
            </tr>
          </thead>
          <tbody>
            {comparison.map((row, i) => (
              <tr key={i} className="border-b hover:bg-slate-50 transition-colors" style={{ borderColor: '#F3F4F6' }}>
                <td className="px-4 py-2.5 font-bold text-[#374151]">{row.label}</td>
                <td className="px-4 py-2.5 text-right font-mono text-xs" style={{ color: C.muted }}>{row.ist}</td>
                <td className="px-4 py-2.5 text-right font-mono text-xs font-bold" style={{ color: C.accent }}>{row.neu}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <ForagePerformancePanel result={result} />

      <RationWarningAdjustmentsPanel
        result={result}
        wizardData={wizardData}
        isOptimizing={isOptimizing}
        onApplySuggestion={onApplySuggestionPatch}
        onGoWizard={onGoWizard}
        onReoptimizeSame={onReoptimize}
      />

      <PastureRiskPanel risk={result?.pasture_risk ?? null} />

      {forageComparison.length > 0 && (
        <div className={card('overflow-hidden p-0')}>
          <div className="px-5 py-3 border-b space-y-1" style={{ background: '#F9FAFB', borderColor: C.border }}>
            <div className="font-bold text-[11px] uppercase tracking-widest" style={{ color: C.muted }}>
              Grundfutterleistung und Ergänzung
            </div>
            <p className="text-[11px] leading-snug max-w-3xl" style={{ color: C.muted }}>
              Ziel (Profil) = gewünschte Milchleistung. E/P-Orientierung: Überhang Protein vs. Energie höchstens{' '}
              {MILK_EP_BALANCE_MAX_PROTEIN_EXCESS_KG} kg (≈ l). Fachliche Sicherheit vor Kosten.
            </p>
          </div>
          <table className="w-full text-left border-collapse text-[12px]">
            <thead>
              <tr>
                <th className="px-4 py-2.5 border-b text-xs font-semibold" style={{ borderColor: C.border, color: '#4B5563' }}>Kennzahl</th>
                <th className="px-4 py-2.5 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }}>IST Grundfutter</th>
                <th className="px-4 py-2.5 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }}>Ziel (Profil)</th>
                <th className="px-4 py-2.5 border-b text-xs font-semibold text-right" style={{ borderColor: C.border, color: '#4B5563' }}>NEU mit Kraftfutter</th>
              </tr>
            </thead>
            <tbody>
              {forageComparison.map((row) => {
                const isEpRow = row.label.includes('Mehr „Milch aus Protein“')
                const epOkIst = epReview && epBalanceWithinGuidance(epReview.ist)
                const epOkNeu = epReview && epBalanceWithinGuidance(epReview.neu)
                return (
                  <tr
                    key={row.label}
                    className="border-b hover:bg-slate-50 transition-colors"
                    style={{
                      borderColor: '#F3F4F6',
                      background: isEpRow && (!epOkIst || !epOkNeu) ? C.deltaBg : undefined,
                    }}
                  >
                    <td className="px-4 py-2.5 font-bold text-[#374151]">{row.label}</td>
                    <td
                      className="px-4 py-2.5 text-right font-mono text-xs"
                      style={{ color: isEpRow && !epOkIst ? C.deltaText : C.muted }}
                    >
                      {row.ist}
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono text-xs" style={{ color: C.deltaText }}>{row.soll}</td>
                    <td
                      className="px-4 py-2.5 text-right font-mono text-xs font-bold"
                      style={{ color: isEpRow && !epOkNeu ? C.deltaText : C.accent }}
                    >
                      {row.neu}
                    </td>
                  </tr>
                )
              })}
              <tr className="border-b" style={{ borderColor: '#F3F4F6' }}>
                <td className="px-4 py-2.5 font-bold text-[#374151]">Kraftfutter / Verdrängung</td>
                <td className="px-4 py-2.5 text-right font-mono text-xs" style={{ color: C.muted }}>–</td>
                <td className="px-4 py-2.5 text-right font-mono text-xs" style={{ color: C.deltaText }}>
                  {result?.forage_performance?.feeding_type}
                </td>
                <td className="px-4 py-2.5 text-right font-mono text-xs font-bold" style={{ color: C.accent }}>
                  {result?.forage_performance
                    ? `${fmt(result.forage_performance.supplemented.concentrate_dmi_kg, 2)} kg TM / ${fmt(result.forage_performance.supplemented.forage_displacement_dmi_kg, 2)} kg TM`
                    : '–'}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Change Log */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-widest" style={{ color: C.dark }}>Rationsvorschlag</h3>
          <ul className="space-y-2">
            {changeLog.map((item, i) => (
              <li key={i} className="flex items-center gap-3 p-3 bg-white border rounded-xl" style={{ borderColor: '#E5E7EB' }}>
                <TrendingUp size={16} style={{ color: C.accent }} />
                <span className="text-sm font-medium text-slate-600">
                  {item.name}: {fmt(item.kgfm, 1)} kg FM / {fmt(item.kgdm, 2)} kg TM
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Checklist */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-widest" style={{ color: C.dark }}>Sicherheits-Checkliste</h3>
          <div className="space-y-2">
            {(
              [
                { text: 'Analysewerte der Silagen aktuell', defaultChecked: true },
                { text: 'Marktpreise für Kraftfutter verifiziert', defaultChecked: true },
                { text: 'Verfügbarkeit der Komponenten bestätigt', defaultChecked: true },
                {
                  text: `E/P-Milchäquivalent: Überhang Protein vs. Energie ≤ ${MILK_EP_BALANCE_MAX_PROTEIN_EXCESS_KG} kg (≈ l) — IST & NEU`,
                  defaultChecked: Boolean(
                    epReview && epBalanceWithinGuidance(epReview.ist) && epBalanceWithinGuidance(epReview.neu),
                  ),
                },
                { text: 'Biologische Plausibilität geprüft (Pansen/RMD)', defaultChecked: false },
              ] as const
            ).map((check, i) => (
              <label key={i} className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl cursor-pointer group hover:bg-white border border-transparent hover:border-slate-200 transition-all">
                <input type="checkbox" defaultChecked={check.defaultChecked} className="w-5 h-5 rounded border-slate-300" style={{ accentColor: C.accent }} />
                <span className="text-sm font-medium text-slate-600 group-hover:text-slate-900 transition-colors">{check.text}</span>
              </label>
            ))}
          </div>
        </div>
      </div>


      {/* Footer */}
      <div className="flex items-center justify-between pt-8 border-t" style={{ borderColor: C.border }}>
        <button
          onClick={onBack}
          className="px-6 py-3 border font-bold rounded-xl hover:bg-slate-50 transition-all flex items-center gap-2"
          style={{ borderColor: C.border, color: '#374151' }}
        >
          <ArrowLeft size={18} /> Zurück editieren
        </button>
        <div className="flex gap-4">
          <button className="px-6 py-3 bg-white border font-bold rounded-xl flex items-center gap-2 hover:bg-slate-50 transition-all" style={{ borderColor: C.border, color: C.dark }}>
            <FileText size={18} /> PDF speichern
          </button>
          <button
            onClick={onFinalize}
            className="px-10 py-3 font-bold rounded-xl text-white shadow-xl flex items-center gap-2 transition-opacity hover:opacity-90"
            style={{ background: C.accent }}
          >
            Ration freigeben <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// ROOT PAGE
// ---------------------------------------------------------------------------

type AppView = 'dashboard' | 'wizard' | 'workbench' | 'review'

export default function Rationsoptimierung() {
  const [view, setView] = useState<AppView>('dashboard')
  const [wizardBoot, setWizardBoot] = useState<{
    key: number
    resumeFrom: WizardData | null
    initialStep: number
  }>({ key: 0, resumeFrom: null, initialStep: 1 })
  const [wizardData, setWizardData] = useState<WizardData | null>(null)
  const [result, setResult] = useState<OptimizationResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Demo-Modus
  const [demoMode, setDemoMode] = useState(false)
  const [demoOverlay, setDemoOverlay] = useState(false)
  const [demoScenarioIdx, setDemoScenarioIdx] = useState(0)
  const [tourStep, setTourStep] = useState<number | null>(null)
  const [demoChatSeed, setDemoChatSeed] = useState<{ role: 'ai' | 'user'; text: string }[]>([])

  const {
    data: feeds = [],
    isLoading: feedsLoading,
  } = useQuery({
    queryKey: ['rations-feeds'],
    queryFn: () => fetchFeeds(),
  })

  const optimizeMutation = useMutation({
    mutationFn: (nextWizardData: WizardData | null) => {
      if (!nextWizardData) return optimizeDemo()
      const profile: CowProfile = {
        breed: 'Holstein',
        body_weight_kg: nextWizardData.group.bodyMass,
        milk_kg_day: nextWizardData.milkYield,
        milk_fat_pct: nextWizardData.fatPercent,
        milk_protein_pct: nextWizardData.proteinPercent,
        lactation_stage_days: nextWizardData.group.lactationDays,
        parity: Math.round(nextWizardData.group.lactationNumber),
        target_dmi_kg: nextWizardData.dmiTarget,
        wizard_dmi_min_kg: nextWizardData.wizardHardBounds?.dmiMinKg,
        wizard_dmi_max_kg: nextWizardData.wizardHardBounds?.dmiMaxKg,
        feeding_type: nextWizardData.feedingType,
      }
      const totalAvail =
        feeds.length +
        (nextWizardData.customFeeds?.length ?? 0) +
        (nextWizardData.compoundFeeds?.length ?? 0)
      const feedIds = nextWizardData.selectedFeedIds.size < totalAvail
        ? [...nextWizardData.selectedFeedIds]
        : undefined
      const customOptimizerFeeds = [
        ...((nextWizardData.customFeeds ?? []).map((gfa) => ({ ...gfa, _source: 'gfa' }))),
        ...((nextWizardData.compoundFeeds ?? []).map((doc) => ({
          ...(doc.optimizer_feed as Record<string, unknown>),
          _source: 'compound_upload',
        }))),
      ]
      // min/max FM → TM-Grenzen für den Solver (kg FM × TM-Anteil = kg TM)
      const dmById = buildFeedDmById(feeds, nextWizardData)
      const maxFmMap = nextWizardData.feedMaxFm ?? {}
      const minFmMap = nextWizardData.feedMinFm ?? {}
      const maxTmOverrides = Object.keys(maxFmMap).length > 0
        ? Object.fromEntries(
            Object.entries(maxFmMap).map(([id, maxFm]) => [id, maxFm * (dmById.get(id) ?? 0.86)]),
          )
        : undefined
      const minTmOverrides = Object.keys(minFmMap).length > 0
        ? Object.fromEntries(
            Object.entries(minFmMap).map(([id, minFm]) => [id, minFm * (dmById.get(id) ?? 0.86)]),
          )
        : undefined
      const prio = nextWizardData.priorityWeights ?? DEFAULT_PRIORITY_WEIGHTS
      const hb = nextWizardData.wizardHardBounds ?? DEFAULT_WIZARD_HARD_BOUNDS
      const sg = nextWizardData.wizardSoftGoals ?? DEFAULT_WIZARD_SOFT_GOALS
      const objective_strategy = deriveObjectiveStrategy(nextWizardData.mode, prio)
      // FAN-MODE-V1: Bewertungsmodus + Relaxation aus Wizard durchreichen
      const extras = {
        objective_strategy,
        fan_options: {
          mode: nextWizardData.fanMode,
          ...(nextWizardData.fanMode === 'reference' ? { reference: nextWizardData.fanReference } : {}),
        },
        relaxation_policy: nextWizardData.relaxationPolicy,
        ...(nextWizardData.seasonProfile ? { season_profile: nextWizardData.seasonProfile } : {}),
        policy_overrides: {
          wizard_priorities: prio,
          wizard_hard_bounds: {
            me_min_mj_per_kg_dm: hb.meMinMjPerKgDm,
            starch_max_pct_tm: hb.starchMaxPctTm,
            andfom_min_pct_tm: hb.andfomMinPctTm,
            andfom_gf_min_pct_tm: hb.andfomGfMinPctTm,
          },
          wizard_soft_goals: {
            minimize_soya: sg.minimizeSoya,
            minimize_deviation_from_baseline: sg.minimizeDeviationFromBaseline,
            maximize_n_efficiency_rmd: sg.maximizeNEfficiencyRmd,
            prefer_homegrown: sg.preferHomegrown,
          },
        },
        ...(nextWizardData.policyProfile ? { policy_profile: nextWizardData.policyProfile } : {}),
        feeding_system_config: defaultFeedingSystemConfig(nextWizardData.feedingType),
      }
      if (nextWizardData.seasonProfile) {
        profile.season_profile = nextWizardData.seasonProfile
      }
      return optimizeFromProfile(
        profile,
        feedIds,
        customOptimizerFeeds.length > 0 ? customOptimizerFeeds : undefined,
        undefined,
        maxTmOverrides,
        minTmOverrides,
        extras,
      )
    },
    onSuccess: (data) => {
      setResult(data)
      setError(null)
      setView('workbench')
    },
    onError: (err: unknown) => {
      setError(getRationsApiErrorMessage(err, 'Optimierung fehlgeschlagen'))
    },
  })

  const openWizardFresh = useCallback(() => {
    setWizardBoot((b) => ({ key: b.key + 1, resumeFrom: null, initialStep: 1 }))
    setView('wizard')
  }, [])

  const openWizardReoptimize = useCallback((data: WizardData) => {
    setWizardBoot((b) => ({ key: b.key + 1, resumeFrom: data, initialStep: 2 }))
    setView('wizard')
  }, [])

  const handleApplySuggestionPatch = useCallback(
    (patch: RationAdjustmentApplyPatch) => {
      if (!wizardData) {
        openWizardFresh()
        return
      }
      const next = patchHasSolverKeys(patch) ? applyRationPatch(wizardData, patch) : wizardData
      setWizardData(next)
      optimizeMutation.mutate(next)
    },
    [wizardData, optimizeMutation, openWizardFresh],
  )

  const demoMutation = useMutation({
    mutationFn: optimizeDemo,
    onSuccess: (data) => {
      setResult(data)
      setError(null)
      setView('workbench')
    },
    onError: (err: unknown) => {
      setError(getRationsApiErrorMessage(err, 'Demo fehlgeschlagen'))
    },
  })

  const isOptimizing = optimizeMutation.isPending || demoMutation.isPending

  function handleWizardComplete(data: WizardData) {
    setWizardData(data)
    optimizeMutation.mutate(data)
  }

  function handleReset() {
    setWizardData(null)
    setResult(null)
    setError(null)
    setDemoMode(false)
    setDemoOverlay(false)
    setTourStep(null)
    setView('dashboard')
  }

  // Demo starten – Overlay zeigen → API-Call → Workbench + Tour
  const handleDemoStart = useCallback((scenarioIdx = 0) => {
    setDemoScenarioIdx(scenarioIdx)
    setDemoChatSeed(DEMO_SCENARIOS[scenarioIdx].chatSeed)
    setDemoOverlay(true)
  }, [])

  // Nachdem Overlay fertig ist und API-Ergebnis vorliegt
  const handleDemoOverlayDone = useCallback(() => {
    setDemoOverlay(false)
    setDemoMode(true)
    setTourStep(0)
    setView('workbench')
    demoMutation.mutate()
  }, [])  // eslint-disable-line react-hooks/exhaustive-deps

  // Szenario wechseln innerhalb Demo
  const handleDemoScenario = useCallback((idx: number) => {
    setDemoScenarioIdx(idx)
    setDemoChatSeed(DEMO_SCENARIOS[idx].chatSeed)
    setDemoOverlay(true)
  }, [])

  // Tab bar
  const TABS: { id: AppView; label: string }[] = [
    { id: 'dashboard', label: 'Startseite' },
    { id: 'wizard', label: 'Neue Ration' },
    { id: 'workbench', label: 'Rations-Workbench' },
    { id: 'review', label: 'Review & Freigabe' },
  ]

  return (
    <div className="min-h-screen flex flex-col" style={{ background: C.bg }}>
      {/* Demo Lade-Overlay */}
      {demoOverlay && (
        <DemoLoadingOverlay
          scenario={DEMO_SCENARIOS[demoScenarioIdx]}
          onDone={handleDemoOverlayDone}
        />
      )}

      {/* Tour Tooltip */}
      {demoMode && tourStep !== null && tourStep < TOUR_STEPS.length && (
        <TourTooltip
          step={TOUR_STEPS[tourStep]}
          onNext={() => tourStep < TOUR_STEPS.length - 1 ? setTourStep(tourStep + 1) : setTourStep(null)}
          onClose={() => setTourStep(null)}
        />
      )}

      {/* Header */}
      <header
        className="h-[50px] text-white flex items-center justify-between px-5 shadow-sm sticky top-0 z-50"
        style={{ background: C.dark }}
      >
        <div
          className="flex items-center gap-1 cursor-pointer font-bold text-lg leading-none tracking-widest uppercase"
          onClick={() => setView('dashboard')}
        >
          KLAR<span style={{ color: C.accent }}>AGRI</span>
          <span className="ml-3 text-[11px] font-normal opacity-60 normal-case tracking-normal">· VALEO NeuroERP</span>
        </div>
        <div className="flex items-center gap-5 text-[13px] opacity-90 font-medium">
          <span>GfE-2023 · HiGHS-Solver</span>
          <button className="hover:underline flex items-center gap-1" onClick={handleReset}>
            <RotateCcw size={14} /> Zurücksetzen
          </button>
        </div>
      </header>

      {/* Nav */}
      <nav
        className="h-[40px] bg-white border-b flex px-5 gap-[30px] items-center sticky z-40"
        style={{ top: 50, borderColor: C.border }}
      >
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              if (tab.id === 'workbench' && !result) return
              if (tab.id === 'review' && !result) return
              if (tab.id === 'wizard') {
                setWizardBoot((b) => ({ key: b.key + 1, resumeFrom: null, initialStep: 1 }))
              }
              setView(tab.id)
            }}
            className="font-semibold text-[13px] h-full flex items-center relative transition-colors cursor-pointer disabled:opacity-40"
            style={{ color: view === tab.id ? C.dark : C.muted }}
            disabled={(tab.id === 'workbench' || tab.id === 'review') && !result}
          >
            {tab.label}
            {view === tab.id && (
              <div className="absolute bottom-0 left-0 right-0 h-[3px] rounded-t" style={{ background: C.accent }} />
            )}
          </button>
        ))}
      </nav>

      {/* Demo Banner (unterhalb Nav) */}
      {demoMode && (
        <DemoBanner
          scenario={DEMO_SCENARIOS[demoScenarioIdx]}
          scenarioIdx={demoScenarioIdx}
          tourStep={tourStep}
          onScenario={handleDemoScenario}
          onNextTour={() => tourStep !== null && tourStep < TOUR_STEPS.length - 1 ? setTourStep(tourStep + 1) : setTourStep(null)}
          onPrevTour={() => tourStep !== null && tourStep > 0 ? setTourStep(tourStep - 1) : undefined}
          onExit={handleReset}
        />
      )}

      {/* Content */}
      <main className="flex-1 flex flex-col w-full overflow-auto">
        {view === 'dashboard' && (
          <Dashboard onStart={openWizardFresh} onDemo={() => handleDemoStart(0)} />
        )}
        {view === 'wizard' && (
          <Wizard
            key={wizardBoot.key}
            feeds={feeds}
            feedsLoading={feedsLoading}
            resumeFrom={wizardBoot.resumeFrom}
            initialStep={wizardBoot.initialStep}
            onComplete={handleWizardComplete}
            onCancel={() => setView('dashboard')}
          />
        )}
        {view === 'workbench' && (
          <Workbench
            key={`wb-${demoScenarioIdx}`}
            feeds={feeds}
            wizardData={wizardData}
            result={result}
            isOptimizing={isOptimizing}
            error={error}
            onOptimize={() => optimizeMutation.mutate(wizardData)}
            onDemo={() => demoMutation.mutate()}
            onReset={handleReset}
            onGoReview={() => setView('review')}
            onGoWizard={() => (wizardData ? openWizardReoptimize(wizardData) : openWizardFresh())}
            onApplySuggestionPatch={handleApplySuggestionPatch}
            chatSeed={demoChatSeed}
            tourStep={tourStep}
            onTourNext={() => tourStep !== null && tourStep < TOUR_STEPS.length - 1 ? setTourStep(tourStep + 1) : setTourStep(null)}
          />
        )}
        {view === 'review' && (
          <Review
            wizardData={wizardData}
            result={result}
            onBack={() => setView('workbench')}
            onFinalize={() => {
              setView('dashboard')
            }}
            isOptimizing={isOptimizing}
            onGoWizard={() => (wizardData ? openWizardReoptimize(wizardData) : openWizardFresh())}
            onApplySuggestionPatch={handleApplySuggestionPatch}
            onReoptimize={() => optimizeMutation.mutate(wizardData)}
          />
        )}
      </main>

      <StatusBar result={result} />

      <p className="text-center text-[10px] pb-1 pt-0" style={{ color: C.muted }}>
        Entscheidungshilfe · ersetzt keine fachliche Beratung · GfE-2023 · DLG-Information 01|25
      </p>
    </div>
  )
}
