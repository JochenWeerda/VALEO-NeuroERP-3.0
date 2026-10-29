import { useEffect, useMemo, useRef, useState } from 'react'
import { isAxiosError } from 'axios'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { createStudioPreviewPlan } from '@/components/mask-builder/render-plan/studio-preview'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import { Button } from '@/components/ui/button'
import { calculateStudioHarvest, type HarvestPreviewResult } from '@/lib/api/studio'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { mockRowsFor } from './studio-reducer'

const sample = {
  delivered_quantity_kg: 25000, unit_price_eur_per_ton: 220, vat_rate_percent: 0,
  impurities_free_pct: 2, windage_pct: 0, impurities_pct: 3, moisture_pct: 0,
  quality_limit_pct: 2,
  hl_weight_kg_per_hl: 76, storage_shrinkage_pct: 0, storage_fee_per_month: 0,
  storage_months: 0, freight_costs: 100, weighing_fees: 15,
}

function calculationError(failure: unknown, definition: ScreenDefinition): string {
  if (isAxiosError<{ detail?: Array<{ loc?: unknown[]; type?: string; ctx?: { gt?: number; ge?: number; le?: number } }> }>(failure)) {
    const detail = failure.response?.data?.detail
    if (Array.isArray(detail)) return detail.map(item => {
      const key = item.loc?.at(-1)
      const label = definition.fields?.find(field => field.key === key)?.label ?? 'Eingabe'
      if (item.type === 'greater_than') return `${label}: muss größer als ${item.ctx?.gt ?? 0} sein.`
      if (item.type === 'greater_than_equal') return `${label}: muss mindestens ${item.ctx?.ge ?? 0} sein.`
      if (item.type === 'less_than_equal') return `${label}: darf höchstens ${item.ctx?.le ?? 0} sein.`
      if (item.type === 'missing') return `${label}: ist erforderlich.`
      return `${label}: ungültiger Wert. Bitte Zahlenformat und Wertebereich prüfen.`
    }).join(' ')
  }
  const message = getAxiosErrorMessage(failure)
  return message.split(';').map(part => {
    const field = definition.fields?.find(item => part.includes(item.key))
    if (!field) return part.trim()
    const lower = /greater than (?:or equal to )?([\d.]+)/.exec(part)
    const upper = /less than (?:or equal to )?([\d.]+)/.exec(part)
    if (lower) return `${field.label}: muss ${part.includes('or equal to') ? 'mindestens' : 'größer als'} ${lower[1]} sein.`
    if (upper) return `${field.label}: darf ${part.includes('or equal to') ? 'höchstens' : 'nur weniger als'} ${upper[1]} sein.`
    return `${field.label}: ungültiger Wert. Bitte Zahlenformat und Wertebereich prüfen.`
  }).join(' ')
}

export function StudioPreview({ definition }: { definition: ScreenDefinition }): JSX.Element {
  const semantic = (definition as ScreenDefinition & { studioSemantic?: { contract: string } }).studioSemantic
  const supported = semantic?.contract === 'agrar.harvest.manual-preview.v1'
  const { plan, suppressedWidgets } = useMemo(() => createStudioPreviewPlan(
    compileRenderPlanFromScreenDefinition(definition)), [definition])
  const form = useUniversalFormState({ screen: definition })
  const [result, setResult] = useState<HarvestPreviewResult>()
  const [error, setError] = useState<string>()
  const [busy, setBusy] = useState(false)
  const generation = useRef(0)
  const fingerprint = JSON.stringify(form.values)
  const previewValues = useMemo<Record<string, unknown>>(() => JSON.parse(fingerprint) as Record<string, unknown>, [fingerprint])
  useEffect(() => {
    const allowed = new Set([...(definition.fields ?? []), ...(definition.tabs ?? []).flatMap(tab => tab.fields ?? [])].map(field => field.key))
    if (Object.keys(previewValues).some(key => !allowed.has(key))) {
      form.resetForm(Object.fromEntries(Object.entries(previewValues).filter(([key]) => allowed.has(key))))
    }
  }, [definition, previewValues, form.resetForm])
  useEffect(() => {
    const request = ++generation.current
    setResult(undefined)
    setError(undefined)
    setBusy(false)
    if (!supported || form.validationPlan.hasBlockingErrors || Object.keys(previewValues).length === 0) return
    const timer = setTimeout(() => {
      setBusy(true)
      void calculateStudioHarvest(previewValues).then(next => {
        if (generation.current === request) setResult(next)
      }).catch(failure => {
        if (generation.current === request) setError(calculationError(failure, definition))
      }).finally(() => { if (generation.current === request) setBusy(false) })
    }, 450)
    return () => { clearTimeout(timer); generation.current++ }
  }, [previewValues, supported, form.validationPlan.hasBlockingErrors, definition])
  const tables = supported ? { calculation: result?.positions ?? [] } : mockRowsFor(definition)
  return <>
    {suppressedWidgets.length > 0 && <p className="p-3 text-sm text-muted-foreground">
      Ohne Live-Zugriff in dieser Vorschau: {suppressedWidgets.join(', ')}. Diese Ansichten benötigen eine eigene Abnahme.
    </p>}
    {supported && <div className="space-y-2 border-b p-3">
      <p className="text-sm font-medium">Interaktive Kalkulationsprobe · keine Buchung · keine Freigabewirkung</p>
      <Button type="button" variant="outline" onClick={() => form.resetForm(Object.fromEntries(
        Object.entries(sample).filter(([key]) => definition.fields?.some(field => field.key === key)),
      ))}>Synthetische Beispieldaten laden</Button>
      <p className="text-xs">Beispiel-Steuersatz 0 % ist ein Testwert. Für die Probe ausdrücklich wählen; keine Steuerempfehlung.</p>
      {busy && <p role="status">Berechnung läuft…</p>}
      {error && <p role="alert">Berechnung gesperrt: {error}</p>}
      {result && <div aria-live="polite" data-testid="studio-calculation-result">
        <p>Netto: {result.total_net_amount_eur} EUR · Steuer: {result.total_vat_amount_eur} EUR · Brutto: {result.total_gross_amount_eur} EUR</p>
        <p>Qualitätsgrenze: {result.quality_limit_exceeded == null ? 'nicht bewertet' : result.quality_limit_exceeded ? 'überschritten' : 'eingehalten'} · Vertragsfreigabe: nicht erteilt</p>
        <ul className="list-disc pl-4 text-xs">{result.warnings.map(warning => <li key={warning}>{warning}</li>)}</ul>
      </div>}
    </div>}
    <UniversalMaskRenderer plan={plan} tables={tables} formState={form} hideFormSubmit />
  </>
}
