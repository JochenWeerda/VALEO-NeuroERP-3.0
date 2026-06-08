/**
 * Ernte-Annahme-Erfassung (Agrar)
 * 1:1 Nachbau der zvoove Ernte-Annahme-Maske
 * Basierend auf Lieferschein-Erfassung (Gewohnheits-Prinzip)
 */

import { lazy, Suspense, useState, useEffect, useMemo, useRef } from 'react'
import { useLocation, useNavigate, useParams, useSearchParams } from '@/app/routing/react-router-compat'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { NativeSelect } from '@/components/ui/native-select'
import { useToast } from '@/components/ui/toast-provider'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import type { Customer } from '@/components/sales/CustomerSelectionDialog'

import type { WeighingTicket } from '@/components/agrar/WeighingTicketSelectionDialog'
import type { AgrarContract } from '@/components/agrar/ContractSelectionDialog'
import type { Variety } from '@/components/agrar/VarietySelectionDialog'

import { apiClient } from '@/lib/api-client'
import { useAuth } from '@/hooks/useAuth'
import { useGlobalShortcutsWithVoice } from '@/features/ki-usability'
import { ShortcutHintButton } from '@/components/shortcuts/ShortcutHelpPanel'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { WorkflowEntryBanner, readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'
import { saveFlowSpineResumeCheckpoint } from '@/lib/api/flow-spines'
import { ChevronLeft, ChevronRight, MoreHorizontal, Save, FileText, Folder, Calculator, Printer, Trash2, Download } from 'lucide-react'

const CustomerSelectionDialog = lazy(() =>
  import('@/components/sales/CustomerSelectionDialog').then((m) => ({ default: m.CustomerSelectionDialog }))
)
const ArtikelSuchDialog = lazy(() =>
  import('@/components/sales/ArtikelSuchDialog').then((m) => ({ default: m.ArtikelSuchDialog }))
)
const WeighingTicketSelectionDialog = lazy(() =>
  import('@/components/agrar/WeighingTicketSelectionDialog').then((m) => ({ default: m.WeighingTicketSelectionDialog }))
)
const ContractSelectionDialog = lazy(() =>
  import('@/components/agrar/ContractSelectionDialog').then((m) => ({ default: m.ContractSelectionDialog }))
)
const VarietySelectionDialog = lazy(() =>
  import('@/components/agrar/VarietySelectionDialog').then((m) => ({ default: m.VarietySelectionDialog }))
)
const DmsAnhangDialog = lazy(() =>
  import('@/components/dms/DmsAnhangDialog').then((m) => ({ default: m.DmsAnhangDialog }))
)

function LazyDialogBoundary({ children }: { children: JSX.Element }) {
  return <Suspense fallback={null}>{children}</Suspense>
}

// API Response Types
type HarvestAcceptanceResponse = {
  id: string
  acceptance_number: string
  tenant_id: string
  branch_id: string | null
  warehouse_id: string | null
  delivery_date: string
  delivery_time: string | null
  sales_rep_id: string | null
  operator_id: string
  weighing_ticket_id: string | null
  cost_center_id: string | null
  customer_id: string
  contract_id: string | null
  forwarder_id: string | null
  intermediate_dealer_id: string | null
  deviating_vat_id: string | null
  article_id: string | null
  variety_id: string | null
  vehicle_plate: string | null
  origin_nuts2_code: string | null
  nuts_version: string | null
  origin_postal_code: string | null
  origin_city: string | null
  origin_country_code: string | null
  is_sustainable_biomass: boolean
  release_status: string
  pricing_mode: string
  price_source_id: string | null
  acceptance_mode?: string | null
  ownership_type?: string | null
  vat_event?: string | null
  advance_payment_amount_eur?: number | null
  advance_payment_date?: string | null
  provisional_invoice_number: string | null
  invoice_id: string | null
  invoice_number: string | null
  stock_movement_id: string | null
  quality_protocol_id: string | null
  remarks: string | null
  print_remarks_on_acceptance_note: boolean
  print_remarks_on_settlement: boolean
  total_net_amount_eur: number | null
  total_vat_amount_eur: number | null
  total_gross_amount_eur: number | null
  vat_rate_percent: number | null
  created_at: string
  created_by: string | null
  updated_at: string | null
  updated_by: string | null
  article_name?: string | null
  positions?: Array<{
    id: string
    harvest_acceptance_id: string
    position_number: number
    description: string
    is_printable: boolean
    is_calculable: boolean
    lab_value_pct: number | null
    quantity_kg: number | null
    unit: string | null
    price_per_unit_eur: number | null
    amount_eur: number | null
    calculation_formula: string | null
  }>
}

type HarvestAcceptanceState = {
  id: string | null
  acceptanceNumber: string
  branchId: string | null
  warehouseId: string | null
  deliveryDate: string
  deliveryTime: string
  salesRepId: string | null
  operatorId: string
  weighingTicketId: string | null
  costCenterId: string | null
  qualityProtocolId: string | null
  customer: Customer | null
  contractId: string | null
  forwarderId: string | null
  intermediateDealerId: string | null
  deviatingVatId: string | null
  articleId: string | null
  articleName: string
  varietyId: string | null
  vehiclePlate: string
  originNuts2Code: string
  nutsVersion: string
  originPostalCode: string
  originCity: string
  originCountryCode: string
  isSustainableBiomass: boolean
  releaseStatus: 'draft' | 'provisional' | 'final' | 'credit_note_created' | 'paid' | 'disputed' | 'cancelled'
  pricingMode: 'fixed_contract' | 'spot_daily' | 'exchange_fix_later'
  priceSourceId: string | null
  acceptanceMode: string
  ownershipType: string
  vatEvent: string
  nawaroNr?: string
  nawaroZweck?: string
  biogasanlage?: string
  eegMenge?: number | null
  nachhaltigkeitsNachweis?: string
  advancePaymentAmountEur: number | null
  advancePaymentDate: string
  provisionalInvoiceNumber: string
  invoiceNumber: string
  remarks: string
  printRemarksOnAcceptanceNote: boolean
  printRemarksOnSettlement: boolean
  totalNetAmountEur: number | null
  totalVatAmountEur: number | null
  totalGrossAmountEur: number | null
  vatRatePercent: number | null
  positions: Array<{
    id?: string
    positionNumber: number
    description: string
    isPrintable: boolean
    isCalculable: boolean
    labValuePct: number | null
    quantityKg: number | null
    unit: string | null
    pricePerUnitEur: number | null
    amountEur: number | null
  }>
  labValues: {
    windabgang: number | null
    besatz: number | null
    feuchte: number | null
    hektolitergewicht: number | null
    lagerschwund: number | null
    lagergeld: number | null
    wiegegebuehren: number | null
  }
}

type QualityCheckHandoverState = {
  fromQualitaetsCheck?: boolean
  artikel?: string
  lieferscheinNr?: string
  lieferant?: string
  vehiclePlate?: string
  qualityProtocolId?: string
  harvestAcceptanceId?: string | null
  qpErgebnis?: 'freigegeben' | 'bedingt' | 'gesperrt'
}

type ArticleLookupCandidate = {
  id: string
  name?: string | null
  description?: string | null
  article_number?: string | null
  vat_rate?: number | null
  mwst_prozent?: number | null
  mehrwertsteuer_prozent?: number | null
}

function appendUniqueLines(baseText: string, lines: Array<string | null | undefined>): string {
  const existingLines = baseText
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
  const nextLines = [...existingLines]
  for (const line of lines.map((entry) => entry?.trim()).filter(Boolean) as string[]) {
    if (!nextLines.includes(line)) {
      nextLines.push(line)
    }
  }
  return nextLines.join('\n')
}

function normalizeArticleLookup(value: string): string {
  return value.trim().toLowerCase().replace(/\s+/g, ' ')
}

function extractArticleLookupCandidates(payload: any): ArticleLookupCandidate[] {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.items)) return payload.items
  if (Array.isArray(payload?.data?.items)) return payload.data.items
  if (Array.isArray(payload?.data)) return payload.data
  return []
}

export default function ErnteAnnahmeErfassungPage(): JSX.Element {
  const location = useLocation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { push } = useToast()
  const { user } = useAuth()
  const { id: acceptanceId } = useParams<{ id?: string }>()
  const workflowContext = useMemo(() => readWorkflowEntryContext(searchParams), [searchParams])

  const buildWorkflowResumeQuery = (savedId?: string | null): string => {
    const params = new URLSearchParams(searchParams)
    if (savedId) params.set('id', savedId)
    return params.toString()
  }

  const persistWorkflowResume = async (savedId?: string | null): Promise<void> => {
    if (!workflowContext?.process || !workflowContext.instanceId) return
    const effectiveId = savedId || state.id || acceptanceId || undefined
    const query = buildWorkflowResumeQuery(effectiveId)
    const basePath = effectiveId ? `/agrar/ernte-annahme-erfassung/${effectiveId}` : '/agrar/ernte-annahme-erfassung'
    await saveFlowSpineResumeCheckpoint(workflowContext.process, workflowContext.instanceId, {
      resume_node_id: 'acceptance',
      resume_route: `${basePath}${query ? `?${query}` : ''}`,
      resume_payload: {
        screen: 'harvest-acceptance',
        acceptanceId: effectiveId,
        workflowCase: workflowContext.caseNumber || undefined,
      },
      business_status: effectiveId ? 'annahme_erfasst' : 'annahme_in_bearbeitung',
      action_label: effectiveId ? 'Ernte-Annahme gespeichert' : 'Ernte-Annahme begonnen',
    })
  }
  const qualityCheckHandoverState = (location.state as QualityCheckHandoverState | null) ?? null

  // Helper: Format date to yyyy-MM-dd for input field
  const formatDateForInput = (date: Date): string => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  // Helper: Extrahiere User-Kürzel aus User-Objekt
  const getUserShortName = (): string => {
    if (!user) return 'SYSTEM'
    const shortName = user.name?.split(' ').map(n => n[0]).join('').toUpperCase() || 
                     user.sub?.substring(0, 2).toUpperCase() || 
                     'USER'
    return shortName.length > 2 ? shortName.substring(0, 2) : shortName
  }

  const [state, setState] = useState<HarvestAcceptanceState>({
    id: null,
    acceptanceNumber: '',
    branchId: null,
    warehouseId: null,
    deliveryDate: formatDateForInput(new Date()),
    deliveryTime: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
    salesRepId: null,
    operatorId: getUserShortName(),
    weighingTicketId: null,
    costCenterId: null,
    qualityProtocolId: null,
    customer: null,
    contractId: null,
    forwarderId: null,
    intermediateDealerId: null,
    deviatingVatId: null,
    articleId: null,
    varietyId: null,
    vehiclePlate: '',
    originNuts2Code: '',
    nutsVersion: 'NUTS 2024',
    originPostalCode: '',
    originCity: '',
    originCountryCode: 'DE',
    isSustainableBiomass: false,
    releaseStatus: 'draft',
    pricingMode: 'spot_daily',
    priceSourceId: null,
    acceptanceMode: 'PURCHASE_AT_DELIVERY_PTBF',
    ownershipType: 'OWN_STOCK',
    vatEvent: 'NO_INVOICE',
    nawaroNr: '',
    nawaroZweck: '',
    biogasanlage: '',
    eegMenge: null,
    nachhaltigkeitsNachweis: '',
    advancePaymentAmountEur: null,
    advancePaymentDate: '',
    provisionalInvoiceNumber: '',
    invoiceNumber: '',
    remarks: '',
    printRemarksOnAcceptanceNote: false,
    printRemarksOnSettlement: false,
    totalNetAmountEur: null,
    totalVatAmountEur: null,
    totalGrossAmountEur: null,
    vatRatePercent: null,
    articleName: '',
    positions: [],
    labValues: {
      windabgang: null,
      besatz: null,
      feuchte: null,
      hektolitergewicht: null,
      lagerschwund: null,
      lagergeld: null,
      wiegegebuehren: null,
    },
  })

  // Bediener aus Session aktualisieren
  useEffect(() => {
    if (user) {
      setState((prev) => ({
        ...prev,
        operatorId: getUserShortName(),
      }))
    }
  }, [user])

  useEffect(() => {
    if (!workflowContext) return
    setState((prev) => ({
      ...prev,
      remarks:
        prev.remarks ||
        [
          workflowContext.caseNumber ? `Workflow-Vorgang ${workflowContext.caseNumber}` : '',
          workflowContext.entryMode ? `Einstieg: ${workflowContext.entryMode}` : '',
          workflowContext.partnerName ? `Anlieferer: ${workflowContext.partnerName}` : '',
          workflowContext.subject,
        ]
          .filter(Boolean)
          .join('\n'),
    }))
  }, [workflowContext])

  useEffect(() => {
    if (acceptanceId) return

    const articleId = searchParams.get('articleId') || ''
    const articleName = searchParams.get('articleName') || qualityCheckHandoverState?.artikel || ''
    const vehiclePlate = searchParams.get('vehiclePlate') || qualityCheckHandoverState?.vehiclePlate || ''
    const qualityProtocolId = searchParams.get('qualityProtocolId') || qualityCheckHandoverState?.qualityProtocolId || ''
    const lieferscheinNr = searchParams.get('lieferscheinNr') || qualityCheckHandoverState?.lieferscheinNr || ''
    const qpResult = searchParams.get('qpResult') || qualityCheckHandoverState?.qpErgebnis || ''
    const partnerName = searchParams.get('partnerName') || qualityCheckHandoverState?.lieferant || ''
    const queueEntryId = searchParams.get('queueEntryId') || ''

    if (!articleId && !articleName && !vehiclePlate && !qualityProtocolId && !lieferscheinNr && !qpResult && !partnerName && !queueEntryId) {
      return
    }

    setState((prev) => ({
      ...prev,
      articleId: prev.articleId || articleId || null,
      articleName: prev.articleName || articleName,
      vehiclePlate: prev.vehiclePlate || vehiclePlate,
      qualityProtocolId: prev.qualityProtocolId || qualityProtocolId || null,
      remarks: appendUniqueLines(prev.remarks, [
        partnerName ? `Anlieferer: ${partnerName}` : '',
        lieferscheinNr ? `Lieferschein: ${lieferscheinNr}` : '',
        qpResult ? `Qualitaetspruefung: ${qpResult}` : '',
        qualityProtocolId ? `Qualitaetsprotokoll: ${qualityProtocolId}` : '',
        queueEntryId ? `Warteschlange: ${queueEntryId}` : '',
      ]),
    }))
  }, [acceptanceId, qualityCheckHandoverState, searchParams])

  useEffect(() => {
    if (acceptanceId || state.articleId || !state.articleName.trim()) {
      return
    }

    let isCancelled = false

    const resolveArticle = async (): Promise<void> => {
      try {
        const response = await apiClient.get<unknown>('/api/v1/articles', {
          params: {
            search: state.articleName.trim(),
            limit: 20,
          },
        })
        const candidates = extractArticleLookupCandidates(response)
        const wanted = normalizeArticleLookup(state.articleName)
        const matched =
          candidates.find((candidate) =>
            [candidate.name, candidate.description, candidate.article_number]
              .filter(Boolean)
              .some((value) => normalizeArticleLookup(String(value)) === wanted),
          ) ?? (candidates.length === 1 ? candidates[0] : null)

        if (!matched || isCancelled) {
          return
        }

        setState((prev) => {
          if (prev.articleId || normalizeArticleLookup(prev.articleName) !== wanted) {
            return prev
          }
          return {
            ...prev,
            articleId: matched.id,
            articleName: matched.name || matched.description || prev.articleName,
            vatRatePercent: matched.vat_rate || matched.mwst_prozent || matched.mehrwertsteuer_prozent || prev.vatRatePercent,
          }
        })
      } catch {
        // Artikel-Vorbelegung bei Übergabe schlägt still fehl — Felder bleiben leer
      }
    }

    void resolveArticle()

    return () => {
      isCancelled = true
    }
  }, [acceptanceId, state.articleId, state.articleName, state.vatRatePercent])

  // Lade bestehende Ernte-Annahme, wenn ID in URL vorhanden
  useEffect(() => {
    const loadHarvestAcceptance = async (): Promise<void> => {
      if (!acceptanceId) return

      try {
        const ha = await apiClient.get<HarvestAcceptanceResponse>(`/api/v1/agrar/harvest-acceptance/${acceptanceId}`)
        const positions = ha.positions ?? []
        const pos15 = positions.find((p: { position_number: number }) => p.position_number === 15)
        const pos20 = positions.find((p: { position_number: number }) => p.position_number === 20)
        const pos40 = positions.find((p: { position_number: number }) => p.position_number === 40)

        // Lade Kunde
        let customer: Customer | null = null
        if (ha.customer_id) {
          try {
            const { data: customerData } = await apiClient.get<any>(`/api/v1/crm/customers/${ha.customer_id}`)
            customer = {
              id: customerData.id,
              customerNumber: customerData.customer_number || customerData.customerNumber || '',
              name: customerData.company_name || customerData.name || '',
              debitorAccount: customerData.customer_number || customerData.customerNumber || '',
              representative: customerData.contact_person || customerData.representative,
              postalCode: customerData.postal_code || customerData.postalCode,
              city: customerData.city,
              chefanweisung: customerData.chefanweisung || customerData.executive_note,
            }
          } catch {
            // Kunden-Vorbelegung schlägt still fehl — Felder werden manuell befüllt
          }
        }

        // Parse delivery_date
        const deliveryDate = ha.delivery_date ? formatDateForInput(new Date(ha.delivery_date)) : formatDateForInput(new Date())

        // Parse delivery_time
        const deliveryTime = ha.delivery_time
          ? ha.delivery_time.substring(0, 5) // HH:MM
          : new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })

        setState({
          id: ha.id,
          acceptanceNumber: ha.acceptance_number,
          branchId: ha.branch_id,
          warehouseId: ha.warehouse_id,
          deliveryDate,
          deliveryTime,
          salesRepId: ha.sales_rep_id,
          operatorId: ha.operator_id || getUserShortName(),
          weighingTicketId: ha.weighing_ticket_id,
          costCenterId: ha.cost_center_id,
          qualityProtocolId: ha.quality_protocol_id,
          customer,
          contractId: ha.contract_id,
          forwarderId: ha.forwarder_id,
          intermediateDealerId: ha.intermediate_dealer_id,
          deviatingVatId: ha.deviating_vat_id,
          articleId: ha.article_id,
          varietyId: ha.variety_id,
          vehiclePlate: ha.vehicle_plate || '',
          originNuts2Code: ha.origin_nuts2_code || '',
          nutsVersion: ha.nuts_version || 'NUTS 2024',
          originPostalCode: ha.origin_postal_code || '',
          originCity: ha.origin_city || '',
          originCountryCode: ha.origin_country_code || 'DE',
          isSustainableBiomass: ha.is_sustainable_biomass,
          releaseStatus: ha.release_status as HarvestAcceptanceState['releaseStatus'],
          pricingMode: ha.pricing_mode as HarvestAcceptanceState['pricingMode'],
          priceSourceId: ha.price_source_id,
          acceptanceMode: ha.acceptance_mode || 'PURCHASE_AT_DELIVERY_PTBF',
          ownershipType: ha.ownership_type || 'OWN_STOCK',
          vatEvent: ha.vat_event || 'NO_INVOICE',
          advancePaymentAmountEur: ha.advance_payment_amount_eur ?? null,
          advancePaymentDate: ha.advance_payment_date || '',
          provisionalInvoiceNumber: ha.provisional_invoice_number || '',
          invoiceNumber: ha.invoice_number || '',
          remarks: ha.remarks || '',
          printRemarksOnAcceptanceNote: ha.print_remarks_on_acceptance_note,
          printRemarksOnSettlement: ha.print_remarks_on_settlement,
          totalNetAmountEur: ha.total_net_amount_eur,
          totalVatAmountEur: ha.total_vat_amount_eur,
          totalGrossAmountEur: ha.total_gross_amount_eur,
          vatRatePercent: ha.vat_rate_percent,
          articleName: ha.article_name ?? '',
          positions: positions.map((pos: { id: string; position_number: number; description: string; is_printable: boolean; is_calculable: boolean; lab_value_pct: number | null; quantity_kg: number | null; unit: string | null; price_per_unit_eur: number | null; amount_eur: number | null }) => ({
            id: pos.id,
            positionNumber: pos.position_number,
            description: pos.description,
            isPrintable: pos.is_printable,
            isCalculable: pos.is_calculable,
            labValuePct: pos.lab_value_pct,
            quantityKg: pos.quantity_kg,
            unit: pos.unit,
            pricePerUnitEur: pos.price_per_unit_eur,
            amountEur: pos.amount_eur,
          })),
          labValues: {
            windabgang: pos15?.lab_value_pct ?? null,
            besatz: pos20?.lab_value_pct ?? null,
            feuchte: pos40?.lab_value_pct ?? null,
            hektolitergewicht: null,
            lagerschwund: null,
            lagergeld: null,
            wiegegebuehren: null,
          },
        })

        push('Ernte-Annahme geladen')
      } catch (error: any) {
        push(`Fehler beim Laden: ${error.response?.data?.detail || error.message}`)
      }
    }

    void loadHarvestAcceptance()
  }, [acceptanceId, user, push])

  const [customerTab, setCustomerTab] = useState<'kunde' | 'rechnung' | 'kontrakt' | 'spediteur' | 'nawaro' | 'zw-haendler'>('kunde')
  const [deliveryTab, setDeliveryTab] = useState<'anlieferung' | 'abrechnung'>('anlieferung')
  const [showCustomerDialog, setShowCustomerDialog] = useState(false)
  const [showArticleDialog, setShowArticleDialog] = useState(false)
  const [showWeighingTicketDialog, setShowWeighingTicketDialog] = useState(false)
  const [showVarietyDialog, setShowVarietyDialog] = useState(false)
  const [showContractDialog, setShowContractDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showAttachmentDialog, setShowAttachmentDialog] = useState(false)
  const [showForwarderDialog, setShowForwarderDialog] = useState(false)
  const [forwarderName, setForwarderName] = useState('')
  const [showIntermediateDealerDialog, setShowIntermediateDealerDialog] = useState(false)
  const [intermediateDealerName, setIntermediateDealerName] = useState('')
  const [showZusFelderDialog, setShowZusFelderDialog] = useState(false)
  const [showUstIdDialog, setShowUstIdDialog] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [ustIdDialogValue, setUstIdDialogValue] = useState('')
  const importAnalyseInputRef = useRef<HTMLInputElement | null>(null)

  // Keyboard Shortcuts
  useGlobalShortcutsWithVoice({
    'copy-previous-full': () => {
      void handleCopyPreviousFull()
    },
    'copy-previous-positions': () => {
      void handleCopyPreviousFull()
    },
    'save-document': () => {
      void handleSave()
    },
    'open-customer-selection': () => {
      setShowCustomerDialog(true)
    },
    'open-article-selection': () => {
      setShowArticleDialog(true)
    },
  })

  // Speichern
  const handleSave = async (): Promise<string | null> => {
    setIsSaving(true)
    try {
      if (!state.customer) {
        push('Bitte wählen Sie einen Kunden aus')
        return null
      }

      const [hours, minutes] = state.deliveryTime.split(':')
      const deliveryTime = `${hours}:${minutes}:00`

      const payload = {
        acceptance_number: state.acceptanceNumber || undefined,
        branch_id: state.branchId || undefined,
        warehouse_id: state.warehouseId || undefined,
        delivery_date: state.deliveryDate,
        delivery_time: deliveryTime,
        sales_rep_id: state.salesRepId || undefined,
        weighing_ticket_id: state.weighingTicketId || undefined,
        cost_center_id: state.costCenterId || undefined,
        quality_protocol_id: state.qualityProtocolId || undefined,
        customer_id: state.customer.id,
        contract_id: state.contractId || undefined,
        forwarder_id: state.forwarderId || undefined,
        intermediate_dealer_id: state.intermediateDealerId || undefined,
        deviating_vat_id: state.deviatingVatId || undefined,
        article_id: state.articleId || undefined,
        variety_id: state.varietyId || undefined,
        vehicle_plate: state.vehiclePlate || undefined,
        origin_nuts2_code: state.originNuts2Code || undefined,
        nuts_version: state.nutsVersion,
        origin_postal_code: state.originPostalCode || undefined,
        origin_city: state.originCity || undefined,
        origin_country_code: state.originCountryCode,
        is_sustainable_biomass: state.isSustainableBiomass,
        pricing_mode: state.pricingMode,
        price_source_id: state.priceSourceId || undefined,
        acceptance_mode: state.acceptanceMode || undefined,
        ownership_type: state.ownershipType || undefined,
        vat_event: state.vatEvent || undefined,
        advance_payment_amount_eur: state.advancePaymentAmountEur ?? undefined,
        advance_payment_date: state.advancePaymentDate || undefined,
        remarks: state.remarks || undefined,
        print_remarks_on_acceptance_note: state.printRemarksOnAcceptanceNote,
        print_remarks_on_settlement: state.printRemarksOnSettlement,
        positions: state.positions.map(pos => ({
          position_number: pos.positionNumber,
          description: pos.description,
          is_printable: pos.isPrintable,
          is_calculable: pos.isCalculable,
          lab_value_pct: pos.labValuePct,
          quantity_kg: pos.quantityKg,
          unit: pos.unit,
          price_per_unit_eur: pos.pricePerUnitEur,
          amount_eur: pos.amountEur,
        })),
      }

      let response: HarvestAcceptanceResponse
      if (state.id) {
        // Update
        response = await apiClient.put<HarvestAcceptanceResponse>(`/api/v1/agrar/harvest-acceptance/${state.id}`, payload)
      } else {
        // Create
        response = await apiClient.post<HarvestAcceptanceResponse>('/api/v1/agrar/harvest-acceptance', payload)
      }

      setState((prev) => ({
        ...prev,
        id: response.id,
        acceptanceNumber: response.acceptance_number,
      }))
      await persistWorkflowResume(response.id)
      if (!state.id) {
        const query = buildWorkflowResumeQuery(response.id)
        navigate(`/agrar/ernte-annahme-erfassung/${response.id}${query ? `?${query}` : ''}`, { replace: true })
      }
      push('Ernte-Annahme erfolgreich gespeichert')
      return response.id
    } catch (error: any) {
      push(`Fehler beim Speichern: ${error.response?.data?.detail || error.message}`)
      return null
    } finally {
      setIsSaving(false)
    }
  }

  // Berechnung neu
  const handleCalculate = async (): Promise<void> => {
    if (!state.id) {
      push('Bitte speichern Sie zuerst die Ernte-Annahme')
      return
    }

    try {
      await apiClient.post(`/api/v1/agrar/harvest-acceptance/${state.id}/calculate`)
      push('Berechnung erfolgreich durchgeführt')
      
      // Lade aktualisierte Daten
      const response = await apiClient.get<HarvestAcceptanceResponse>(`/api/v1/agrar/harvest-acceptance/${state.id}`)
      _applyAcceptanceResponse(response)
    } catch (error: any) {
      push(`Fehler bei der Berechnung: ${error.response?.data?.detail || error.message}`)
    }
  }

  const _applyAcceptanceResponse = (response: HarvestAcceptanceResponse): void => {
    setState((prev) => ({
      ...prev,
      positions: response.positions?.map(pos => ({
        id: pos.id,
        positionNumber: pos.position_number,
        description: pos.description,
        isPrintable: pos.is_printable,
        isCalculable: pos.is_calculable,
        labValuePct: pos.lab_value_pct,
        quantityKg: pos.quantity_kg,
        unit: pos.unit,
        pricePerUnitEur: pos.price_per_unit_eur,
        amountEur: pos.amount_eur,
      })) || [],
      totalNetAmountEur: response.total_net_amount_eur,
      totalVatAmountEur: response.total_vat_amount_eur,
      totalGrossAmountEur: response.total_gross_amount_eur,
      vatRatePercent: response.vat_rate_percent,
    }))
  }

  const handleAbschlagrechnung = async (): Promise<void> => {
    if (!state.id) { push('Bitte zuerst Ernte-Annahme speichern'); return }
    try {
      const calcResult = await apiClient.post<{ total_gross_amount_eur?: number }>(`/api/v1/agrar/harvest-acceptance/${state.id}/calculate`)
      const brutto = calcResult?.total_gross_amount_eur != null ? `${Number(calcResult.total_gross_amount_eur).toFixed(2)} EUR` : '-'
      push(`Abschlagrechnung berechnet. Bruttobetrag: ${brutto}`)
      const response = await apiClient.get<HarvestAcceptanceResponse>(`/api/v1/agrar/harvest-acceptance/${state.id}`)
      _applyAcceptanceResponse(response)
    } catch (error: any) {
      push(`Fehler: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleEndabrechnung = async (): Promise<void> => {
    if (!state.id) { push('Bitte zuerst Ernte-Annahme speichern'); return }
    try {
      const calcResult = await apiClient.post<{ total_gross_amount_eur?: number }>(`/api/v1/agrar/harvest-acceptance/${state.id}/calculate`)
      const brutto = calcResult?.total_gross_amount_eur != null ? `${Number(calcResult.total_gross_amount_eur).toFixed(2)} EUR` : '-'
      push(`Endabrechnung berechnet. Bruttobetrag: ${brutto}`)
      const response = await apiClient.get<HarvestAcceptanceResponse>(`/api/v1/agrar/harvest-acceptance/${state.id}`)
      _applyAcceptanceResponse(response)
    } catch (error: any) {
      push(`Fehler: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleImportAnalyse = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      try {
        const text = String(reader.result ?? '')
        const lines = text.split(/\r?\n/).filter(Boolean)
        if (lines.length < 2) { push('Datei enthält keine Daten (mind. Kopfzeile + eine Zeile).'); return }
        const sep = text.includes(';') ? ';' : ','
        const headers = lines[0].split(sep).map(h => h.trim().toLowerCase().replace(/\s+/g, ''))
        const valIdx = headers.findIndex(h => h === 'wert' || h === 'value' || h === 'laborwert')
        const nameIdx = headers.findIndex(h => h === 'parameter' || h === 'bezeichnung' || h === 'name')
        const lab: Record<string, number | null> = {
          windabgang: state.labValues.windabgang,
          besatz: state.labValues.besatz,
          feuchte: state.labValues.feuchte,
          hektolitergewicht: state.labValues.hektolitergewicht,
          lagerschwund: state.labValues.lagerschwund,
          lagergeld: state.labValues.lagergeld,
          wiegegebuehren: state.labValues.wiegegebuehren,
        }
        const nameToKey: Record<string, keyof typeof lab> = {
          windabgang: 'windabgang', besatz: 'besatz', feuchte: 'feuchte',
          hektolitergewicht: 'hektolitergewicht', 'hektoliter-gewicht': 'hektolitergewicht',
          lagerschwund: 'lagerschwund', lagergeld: 'lagergeld', wiegegebuehren: 'wiegegebuehren',
        }
        for (let i = 1; i < lines.length; i++) {
          const cells = lines[i].split(sep).map(c => c.trim())
          const name = nameIdx >= 0 ? cells[nameIdx]?.toLowerCase().replace(/\s+/g, '') : (headers[0] ? cells[0] : '')
          const val = valIdx >= 0 ? parseFloat(cells[valIdx]?.replace(',', '.')) : parseFloat(cells[1]?.replace(',', '.'))
          const key = nameToKey[name] ?? (name in lab ? (name as keyof typeof lab) : null)
          if (key && !Number.isNaN(val)) lab[key] = val
        }
        const updatedLabValues = { ...state.labValues, ...lab }
        const updatedPositions = state.positions.map(p => {
          if (p.positionNumber === 15 && lab.windabgang != null) return { ...p, labValuePct: lab.windabgang }
          if (p.positionNumber === 20 && lab.besatz != null) return { ...p, labValuePct: lab.besatz }
          if (p.positionNumber === 40 && lab.feuchte != null) return { ...p, labValuePct: lab.feuchte }
          if (p.positionNumber === 60 && lab.hektolitergewicht != null) return { ...p, quantityKg: lab.hektolitergewicht }
          if (p.positionNumber === 63 && lab.lagerschwund != null) return { ...p, labValuePct: lab.lagerschwund }
          if (p.positionNumber === 75 && lab.lagergeld != null) return { ...p, amountEur: lab.lagergeld }
          if (p.positionNumber === 80 && lab.wiegegebuehren != null) return { ...p, amountEur: lab.wiegegebuehren }
          return p
        })
        setState(prev => ({ ...prev, labValues: updatedLabValues, positions: updatedPositions }))
        push('Laborwerte aus Datei übernommen.')
      } catch (err) {
        push('Import fehlgeschlagen. Erwartet: CSV mit Kopfzeile (z. B. Parameter;Wert oder Bezeichnung;Wert).')
      }
      e.target.value = ''
    }
    reader.readAsText(file, 'utf-8')
  }

  // Freigabe
  const handleRelease = async (status: 'provisional' | 'final'): Promise<void> => {
    if (!state.id) {
      push('Bitte speichern Sie zuerst die Ernte-Annahme')
      return
    }

    setIsSaving(true)
    try {
      await apiClient.post(`/api/v1/agrar/harvest-acceptance/${state.id}/release`, {
        release_status: status,
        create_stock_movement: true,
      })
      push(`Ernte-Annahme erfolgreich freigegeben (${status})`)
      
      // Lade aktualisierte Daten
      const response = await apiClient.get<HarvestAcceptanceResponse>(`/api/v1/agrar/harvest-acceptance/${state.id}`)
      setState((prev) => ({
        ...prev,
        releaseStatus: response.release_status as HarvestAcceptanceState['releaseStatus'],
      }))
    } catch (error: any) {
      push(`Fehler bei der Freigabe: ${error.response?.data?.detail || error.message}`)
    } finally {
      setIsSaving(false)
    }
  }

  // Kunde auswählen
  const handleCustomerSelect = (customer: Customer): void => {
    setState((prev) => ({
      ...prev,
      customer,
      salesRepId: customer.representative || null,
    }))
    setShowCustomerDialog(false)
  }

  // Artikel auswählen
  const handleArticleSelect = (article: any): void => {
    setState((prev) => ({
      ...prev,
      articleId: article.id,
      articleName: article.name || article.bezeichnung || article.description || '',
      vatRatePercent: article.vat_rate || article.mwst_prozent || article.mehrwertsteuer_prozent || 7.0,
    }))
    setShowArticleDialog(false)
  }

  // Wiegeschein auswählen
  const handleWeighingTicketSelect = (ticket: WeighingTicket): void => {
    // Übernehme Netto-Gewicht in Position 10 (Angelieferte Menge)
    const updatedPositions = [...state.positions]
    const pos10Index = updatedPositions.findIndex(p => p.positionNumber === 10)
    if (pos10Index >= 0 && ticket.net_weight) {
      updatedPositions[pos10Index].quantityKg = ticket.net_weight
    }

    // Übernehme Laborwerte
    const updatedLabValues = { ...state.labValues }
    if (ticket.moisture_pct !== null) {
      updatedLabValues.feuchte = ticket.moisture_pct
      // Position 40 (Feuchte/Tr.verlust)
      const pos40Index = updatedPositions.findIndex(p => p.positionNumber === 40)
      if (pos40Index >= 0) {
        updatedPositions[pos40Index].labValuePct = ticket.moisture_pct
      }
    }
    if (ticket.impurities_pct !== null) {
      updatedLabValues.besatz = ticket.impurities_pct
      // Position 20 (Besatz 2% frei)
      const pos20Index = updatedPositions.findIndex(p => p.positionNumber === 20)
      if (pos20Index >= 0) {
        updatedPositions[pos20Index].labValuePct = ticket.impurities_pct
      }
    }
    if (ticket.hl_weight !== null) {
      updatedLabValues.hektolitergewicht = ticket.hl_weight
      // Position 60 (Hektolitergewicht)
      const pos60Index = updatedPositions.findIndex(p => p.positionNumber === 60)
      if (pos60Index >= 0) {
        updatedPositions[pos60Index].quantityKg = ticket.hl_weight
      }
    }

    setState((prev) => ({
      ...prev,
      weighingTicketId: ticket.id,
      vehiclePlate: ticket.vehicle_plate || prev.vehiclePlate,
      positions: updatedPositions,
      labValues: updatedLabValues,
    }))
    setShowWeighingTicketDialog(false)
  }

  // Kontrakt auswählen
  const handleContractSelect = (contract: AgrarContract): void => {
    setState((prev) => ({
      ...prev,
      contractId: contract.id,
      pricingMode: contract.pricing_model === 'fixed' ? 'fixed_contract' : 'spot_daily',
    }))
    setShowContractDialog(false)
  }

  // Sorte auswählen
  const handleVarietySelect = (variety: Variety): void => {
    setState((prev) => ({
      ...prev,
      varietyId: variety.variety_number, // Oder variety.id, je nach Backend-Erwartung
    }))
    setShowVarietyDialog(false)
  }

  // Wie vorheriger Annahmeschein (F11 / Strg+F8)
  const handleCopyPreviousFull = async (): Promise<void> => {
    try {
      const response = await apiClient.get<HarvestAcceptanceResponse | null>('/api/v1/agrar/harvest-acceptance/last', {
        params: {
          operator_id: user?.sub || undefined,
          customer_id: state.customer?.id || undefined,
        },
      })
      
      if (!response) {
        push('Kein vorheriger Annahmeschein gefunden')
        return
      }
      
      // Lade Kunde
      let customer: Customer | null = null
      if (response.customer_id) {
        try {
          const customerData = await apiClient.get<any>(`/api/v1/crm/customers/${response.customer_id}`)
          customer = {
            id: customerData.id,
            customerNumber: customerData.customer_number || customerData.customerNumber || '',
            name: customerData.company_name || customerData.name || '',
            debitorAccount: customerData.customer_number || customerData.customerNumber || '',
            representative: customerData.contact_person || customerData.representative,
            postalCode: customerData.postal_code || customerData.postalCode,
            city: customerData.city,
            chefanweisung: customerData.chefanweisung || customerData.executive_note,
          }
        } catch {
          // Kunden-Vorbelegung schlägt still fehl — Felder werden manuell befüllt
        }
      }

      // Parse delivery_date
      const deliveryDate = response.delivery_date ? formatDateForInput(new Date(response.delivery_date)) : formatDateForInput(new Date())
      
      // Parse delivery_time
      const deliveryTime = response.delivery_time 
        ? response.delivery_time.substring(0, 5) // HH:MM
        : new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })

      // Mappe Positionen
      const positions = response.positions?.map(pos => ({
        id: pos.id,
        positionNumber: pos.position_number,
        description: pos.description,
        isPrintable: pos.is_printable,
        isCalculable: pos.is_calculable,
        labValuePct: pos.lab_value_pct,
        quantityKg: pos.quantity_kg,
        unit: pos.unit,
        pricePerUnitEur: pos.price_per_unit_eur,
        amountEur: pos.amount_eur,
      })) || []

      // Extrahiere Laborwerte aus Positionen
      const labValues = {
        windabgang: positions.find(p => p.positionNumber === 15)?.labValuePct || null,
        besatz: positions.find(p => p.positionNumber === 20)?.labValuePct || null,
        feuchte: positions.find(p => p.positionNumber === 40)?.labValuePct || null,
        hektolitergewicht: positions.find(p => p.positionNumber === 60)?.quantityKg || null,
        lagerschwund: positions.find(p => p.positionNumber === 63)?.labValuePct || null,
        lagergeld: positions.find(p => p.positionNumber === 75)?.amountEur || null,
        wiegegebuehren: positions.find(p => p.positionNumber === 80)?.amountEur || null,
      }

      // Setze State (ohne ID und acceptance_number, damit neue Ernte-Annahme erstellt wird)
      setState((prev) => ({
        ...prev,
        id: null, // Neue Ernte-Annahme
        acceptanceNumber: '', // Wird vom Backend generiert
        branchId: response.branch_id,
        warehouseId: response.warehouse_id,
        deliveryDate,
        deliveryTime,
        salesRepId: response.sales_rep_id,
        operatorId: response.operator_id || getUserShortName(),
        weighingTicketId: null, // Nicht übernehmen
        costCenterId: response.cost_center_id,
        customer,
        contractId: response.contract_id,
        forwarderId: response.forwarder_id,
        intermediateDealerId: response.intermediate_dealer_id,
        deviatingVatId: response.deviating_vat_id,
        articleId: response.article_id,
        varietyId: response.variety_id,
        vehiclePlate: response.vehicle_plate || '',
        originNuts2Code: response.origin_nuts2_code || '',
        nutsVersion: response.nuts_version || 'NUTS 2024',
        originPostalCode: response.origin_postal_code || '',
        originCity: response.origin_city || '',
        originCountryCode: response.origin_country_code || 'DE',
        isSustainableBiomass: response.is_sustainable_biomass,
        releaseStatus: 'draft', // Immer Draft für neue Ernte-Annahme
        pricingMode: response.pricing_mode as HarvestAcceptanceState['pricingMode'],
        priceSourceId: response.price_source_id,
        acceptanceMode: response.acceptance_mode || 'PURCHASE_AT_DELIVERY_PTBF',
        ownershipType: response.ownership_type || 'OWN_STOCK',
        vatEvent: response.vat_event || 'NO_INVOICE',
        advancePaymentAmountEur: response.advance_payment_amount_eur ?? null,
        advancePaymentDate: response.advance_payment_date || '',
        provisionalInvoiceNumber: '',
        invoiceNumber: '',
        remarks: response.remarks || '',
        printRemarksOnAcceptanceNote: response.print_remarks_on_acceptance_note,
        printRemarksOnSettlement: response.print_remarks_on_settlement,
        totalNetAmountEur: null, // Wird neu berechnet
        totalVatAmountEur: null,
        totalGrossAmountEur: null,
        vatRatePercent: response.vat_rate_percent,
        articleName: response.article_name ?? '',
        positions,
        labValues,
      }))

      push('Daten vom vorherigen Annahmeschein übernommen')
    } catch (error: any) {
      push(`Fehler: ${error.response?.data?.detail || error.message}`)
    }
  }

  // Löschen
  const handleDelete = async (): Promise<void> => {
    if (!state.id) {
      push('Keine Ernte-Annahme zum Löschen vorhanden')
      return
    }

    if (state.releaseStatus !== 'draft') {
      push(`Ernte-Annahme kann nicht gelöscht werden. Status: ${state.releaseStatus}. Nur 'draft' kann gelöscht werden.`)
      return
    }

    setIsSaving(true)
    try {
      await apiClient.delete(`/api/v1/agrar/harvest-acceptance/${state.id}`)
      push('Ernte-Annahme erfolgreich gelöscht')
      setShowDeleteDialog(false)
      navigate('/agrar/ernte')
    } catch (error: any) {
      push(`Fehler beim Löschen: ${error.response?.data?.detail || error.message}`)
    } finally {
      setIsSaving(false)
    }
  }

  // Standard-Positionen initialisieren (14 Positionen)
  const initializePositions = (): void => {
    const standardPositions = [
      { positionNumber: 10, description: 'Angelieferte Menge', isPrintable: true, isCalculable: true, unit: 'kg' },
      { positionNumber: 15, description: 'Windabgang', isPrintable: true, isCalculable: false, unit: 'kg' },
      { positionNumber: 20, description: 'Besatz 2% frei', isPrintable: true, isCalculable: false, unit: 'kg' },
      { positionNumber: 30, description: 'Gereinigte Menge', isPrintable: true, isCalculable: true, unit: 'kg' },
      { positionNumber: 40, description: 'Feuchte/Tr.verlust', isPrintable: true, isCalculable: true, unit: 'kg' },
      { positionNumber: 50, description: 'Zwischenmenge', isPrintable: false, isCalculable: false, unit: 'kg' },
      { positionNumber: 60, description: 'Hektolitergewicht', isPrintable: true, isCalculable: false, unit: 'kg/hl' },
      { positionNumber: 63, description: 'Lagerschwund', isPrintable: false, isCalculable: true, unit: 'kg' },
      { positionNumber: 65, description: 'Nettogewicht', isPrintable: true, isCalculable: true, unit: 'kg' },
      { positionNumber: 70, description: 'Feuchtigkeitsabzug', isPrintable: true, isCalculable: false, unit: 'kg' },
      { positionNumber: 75, description: 'Lagergeld', isPrintable: false, isCalculable: false, unit: 'Mon.' },
      { positionNumber: 78, description: 'Frachtkosten', isPrintable: false, isCalculable: true, unit: 'kg' },
      { positionNumber: 80, description: 'Wiegegebühren', isPrintable: false, isCalculable: false, unit: 'Euro/St' },
      { positionNumber: 110, description: 'Gutschriftsbetrag', isPrintable: true, isCalculable: true, unit: 'kg' },
    ]

    setState((prev) => ({
      ...prev,
      positions: standardPositions.map(pos => ({
        positionNumber: pos.positionNumber,
        description: pos.description,
        isPrintable: pos.isPrintable,
        isCalculable: pos.isCalculable,
        labValuePct: null,
        quantityKg: null,
        unit: pos.unit,
        pricePerUnitEur: null,
        amountEur: null,
      })),
    }))
  }

  // Initialisiere Positionen beim ersten Laden
  useEffect(() => {
    if (state.positions.length === 0 && !acceptanceId) {
      initializePositions()
    }
  }, [])

  return (
    <div className="space-y-4 p-4">
      <ModuleToolbar
        backTarget="/agrar/ernte"
        closeTarget="/agrar/ernte"
        title="Ernte-Annahme-Erfassung"
      />
      {workflowContext ? (
        <WorkflowEntryBanner
          context={workflowContext}
          title="Workflow-Handover aus Harvest-to-Settlement"
          description="Wiegeschein, Qualitaet, Trocknung, Kontraktbezug und Settlement werden jetzt in der Annahme-Maske gepflegt. Der Flow-Fall bleibt als Referenz erhalten."
        />
      ) : null}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Ernte-Annahme-Erfassung</h1>
          <p className="text-sm text-muted-foreground">Erfassung und Abrechnung von Ernte-Anlieferungen</p>
        </div>
        <div className="flex gap-2">
          <ShortcutHintButton shortcut="Strg+S">
            <Button onClick={() => void handleSave()} size="sm" className="gap-2" disabled={isSaving}>
              <Save className="h-4 w-4" />
              Speichern
            </Button>
          </ShortcutHintButton>
          <Button variant="outline" onClick={() => navigate('/agrar/ernte')} size="sm">
            Schließen
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Linke Spalte - Hauptbereich */}
        <div className="lg:col-span-2 space-y-4">
          {/* Header-Bereich */}
          <Card className="p-4">
            <h2 className="mb-4 font-semibold text-sm">Ernte-Abrechnung</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Annahmesch.-Nr.:</Label>
                <div className="flex gap-1">
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Input
                    value={state.acceptanceNumber}
                    onChange={(e) => setState((prev) => ({ ...prev, acceptanceNumber: e.target.value }))}
                    className="h-8 flex-1"
                    placeholder="Auto-generiert"
                  />
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Niederlassung:</Label>
                <Input
                  value={state.branchId || ''}
                  onChange={(e) => setState((prev) => ({ ...prev, branchId: e.target.value || null }))}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Lagerhalle:</Label>
                <Input
                  value={state.warehouseId || ''}
                  onChange={(e) => setState((prev) => ({ ...prev, warehouseId: e.target.value || null }))}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Liefer-Datum:</Label>
                <div className="flex gap-1">
                  <Input
                    type="date"
                    value={state.deliveryDate}
                    onChange={(e) => setState((prev) => ({ ...prev, deliveryDate: e.target.value }))}
                    className="h-8 flex-1"
                  />
                  <Input
                    type="time"
                    value={state.deliveryTime}
                    onChange={(e) => setState((prev) => ({ ...prev, deliveryTime: e.target.value }))}
                    className="h-8 w-20"
                  />
                </div>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Vertriebsbeauftragter:</Label>
                <Input
                  value={state.salesRepId || ''}
                  onChange={(e) => setState((prev) => ({ ...prev, salesRepId: e.target.value || null }))}
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Bediener:</Label>
                <Input
                  value={state.operatorId}
                  readOnly
                  className="h-8"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Wiegeschein-Nr.:</Label>
                <div className="flex gap-1">
                  <Input
                    value={state.weighingTicketId || ''}
                    onChange={(e) => setState((prev) => ({ ...prev, weighingTicketId: e.target.value || null }))}
                    className="h-8 flex-1"
                  />
                  <ShortcutHintButton shortcut="Strg+F3">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={() => setShowWeighingTicketDialog(true)}
                    >
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </ShortcutHintButton>
                </div>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Kostenstelle:</Label>
                <Input
                  value={state.costCenterId || ''}
                  onChange={(e) => setState((prev) => ({ ...prev, costCenterId: e.target.value || null }))}
                  className="h-8"
                />
              </div>
            </div>
          </Card>

          {/* Tabs: KUNDE, RECHNUNG, KONTRAKT, etc. */}
          <Card className="p-4">
            <Tabs value={customerTab} onValueChange={(v) => setCustomerTab(v as typeof customerTab)}>
              <TabsList className="grid w-full grid-cols-6 h-auto">
                <TabsTrigger value="kunde" className="text-xs py-1">KUNDE</TabsTrigger>
                <TabsTrigger value="rechnung" className="text-xs py-1">RECHNUNG</TabsTrigger>
                <TabsTrigger value="kontrakt" className="text-xs py-1">KONTRAKT</TabsTrigger>
                <TabsTrigger value="spediteur" className="text-xs py-1">SPEDITEUR</TabsTrigger>
                <TabsTrigger value="nawaro" className="text-xs py-1">NAWARO</TabsTrigger>
                <TabsTrigger value="zw-haendler" className="text-xs py-1">ZW-HÄNDLER</TabsTrigger>
              </TabsList>

              <TabsContent value="kunde" className="mt-4 space-y-2">
                <div className="flex items-center gap-2">
                  <Label className="w-32 text-sm">Debitor-Kto.:</Label>
                  <Input
                    value={state.customer?.debitorAccount || ''}
                    readOnly
                    className="flex-1 h-8"
                  />
                  <ShortcutHintButton shortcut="Strg+F1">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0"
                      onClick={() => setShowCustomerDialog(true)}
                    >
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </ShortcutHintButton>
                </div>
                {state.customer && (
                  <div className="text-sm space-y-1 pl-32">
                    <div>{state.customer.name}</div>
                    {state.customer.address?.street && (
                      <div>{state.customer.address.street}</div>
                    )}
                    {(state.customer.postalCode || state.customer.city) && (
                      <div>{[state.customer.postalCode, state.customer.city].filter(Boolean).join(' ')}</div>
                    )}
                  </div>
                )}
                <div className="flex items-center gap-2 pl-32">
                  <Checkbox id="wie-vorheriger-as" />
                  <Label htmlFor="wie-vorheriger-as" className="text-sm cursor-pointer">
                    &gt;&gt; wie vorheriger AS (F11)
                  </Label>
                </div>
                <div className="flex items-center gap-2 pl-32">
                  <Checkbox id="kunden-stamm" />
                  <Label htmlFor="kunden-stamm" className="text-sm cursor-pointer">
                    Kunden-Stamm
                  </Label>
                </div>
                <div className="flex items-center gap-2 pl-32">
                  <Checkbox
                    id="abweichende-ustid"
                    checked={!!state.deviatingVatId}
                    onCheckedChange={(checked) => {
                      if (checked) {
                        setUstIdDialogValue(state.deviatingVatId || '')
                        setShowUstIdDialog(true)
                      } else {
                        setState((prev) => ({ ...prev, deviatingVatId: null }))
                      }
                    }}
                  />
                  <Label
                    htmlFor="abweichende-ustid"
                    className="text-sm cursor-pointer"
                    onClick={() => {
                      setUstIdDialogValue(state.deviatingVatId || '')
                      setShowUstIdDialog(true)
                    }}
                  >
                    Abweichende USTID
                    {state.deviatingVatId && (
                      <span className="ml-2 text-muted-foreground font-normal">({state.deviatingVatId})</span>
                    )}
                  </Label>
                </div>
              </TabsContent>

              <TabsContent value="rechnung" className="mt-4 space-y-2">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label className="w-40 text-sm">Preismodell:</Label>
                    <NativeSelect
                      value={state.pricingMode}
                      onValueChange={(v) => setState((prev) => ({ ...prev, pricingMode: v as HarvestAcceptanceState['pricingMode'] }))}
                      options={[
                        { value: 'fixed_contract', label: 'Festpreis Vertrag' },
                        { value: 'spot_daily', label: 'Tagespreis' },
                        { value: 'exchange_fix_later', label: 'Börse / später festlegen' },
                      ]}
                      placeholder="Preismodell wählen"
                      className="flex-1 h-8"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="w-40 text-sm">Preisquelle:</Label>
                    <Input
                      value={state.priceSourceId || ''}
                      onChange={(e) => setState((prev) => ({ ...prev, priceSourceId: e.target.value || null }))}
                      className="flex-1 h-8"
                      placeholder="ID der Preisquelle"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="w-40 text-sm">Geschäftsmodell:</Label>
                    <NativeSelect
                      value={state.acceptanceMode}
                      onValueChange={(v) => setState((prev) => ({ ...prev, acceptanceMode: v }))}
                      options={[
                        { value: 'STORAGE_ONLY', label: 'Nur Lagerung (Fremdware)' },
                        { value: 'PURCHASE_AT_DELIVERY_PTBF', label: 'Ankauf bei Lieferung' },
                        { value: 'ADVANCE_ON_STORAGE', label: 'Einlagerung + Anzahlung' },
                      ]}
                      placeholder="Geschäftsmodell wählen"
                      className="flex-1 h-8"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="w-40 text-sm">Eigentumsverhältnis:</Label>
                    <NativeSelect
                      value={state.ownershipType}
                      onValueChange={(v) => setState((prev) => ({ ...prev, ownershipType: v }))}
                      options={[
                        { value: 'THIRD_PARTY_STOCK', label: 'Fremdware' },
                        { value: 'OWN_STOCK', label: 'Eigene Ware' },
                      ]}
                      placeholder="Eigentumsverhältnis wählen"
                      className="flex-1 h-8"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="w-40 text-sm">USt-Ereignis:</Label>
                    <NativeSelect
                      value={state.vatEvent}
                      onValueChange={(v) => setState((prev) => ({ ...prev, vatEvent: v }))}
                      options={[
                        { value: 'NO_INVOICE', label: 'Keine Rechnung' },
                        { value: 'PROVISIONAL_CREDIT_NOTE_CREATED', label: 'Vorläufige Gutschrift' },
                        { value: 'FINAL_CREDIT_NOTE_CREATED', label: 'Endgültige Gutschrift' },
                        { value: 'CORRECTION_ISSUED', label: 'Korrektur erstellt' },
                      ]}
                      placeholder="USt-Ereignis wählen"
                      className="flex-1 h-8"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="w-40 text-sm">Anzahlungsbetrag (EUR):</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      value={state.advancePaymentAmountEur ?? ''}
                      onChange={(e) => setState((prev) => ({
                        ...prev,
                        advancePaymentAmountEur: e.target.value ? parseFloat(e.target.value) : null,
                      }))}
                      className="flex-1 h-8"
                      placeholder="Für Einlagerung + Anzahlung"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="w-40 text-sm">Anzahlungsdatum:</Label>
                    <Input
                      type="date"
                      value={state.advancePaymentDate}
                      onChange={(e) => setState((prev) => ({ ...prev, advancePaymentDate: e.target.value }))}
                      className="flex-1 h-8"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="w-40 text-sm">vorl. Rechn.-Nr.:</Label>
                    <Input
                      value={state.provisionalInvoiceNumber}
                      onChange={(e) => setState((prev) => ({ ...prev, provisionalInvoiceNumber: e.target.value }))}
                      className="flex-1 h-8"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="w-40 text-sm">Rechnungs-Nr.:</Label>
                    <Input
                      value={state.invoiceNumber}
                      readOnly
                      className="flex-1 h-8"
                    />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="kontrakt" className="mt-4 space-y-2">
                <div className="flex items-center gap-2">
                  <Label className="w-32 text-sm">Kontrakt-Nr.:</Label>
                  <Input
                    value={state.contractId || ''}
                    onChange={(e) => setState((prev) => ({ ...prev, contractId: e.target.value || null }))}
                    className="flex-1 h-8"
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0"
                    onClick={() => setShowContractDialog(true)}
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </TabsContent>

              <TabsContent value="spediteur" className="mt-4 space-y-2">
                <div className="flex items-center gap-2">
                  <Label className="w-32 text-sm">Spediteur-Kto.:</Label>
                  <Input
                    value={state.forwarderId || ''}
                    onChange={(e) => setState((prev) => ({ ...prev, forwarderId: e.target.value || null }))}
                    className="flex-1 h-8"
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0"
                    onClick={() => setShowForwarderDialog(true)}
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
                {forwarderName && (
                  <div className="flex items-center gap-2">
                    <Label className="w-32 text-sm">Name:</Label>
                    <span className="text-sm">{forwarderName}</span>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="nawaro" className="mt-4 space-y-2">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label className="w-40 text-sm shrink-0">NAWARO-Nummer:</Label>
                      <Input
                        value={state.nawaroNr || ''}
                        onChange={(e) => setState((prev) => ({ ...prev, nawaroNr: e.target.value }))}
                        placeholder="z.B. NAW-2026-001"
                        className="flex-1 h-8" />
                    </div>
                    <div className="flex items-center gap-2">
                      <Label className="w-40 text-sm shrink-0">Verwendungszweck:</Label>
                      <select
                        value={state.nawaroZweck || ''}
                        onChange={(e) => setState((prev) => ({ ...prev, nawaroZweck: e.target.value }))}
                        className="flex-1 h-8 border rounded px-2">
                        <option value="">-- bitte wählen --</option>
                        <option value="biogas">Biogas</option>
                        <option value="bioethanol">Bioethanol</option>
                        <option value="biodiesel">Biodiesel</option>
                        <option value="holz">Holz/Pellets</option>
                        <option value="sonstige">Sonstige</option>
                      </select>
                    </div>
                    <div className="flex items-center gap-2">
                      <Label className="w-40 text-sm shrink-0">Biogasanlage:</Label>
                      <Input
                        value={state.biogasanlage || ''}
                        onChange={(e) => setState((prev) => ({ ...prev, biogasanlage: e.target.value }))}
                        placeholder="Name / Betreiber"
                        className="flex-1 h-8" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label className="w-40 text-sm shrink-0">EEG-Menge (t):</Label>
                      <Input
                        type="number" min={0} step={0.001}
                        value={state.eegMenge ?? ''}
                        onChange={(e) => setState((prev) => ({ ...prev, eegMenge: parseFloat(e.target.value) || 0 }))}
                        className="flex-1 h-8" />
                    </div>
                    <div className="flex items-center gap-2">
                      <Label className="w-40 text-sm shrink-0">Nachhaltigkeitsnachweis:</Label>
                      <Input
                        value={state.nachhaltigkeitsNachweis || ''}
                        onChange={(e) => setState((prev) => ({ ...prev, nachhaltigkeitsNachweis: e.target.value }))}
                        placeholder="REDcert / ISCC Zertifikat-Nr."
                        className="flex-1 h-8" />
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="zw-haendler" className="mt-4 space-y-2">
                <div className="flex items-center gap-2">
                  <Label className="w-32 text-sm">Zw-Händler-Kto.:</Label>
                  <Input
                    value={state.intermediateDealerId || ''}
                    onChange={(e) => setState((prev) => ({ ...prev, intermediateDealerId: e.target.value || null }))}
                    className="flex-1 h-8"
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0"
                    onClick={() => setShowIntermediateDealerDialog(true)}
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
                {intermediateDealerName && (
                  <div className="flex items-center gap-2">
                    <Label className="w-32 text-sm">Name:</Label>
                    <span className="text-sm">{intermediateDealerName}</span>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </Card>

          {/* ANLIEFERUNG / ABRECHNUNG Tabs */}
          <Card className="p-4">
            <Tabs value={deliveryTab} onValueChange={(v) => setDeliveryTab(v as typeof deliveryTab)}>
              <TabsList className="grid w-full grid-cols-2 h-auto">
                <TabsTrigger value="anlieferung" className="text-xs py-1">ANLIEFERUNG</TabsTrigger>
                <TabsTrigger value="abrechnung" className="text-xs py-1">ABRECHNUNG</TabsTrigger>
              </TabsList>

              <TabsContent value="anlieferung" className="mt-4 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <Label className="text-xs">Artikel-Nr.:</Label>
                    <div className="flex gap-1">
                      <Input
                        value={state.articleId || ''}
                        readOnly
                        className="flex-1 h-8"
                      />
                      <ShortcutHintButton shortcut="Strg+F2">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                          onClick={() => setShowArticleDialog(true)}
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </ShortcutHintButton>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Fahrzeug-Kennzeichen:</Label>
                    <Input
                      value={state.vehiclePlate}
                      onChange={(e) => setState((prev) => ({ ...prev, vehiclePlate: e.target.value }))}
                      className="h-8"
                      placeholder="AUR-TK-515"
                    />
                  </div>
                  <div className="space-y-1 col-span-2">
                    <Label className="text-xs">Bezeichnung:</Label>
                    <Input
                      value={state.articleName}
                      readOnly
                      className="h-8"
                      placeholder="Wird aus Artikel geladen"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Sorte:</Label>
                    <div className="flex gap-1">
                      <Input
                        value={state.varietyId || ''}
                        onChange={(e) => setState((prev) => ({ ...prev, varietyId: e.target.value || null }))}
                        className="flex-1 h-8"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                        onClick={() => setShowVarietyDialog(true)}
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Menge:</Label>
                    <Input
                      readOnly
                      className="h-8"
                      placeholder="Wird aus Wiegeschein geladen"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">MWSt. %:</Label>
                    <Input
                      value={state.vatRatePercent?.toFixed(2) || '7,00'}
                      readOnly
                      className="h-8"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">NUTS-2-Code:</Label>
                    <Input
                      value={state.originNuts2Code}
                      onChange={(e) => setState((prev) => ({ ...prev, originNuts2Code: e.target.value }))}
                      className="h-8"
                    />
                  </div>
                  <div className="space-y-1 flex items-center">
                    <Checkbox
                      id="nachhaltige-biomasse"
                      checked={state.isSustainableBiomass}
                      onCheckedChange={(checked) => setState((prev) => ({ ...prev, isSustainableBiomass: checked === true }))}
                    />
                    <Label htmlFor="nachhaltige-biomasse" className="text-xs cursor-pointer ml-2">
                      Nachhaltige Biomasse
                    </Label>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="abrechnung" className="mt-4">
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-16">Pos.</TableHead>
                        <TableHead className="w-48">Bezeichnung</TableHead>
                        <TableHead className="w-16 text-center">drucken</TableHead>
                        <TableHead className="w-16 text-center">berechnen</TableHead>
                        <TableHead className="w-24">Laborwert</TableHead>
                        <TableHead className="w-20">Einheit</TableHead>
                        <TableHead className="w-24">Menge</TableHead>
                        <TableHead className="w-24">Preis EUR</TableHead>
                        <TableHead className="w-24">Betrag EUR</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {state.positions.map((pos, idx) => (
                        <TableRow key={idx}>
                          <TableCell>{pos.positionNumber}</TableCell>
                          <TableCell>{pos.description}</TableCell>
                          <TableCell className="text-center">
                            <Checkbox
                              checked={pos.isPrintable}
                              onCheckedChange={(checked) => {
                                const newPositions = [...state.positions]
                                newPositions[idx].isPrintable = checked === true
                                setState((prev) => ({ ...prev, positions: newPositions }))
                              }}
                            />
                          </TableCell>
                          <TableCell className="text-center">
                            <Checkbox
                              checked={pos.isCalculable}
                              onCheckedChange={(checked) => {
                                const newPositions = [...state.positions]
                                newPositions[idx].isCalculable = checked === true
                                setState((prev) => ({ ...prev, positions: newPositions }))
                              }}
                            />
                          </TableCell>
                          <TableCell>
                            <Input
                              type="number"
                              step="0.01"
                              value={pos.labValuePct || ''}
                              onChange={(e) => {
                                const newPositions = [...state.positions]
                                newPositions[idx].labValuePct = e.target.value ? parseFloat(e.target.value) : null
                                setState((prev) => ({ ...prev, positions: newPositions }))
                              }}
                              className="h-8 w-full"
                            />
                          </TableCell>
                          <TableCell>{pos.unit}</TableCell>
                          <TableCell>
                            <Input
                              type="number"
                              step="0.001"
                              value={pos.quantityKg || ''}
                              onChange={(e) => {
                                const newPositions = [...state.positions]
                                newPositions[idx].quantityKg = e.target.value ? parseFloat(e.target.value) : null
                                setState((prev) => ({ ...prev, positions: newPositions }))
                              }}
                              className="h-8 w-full"
                            />
                          </TableCell>
                          <TableCell>
                            <Input
                              type="number"
                              step="0.01"
                              value={pos.pricePerUnitEur || ''}
                              onChange={(e) => {
                                const newPositions = [...state.positions]
                                newPositions[idx].pricePerUnitEur = e.target.value ? parseFloat(e.target.value) : null
                                setState((prev) => ({ ...prev, positions: newPositions }))
                              }}
                              className="h-8 w-full"
                            />
                          </TableCell>
                          <TableCell>
                            <Input
                              type="number"
                              step="0.01"
                              value={pos.amountEur?.toFixed(2) || ''}
                              readOnly
                              className="h-8 w-full"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </TabsContent>
            </Tabs>
          </Card>

          {/* Footer - Action Buttons */}
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex gap-2">
                <ShortcutHintButton shortcut="Strg+F5">
                  <Button variant="outline" onClick={() => void handleCalculate()} size="sm" className="gap-2">
                    <Calculator className="h-4 w-4" />
                    → Berechnung neu
                  </Button>
                </ShortcutHintButton>
                <Button variant="outline" size="sm" className="gap-2" onClick={() => void handleAbschlagrechnung()} title="Abschlagrechnung">
                  Abschlagrechnung
                </Button>
                <Button variant="outline" size="sm" className="gap-2" onClick={() => void handleEndabrechnung()} title="Endabrechnung">
                  Endabrechnung
                </Button>
                <Button variant="outline" size="sm" className="gap-2" onClick={() => setShowVarietyDialog(true)} title="Sorte bearbeiten">
                  Sorte bearbeiten
                </Button>
              </div>
              <div className="flex gap-2">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      id="release-draft"
                      name="release-status"
                      value="draft"
                      checked={state.releaseStatus === 'draft'}
                      onChange={(e) => setState((prev) => ({ ...prev, releaseStatus: e.target.value as HarvestAcceptanceState['releaseStatus'] }))}
                      className="h-4 w-4"
                    />
                    <Label htmlFor="release-draft" className="text-sm cursor-pointer">Entwurf</Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      id="release-provisional"
                      name="release-status"
                      value="provisional"
                      checked={state.releaseStatus === 'provisional'}
                      onChange={(e) => setState((prev) => ({ ...prev, releaseStatus: e.target.value as HarvestAcceptanceState['releaseStatus'] }))}
                      className="h-4 w-4"
                    />
                    <Label htmlFor="release-provisional" className="text-sm cursor-pointer">vorläufig</Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      id="release-final"
                      name="release-status"
                      value="final"
                      checked={state.releaseStatus === 'final'}
                      onChange={(e) => setState((prev) => ({ ...prev, releaseStatus: e.target.value as HarvestAcceptanceState['releaseStatus'] }))}
                      className="h-4 w-4"
                    />
                    <Label htmlFor="release-final" className="text-sm cursor-pointer">endgültig</Label>
                  </div>
                </div>
                <Button variant="outline" size="sm" className="gap-2">
                  <Printer className="h-4 w-4" />
                  Annahmeschein drucken
                </Button>
                <Button variant="outline" size="sm" className="gap-2" onClick={() => void handleRelease('provisional')} disabled={isSaving}>
                  Berechnung und Freigabe
                </Button>
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button 
                variant="outline" 
                size="sm" 
                className="gap-2 text-red-600"
                onClick={() => {
                  if (!state.id) {
                    push('Keine Ernte-Annahme zum Löschen vorhanden')
                    return
                  }
                  if (state.releaseStatus !== 'draft') {
                    push(`Ernte-Annahme kann nicht gelöscht werden. Status: ${state.releaseStatus}. Nur 'draft' kann gelöscht werden.`)
                    return
                  }
                  setShowDeleteDialog(true)
                }}
                disabled={!state.id || state.releaseStatus !== 'draft'}
              >
                <Trash2 className="h-4 w-4" />
                Annahmeschein löschen
              </Button>
              <Button variant="outline" size="sm" className="gap-2">
                <FileText className="h-4 w-4" />
                Aufteilungs-Buchung
              </Button>
              <Button variant="outline" size="sm" className="gap-2" onClick={() => setShowAttachmentDialog(true)}>
                <Folder className="h-4 w-4" />
                Unterlagen
              </Button>
              <Button variant="outline" size="sm" className="gap-2" onClick={() => setShowAttachmentDialog(true)}>
                <Folder className="h-4 w-4" />
                Dateien
              </Button>
              <Button variant="outline" size="sm" className="gap-2" onClick={() => setShowZusFelderDialog(true)} title="Zus. Felder">
                Zus. Felder
              </Button>
            </div>
          </Card>
        </div>

        {/* Rechte Spalte */}
        <div className="space-y-4">
          {/* Labor-Werte */}
          <Card className="p-4">
            <CardHeader>
              <CardTitle className="text-sm">Labor-Werte</CardTitle>
              <CardDescription className="text-xs mt-1">
                Analyse-Bon (Druck): CSV/Export importieren. Gerät ohne Export: Werte unten manuell eintragen. Raps: Analyse per Schriftform oder E-Mail mit PDF-Anhang (Ölgehalte) → PDF unter „Unterlagen“ anhängen.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col gap-2">
                <input type="file" accept=".csv,.txt" className="hidden" ref={importAnalyseInputRef} onChange={handleImportAnalyse} />
                <Button variant="outline" size="sm" className="w-full" onClick={() => importAnalyseInputRef?.current?.click()} title="CSV/Text mit Parametern (z. B. Parameter;Wert) von Geräten mit Datenexport oder Analyse-Bon">
                  <Download className="h-4 w-4 mr-2" />
                  Import CSV (Analyse-Bon / Gerät-Export)
                </Button>
                <Button variant="outline" size="sm" className="w-full" onClick={() => { setShowAttachmentDialog(true); push('Raps-Analyse-PDF (Ölgehalte) unter Unterlagen anhängen. Automatische Auswertung ist in Vorbereitung.'); }} title="Raps: Analyse-Ergebnisse als PDF (z. B. aus E-Mail) anhängen">
                  <FileText className="h-4 w-4 mr-2" />
                  PDF anhängen (Raps Ölgehalte)
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">Manuelle Eingabe (vom Gerät ablesen):</p>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-32">Bezeichnung</TableHead>
                    <TableHead className="w-24">Laborwert</TableHead>
                    <TableHead className="w-20">Einheit</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell>► Windabgang</TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        step="0.01"
                        value={state.labValues.windabgang || ''}
                        onChange={(e) => setState((prev) => ({
                          ...prev,
                          labValues: { ...prev.labValues, windabgang: e.target.value ? parseFloat(e.target.value) : null },
                        }))}
                        className="h-8 w-full"
                      />
                    </TableCell>
                    <TableCell>%</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Besatz</TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        step="0.01"
                        value={state.labValues.besatz || ''}
                        onChange={(e) => setState((prev) => ({
                          ...prev,
                          labValues: { ...prev.labValues, besatz: e.target.value ? parseFloat(e.target.value) : null },
                        }))}
                        className="h-8 w-full"
                      />
                    </TableCell>
                    <TableCell>%</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Feuchte/Tr.verlust</TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        step="0.01"
                        value={state.labValues.feuchte || ''}
                        onChange={(e) => setState((prev) => ({
                          ...prev,
                          labValues: { ...prev.labValues, feuchte: e.target.value ? parseFloat(e.target.value) : null },
                        }))}
                        className="h-8 w-full"
                      />
                    </TableCell>
                    <TableCell>%</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Hektolitergewicht</TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        step="0.01"
                        value={state.labValues.hektolitergewicht || ''}
                        onChange={(e) => setState((prev) => ({
                          ...prev,
                          labValues: { ...prev.labValues, hektolitergewicht: e.target.value ? parseFloat(e.target.value) : null },
                        }))}
                        className="h-8 w-full"
                      />
                    </TableCell>
                    <TableCell>kg/hl</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Lagerschwund</TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        step="0.01"
                        value={state.labValues.lagerschwund || ''}
                        onChange={(e) => setState((prev) => ({
                          ...prev,
                          labValues: { ...prev.labValues, lagerschwund: e.target.value ? parseFloat(e.target.value) : null },
                        }))}
                        className="h-8 w-full"
                      />
                    </TableCell>
                    <TableCell>%</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Lagergeld</TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        step="0.01"
                        value={state.labValues.lagergeld || ''}
                        onChange={(e) => setState((prev) => ({
                          ...prev,
                          labValues: { ...prev.labValues, lagergeld: e.target.value ? parseFloat(e.target.value) : null },
                        }))}
                        className="h-8 w-full"
                      />
                    </TableCell>
                    <TableCell>Mon.</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Wiegegebühren</TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        step="0.01"
                        value={state.labValues.wiegegebuehren || ''}
                        onChange={(e) => setState((prev) => ({
                          ...prev,
                          labValues: { ...prev.labValues, wiegegebuehren: e.target.value ? parseFloat(e.target.value) : null },
                        }))}
                        className="h-8 w-full"
                      />
                    </TableCell>
                    <TableCell>Euro/...</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Bemerkungen */}
          <Card className="p-4">
            <CardHeader>
              <CardTitle className="text-sm">Bemerkungen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={state.remarks}
                onChange={(e) => setState((prev) => ({ ...prev, remarks: e.target.value }))}
                className="min-h-32"
                placeholder="Bemerkungen..."
              />
              <div className="space-y-2">
                <Label className="text-xs">Druck Bemerkungen auf:</Label>
                <div className="flex items-center gap-2">
                  <Checkbox
                    id="druck-annahmeschein"
                    checked={state.printRemarksOnAcceptanceNote}
                    onCheckedChange={(checked) => setState((prev) => ({ ...prev, printRemarksOnAcceptanceNote: checked === true }))}
                  />
                  <Label htmlFor="druck-annahmeschein" className="text-sm cursor-pointer">
                    Annahmeschein
                  </Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox
                    id="druck-abrechnung"
                    checked={state.printRemarksOnSettlement}
                    onCheckedChange={(checked) => setState((prev) => ({ ...prev, printRemarksOnSettlement: checked === true }))}
                  />
                  <Label htmlFor="druck-abrechnung" className="text-sm cursor-pointer">
                    Abrechnung
                  </Label>
                </div>
              </div>
              <Button className="w-full">OK</Button>
            </CardContent>
          </Card>

          {/* Summen */}
          <Card className="p-4">
            <CardHeader>
              <CardTitle className="text-sm">Summen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1">
                <Label className="text-xs">Netto-Betrag:</Label>
                <Input
                  value={state.totalNetAmountEur?.toFixed(2) || ''}
                  readOnly
                  className="h-8"
                />
                <span className="text-xs text-muted-foreground">EUR</span>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">
                  {state.vatRatePercent?.toFixed(2) || '7,00'} % MWSt.:
                </Label>
                <Input
                  value={state.totalVatAmountEur?.toFixed(2) || ''}
                  readOnly
                  className="h-8"
                />
                <span className="text-xs text-muted-foreground">EUR</span>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Brutto-Betrag:</Label>
                <Input
                  value={state.totalGrossAmountEur?.toFixed(2) || ''}
                  readOnly
                  className="h-8"
                />
                <span className="text-xs text-muted-foreground">EUR</span>
              </div>
              <Button className="w-full">OK</Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Dialoge */}
      {(showForwarderDialog ||
        showIntermediateDealerDialog ||
        showAttachmentDialog ||
        showCustomerDialog ||
        showArticleDialog ||
        showWeighingTicketDialog ||
        showContractDialog ||
        showVarietyDialog) && (
        <LazyDialogBoundary>
          <>
            <CustomerSelectionDialog
              open={showForwarderDialog}
              onClose={() => setShowForwarderDialog(false)}
              onSelect={(customer) => {
                setState((prev) => ({ ...prev, forwarderId: customer.id }))
                setForwarderName(customer.name)
                setShowForwarderDialog(false)
              }}
              title="SPEDITEUR AUSW?HLEN"
            />
            <CustomerSelectionDialog
              open={showIntermediateDealerDialog}
              onClose={() => setShowIntermediateDealerDialog(false)}
              onSelect={(customer) => {
                setState((prev) => ({ ...prev, intermediateDealerId: customer.id }))
                setIntermediateDealerName(customer.name)
                setShowIntermediateDealerDialog(false)
              }}
              title="ZWISCHENH?NDLER AUSW?HLEN"
            />
            <DmsAnhangDialog
              open={showAttachmentDialog}
              onClose={() => setShowAttachmentDialog(false)}
              businessObjectType="harvest_reception"
              businessObjectId={state.id}
              title="UNTERLAGEN / DATEIEN ??? ERNTE-ANNAHME"
            />
            <CustomerSelectionDialog
              open={showCustomerDialog}
              onClose={() => setShowCustomerDialog(false)}
              onSelect={handleCustomerSelect}
            />
            <ArtikelSuchDialog
              open={showArticleDialog}
              onClose={() => setShowArticleDialog(false)}
              onSelect={handleArticleSelect}
              customerId={state.customer?.id}
            />
            <WeighingTicketSelectionDialog
              open={showWeighingTicketDialog}
              onClose={() => setShowWeighingTicketDialog(false)}
              onSelect={handleWeighingTicketSelect}
              customerId={state.customer?.id}
            />
            <ContractSelectionDialog
              open={showContractDialog}
              onClose={() => setShowContractDialog(false)}
              onSelect={handleContractSelect}
              customerId={state.customer?.id}
            />
            <VarietySelectionDialog
              open={showVarietyDialog}
              onClose={() => setShowVarietyDialog(false)}
              onSelect={handleVarietySelect}
              articleId={state.articleId}
            />
          </>
        </LazyDialogBoundary>
      )}

      <Dialog open={showZusFelderDialog} onOpenChange={setShowZusFelderDialog}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Zusätzliche Felder</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Bemerkungen</Label>
              <Textarea
                value={state.remarks}
                onChange={(e) => setState((prev) => ({ ...prev, remarks: e.target.value }))}
                placeholder="Optionale Bemerkungen zur Ernte-Annahme"
                rows={4}
                className="mt-1"
              />
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="print-remarks-note"
                checked={state.printRemarksOnAcceptanceNote}
                onCheckedChange={(v) => setState((prev) => ({ ...prev, printRemarksOnAcceptanceNote: !!v }))}
              />
              <Label htmlFor="print-remarks-note" className="text-sm font-normal cursor-pointer">Auf Annahmeschein drucken</Label>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="print-remarks-settlement"
                checked={state.printRemarksOnSettlement}
                onCheckedChange={(v) => setState((prev) => ({ ...prev, printRemarksOnSettlement: !!v }))}
              />
              <Label htmlFor="print-remarks-settlement" className="text-sm font-normal cursor-pointer">Auf Abrechnung drucken</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowZusFelderDialog(false)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showUstIdDialog} onOpenChange={setShowUstIdDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Abweichende USt-ID</DialogTitle>
            <DialogDescription>USt-Identifikationsnummer des Empfängers (z. B. bei innergemeinschaftlichem Erwerb).</DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="ustid-input" className="text-sm">USt-ID</Label>
            <Input
              id="ustid-input"
              value={ustIdDialogValue}
              onChange={(e) => setUstIdDialogValue(e.target.value)}
              placeholder="z. B. DE123456789"
              className="mt-2"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowUstIdDialog(false)}>
              Abbrechen
            </Button>
            <Button
              onClick={() => {
                const trimmed = ustIdDialogValue.trim()
                setState((prev) => ({ ...prev, deviatingVatId: trimmed || null }))
                if (trimmed) push(`Abweichende USt-ID hinterlegt: ${trimmed}`)
                setShowUstIdDialog(false)
              }}
            >
              Übernehmen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Ernte-Annahme löschen</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <p className="text-sm">
              Möchten Sie die Ernte-Annahme <strong>{state.acceptanceNumber}</strong> wirklich löschen?
            </p>
            <p className="text-xs text-muted-foreground">
              Diese Aktion kann nicht rückgängig gemacht werden. Nur Ernte-Annahmen im Status 'draft' können gelöscht werden.
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Abbrechen
            </Button>
            <Button variant="destructive" onClick={() => void handleDelete()} disabled={isSaving}>
              Löschen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

