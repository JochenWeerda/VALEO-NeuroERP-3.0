import type { RenderPlan } from '../../render-plan/types'
import { canDomainAction, fieldsEditable, useDomainDispatch } from './domain-runtime'
import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useToast } from '@/hooks/use-toast'
import { api } from '@/lib/axios'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { summarizeSupplyTransfer } from '@/lib/domain-depth'
import { summarizeSupplyOps } from '@/lib/professional-control-centers'
import { normalizeOperationalStatus } from '@/lib/operational-status'

export type RohwareFormState = {
  lieferant: string
  kennzeichen: string
  lieferscheinNr: string
  datum: string
  artikel: string
  bruttoKg: number
  taraKg: number
  lagerZiel: string
  feuchtePct: string
  besatzPct: string
  fallzahl: string
  customer_id: string
}

export type HarvestAcceptanceResponse = {
  id: string
  acceptance_number?: string
  status?: string
}

export const ARTIKEL_OPTIONEN = [
  'Weizen',
  'Gerste',
  'Raps',
  'Mais',
  'Sonnenblumen',
  'Sonstige',
] as const

export const LAGER_OPTIONEN = [
  { id: 'Silo 1', label: 'Silo 1', description: 'Weizen / Roggen' },
  { id: 'Silo 2', label: 'Silo 2', description: 'Gerste / Hafer' },
  { id: 'Hauptlager', label: 'Hauptlager', description: 'Schüttgut allgemein' },
  { id: 'Außenlager', label: 'Außenlager', description: 'Sonderlager / Saisonware' },
]

const EDIT_KEYS: Array<keyof RohwareFormState> = [
  'lieferant', 'kennzeichen', 'lieferscheinNr', 'datum', 'artikel',
  'bruttoKg', 'taraKg', 'lagerZiel', 'feuchtePct', 'besatzPct', 'fallzahl', 'customer_id',
]

export function useRohwareController(plan: RenderPlan) {
  const navigate = useNavigate()
  const { toast } = useToast()
  const isTouch = useTouchDevice()
  const { data: chain } = useSupplyChainOverview()
  const supplyOps = useMemo(() => summarizeSupplyOps(chain), [chain])
  const transferSummary = useMemo(() => summarizeSupplyTransfer(chain), [chain])

  const [form, setForm] = useState<RohwareFormState>({
    lieferant: '',
    kennzeichen: '',
    lieferscheinNr: '',
    datum: new Date().toISOString().slice(0, 16),
    artikel: '',
    bruttoKg: 0,
    taraKg: 0,
    lagerZiel: '',
    feuchtePct: '',
    besatzPct: '',
    fallzahl: '',
    customer_id: '',
  })
  const [acceptanceResult, setAcceptanceResult] = useState<HarvestAcceptanceResponse | null>(null)
  const [submitting, setSubmitting] = useState(false)

  function updateField<K extends keyof RohwareFormState>(key: K, value: RohwareFormState[K]): void {
    if (!plan.fieldsByKey[key]?.visible || plan.fieldsByKey[key]?.readOnly) return
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const nettoKg = useMemo(
    () => Math.max(0, form.bruttoKg - form.taraKg),
    [form.bruttoKg, form.taraKg],
  )
  const operationalStatus = normalizeOperationalStatus(
    form.artikel && nettoKg > 0
      ? 'in_pruefung'
      : supplyOps.pressure === 'hoch'
        ? 'eskaliert'
        : 'offen',
  )
  const operationalBlocker = !form.lagerZiel && form.artikel
    ? 'Lagerziel ist fuer die Annahme noch nicht festgelegt.'
    : supplyOps.pressure === 'hoch'
      ? `Physische Kette unter Druck: ${supplyOps.bottleneck}.`
      : null
  const operationalNextAction = !form.lieferant
    ? 'Lieferant und Kennzeichen erfassen'
    : !form.artikel
      ? 'Ware und Lagerziel festlegen'
      : nettoKg <= 0
        ? 'Brutto/Tara pruefen und Nettogewicht absichern'
        : 'Annahme pruefen und uebernehmen'
  const contextSections = [
    {
      title: 'Vorgang',
      items: [
        { label: 'Lieferant', value: form.lieferant || 'Noch offen' },
        { label: 'Kennzeichen', value: form.kennzeichen || 'Noch offen' },
        { label: 'Lieferschein', value: form.lieferscheinNr || 'Noch offen' },
      ],
    },
    {
      title: 'Ressourcenlage',
      items: [
        { label: 'Artikel', value: form.artikel || 'Nicht zugewiesen' },
        { label: 'Netto', value: `${nettoKg.toLocaleString('de-DE')} kg` },
        { label: 'Lagerziel', value: form.lagerZiel || 'Nicht festgelegt' },
      ],
    },
    {
      title: 'Betrieb',
      items: [
        { label: 'Bottleneck', value: supplyOps.bottleneck },
        { label: 'Druck', value: supplyOps.pressure },
        { label: 'Naechster Hebel', value: supplyOps.nextAction },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Annahmekontext geladen', detail: `${chain.waitingInbound} offene Annahmen in der Warteschlange.` },
    ...(form.datum ? [{ label: 'Geplanter Erfassungszeitpunkt', timestamp: new Date(form.datum).toISOString() }] : []),
    form.artikel
      ? { label: 'Ware zugeordnet', detail: `${form.artikel} -> ${form.lagerZiel || 'Lagerziel offen'}` }
      : { label: 'Vorgang angelegt', detail: 'Lieferant, Fahrzeug und Ware werden jetzt aufgenommen.' },
  ]

  function validateRohwareStep(stepId: string): string | null {
    if (stepId === 'lieferant-fahrzeug') {
      if (!form.lieferant.trim()) return 'Lieferant ist ein Pflichtfeld.'
      if (!form.kennzeichen.trim()) return 'Kennzeichen ist ein Pflichtfeld.'
      return null
    }
    if (stepId === 'ware-gewicht') {
      if (!form.artikel.trim()) return 'Bitte einen Artikel auswaehlen.'
      if (!form.lagerZiel.trim()) return 'Bitte ein Lagerziel auswaehlen.'
      if (nettoKg <= 0) return 'Nettogewicht muss groesser 0 kg sein (Brutto und Tara pruefen).'
      return null
    }
    return null
  }

  function handleRohwareStepValidationError(_stepId: string, message: string): void {
    toast({ title: 'Schritt unvollstaendig', description: message, variant: 'destructive' })
  }

  async function handleSubmit(): Promise<void> {
    if (submitting || !canDomainAction(plan, 'submit') || !fieldsEditable(plan, EDIT_KEYS as unknown as string[])) return
    const err = validateRohwareStep('lieferant-fahrzeug') || validateRohwareStep('ware-gewicht')
    if (err) { handleRohwareStepValidationError('ware-gewicht', err); return }
    setSubmitting(true)
    try {
      const { data } = await api.post<HarvestAcceptanceResponse>('/api/v1/agrar/harvest-acceptance/rohware', {
        acceptance_mode: 'STORAGE_ONLY',
        artikel: form.artikel,
        brutto_kg: form.bruttoKg,
        tara_kg: form.taraKg,
        netto_kg: nettoKg,
        feuchte_pct: form.feuchtePct ? Number(form.feuchtePct) : null,
        besatz_pct: form.besatzPct ? Number(form.besatzPct) : null,
        fallzahl: form.fallzahl ? Number(form.fallzahl) : null,
        lieferant: form.lieferant,
        kennzeichen: form.kennzeichen,
        lieferschein_nr: form.lieferscheinNr,
        lager_ziel: form.lagerZiel,
        datum: form.datum || new Date().toISOString(),
        is_rohware: true,
        customer_id: form.customer_id || null,
      })
      setAcceptanceResult(data)
      toast({
        title: 'Rohware-Annahme gespeichert',
        description: `Annahmenummer: ${data.acceptance_number ?? data.id}`,
      })
    } catch (_rawErr: unknown) {
      const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string }
      toast({
        title: 'Fehler beim Speichern',
        description: e.response?.data?.detail ?? e.message ?? 'Unbekannter Fehler',
        variant: 'destructive',
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleFinish = (): void => {
    if (submitting) return
    void handleSubmit()
  }

  const shortcuts = buildCoreMaskShortcuts({
    onSave: handleFinish,
    onCancel: () => navigate('/annahme/warteschlange'),
    isSaveDisabled: submitting,
  })
  useKeyboardShortcuts(shortcuts)

  useDomainDispatch(plan, {
    submit: handleSubmit,
    cancel: () => navigate('/annahme/warteschlange'),
    billing: () => navigate('/annahme/abrechnung', {
      state: {
        fromQualitaetsCheck: true,
        artikel: form.artikel,
        feuchtigkeit: form.feuchtePct ? Number(form.feuchtePct) : 0,
        verunreinigung: form.besatzPct ? Number(form.besatzPct) : 0,
      },
    }),
  })

  return {
    plan,
    navigate,
    isTouch,
    chain,
    supplyOps,
    transferSummary,
    form,
    updateField,
    nettoKg,
    operationalStatus,
    operationalBlocker,
    operationalNextAction,
    contextSections,
    timelineItems,
    acceptanceResult,
    submitting,
    validateRohwareStep,
    handleRohwareStepValidationError,
    handleFinish,
    shortcuts,
  }
}

export type RohwareState = ReturnType<typeof useRohwareController>
