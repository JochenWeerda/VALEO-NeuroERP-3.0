import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { NativeSelect } from '@/components/ui/native-select'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/hooks/useAuth'
import { CustomerSelectionDialog, type Customer } from '@/components/sales/CustomerSelectionDialog'
import { ArtikelSuchDialog, type Article as LookupArticle } from '@/components/sales/ArtikelSuchDialog'
import {
  cancelKontrakt,
  createKontrakt,
  deleteKontrakt,
  getKontrakt,
  type Kontrakt,
  type KontraktLine,
  type KontraktSteering,
  updateKontrakt,
} from '@/lib/api/kontrakte'
import DlgAuswahlVerkaufKontrakte from '@/pages/kontrakte/DlgAuswahlVerkaufKontrakte'
import DlgKontraktUmSaetze from '@/pages/kontrakte/DlgKontraktUmSaetze'
import DlgMatifPreisfixierung from '@/pages/kontrakte/DlgMatifPreisfixierung'
import FrmKontraktProtokoll from '@/pages/kontrakte/FrmKontraktProtokoll'
import { buildDecisionView } from '@/policy/decision-view'
import { ProcessStatusPanel } from '@/components/workflow/ProcessStatusPanel'
import { apiClient } from '@/lib/api-client'
import { useTenant } from '@/hooks/useTenant'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { WorkflowEntryBanner, readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'
import { ShieldAlert, ShieldCheck } from 'lucide-react'

type FormState = Omit<Kontrakt, 'contract_id' | 'rest_quantity'>
type SteeringKey = keyof KontraktSteering

function getSteeringSnapshot(state: FormState): KontraktSteering {
  const conditions = (state.conditions_json ?? {}) as Record<string, unknown>
  return {
    contract_class: typeof conditions.contract_class === 'string' ? conditions.contract_class : null,
    contract_group: typeof conditions.contract_group === 'string' ? conditions.contract_group : null,
    contract_variant: typeof conditions.contract_variant === 'string' ? conditions.contract_variant : null,
    disposition_flag: typeof conditions.disposition_flag === 'string' ? conditions.disposition_flag : null,
    parity_code: typeof conditions.parity_code === 'string' ? conditions.parity_code : null,
    parity_label: typeof conditions.parity_label === 'string' ? conditions.parity_label : null,
    fallback_route: typeof conditions.fallback_route === 'string' ? conditions.fallback_route : null,
    alternate_articles: Array.isArray(conditions.alternate_articles)
      ? conditions.alternate_articles.filter((item): item is string => typeof item === 'string')
      : typeof conditions.alternate_articles === 'string'
        ? conditions.alternate_articles.split(',').map((item) => item.trim()).filter(Boolean)
        : [],
    print_template: typeof conditions.print_template === 'string' ? conditions.print_template : null,
    print_channel: typeof conditions.print_channel === 'string' ? conditions.print_channel : null,
    print_copy_count: typeof conditions.print_copy_count === 'number' ? conditions.print_copy_count : null,
    last_printed_at: typeof conditions.last_printed_at === 'string' ? conditions.last_printed_at : null,
    print_ready: state.steering?.print_ready ?? false,
    washout_status: typeof conditions.washout_status === 'string' ? conditions.washout_status : null,
    washout_quantity_t: typeof conditions.washout_quantity_t === 'number' ? conditions.washout_quantity_t : null,
    washout_reason: typeof conditions.washout_reason === 'string' ? conditions.washout_reason : null,
    writeoff_quantity_t: typeof conditions.writeoff_quantity_t === 'number' ? conditions.writeoff_quantity_t : null,
    writeoff_reason: typeof conditions.writeoff_reason === 'string' ? conditions.writeoff_reason : null,
    writeoff_candidate: state.steering?.writeoff_candidate ?? false,
    hedge_strategy: typeof conditions.hedge_strategy === 'string' ? conditions.hedge_strategy : null,
    hedge_market: typeof conditions.hedge_market === 'string' ? conditions.hedge_market : null,
    hedge_status: typeof conditions.hedge_status === 'string' ? conditions.hedge_status : null,
    hedge_target_pct: typeof conditions.hedge_target_pct === 'number' ? conditions.hedge_target_pct : null,
    hedge_quantity_t: typeof conditions.hedge_quantity_t === 'number' ? conditions.hedge_quantity_t : null,
    market_price_source: typeof conditions.market_price_source === 'string' ? conditions.market_price_source : null,
    market_price_eur_t: typeof conditions.market_price_eur_t === 'number' ? conditions.market_price_eur_t : null,
    market_price_date: typeof conditions.market_price_date === 'string' ? conditions.market_price_date : null,
    dunning_level: typeof conditions.dunning_level === 'number' ? conditions.dunning_level : null,
    dunning_blocked: Boolean(conditions.dunning_blocked),
    dunning_due_at: typeof conditions.dunning_due_at === 'string' ? conditions.dunning_due_at : null,
    dunning_last_at: typeof conditions.dunning_last_at === 'string' ? conditions.dunning_last_at : null,
    dunning_reason: typeof conditions.dunning_reason === 'string' ? conditions.dunning_reason : null,
    hedge_quote_pct: state.steering?.hedge_quote_pct ?? null,
    hedge_gap_pct: state.steering?.hedge_gap_pct ?? null,
    market_price_delta_eur_t: state.steering?.market_price_delta_eur_t ?? null,
    market_valuation_eur: state.steering?.market_valuation_eur ?? null,
    reference_price_eur_t: state.steering?.reference_price_eur_t ?? null,
    dunning_candidate: state.steering?.dunning_candidate ?? false,
  }
}

function updateSteeringValue(state: FormState, key: SteeringKey, value: unknown): FormState {
  return {
    ...state,
    conditions_json: {
      ...(state.conditions_json || {}),
      [key]: value,
    },
  }
}

function updateSteeringList(state: FormState, key: 'alternate_articles', rawValue: string): FormState {
  return updateSteeringValue(
    state,
    key,
    rawValue
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean),
  )
}

function formatNumber(value: number | null | undefined, decimals = 0): string {
  if (value == null) return '-'
  return value.toLocaleString('de-DE', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

function createEmptyLine(position_no: number): KontraktLine {
  return {
    position_no,
    article_id: '',
    qty_contract: 0,
    unit_price: 0,
    discount_pct: 0,
    description1: '',
    description2: '',
    price_unit: 'kg',
    surcharge: 0,
    rebate_type: '',
    is_bio: false,
    is_matif: false,
  }
}

function createEmptyState(): FormState {
  return {
    contract_no: '',
    contract_type: 'VERKAUF',
    branch_id: '',
    clerk_id: '',
    party_id: '',
    debitor_kto: '',
    kreditor_kto: '',
    contract_date: new Date().toISOString(),
    valid_from: '',
    valid_to: '',
    quantity_type: 'GESAMTKONTRAKT',
    total_quantity: 0,
    unit: 'kg',
    allow_overdelivery: false,
    status: 'OFFEN',
    notes: '',
    payment_terms: '',
    conditions_json: {},
    pricing_model: 'fixed',
    min_price: null,
    premium_type: '',
    premium_value: null,
    basis_reference: '',
    pricing_window_from: '',
    pricing_window_to: '',
    lines: [createEmptyLine(1)],
  }
}

export default function FrmKontraktDetail(): JSX.Element {
  const { id } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { toast } = useToast()
  const { hasRole } = useAuth()
  const { tenantId } = useTenant()
  const workflowContext = readWorkflowEntryContext(searchParams)

  const isEdit = Boolean(id)
  const [state, setState] = useState<FormState>(createEmptyState())
  const [showLookupDlg, setShowLookupDlg] = useState(false)
  const [showUmsaetze, setShowUmsaetze] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [showMatifDialog, setShowMatifDialog] = useState(false)
  const [showCustomerDlg, setShowCustomerDlg] = useState(false)
  const [showArticleDlg, setShowArticleDlg] = useState(false)
  const [activeLineIndex, setActiveLineIndex] = useState<number | null>(null)
  const [selectedCustomerName, setSelectedCustomerName] = useState('')

  const canEdit = hasRole('KONTRAKT_BEARBEITEN') || hasRole('KONTRAKT_ADMIN')
  const canDelete = hasRole('KONTRAKT_LOESCHEN') || hasRole('KONTRAKT_ADMIN')
  const isAdmin = hasRole('KONTRAKT_ADMIN')
  const isDraftEditable = canEdit && (!isEdit || state.status === 'OFFEN')
  const steering = useMemo(() => getSteeringSnapshot(state), [state])

  const detailQuery = useQuery({
    queryKey: ['kontrakte', 'detail', id],
    queryFn: () => getKontrakt(String(id)),
    enabled: isEdit,
  })

  const articleIdsForPosition = useMemo(
    () => state.lines.map((l) => l.article_id).filter(Boolean),
    [state.lines],
  )

  const positionQuery = useQuery({
    queryKey: ['kontrakte', 'positionen', articleIdsForPosition],
    queryFn: () =>
      apiClient.get<{
        positions: Array<{
          article_id: string
          article_desc: string
          net_position: number
          signal: string
          coverage_pct: number | null
          sell_rest_qty: number
          buy_rest_qty: number
        }>
        total_short_articles: number
      }>(`/api/v1/kontrakte/positionen?article_ids=${articleIdsForPosition.join(',')}`),
    enabled: isEdit && articleIdsForPosition.length > 0,
    refetchInterval: 60_000,
  })

  const shortArticles = useMemo(
    () => (positionQuery.data?.positions ?? []).filter((p) => p.signal === 'SHORT'),
    [positionQuery.data],
  )

  useEffect(() => {
    if (detailQuery.data) {
      const { contract_id: _contractId, rest_quantity: _rest, ...rest } = detailQuery.data
      setState({
        ...rest,
        contract_date: rest.contract_date || '',
        valid_from: rest.valid_from || '',
        valid_to: rest.valid_to || '',
        pricing_window_from: rest.pricing_window_from || '',
        pricing_window_to: rest.pricing_window_to || '',
      })
    }
  }, [detailQuery.data])

  useEffect(() => {
    if (!workflowContext || isEdit) return
    setState((prev) => ({
      ...prev,
      notes: prev.notes || [
        workflowContext.caseNumber ? `Workflow-Vorgang ${workflowContext.caseNumber}` : '',
        workflowContext.entryMode ? `Einstieg: ${workflowContext.entryMode}` : '',
        workflowContext.partnerName ? `Partner: ${workflowContext.partnerName}` : '',
        workflowContext.subject,
      ].filter(Boolean).join('\n'),
    }))
    setSelectedCustomerName((prev) => prev || workflowContext.partnerName)
  }, [isEdit, workflowContext])

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!state.party_id || !state.contract_type) {
        throw new Error('Pflichtfelder fehlen')
      }
      if (state.lines.length < 1 || state.lines.length > 3) {
        throw new Error('Sammelkontrakt muss zwischen 1 und 3 Artikel-Positionen enthalten')
      }
      const missingArticle = state.lines.find((line) => !line.article_id?.trim())
      if (missingArticle) {
        throw new Error(`Artikel fehlt in Position ${missingArticle.position_no}`)
      }
      if (state.quantity_type === 'GESAMTKONTRAKT') {
        const sumLines = state.lines.reduce((acc, line) => acc + Number(line.qty_contract || 0), 0)
        const total = Number(state.total_quantity || 0)
        if (Math.abs(sumLines - total) > 0.0001) {
          throw new Error(`Gesamt-Menge (${total}) muss Summe der Positionen (${sumLines}) entsprechen`)
        }
      }
      if (isEdit) return updateKontrakt(String(id), state)
      return createKontrakt(state)
    },
    onSuccess: (saved) => {
      toast({ title: 'Gespeichert', description: `Kontrakt ${saved.contract_no}` })
      navigate(`/kontrakte/${saved.contract_id}`)
    },
    onError: (err: any) => {
      toast({ title: 'Fehler', description: err?.message || 'Speichern fehlgeschlagen', variant: 'destructive' })
    },
  })

  const cancelMutation = useMutation({
    mutationFn: async () => cancelKontrakt(String(id), 'Manueller Storno aus FrmKontraktDetail'),
    onSuccess: () => {
      toast({ title: 'Storniert' })
      detailQuery.refetch()
    },
  })

  const hedgeMutation = useMutation({
    mutationFn: async () => {
      if (!isEdit || !id) throw new Error('Kontrakt muss zuerst gespeichert werden')
      if (!steering.hedge_market) throw new Error('Terminmarktprodukt fehlt')
      if (!steering.hedge_quantity_t || steering.hedge_quantity_t <= 0) throw new Error('Hedge-Menge fehlt')
      const hedgeType = state.contract_type === 'VERKAUF' ? 'short' : 'long'
      return apiClient.post('/api/v1/price-hedge/hedges', {
        tenant_id: tenantId || 'default',
        produkt: steering.hedge_market,
        typ: hedgeType,
        menge_t: steering.hedge_quantity_t,
        basis_preis_eur_t: steering.reference_price_eur_t ?? state.min_price ?? state.lines[0]?.unit_price ?? 0,
        verfall_datum: (state.valid_to || new Date().toISOString()).slice(0, 10),
        kontrakt_id: id,
        broker_referenz: steering.fallback_route || null,
      })
    },
    onSuccess: () => {
      toast({ title: 'Hedge angelegt', description: 'Die Hedge-Referenz wurde aus dem Kontrakt heraus erzeugt.' })
      setState((prev) => updateSteeringValue(prev, 'hedge_status', 'offen'))
    },
    onError: (err: any) => {
      toast({ title: 'Hedge fehlgeschlagen', description: err?.message || 'Hedge konnte nicht angelegt werden', variant: 'destructive' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async () => deleteKontrakt(String(id)),
    onSuccess: () => {
      toast({ title: 'Geloescht' })
      navigate('/kontrakte')
    },
    onError: (err: any) => {
      toast({ title: 'Loeschen fehlgeschlagen', description: err?.message || '', variant: 'destructive' })
    },
  })

  const restMenge = useMemo(() => {
    const total = state.lines.reduce((acc, l) => acc + Number(l.qty_contract || 0), 0)
    return Number(state.total_quantity || total)
  }, [state.lines, state.total_quantity])

  const steeringHighlights = useMemo(
    () => [
      steering.contract_class ? { label: 'Klasse', value: steering.contract_class } : null,
      steering.contract_group ? { label: 'Gruppe', value: steering.contract_group } : null,
      steering.contract_variant ? { label: 'Variante', value: steering.contract_variant } : null,
      steering.parity_code ? { label: 'Paritaet', value: [steering.parity_code, steering.parity_label].filter(Boolean).join(' · ') } : null,
      steering.disposition_flag ? { label: 'Disposition', value: steering.disposition_flag } : null,
      steering.hedge_strategy ? { label: 'Hedging', value: steering.hedge_strategy } : null,
      steering.dunning_level ? { label: 'Mahnstufe', value: `Stufe ${steering.dunning_level}` } : null,
    ].filter(Boolean) as Array<{ label: string; value: string }>,
    [steering],
  )

  const kontraktStatusView = useMemo(() => {
    const explainability = {
      status:
        state.status === 'STORNIERT'
          ? ('blocked' as const)
          : state.status === 'ERLEDIGT'
            ? ('allowed' as const)
            : state.pricing_model === 'matif'
              ? ('approval-required' as const)
              : ('allowed' as const),
      summary:
        state.status === 'STORNIERT'
          ? 'Kontrakt wurde storniert und ist gesperrt.'
          : state.status === 'ERLEDIGT'
            ? 'Kontrakt ist vollstaendig erfuellt.'
            : state.pricing_model === 'matif'
              ? 'MATIF-Preisfestsetzung offen – Kontrakt wartet auf Preisbestaetigung.'
              : 'Kontrakt ist aktiv und kann bearbeitet werden.',
      source_scope: 'contract',
      details: [
        { label: 'Status', value: state.status },
        ...(state.pricing_model ? [{ label: 'Preismodell', value: state.pricing_model }] : []),
        ...(state.valid_to ? [{ label: 'Gueltig bis', value: state.valid_to.slice(0, 10) }] : []),
      ],
    }
    return buildDecisionView(explainability)
  }, [state.status, state.pricing_model, state.valid_to])

  const updateLine = (index: number, patch: Partial<KontraktLine>): void => {
    setState((prev) => {
      const lines = [...prev.lines]
      lines[index] = { ...lines[index], ...patch }
      return { ...prev, lines }
    })
  }

  const moveLine = (index: number, direction: -1 | 1): void => {
    setState((prev) => {
      const target = index + direction
      if (target < 0 || target >= prev.lines.length) return prev
      const lines = [...prev.lines]
      const temp = lines[index]
      lines[index] = lines[target]
      lines[target] = temp
      const normalized = lines.map((line, i) => ({ ...line, position_no: i + 1 }))
      return { ...prev, lines: normalized }
    })
  }

  const removeLine = (index: number): void => {
    setState((prev) => {
      if (prev.lines.length <= 1) return prev
      const lines = prev.lines.filter((_, i) => i !== index).map((line, i) => ({ ...line, position_no: i + 1 }))
      return { ...prev, lines }
    })
  }

  const shortcuts = buildCoreMaskShortcuts({
    onSave: () => saveMutation.mutate(),
    onRefresh: () => { void detailQuery.refetch() },
    isSaveDisabled: !isDraftEditable || saveMutation.isPending,
  })
  useKeyboardShortcuts(shortcuts)

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      {workflowContext ? (
        <WorkflowEntryBanner
          context={workflowContext}
          title="Workflow-Handover aus Contract-to-Settlement"
          description="Kontraktstammdaten, Mengen, Preise, Staffeln und Bedingungen werden jetzt in der Kontraktmaske gepflegt. Der Flow-Fall bleibt als Referenz erhalten."
        />
      ) : null}
      <Card>
        <CardHeader>
          <CardTitle>FrmKontraktDetail</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Button disabled={!isDraftEditable || saveMutation.isPending} onClick={() => saveMutation.mutate()}>Speichern</Button>
            <Button variant="outline" disabled={!canDelete || !isEdit || deleteMutation.isPending || !isDraftEditable} onClick={() => setShowDeleteConfirm(true)}>Loeschen</Button>
            <Button variant="outline" disabled={!isEdit} onClick={() => window.print()}>Drucken</Button>
            <Button variant="outline" disabled={!isEdit} onClick={() => setShowUmsaetze(true)}>Umsaetze</Button>
            <Button variant="outline" onClick={() => setShowLookupDlg(true)}>Lookup/Matchcode</Button>
            <Button variant="outline" onClick={() => navigate('/dokumente/ablage')}>Unterlagen/Dateien</Button>
            {state.pricing_model === 'matif' && isEdit && (
              <Button variant="outline" onClick={() => setShowMatifDialog(true)}>MATIF-Preisfixierung</Button>
            )}
            <Button
              variant="outline"
              disabled={!isEdit || hedgeMutation.isPending || !steering.hedge_market || !steering.hedge_quantity_t}
              onClick={() => hedgeMutation.mutate()}
            >
              Hedge anlegen
            </Button>
            <Button variant="outline" disabled={!isEdit} onClick={() => navigate('/finance/mahnwesen')}>
              Mahnwesen
            </Button>
            <Button variant="outline" disabled={!isEdit || !canEdit || cancelMutation.isPending} onClick={() => cancelMutation.mutate()}>Workflow erledigt/stornieren</Button>
          </div>

          {isEdit && kontraktStatusView ? (
            <ProcessStatusPanel view={kontraktStatusView} title="Prozessstatus" />
          ) : null}

          <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Kontrakt-Steuerung</div>
                <div className="mt-2 text-sm font-medium">
                  {[steering.contract_class, steering.contract_group, steering.contract_variant].filter(Boolean).join(' / ') || 'Noch nicht klassifiziert'}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">Klasse, Gruppe und Variante fuer Vertragslogik und Reporting.</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Paritaet / Disposition</div>
                <div className="mt-2 text-sm font-medium">
                  {steering.parity_code || 'Keine Paritaet'}{steering.disposition_flag ? ` · ${steering.disposition_flag}` : ''}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{steering.parity_label || 'Liefer- und Dispositionssteuerung noch nicht hinterlegt.'}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Hedging / Marktwert</div>
                <div className="mt-2 text-sm font-medium">
                  {steering.hedge_quote_pct != null ? `${formatNumber(steering.hedge_quote_pct, 1)}% abgesichert` : 'Keine Hedge-Quote'}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {steering.market_valuation_eur != null
                    ? `Marktbewertung ${formatNumber(steering.market_valuation_eur, 2)} EUR`
                    : 'Noch keine Marktpreisbewertung hinterlegt.'}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Mahnung / Druck</div>
                <div className="mt-2 text-sm font-medium">
                  {steering.dunning_candidate
                    ? 'Mahnung faellig'
                    : steering.dunning_level
                      ? `Mahnstufe ${steering.dunning_level}`
                      : 'Keine Mahnstufe'}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {steering.print_template || 'Ohne Formulardefinition'}
                  {steering.print_channel ? ` · ${steering.print_channel}` : ''}
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Ausweichliste</div>
                <div className="mt-2 text-sm font-medium">
                  {steering.alternate_articles && steering.alternate_articles.length > 0
                    ? steering.alternate_articles.join(', ')
                    : 'Keine Ausweichartikel'}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {steering.fallback_route || 'Keine definierte Ausweichroute'}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Washout / Abschreibung</div>
                <div className="mt-2 text-sm font-medium">
                  {steering.writeoff_candidate
                    ? `${formatNumber(steering.washout_quantity_t ?? steering.writeoff_quantity_t, 3)} t vorgemerkt`
                    : 'Keine Abschreibung vorgemerkt'}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {steering.washout_status || steering.writeoff_reason || 'Noch kein Washout-/Abschreibungspfad definiert.'}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Druckpaket</div>
                <div className="mt-2 text-sm font-medium">
                  {steering.print_ready ? 'Druckfaehig' : 'Druckkonfiguration unvollstaendig'}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {steering.print_copy_count ? `${steering.print_copy_count} Kopien` : 'Kopien nicht hinterlegt'}
                  {steering.last_printed_at ? ` · zuletzt ${steering.last_printed_at.slice(0, 10)}` : ''}
                </p>
              </CardContent>
            </Card>
          </div>

          {steeringHighlights.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {steeringHighlights.map((item) => (
                <Badge key={item.label} variant="outline">
                  {item.label}: {item.value}
                </Badge>
              ))}
            </div>
          ) : null}

          {isEdit && shortArticles.length > 0 && (
            <Alert variant="destructive" className="border-red-300 bg-red-50">
              <ShieldAlert className="h-4 w-4" />
              <AlertTitle className="flex items-center gap-2">
                Unterdeckung (Short-Position)
                <Badge className="bg-red-600 text-white">{shortArticles.length} Artikel</Badge>
              </AlertTitle>
              <AlertDescription className="mt-1 space-y-1">
                {shortArticles.map((a) => (
                  <p key={a.article_id} className="text-sm">
                    <strong>{a.article_desc}</strong>: VK offen {a.sell_rest_qty.toLocaleString('de-DE')} t,
                    EK gedeckt {a.buy_rest_qty.toLocaleString('de-DE')} t
                    → Netto {a.net_position.toLocaleString('de-DE')} t
                    {a.coverage_pct != null && ` (Deckung ${a.coverage_pct.toFixed(1)}%)`}
                  </p>
                ))}
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-2 border-red-300 text-red-700 hover:bg-red-100"
                  onClick={() => navigate('/kontrakte/positionen')}
                >
                  Zum Positionsmonitor
                </Button>
              </AlertDescription>
            </Alert>
          )}

          {isEdit && positionQuery.data && shortArticles.length === 0 && articleIdsForPosition.length > 0 && (
            <div className="flex items-center gap-2 rounded border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-800">
              <ShieldCheck className="h-4 w-4" />
              Alle Artikel dieses Kontrakts sind gedeckt (Long oder Balanced).
            </div>
          )}

          {!isEdit ? (
            <Card className="border-dashed border-slate-300/60 bg-slate-50/40 dark:bg-slate-900/20">
              <CardContent className="py-3 text-sm text-muted-foreground">
                <div className="font-medium text-foreground">Kontraktnummer</div>
                <div>Wird beim Speichern standardmäßig serverseitig aus dem Nummernkreis vergeben. Partner, Laufzeit, Mengenstaffel, Preise und Konditionen pflegst du in dieser Kontraktmaske.</div>
              </CardContent>
            </Card>
          ) : null}

          <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
            <div className="space-y-1">
              <Label>Kontrakt-Nr.</Label>
              <Input
                value={state.contract_no || ''}
                onChange={(e) => setState((s) => ({ ...s, contract_no: e.target.value }))}
                disabled={isEdit ? !isAdmin : Boolean(workflowContext && !isAdmin)}
                placeholder={!isEdit ? 'Wird beim Speichern aus dem Nummernkreis vergeben' : undefined}
              />
            </div>
            <div className="space-y-1">
              <Label>Kontrakt-Typ</Label>
              <NativeSelect
                value={state.contract_type}
                onValueChange={(v) => setState((s) => ({ ...s, contract_type: v as FormState['contract_type'] }))}
                options={[
                  { value: 'VERKAUF', label: 'VERKAUF' },
                  { value: 'ZUKAUF', label: 'ZUKAUF' },
                  { value: 'EINKAUF', label: 'EINKAUF' },
                ]}
                disabled={!isDraftEditable}
              />
            </div>
            <div className="space-y-1">
              <Label>Niederlassung</Label>
              <Input value={state.branch_id || ''} onChange={(e) => setState((s) => ({ ...s, branch_id: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>Bediener</Label>
              <Input value={state.clerk_id || ''} onChange={(e) => setState((s) => ({ ...s, clerk_id: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>Kunde/Lieferant</Label>
              <div className="flex gap-2">
                <Input value={state.party_id} onChange={(e) => setState((s) => ({ ...s, party_id: e.target.value }))} disabled={!isDraftEditable} />
                <Button type="button" variant="outline" disabled={!isDraftEditable} onClick={() => setShowCustomerDlg(true)}>Suchen</Button>
              </div>
              {selectedCustomerName ? <p className="text-xs text-muted-foreground">{selectedCustomerName}</p> : null}
            </div>
            <div className="space-y-1">
              <Label>Kontrakt-Datum</Label>
              <Input type="date" value={(state.contract_date || '').slice(0, 10)} onChange={(e) => setState((s) => ({ ...s, contract_date: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>gueltig von</Label>
              <Input type="date" value={(state.valid_from || '').slice(0, 10)} onChange={(e) => setState((s) => ({ ...s, valid_from: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>gueltig bis</Label>
              <Input type="date" value={(state.valid_to || '').slice(0, 10)} onChange={(e) => setState((s) => ({ ...s, valid_to: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>Mengen-Art</Label>
              <NativeSelect
                value={state.quantity_type}
                onValueChange={(v) => setState((s) => ({ ...s, quantity_type: v as FormState['quantity_type'] }))}
                options={[
                  { value: 'GESAMTKONTRAKT', label: 'Gesamtkontrakt' },
                  { value: 'EINZELMENGEN', label: 'Einzelmengen' },
                ]}
                disabled={!isDraftEditable}
              />
            </div>
            <div className="space-y-1">
              <Label>Gesamt-Menge</Label>
              <Input type="number" value={state.total_quantity} onChange={(e) => setState((s) => ({ ...s, total_quantity: Number(e.target.value) }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>Einheit</Label>
              <Input value={state.unit} onChange={(e) => setState((s) => ({ ...s, unit: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>Rest-Menge</Label>
              <Input value={restMenge} disabled />
            </div>
            <div className="flex items-center gap-2 pt-6">
              <Checkbox checked={state.allow_overdelivery} onCheckedChange={(v) => setState((s) => ({ ...s, allow_overdelivery: v === true }))} disabled={!isDraftEditable} />
              <Label>Ueberschreiten der Kontraktmenge erlaubt</Label>
            </div>
          </div>

          <Tabs defaultValue={state.contract_type === 'VERKAUF' ? 'partner' : 'partner'}>
            <TabsList className="flex flex-wrap">
              <TabsTrigger value="partner">PARTNER</TabsTrigger>
              <TabsTrigger value="lieferanschrift">LIEFERANSCHR.</TabsTrigger>
              <TabsTrigger value="zahlungsbed">ZAHLUNGSBED.</TabsTrigger>
              <TabsTrigger value="preismodell">PREISMODELL</TabsTrigger>
              <TabsTrigger value="steuerung">STEUERUNG</TabsTrigger>
              <TabsTrigger value="bedingungen">BEDINGUNGEN</TabsTrigger>
              <TabsTrigger value="notizen">NOTIZEN</TabsTrigger>
              <TabsTrigger value="unterlagen">UNTERLAGEN</TabsTrigger>
              <TabsTrigger value="protokoll">PROTOKOLL</TabsTrigger>
            </TabsList>

            <TabsContent value="partner">
              <div className="space-y-3 py-2">
                <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                  <div className="space-y-1">
                    <Label>{state.contract_type === 'VERKAUF' ? 'Kunde (Party-ID)' : 'Lieferant (Party-ID)'}</Label>
                    <div className="flex gap-2">
                      <Input value={state.party_id} onChange={(e) => setState((s) => ({ ...s, party_id: e.target.value }))} disabled={!isDraftEditable} />
                      <Button type="button" variant="outline" disabled={!isDraftEditable} onClick={() => setShowCustomerDlg(true)}>Suchen</Button>
                    </div>
                    {selectedCustomerName ? <p className="text-xs text-muted-foreground">{selectedCustomerName}</p> : null}
                  </div>
                  <div className="space-y-1">
                    <Label>{state.contract_type === 'VERKAUF' ? 'Debitor-Konto' : 'Kreditor-Konto'}</Label>
                    <Input
                      value={state.contract_type === 'VERKAUF' ? (state.debitor_kto || '') : (state.kreditor_kto || '')}
                      onChange={(e) => {
                        const field = state.contract_type === 'VERKAUF' ? 'debitor_kto' : 'kreditor_kto'
                        setState((s) => ({ ...s, [field]: e.target.value }))
                      }}
                      disabled={!isDraftEditable}
                    />
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="lieferanschrift">
              <div className="space-y-2 py-2">
                <Label>Lieferanschrift / Abholadresse</Label>
                <Textarea
                  value={(state.conditions_json as Record<string, string>)?.lieferanschrift || ''}
                  onChange={(e) => setState((s) => ({
                    ...s,
                    conditions_json: { ...(s.conditions_json || {}), lieferanschrift: e.target.value },
                  }))}
                  disabled={!isDraftEditable}
                  placeholder="Strasse, PLZ, Ort"
                  rows={4}
                />
              </div>
            </TabsContent>

            <TabsContent value="zahlungsbed">
              <div className="space-y-2 py-2">
                <Label>Zahlungsbedingungen</Label>
                <Textarea
                  value={state.payment_terms || ''}
                  onChange={(e) => setState((s) => ({ ...s, payment_terms: e.target.value }))}
                  disabled={!isDraftEditable}
                  placeholder="z.B. 30 Tage netto, 2% Skonto bei Zahlung innerhalb 10 Tagen"
                  rows={4}
                />
              </div>
            </TabsContent>

            <TabsContent value="preismodell">
              <div className="space-y-3 py-2">
                <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
                  <div className="space-y-1">
                    <Label>Preismodell</Label>
                    <NativeSelect
                      value={state.pricing_model || 'fixed'}
                      onValueChange={(v) => setState((s) => ({ ...s, pricing_model: v }))}
                      options={[
                        { value: 'fixed', label: 'Festpreis' },
                        { value: 'matif', label: 'MATIF-Kopplung' },
                        { value: 'premium', label: 'Praemienmodell' },
                        { value: 'index', label: 'Indexbasiert' },
                      ]}
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Basis-Referenz</Label>
                    <Input
                      value={state.basis_reference || ''}
                      onChange={(e) => setState((s) => ({ ...s, basis_reference: e.target.value }))}
                      disabled={!isDraftEditable}
                      placeholder="z.B. MATIF Weizen Dez 26"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Mindestpreis (EUR/t)</Label>
                    <Input
                      type="number"
                      value={state.min_price ?? ''}
                      onChange={(e) => setState((s) => ({ ...s, min_price: e.target.value ? Number(e.target.value) : null }))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Praemien-Typ</Label>
                    <NativeSelect
                      value={state.premium_type || ''}
                      onValueChange={(v) => setState((s) => ({ ...s, premium_type: v }))}
                      options={[
                        { value: 'absolut', label: 'Absolut (EUR/t)' },
                        { value: 'prozentual', label: 'Prozentual (%)' },
                      ]}
                      placeholder="Keine"
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Praemien-Wert</Label>
                    <Input
                      type="number"
                      value={state.premium_value ?? ''}
                      onChange={(e) => setState((s) => ({ ...s, premium_value: e.target.value ? Number(e.target.value) : null }))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                  <div className="space-y-1">
                    <Label>Preisfenster von</Label>
                    <Input
                      type="date"
                      value={(state.pricing_window_from || '').slice(0, 10)}
                      onChange={(e) => setState((s) => ({ ...s, pricing_window_from: e.target.value }))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Preisfenster bis</Label>
                    <Input
                      type="date"
                      value={(state.pricing_window_to || '').slice(0, 10)}
                      onChange={(e) => setState((s) => ({ ...s, pricing_window_to: e.target.value }))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="steuerung">
              <div className="space-y-4 py-2">
                <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
                  <div className="space-y-1">
                    <Label>Kontraktklasse</Label>
                    <NativeSelect
                      value={steering.contract_class || ''}
                      onValueChange={(v) => setState((s) => updateSteeringValue(s, 'contract_class', v))}
                      options={[
                        { value: 'standard', label: 'Standard' },
                        { value: 'saison', label: 'Saisonvertrag' },
                        { value: 'pool', label: 'Pool / Sammelvertrag' },
                        { value: 'basis', label: 'Basis-/Preisvertrag' },
                        { value: 'sonder', label: 'Sonderkontrakt' },
                      ]}
                      placeholder="Bitte waehlen"
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Kontraktgruppe</Label>
                    <Input
                      value={steering.contract_group || ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'contract_group', e.target.value))}
                      disabled={!isDraftEditable}
                      placeholder="z. B. Ernte 2026"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Variante</Label>
                    <Input
                      value={steering.contract_variant || ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'contract_variant', e.target.value))}
                      disabled={!isDraftEditable}
                      placeholder="z. B. Qualitaetsstaffel A"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
                  <div className="space-y-1">
                    <Label>Paritaet</Label>
                    <NativeSelect
                      value={steering.parity_code || ''}
                      onValueChange={(v) => setState((s) => updateSteeringValue(s, 'parity_code', v))}
                      options={[
                        { value: 'ab_hof', label: 'ab Hof' },
                        { value: 'frei_lager', label: 'frei Lager' },
                        { value: 'frei_rampon', label: 'frei Rampe' },
                        { value: 'franko_werk', label: 'franko Werk' },
                      ]}
                      placeholder="Bitte waehlen"
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Paritaetstext</Label>
                    <Input
                      value={steering.parity_label || ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'parity_label', e.target.value))}
                      disabled={!isDraftEditable}
                      placeholder="Liefer- / Uebergabetext"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Dispositionskennzeichen</Label>
                    <NativeSelect
                      value={steering.disposition_flag || ''}
                      onValueChange={(v) => setState((s) => updateSteeringValue(s, 'disposition_flag', v))}
                      options={[
                        { value: 'fix_zuweisen', label: 'Fix zuweisen' },
                        { value: 'frei_disponieren', label: 'Frei disponieren' },
                        { value: 'andienung', label: 'Andienung / Androhung' },
                        { value: 'ausweichartikel', label: 'Ausweichartikel zulassen' },
                      ]}
                      placeholder="Bitte waehlen"
                      disabled={!isDraftEditable}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                  <div className="space-y-1">
                    <Label>Ausweichroute / Brokerreferenz</Label>
                    <Input
                      value={steering.fallback_route || ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'fallback_route', e.target.value))}
                      disabled={!isDraftEditable}
                      placeholder="z. B. Lager Ost, Broker 42"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Ausweichartikel / Alternativen</Label>
                    <Input
                      value={(steering.alternate_articles || []).join(', ')}
                      onChange={(e) => setState((s) => updateSteeringList(s, 'alternate_articles', e.target.value))}
                      disabled={!isDraftEditable}
                      placeholder="z. B. WEIZEN_A, WEIZEN_B"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
                  <div className="space-y-1">
                    <Label>Druckvorlage</Label>
                    <Input
                      value={steering.print_template || ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'print_template', e.target.value))}
                      disabled={!isDraftEditable}
                      placeholder="z. B. KON_STD_A4"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Druck-/Versandkanal</Label>
                    <NativeSelect
                      value={steering.print_channel || ''}
                      onValueChange={(v) => setState((s) => updateSteeringValue(s, 'print_channel', v))}
                      options={[
                        { value: 'print', label: 'Druck' },
                        { value: 'mail', label: 'E-Mail' },
                        { value: 'portal', label: 'Portal' },
                        { value: 'edi', label: 'EDI / Datentransfer' },
                      ]}
                      placeholder="Bitte waehlen"
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Kopien</Label>
                    <Input
                      type="number"
                      value={steering.print_copy_count ?? ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'print_copy_count', e.target.value ? Number(e.target.value) : 0))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Letzter Druck</Label>
                    <Input
                      type="date"
                      value={(steering.last_printed_at || '').slice(0, 10)}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'last_printed_at', e.target.value || null))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Mahnstufe</Label>
                    <NativeSelect
                      value={String(steering.dunning_level ?? '')}
                      onValueChange={(v) => setState((s) => updateSteeringValue(s, 'dunning_level', v ? Number(v) : 0))}
                      options={[
                        { value: '0', label: 'Keine Mahnstufe' },
                        { value: '1', label: 'Mahnstufe 1' },
                        { value: '2', label: 'Mahnstufe 2' },
                        { value: '3', label: 'Mahnstufe 3 / Inkasso-Vorstufe' },
                      ]}
                      disabled={!isDraftEditable}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
                  <div className="space-y-1">
                    <Label>Washout-Status</Label>
                    <NativeSelect
                      value={steering.washout_status || ''}
                      onValueChange={(v) => setState((s) => updateSteeringValue(s, 'washout_status', v))}
                      options={[
                        { value: 'keiner', label: 'Keiner' },
                        { value: 'pruefen', label: 'Pruefen' },
                        { value: 'vereinbart', label: 'Vereinbart' },
                        { value: 'abgeschlossen', label: 'Abgeschlossen' },
                      ]}
                      placeholder="Bitte waehlen"
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Washout-Menge t</Label>
                    <Input
                      type="number"
                      value={steering.washout_quantity_t ?? ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'washout_quantity_t', e.target.value ? Number(e.target.value) : null))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Abschreibungsmenge t</Label>
                    <Input
                      type="number"
                      value={steering.writeoff_quantity_t ?? ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'writeoff_quantity_t', e.target.value ? Number(e.target.value) : null))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Washout-/Abschreibungsgrund</Label>
                    <Input
                      value={steering.washout_reason || steering.writeoff_reason || ''}
                      onChange={(e) => {
                        const value = e.target.value
                        setState((s) => updateSteeringValue(updateSteeringValue(s, 'washout_reason', value), 'writeoff_reason', value))
                      }}
                      disabled={!isDraftEditable}
                      placeholder="z. B. Qualitaetsabweichung / Kunde storniert"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
                  <div className="space-y-1">
                    <Label>Hedge-Strategie</Label>
                    <NativeSelect
                      value={steering.hedge_strategy || ''}
                      onValueChange={(v) => setState((s) => updateSteeringValue(s, 'hedge_strategy', v))}
                      options={[
                        { value: 'keine', label: 'Keine' },
                        { value: 'vollabsicherung', label: 'Vollabsicherung' },
                        { value: 'teilabsicherung', label: 'Teilabsicherung' },
                        { value: 'preisfenster', label: 'Preisfenster / Optionsstrategie' },
                      ]}
                      placeholder="Bitte waehlen"
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Terminmarktprodukt</Label>
                    <NativeSelect
                      value={steering.hedge_market || ''}
                      onValueChange={(v) => setState((s) => updateSteeringValue(s, 'hedge_market', v))}
                      options={[
                        { value: 'weizen_matif', label: 'Weizen MATIF' },
                        { value: 'mais_matif', label: 'Mais MATIF' },
                        { value: 'raps_matif', label: 'Raps MATIF' },
                        { value: 'sojaschrot_cbot', label: 'Sojaschrot CBOT' },
                        { value: 'futtergerste_matif', label: 'Futtergerste MATIF' },
                      ]}
                      placeholder="Bitte waehlen"
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Hedge-Status</Label>
                    <NativeSelect
                      value={steering.hedge_status || ''}
                      onValueChange={(v) => setState((s) => updateSteeringValue(s, 'hedge_status', v))}
                      options={[
                        { value: 'offen', label: 'Offen' },
                        { value: 'teilweise_gesichert', label: 'Teilweise gesichert' },
                        { value: 'voll_gesichert', label: 'Voll gesichert' },
                        { value: 'verfallen', label: 'Verfallen / glattgestellt' },
                      ]}
                      placeholder="Bitte waehlen"
                      disabled={!isDraftEditable}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
                  <div className="space-y-1">
                    <Label>Hedge-Ziel %</Label>
                    <Input
                      type="number"
                      value={steering.hedge_target_pct ?? ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'hedge_target_pct', e.target.value ? Number(e.target.value) : null))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Hedge-Menge t</Label>
                    <Input
                      type="number"
                      value={steering.hedge_quantity_t ?? ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'hedge_quantity_t', e.target.value ? Number(e.target.value) : null))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Marktpreis EUR/t</Label>
                    <Input
                      type="number"
                      value={steering.market_price_eur_t ?? ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'market_price_eur_t', e.target.value ? Number(e.target.value) : null))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Marktpreis-Datum</Label>
                    <Input
                      type="date"
                      value={(steering.market_price_date || '').slice(0, 10)}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'market_price_date', e.target.value || null))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
                  <div className="space-y-1">
                    <Label>Marktpreisquelle</Label>
                    <Input
                      value={steering.market_price_source || ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'market_price_source', e.target.value))}
                      disabled={!isDraftEditable}
                      placeholder="z. B. MATIF Settlement"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Mahnfaellig ab</Label>
                    <Input
                      type="date"
                      value={(steering.dunning_due_at || '').slice(0, 10)}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'dunning_due_at', e.target.value || null))}
                      disabled={!isDraftEditable}
                    />
                  </div>
                  <div className="flex items-center gap-2 pt-6">
                    <Checkbox
                      checked={Boolean(steering.dunning_blocked)}
                      onCheckedChange={(v) => setState((s) => updateSteeringValue(s, 'dunning_blocked', v === true))}
                      disabled={!isDraftEditable}
                    />
                    <Label>Mahnung gesperrt</Label>
                  </div>
                  <div className="space-y-1">
                    <Label>Mahn-Hinweis</Label>
                    <Input
                      value={steering.dunning_reason || ''}
                      onChange={(e) => setState((s) => updateSteeringValue(s, 'dunning_reason', e.target.value))}
                      disabled={!isDraftEditable}
                      placeholder="z. B. Wartet auf Qualitaetsabrechnung"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
                  <Card>
                    <CardContent className="py-4 text-sm">
                      <div className="text-xs uppercase tracking-wide text-muted-foreground">Hedge-Quote</div>
                      <div className="mt-2 text-lg font-semibold">
                        {steering.hedge_quote_pct != null ? `${formatNumber(steering.hedge_quote_pct, 1)}%` : '-'}
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {steering.hedge_gap_pct != null ? `Noch ${formatNumber(steering.hedge_gap_pct, 1)}% bis zum Ziel.` : 'Noch keine Absicherungsquote berechnet.'}
                      </p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="py-4 text-sm">
                      <div className="text-xs uppercase tracking-wide text-muted-foreground">Referenzpreis vs. Markt</div>
                      <div className="mt-2 text-lg font-semibold">
                        {steering.market_price_delta_eur_t != null ? `${formatNumber(steering.market_price_delta_eur_t, 2)} EUR/t` : '-'}
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Referenz {steering.reference_price_eur_t != null ? `${formatNumber(steering.reference_price_eur_t, 2)} EUR/t` : 'nicht gesetzt'}
                      </p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="py-4 text-sm">
                      <div className="text-xs uppercase tracking-wide text-muted-foreground">Marktbewertung Restmenge</div>
                      <div className="mt-2 text-lg font-semibold">
                        {steering.market_valuation_eur != null ? `${formatNumber(steering.market_valuation_eur, 2)} EUR` : '-'}
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Mahnung {steering.dunning_candidate ? 'waere heute faellig.' : 'aktuell nicht automatisch faellig.'}
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="bedingungen">
              <div className="space-y-2 py-2">
                <Label>Bedingungen (strukturiert)</Label>
                <Textarea
                  value={JSON.stringify(state.conditions_json || {}, null, 2)}
                  onChange={(e) => { try { setState((s) => ({ ...s, conditions_json: JSON.parse(e.target.value) })) } catch (_error) { /* ignore parse errors while typing */ } }}
                  disabled={!isDraftEditable}
                  rows={8}
                  className="font-mono text-xs"
                />
                <p className="text-xs text-muted-foreground">JSON-Format: Qualitaetsparameter, Trocknungsregeln, Sonderbedingungen</p>
              </div>
            </TabsContent>

            <TabsContent value="notizen">
              <div className="space-y-2 py-2">
                <Label>Interne Notizen</Label>
                <Textarea
                  value={state.notes || ''}
                  onChange={(e) => setState((s) => ({ ...s, notes: e.target.value }))}
                  disabled={!isDraftEditable}
                  rows={6}
                  placeholder="Interne Bemerkungen, Verhandlungsnotizen, Sonderwuensche ..."
                />
              </div>
            </TabsContent>

            <TabsContent value="unterlagen">
              <div className="space-y-2 py-2">
                <p className="text-sm text-muted-foreground">Kontraktbezogene Dokumente und Dateien.</p>
                <Button variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumentenablage oeffnen</Button>
              </div>
            </TabsContent>

            <TabsContent value="protokoll">{isEdit ? <FrmKontraktProtokoll contractId={String(id)} /> : <p className="py-2 text-sm text-muted-foreground">Protokoll erst nach dem Speichern verfuegbar.</p>}</TabsContent>
          </Tabs>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Positionen</CardTitle>
              <Button variant="outline" onClick={() => setState((s) => ({ ...s, lines: [...s.lines, createEmptyLine(s.lines.length + 1)] }))} disabled={!isDraftEditable || state.lines.length >= 3}>
                Position hinzufuegen
              </Button>
            </CardHeader>
            <CardContent>
              <div className="max-h-[320px] overflow-auto rounded border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Pos.-Nr</TableHead>
                      <TableHead>Artikel-Nr</TableHead>
                      <TableHead>Bezeichnung-1</TableHead>
                      <TableHead>Bezeichnung-2</TableHead>
                      <TableHead>Menge</TableHead>
                      <TableHead>Rest-Menge</TableHead>
                      <TableHead>Einheit</TableHead>
                      <TableHead>Einh.-Preis</TableHead>
                      <TableHead>Rabatt %</TableHead>
                      <TableHead>Aktionen</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {state.lines.map((line, index) => (
                      <TableRow key={`${line.line_id ?? 'new'}-${index}`}>
                        <TableCell>{line.position_no}</TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Input value={line.article_id} onChange={(e) => updateLine(index, { article_id: e.target.value })} disabled={!isDraftEditable} />
                            <Button type="button" variant="outline" disabled={!isDraftEditable} onClick={() => { setActiveLineIndex(index); setShowArticleDlg(true) }}>Suchen</Button>
                          </div>
                        </TableCell>
                        <TableCell><Input value={line.description1 || ''} onChange={(e) => updateLine(index, { description1: e.target.value })} disabled={!isDraftEditable} /></TableCell>
                        <TableCell><Input value={line.description2 || ''} onChange={(e) => updateLine(index, { description2: e.target.value })} disabled={!isDraftEditable} /></TableCell>
                        <TableCell><Input type="number" value={line.qty_contract} onChange={(e) => updateLine(index, { qty_contract: Number(e.target.value) })} disabled={!isDraftEditable} /></TableCell>
                        <TableCell>{line.qty_remaining ?? line.qty_contract}</TableCell>
                        <TableCell>{state.unit}</TableCell>
                        <TableCell><Input type="number" value={line.unit_price ?? 0} onChange={(e) => updateLine(index, { unit_price: Number(e.target.value) })} disabled={!isDraftEditable} /></TableCell>
                        <TableCell><Input type="number" value={line.discount_pct ?? 0} onChange={(e) => updateLine(index, { discount_pct: Number(e.target.value) })} disabled={!isDraftEditable} /></TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button type="button" variant="outline" disabled={!isDraftEditable || index === 0} onClick={() => moveLine(index, -1)}>?</Button>
                            <Button type="button" variant="outline" disabled={!isDraftEditable || index === state.lines.length - 1} onClick={() => moveLine(index, 1)}>?</Button>
                            <Button type="button" variant="destructive" disabled={!isDraftEditable || state.lines.length <= 1} onClick={() => removeLine(index)}>Loeschen</Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">Sammelkontrakt: 1 bis 3 Artikelpositionen. Bei "Gesamtkontrakt" muss die Summe der Positionsmengen der Gesamt-Menge entsprechen.</p>
            </CardContent>
          </Card>
        </CardContent>
      </Card>

      <DlgAuswahlVerkaufKontrakte
        open={showLookupDlg}
        onOpenChange={setShowLookupDlg}
        onSelect={(item) => {
          if (!state.lines.length) return
          updateLine(0, { article_id: item.article_id, description1: item.bezeichnung })
          toast({ title: 'Lookup uebernommen', description: `${item.contract_no}/${item.position_no}` })
        }}
      />

      <CustomerSelectionDialog
        open={showCustomerDlg}
        onClose={() => setShowCustomerDlg(false)}
        onSelect={(customer: Customer) => {
          setState((s) => ({ ...s, party_id: customer.id }))
          setSelectedCustomerName(customer.name || customer.company_name || customer.id)
          setShowCustomerDlg(false)
          toast({ title: 'Kunde uebernommen', description: `${customer.customerNumber} - ${customer.name}` })
        }}
        title="Kunde/Lieferant auswaehlen"
      />

      <ArtikelSuchDialog
        open={showArticleDlg}
        onClose={() => setShowArticleDlg(false)}
        onSelect={(article: LookupArticle) => {
          if (activeLineIndex === null) return
          updateLine(activeLineIndex, {
            article_id: article.articleNumber || article.id,
            description1: article.description || article.name || '',
            description2: article.description2 || '',
          })
          setShowArticleDlg(false)
          setActiveLineIndex(null)
          toast({ title: 'Artikel uebernommen', description: `${article.articleNumber} - ${article.description}` })
        }}
      />

      {isEdit && (
        <DlgKontraktUmSaetze
          open={showUmsaetze}
          onOpenChange={setShowUmsaetze}
          contractId={String(id)}
          contractNo={state.contract_no}
          validFrom={state.valid_from || null}
          validTo={state.valid_to || null}
          partner={state.party_id}
          quantityType={state.quantity_type}
          done={state.status === 'ERLEDIGT'}
          contractQty={state.total_quantity}
          restQty={detailQuery.data?.rest_quantity}
        />
      )}
      {showMatifDialog && (
        <DlgMatifPreisfixierung
          open={showMatifDialog}
          onOpenChange={setShowMatifDialog}
          contractNo={state.contract_no}
          pricingModel={state.pricing_model ?? null}
          basisReference={state.basis_reference ?? null}
          premiumType={state.premium_type ?? null}
          premiumValue={state.premium_value ?? null}
          minPrice={state.min_price ?? null}
          pricingWindowFrom={state.pricing_window_from ?? null}
          pricingWindowTo={state.pricing_window_to ?? null}
          lines={state.lines.map((l) => ({
            position_no: l.position_no,
            article_id: l.article_id,
            description1: l.description1,
            qty_contract: l.qty_contract,
            unit_price: l.unit_price ?? null,
          }))}
          onFixPrice={(lineIndex, fixedPrice) => {
            updateLine(lineIndex, { unit_price: fixedPrice })
            toast({ title: 'Preis fixiert', description: `Position ${lineIndex + 1}: ${fixedPrice} EUR/t` })
          }}
        />
      )}

      <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Kontrakt loeschen?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Kontrakt <strong>{state.contract_no || '(neu)'}</strong> wird als geloescht markiert
            und ist danach nicht mehr in der Kontraktliste sichtbar.
            {isAdmin && ' Als Admin kannst du mit force=true auch physisch loeschen.'}
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteConfirm(false)}>Abbrechen</Button>
            <Button variant="destructive" onClick={() => { setShowDeleteConfirm(false); deleteMutation.mutate() }}>
              Loeschen bestaetigen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
