import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { isAxiosError } from 'axios'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { NativeSelect } from '@/components/ui/native-select'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { Calculator, FileText, Save, Truck } from 'lucide-react'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { buildDecisionView } from '@/policy/decision-view'
import { ProcessStatusPanel } from '@/components/workflow/ProcessStatusPanel'
import { useApprovalDensityProfile } from '@/features/workflow/useApprovalDensityProfile'
import { CompactDecisionCard } from '@/components/workflow/CompactDecisionCard'

type DeductionType = 'drying' | 'cleaning' | 'freight' | 'other'
type DeductionMode = 'per_ton' | 'fixed'

type SettlementDeduction = {
  id: string
  deduction_type: DeductionType
  mode: DeductionMode
  rate_per_ton_eur?: number | null
  fixed_amount_eur?: number | null
  basis_quantity_tons?: number | null
  amount_eur: number
  note?: string | null
}

type Settlement = {
  id: string
  settlement_number: string
  supplier_id: string
  article_id?: string | null
  gross_quantity_kg: number
  billing_quantity_kg: number
  unit_price_eur_per_ton: number
  gross_amount_eur: number
  total_deductions_eur: number
  net_amount_eur: number
  status: 'draft' | 'posted' | 'cancelled'
  posted_journal_ref?: string | null
  approval_status: 'ENTWURF' | 'ZUR_FREIGABE' | 'TEILWEISE_FREIGEGEBEN' | 'FREIGEGEBEN' | 'ABGELEHNT' | 'VERBUCHT'
  approval_history: Array<{
    actor_id: string
    actor_type: string
    previous_status: string
    new_status: string
    reason: string
    decided_at: string
  }>
  allowed_transitions: string[]
  can_post_fibu: boolean
  correction_options: Array<{
    memo_type: 'credit' | 'debit' | 'rework'
    label: string
    reason: string
  }>
  reference_context?: {
    process_key: string
    anchor_entity: string
    anchor_id: string
    chain: Record<string, string>
  } | null
  exception_hints?: Array<{
    rule_id: string
    category: string
    decision_mode: string
    requires_approval: boolean
    approver_roles: string[]
    description: string
  }>
  explainability?: unknown
  deductions: SettlementDeduction[]
  /** Optimistic locking (Backend AgrarSettlement.row_version) */
  row_version?: number
  created_at?: string | null
}

type SettlementFreigabeResponse = {
  allowed: boolean
  reason: string
  new_status: string
  previous_status: string
}

function settlementRowVersion(s: Settlement): number {
  return typeof s.row_version === 'number' && s.row_version >= 1 ? s.row_version : 1
}

function describeApiError(e: unknown): string {
  if (isAxiosError(e)) {
    const d = e.response?.data?.detail
    if (typeof d === 'string') return d
    if (d && typeof d === 'object' && 'message' in d && typeof (d as { message: unknown }).message === 'string') {
      return (d as { message: string }).message
    }
  }
  return e instanceof Error ? e.message : 'Anfrage fehlgeschlagen'
}

type BillingPreview = {
  net_weight_kg: number
  billing_weight_kg: number
  deduction_kg: number
  moisture_factor: number
  impurities_factor: number
}

type SettlementPreview = {
  gross_quantity_kg: number
  billing_quantity_kg: number
  gross_amount_eur: number
  total_deductions_eur: number
  net_amount_eur: number
  reference_context?: {
    process_key: string
    anchor_entity: string
    anchor_id: string
    chain: Record<string, string>
  } | null
  exception_hints?: Array<{
    rule_id: string
    category: string
    decision_mode: string
    requires_approval: boolean
    approver_roles: string[]
    description: string
  }>
  explainability?: unknown
}

type FormState = {
  settlementNumber: string
  supplierId: string
  articleId: string
  bruttoGewicht: number
  taraGewicht: number
  feuchtigkeit: number
  verunreinigung: number
  basisPreis: number
  dryingRate: number
  cleaningRate: number
  freightFixed: number
}

const initialForm: FormState = {
  settlementNumber: '',
  supplierId: '',
  articleId: 'WEIZEN',
  bruttoGewicht: 26500,
  taraGewicht: 1500,
  feuchtigkeit: 16.5,
  verunreinigung: 1.8,
  basisPreis: 220,
  dryingRate: 2,
  cleaningRate: 4,
  freightFixed: 0,
}

/** Artikel/Erntegut → crop_code für Drying Rule Engine (regelbasiert, versioniert) */
const ARTICLE_TO_CROP: Record<string, string> = {
  WEIZEN: 'WHEAT',
  WEIZEN_WEICH: 'WHEAT',
  WEIZEN_HART: 'WHEAT',
  WEIZE: 'WHEAT',
  WHEAT: 'WHEAT',
  MAIS: 'MAIZE',
  KÖRNERMAIS: 'MAIZE',
  MAIZE: 'MAIZE',
  RAPS: 'RAPESEED',
  RAPESEED: 'RAPESEED',
  GERSTE: 'BARLEY',
  BARLEY: 'BARLEY',
  HAFER: 'OATS',
  OATS: 'OATS',
  ERBSEN: 'PEAS',
  PEAS: 'PEAS',
  Ackerbohnen: 'FIELD_BEANS',
  AECKERBOHNE: 'FIELD_BEANS',
  ERBSE: 'PEAS',
  LUPINE: 'LUPINS',
  Lupinen: 'LUPINS',
  FIELD_BEANS: 'FIELD_BEANS',
  LUPINS: 'LUPINS',
}

function toCropCode(articleId: string): string {
  const normalized = articleId.trim().toUpperCase().replace(/[ÄÖÜ]/g, (c) => ({ Ä: 'A', Ö: 'O', Ü: 'U' }[c] ?? c))
  return ARTICLE_TO_CROP[normalized] ?? normalized
}

type DryingComputeResult = {
  invoice_weight_kg: number
  loss_kg: number
  loss_pct: number
  drying_fee_eur: number | null
  used_rule_set_id: string
  used_rule_version: number
  warnings: string[]
}

function money(value: number): string {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value)
}

type QualitaetsCheckState = {
  fromQualitaetsCheck?: boolean
  artikel?: string
  feuchtigkeit?: number
  verunreinigung?: number
  lieferscheinNr?: string
}

export default function AnnahmeAbrechnungPage(): JSX.Element {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [form, setForm] = useState<FormState>(initialForm)
  const [approvalActor, setApprovalActor] = useState({ actorId: 'ui-user', actorType: 'SACHBEARBEITER' })

  useEffect(() => {
    const state = location.state as QualitaetsCheckState | null
    if (state?.fromQualitaetsCheck && (state.artikel ?? state.feuchtigkeit ?? state.verunreinigung)) {
      setForm((prev) => ({
        ...prev,
        ...(state.artikel != null && { articleId: state.artikel }),
        ...(state.feuchtigkeit != null && { feuchtigkeit: state.feuchtigkeit }),
        ...(state.verunreinigung != null && { verunreinigung: state.verunreinigung }),
      }))
    }
  }, [location.state])

  const nettoGewicht = useMemo(() => Math.max(0, form.bruttoGewicht - form.taraGewicht), [form.bruttoGewicht, form.taraGewicht])

  /** Abzüge inkl. manueller Trocknung (Fallback wenn keine Drying Rule existiert) */
  const deductions = useMemo(() => {
    const items: Array<{
      deduction_type: DeductionType
      mode: DeductionMode
      rate_per_ton_eur?: number
      fixed_amount_eur?: number
      note?: string
    }> = []

    if (form.feuchtigkeit > 14) {
      items.push({
        deduction_type: 'drying',
        mode: 'per_ton',
        rate_per_ton_eur: form.dryingRate,
        note: `Moisture ${form.feuchtigkeit.toFixed(1)}%`,
      })
    }
    if (form.verunreinigung > 2) {
      items.push({
        deduction_type: 'cleaning',
        mode: 'per_ton',
        rate_per_ton_eur: form.cleaningRate,
        note: `Impurities ${form.verunreinigung.toFixed(1)}%`,
      })
    }
    if (form.freightFixed > 0) {
      items.push({
        deduction_type: 'freight',
        mode: 'fixed',
        fixed_amount_eur: form.freightFixed,
      })
    }
    return items
  }, [form.feuchtigkeit, form.verunreinigung, form.dryingRate, form.cleaningRate, form.freightFixed])

  /** Abzüge ohne Trocknung (nur Reinigung + Fracht) – bei Nutzung der Drying Rule Engine */
  const deductionsWithoutDrying = useMemo(() => {
    const items: Array<{
      deduction_type: DeductionType
      mode: DeductionMode
      rate_per_ton_eur?: number
      fixed_amount_eur?: number
      note?: string
    }> = []
    if (form.verunreinigung > 2) {
      items.push({
        deduction_type: 'cleaning',
        mode: 'per_ton',
        rate_per_ton_eur: form.cleaningRate,
        note: `Impurities ${form.verunreinigung.toFixed(1)}%`,
      })
    }
    if (form.freightFixed > 0) {
      items.push({
        deduction_type: 'freight',
        mode: 'fixed',
        fixed_amount_eur: form.freightFixed,
      })
    }
    return items
  }, [form.verunreinigung, form.cleaningRate, form.freightFixed])

  const { data: settlements, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['agrar', 'settlements'],
    queryFn: async () => (await apiClient.get<Settlement[]>('/api/v1/agrar/settlements')).data,
    staleTime: 60 * 1000,
  })

  const billingPreview = useMutation({
    mutationFn: async () => {
      const payload = {
        net_weight_kg: nettoGewicht,
        moisture_pct: form.feuchtigkeit,
        impurities_pct: form.verunreinigung,
        target_moisture_pct: 14,
        base_impurities_pct: 2,
        allow_bonus: false,
      }
      return (await apiClient.post<BillingPreview>('/api/v1/agrar/settlements/billing-weight/preview', payload)).data
    },
  })

  const dryingCompute = useMutation({
    mutationFn: async () => {
      const cropCode = toCropCode(form.articleId)
      const payload = {
        crop_code: cropCode,
        net_weight_kg: nettoGewicht,
        moisture_pct: form.feuchtigkeit,
      }
      return (await apiClient.post<DryingComputeResult>('/api/v1/agrar/settlements/drying/compute', payload)).data
    },
  })

  const settlementPreview = useMutation({
    mutationFn: async (opts: { billingWeightKg: number; deductions: typeof deductions }) => {
      const payload = {
        settlement_number: form.settlementNumber || undefined,
        supplier_id: form.supplierId,
        article_id: form.articleId,
        gross_quantity_kg: nettoGewicht,
        billing_quantity_kg: opts.billingWeightKg,
        unit_price_eur_per_ton: form.basisPreis,
        deductions: opts.deductions,
      }
      return (await apiClient.post<SettlementPreview>('/api/v1/agrar/settlements/preview', payload)).data
    },
  })

  const createSettlement = useMutation({
    mutationFn: async (opts: { billingWeightKg: number; drying?: { crop_code: string; moisture_pct: number }; deductions: typeof deductions }) => {
      const payload: Record<string, unknown> = {
        settlement_number: form.settlementNumber || undefined,
        supplier_id: form.supplierId,
        article_id: form.articleId,
        gross_quantity_kg: nettoGewicht,
        billing_quantity_kg: opts.billingWeightKg,
        unit_price_eur_per_ton: form.basisPreis,
        deductions: opts.deductions,
        note: 'Created from annahme/abrechnung UI',
      }
      if (opts.drying) {
        payload.drying = opts.drying
      }
      return (await apiClient.post<Settlement>('/api/v1/agrar/settlements', payload)).data
    },
    onSuccess: () => {
      toast({ title: 'Settlement erstellt', description: 'Self-billing Beleg wurde gespeichert.' })
      void queryClient.invalidateQueries({ queryKey: ['agrar', 'settlements'] })
    },
    onError: (e: unknown) => {
      const message = e instanceof Error ? e.message : 'Settlement konnte nicht erstellt werden'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    },
  })

  const postSettlement = useMutation({
    mutationFn: async ({ settlementId, expectedRowVersion }: { settlementId: string; expectedRowVersion: number }) => {
      const payload = {
        debit_account: '5000',
        credit_account_supplier: '3300',
        credit_account_deductions: '5490',
        expected_row_version: expectedRowVersion,
      }
      return (await apiClient.post(`/api/v1/agrar/settlements/${settlementId}/post-fibu`, payload)).data
    },
    onSuccess: () => {
      toast({ title: 'Fibu-Buchung erstellt', description: 'Settlement wurde als Journal Entry verbucht.' })
      void queryClient.invalidateQueries({ queryKey: ['agrar', 'settlements'] })
    },
    onError: (e: unknown) => {
      if (
        isAxiosError(e)
        && e.response?.status === 409
        && typeof e.response.data?.detail === 'object'
        && e.response.data?.detail !== null
        && (e.response.data.detail as { code?: string }).code === 'row_version_conflict'
      ) {
        void queryClient.invalidateQueries({ queryKey: ['agrar', 'settlements'] })
        toast({
          title: 'Daten veraltet',
          description: 'Abrechnung wurde zwischenzeitlich geaendert. Liste wurde aktualisiert.',
          variant: 'destructive',
        })
        return
      }
      toast({ title: 'Fehler', description: describeApiError(e), variant: 'destructive' })
    },
  })

  const approveSettlement = useMutation({
    mutationFn: async ({
      settlementId,
      targetStatus,
      reason,
      expectedRowVersion,
    }: { settlementId: string; targetStatus: string; reason?: string; expectedRowVersion: number }) => {
      const payload = {
        actor_id: approvalActor.actorId,
        actor_type: approvalActor.actorType,
        target_status: targetStatus,
        reason,
        expected_row_version: expectedRowVersion,
      }
      return (await apiClient.post<SettlementFreigabeResponse>(`/api/v1/agrar/settlements/${settlementId}/freigabe`, payload)).data
    },
    onSuccess: (result) => {
      toast({
        title: result.allowed ? 'Freigabeschritt gespeichert' : 'Freigabeschritt abgelehnt',
        description: result.reason,
        variant: result.allowed ? 'default' : 'destructive',
      })
      void queryClient.invalidateQueries({ queryKey: ['agrar', 'settlements'] })
    },
    onError: (e: unknown) => {
      if (
        isAxiosError(e)
        && e.response?.status === 409
        && typeof e.response.data?.detail === 'object'
        && e.response.data?.detail !== null
        && (e.response.data.detail as { code?: string }).code === 'row_version_conflict'
      ) {
        void queryClient.invalidateQueries({ queryKey: ['agrar', 'settlements'] })
        toast({
          title: 'Daten veraltet',
          description: 'Abrechnung wurde zwischenzeitlich geaendert. Liste wurde aktualisiert.',
          variant: 'destructive',
        })
        return
      }
      toast({ title: 'Fehler', description: describeApiError(e), variant: 'destructive' })
    },
  })

  const cancelSettlement = useMutation({
    mutationFn: async ({ settlementId, expectedRowVersion }: { settlementId: string; expectedRowVersion: number }) => {
      return (
        await apiClient.post<{ ok: boolean; settlement_id: string; status: string }>(
          `/api/v1/agrar/settlements/${settlementId}/cancel`,
          {},
          { params: { expected_row_version: expectedRowVersion } },
        )
      ).data
    },
    onSuccess: () => {
      toast({ title: 'Storniert', description: 'Abrechnung wurde storniert.' })
      void queryClient.invalidateQueries({ queryKey: ['agrar', 'settlements'] })
    },
    onError: (e: unknown) => {
      if (
        isAxiosError(e)
        && e.response?.status === 409
        && typeof e.response.data?.detail === 'object'
        && e.response.data?.detail !== null
        && (e.response.data.detail as { code?: string }).code === 'row_version_conflict'
      ) {
        void queryClient.invalidateQueries({ queryKey: ['agrar', 'settlements'] })
        toast({
          title: 'Daten veraltet',
          description: 'Abrechnung wurde zwischenzeitlich geaendert. Liste wurde aktualisiert.',
          variant: 'destructive',
        })
        return
      }
      toast({ title: 'Fehler', description: describeApiError(e), variant: 'destructive' })
    },
  })

  function openCorrection(settlement: Settlement, memoType: 'credit' | 'debit'): void {
    navigate(`/einkauf/gutschriften-belastungen/${memoType}?settlementId=${settlement.id}`)
  }

  async function runPreview(): Promise<void> {
    if (!form.supplierId.trim()) {
      toast({ title: 'Lieferant fehlt', description: 'Bitte supplier_id eingeben.', variant: 'destructive' })
      return
    }
    let billingWeightKg: number
    let useDeductions = deductions
    try {
      const drying = await dryingCompute.mutateAsync()
      billingWeightKg = drying.invoice_weight_kg
      useDeductions = deductionsWithoutDrying
    } catch {
      const billing = await billingPreview.mutateAsync()
      billingWeightKg = billing.billing_weight_kg
    }
    await settlementPreview.mutateAsync({ billingWeightKg, deductions: useDeductions })
  }

  async function saveSettlement(): Promise<void> {
    if (!form.supplierId.trim()) {
      toast({ title: 'Lieferant fehlt', description: 'Bitte supplier_id eingeben.', variant: 'destructive' })
      return
    }
    let billingWeightKg: number
    let useDrying: { crop_code: string; moisture_pct: number } | undefined
    let useDeductions = deductions
    try {
      const drying = await dryingCompute.mutateAsync()
      billingWeightKg = drying.invoice_weight_kg
      useDrying = { crop_code: toCropCode(form.articleId), moisture_pct: form.feuchtigkeit }
      useDeductions = deductionsWithoutDrying
    } catch {
      const billing = billingPreview.data ?? (await billingPreview.mutateAsync())
      billingWeightKg = billing.billing_weight_kg
    }
    await createSettlement.mutateAsync({ billingWeightKg, drying: useDrying, deductions: useDeductions })
  }

  const shortcuts = buildCoreMaskShortcuts({
    onSave: () => { void saveSettlement() },
    onCancel: () => navigate('/annahme/warteschlange'),
    isSaveDisabled: createSettlement.isPending,
  })
  useKeyboardShortcuts(shortcuts)

  const previewData = settlementPreview.data
  const billingData = billingPreview.data
  const qualityOk = form.feuchtigkeit <= 14.5 && form.verunreinigung <= 2
  const previewDecisionView = buildDecisionView(previewData?.explainability)
  const previewDensityProfile = useApprovalDensityProfile('agrar-settlement', previewDecisionView)
  const campaignName = searchParams.get('campaignName') || ''
  const campaignStart = searchParams.get('campaignStart') || ''
  const campaignEnd = searchParams.get('campaignEnd') || ''
  const filteredSettlements = useMemo(() => {
    const items = settlements ?? []
    if (!campaignStart || !campaignEnd) {
      return items
    }
    return items.filter((settlement) => {
      if (!settlement.created_at) return false
      const createdAt = String(settlement.created_at).slice(0, 10)
      return createdAt >= campaignStart && createdAt <= campaignEnd
    })
  }, [campaignEnd, campaignStart, settlements])
  const filteredNetTotal = filteredSettlements.reduce((sum, settlement) => sum + settlement.net_amount_eur, 0)
  const filteredOpenCount = filteredSettlements.filter(
    (settlement) => settlement.status !== 'posted' || settlement.approval_status !== 'VERBUCHT',
  ).length

  return (
    <div className="flex flex-col">
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Annahme-Abrechnung</h1>
          <p className="text-muted-foreground">Self-billing mit Abzugsnachweis und Fibu-Posting</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/annahme/warteschlange')}>Zurueck</Button>
          <Button variant="outline" className="gap-2" onClick={() => { void runPreview() }} disabled={billingPreview.isPending || settlementPreview.isPending}>
            <Calculator className="h-4 w-4" />
            Vorschau
          </Button>
          <Button onClick={() => { void saveSettlement() }} className="gap-2" disabled={createSettlement.isPending}>
            <Save className="h-4 w-4" />
            Settlement speichern
          </Button>
        </div>
      </div>

      {campaignName ? (
        <Card>
          <CardHeader>
            <CardTitle>Kampagnenabschluss: {campaignName}</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-3">
            <div>
              <div className="text-xs text-muted-foreground">Kampagnenfenster</div>
              <div className="font-semibold">{campaignStart} bis {campaignEnd}</div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Gefilterte Settlements</div>
              <div className="font-semibold">{filteredSettlements.length}</div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Offen / Netto</div>
              <div className="font-semibold">{filteredOpenCount} / {money(filteredNetTotal)}</div>
            </div>
          </CardContent>
        </Card>
      ) : null}

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Truck className="h-5 w-5" />Lieferdaten</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div>
              <Label htmlFor="supplierId">Supplier ID</Label>
              <Input id="supplierId" value={form.supplierId} onChange={(e) => setForm((p) => ({ ...p, supplierId: e.target.value }))} placeholder="z.B. LW-10001" />
            </div>
            <div>
              <Label htmlFor="settlementNumber">Settlement Nummer (optional)</Label>
              <Input id="settlementNumber" value={form.settlementNumber} onChange={(e) => setForm((p) => ({ ...p, settlementNumber: e.target.value }))} />
            </div>
            <div>
              <Label htmlFor="articleId">Artikel</Label>
              <Input id="articleId" value={form.articleId} onChange={(e) => setForm((p) => ({ ...p, articleId: e.target.value }))} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Gewicht und Qualitaet</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <Label htmlFor="bruttoGewicht">Brutto (kg)</Label>
                <Input id="bruttoGewicht" type="number" value={form.bruttoGewicht} onChange={(e) => setForm((p) => ({ ...p, bruttoGewicht: Number(e.target.value) }))} />
              </div>
              <div>
                <Label htmlFor="taraGewicht">Tara (kg)</Label>
                <Input id="taraGewicht" type="number" value={form.taraGewicht} onChange={(e) => setForm((p) => ({ ...p, taraGewicht: Number(e.target.value) }))} />
              </div>
            </div>
            <div className="rounded-md bg-muted p-3 text-sm">Netto: <span className="font-semibold">{nettoGewicht.toLocaleString('de-DE')} kg</span></div>
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <Label htmlFor="feuchtigkeit">Feuchtigkeit (%)</Label>
                <Input id="feuchtigkeit" type="number" step="0.1" value={form.feuchtigkeit} onChange={(e) => setForm((p) => ({ ...p, feuchtigkeit: Number(e.target.value) }))} />
              </div>
              <div>
                <Label htmlFor="verunreinigung">Verunreinigung (%)</Label>
                <Input id="verunreinigung" type="number" step="0.1" value={form.verunreinigung} onChange={(e) => setForm((p) => ({ ...p, verunreinigung: Number(e.target.value) }))} />
              </div>
            </div>
            <Badge variant={qualityOk ? 'outline' : 'secondary'}>{qualityOk ? 'Qualitaet ok' : 'Abzuege erforderlich'}</Badge>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><FileText className="h-5 w-5" />Preis und Abzuege</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-4">
            <div>
              <Label htmlFor="basisPreis">Basispreis (EUR/t)</Label>
              <Input id="basisPreis" type="number" step="0.01" value={form.basisPreis} onChange={(e) => setForm((p) => ({ ...p, basisPreis: Number(e.target.value) }))} />
            </div>
            <div>
              <Label htmlFor="dryingRate">Trocknung (EUR/t)</Label>
              <Input id="dryingRate" type="number" step="0.01" value={form.dryingRate} onChange={(e) => setForm((p) => ({ ...p, dryingRate: Number(e.target.value) }))} />
            </div>
            <div>
              <Label htmlFor="cleaningRate">Reinigung (EUR/t)</Label>
              <Input id="cleaningRate" type="number" step="0.01" value={form.cleaningRate} onChange={(e) => setForm((p) => ({ ...p, cleaningRate: Number(e.target.value) }))} />
            </div>
            <div>
              <Label htmlFor="freightFixed">Fracht fix (EUR)</Label>
              <Input id="freightFixed" type="number" step="0.01" value={form.freightFixed} onChange={(e) => setForm((p) => ({ ...p, freightFixed: Number(e.target.value) }))} />
            </div>
          </div>

          {(billingData || previewData || dryingCompute.data) && (
            <div className="rounded border p-3 text-sm">
              Abrechnungsgewicht: <span className="font-semibold">{(previewData?.billing_quantity_kg ?? dryingCompute.data?.invoice_weight_kg ?? billingData?.billing_weight_kg ?? 0).toLocaleString('de-DE')} kg</span>
              {' | '}Abzug: <span className="font-semibold">{(dryingCompute.data?.loss_kg ?? billingData?.deduction_kg ?? (nettoGewicht - (previewData?.billing_quantity_kg ?? nettoGewicht))).toLocaleString('de-DE')} kg</span>
            </div>
          )}

          {previewData && (
            <div className="rounded border bg-muted/40 p-4">
              <div className="flex justify-between"><span>Bruttobetrag</span><span className="font-semibold">{money(previewData.gross_amount_eur)}</span></div>
              <div className="flex justify-between text-orange-700"><span>Abzuege gesamt</span><span className="font-semibold">{money(previewData.total_deductions_eur)}</span></div>
              <div className="mt-2 flex justify-between border-t pt-2 text-lg"><span className="font-bold">Nettobetrag</span><span className="font-bold">{money(previewData.net_amount_eur)}</span></div>
            </div>
          )}

          {previewDecisionView ? (
            <ProcessStatusPanel view={previewDecisionView} densityProfileOverride={previewDensityProfile} />
          ) : null}

          {previewData?.exception_hints && previewData.exception_hints.length > 0 ? (
            <div className="rounded-md border border-amber-300 bg-amber-50 p-3">
              <div className="text-sm font-semibold text-amber-900">Ausnahmehinweise</div>
              <ul className="mt-2 space-y-2 text-sm text-amber-900">
                {previewData.exception_hints.map((hint) => (
                  <li key={hint.rule_id}>
                    <div className="font-medium">{hint.description}</div>
                    <div className="text-xs">
                      {hint.category} | {hint.decision_mode}
                      {hint.requires_approval ? ` | Freigabe: ${hint.approver_roles.join(', ')}` : ''}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {previewData?.reference_context ? (
            <div className="rounded-md border p-3">
              <div className="text-sm font-semibold">Prozessreferenz</div>
              <div className="mt-2 text-xs text-muted-foreground">
                {previewData.reference_context.process_key} | {previewData.reference_context.anchor_entity}: {previewData.reference_context.anchor_id}
              </div>
              <pre className="mt-2 whitespace-pre-wrap text-xs">{JSON.stringify(previewData.reference_context.chain, null, 2)}</pre>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Freigabe-Kontext</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          <div>
            <Label htmlFor="approvalActorId">Aktor-ID</Label>
            <Input
              id="approvalActorId"
              value={approvalActor.actorId}
              onChange={(e) => setApprovalActor((prev) => ({ ...prev, actorId: e.target.value }))}
            />
          </div>
          <div>
            <Label htmlFor="approvalActorType">Aktor-Rolle</Label>
            <NativeSelect
              value={approvalActor.actorType}
              onValueChange={(value) => setApprovalActor((prev) => ({ ...prev, actorType: value }))}
              options={[
                { value: 'SACHBEARBEITER', label: 'Sachbearbeiter' },
                { value: 'ABTEILUNGSLEITER', label: 'Abteilungsleiter' },
                { value: 'PROKURIST', label: 'Prokurist' },
                { value: 'SYSTEM', label: 'System' },
                { value: 'AGENT', label: 'Agent' },
              ]}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Bestehende Settlements</CardTitle></CardHeader>
        <CardContent>
          {isLoading && <div className="text-sm text-muted-foreground">Lade Settlements...</div>}
          {isError && <ErrorState error={(error as Error) ?? new Error('Settlements konnten nicht geladen werden')} onRetry={() => { void refetch() }} />}
          {!isLoading && !isError && (
            <div className="space-y-3">
              {filteredSettlements.length === 0 && <div className="text-sm text-muted-foreground">Keine Settlements vorhanden.</div>}
              {filteredSettlements.map((s) => (
                <div key={s.id} className="rounded border p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="font-semibold">{s.settlement_number}</div>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant={s.status === 'posted' ? 'outline' : 'secondary'}>{s.status}</Badge>
                      <Badge variant={s.approval_status === 'FREIGEGEBEN' || s.approval_status === 'VERBUCHT' ? 'outline' : 'secondary'}>
                        {s.approval_status}
                      </Badge>
                    </div>
                  </div>
                  <div className="mt-1 text-sm text-muted-foreground">
                    Lieferant: {s.supplier_id} | Netto: {money(s.net_amount_eur)} | Abzuege: {money(s.total_deductions_eur)}
                  </div>
                  {s.deductions.length > 0 && (
                    <div className="mt-2 space-y-1 text-sm">
                      {s.deductions.map((d) => (
                        <div key={d.id} className="flex justify-between">
                          <span>{d.deduction_type} ({d.mode})</span>
                          <span className="font-semibold">{money(d.amount_eur)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {s.status === 'draft' && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {s.allowed_transitions.includes('ZUR_FREIGABE') ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            void approveSettlement.mutateAsync({
                              settlementId: s.id,
                              targetStatus: 'ZUR_FREIGABE',
                              reason: 'Settlement aus UI zur Freigabe eingereicht.',
                              expectedRowVersion: settlementRowVersion(s),
                            })
                          }}
                          disabled={approveSettlement.isPending}
                        >
                          Zur Freigabe
                        </Button>
                      ) : null}
                      {s.allowed_transitions.includes('FREIGEGEBEN') ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            void approveSettlement.mutateAsync({
                              settlementId: s.id,
                              targetStatus: 'FREIGEGEBEN',
                              reason: 'Settlement fachlich freigegeben.',
                              expectedRowVersion: settlementRowVersion(s),
                            })
                          }}
                          disabled={approveSettlement.isPending}
                        >
                          Freigeben
                        </Button>
                      ) : null}
                      {s.allowed_transitions.includes('ABGELEHNT') ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            void approveSettlement.mutateAsync({
                              settlementId: s.id,
                              targetStatus: 'ABGELEHNT',
                              reason: 'Settlement zur Korrektur abgelehnt.',
                              expectedRowVersion: settlementRowVersion(s),
                            })
                          }}
                          disabled={approveSettlement.isPending}
                        >
                          Ablehnen
                        </Button>
                      ) : null}
                      {s.allowed_transitions.includes('ENTWURF') ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            void approveSettlement.mutateAsync({
                              settlementId: s.id,
                              targetStatus: 'ENTWURF',
                              reason: 'Settlement zur Ueberarbeitung in Entwurf zurueckgesetzt.',
                              expectedRowVersion: settlementRowVersion(s),
                            })
                          }}
                          disabled={approveSettlement.isPending}
                        >
                          Zurueck in Entwurf
                        </Button>
                      ) : null}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          void postSettlement.mutateAsync({ settlementId: s.id, expectedRowVersion: settlementRowVersion(s) })
                        }}
                        disabled={postSettlement.isPending || !s.can_post_fibu}
                      >
                        In Fibu buchen
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => {
                          if (!window.confirm('Abrechnung wirklich stornieren?')) return
                          void cancelSettlement.mutateAsync({
                            settlementId: s.id,
                            expectedRowVersion: settlementRowVersion(s),
                          })
                        }}
                        disabled={
                          cancelSettlement.isPending
                          || postSettlement.isPending
                          || approveSettlement.isPending
                        }
                      >
                        Stornieren
                      </Button>
                    </div>
                  )}
                  {s.status === 'posted' && s.correction_options.length > 0 ? (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {s.correction_options.some((option) => option.memo_type === 'credit') ? (
                        <Button size="sm" variant="outline" onClick={() => openCorrection(s, 'credit')}>
                          Gutschrift
                        </Button>
                      ) : null}
                      {s.correction_options.some((option) => option.memo_type === 'debit') ? (
                        <Button size="sm" variant="outline" onClick={() => openCorrection(s, 'debit')}>
                          Belastung
                        </Button>
                      ) : null}
                    </div>
                  ) : null}
                  {s.posted_journal_ref && (
                    <div className="mt-2 text-xs text-muted-foreground">Journal: {s.posted_journal_ref}</div>
                  )}
                  {s.approval_history.length > 0 ? (
                    <div className="mt-3 rounded-md border bg-muted/20 p-3">
                      <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Freigabehistorie</div>
                      <div className="mt-2 space-y-2 text-xs">
                        {s.approval_history.map((entry, idx) => (
                          <div key={`${entry.decided_at}-${idx}`} className="flex flex-wrap justify-between gap-2">
                            <span>{entry.previous_status || 'START'} {'->'} {entry.new_status}</span>
                            <span>{entry.actor_type} / {entry.actor_id}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                  {s.explainability ? (
                    (() => {
                      const view = buildDecisionView(s.explainability)
                      return view ? (
                        <CompactDecisionCard view={view} pageDomain="agrar-settlement" className="mt-3" showDetails={false} />
                      ) : null
                    })()
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
