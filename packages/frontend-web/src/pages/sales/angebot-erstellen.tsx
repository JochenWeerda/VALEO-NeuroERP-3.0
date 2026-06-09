/**
 * Angebot-Erfassung (Verkauf)
 * Im Stil der Lieferschein-Erfassung — einheitliches ERP-Look & Feel
 */

import { useState, useEffect, useMemo, useCallback } from 'react'
import { useNavigate, useParams, useSearchParams } from '@/app/routing/typed-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Card } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { CustomerSelectionDialog, type Customer } from '@/components/sales/CustomerSelectionDialog'
import { ArtikelSuchDialog, type Article } from '@/components/sales/ArtikelSuchDialog'
import { LieferscheinDruckDialog, type PrintOptions } from '@/components/sales/LieferscheinDruckDialog'
import { DmsAnhangDialog } from '@/components/dms/DmsAnhangDialog'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'
import { useAngebote, type Angebot, type SalesOffer } from '@/lib/api/sales'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/components/ui/toast-provider'
import {
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  MoreHorizontal,
  Check,
  Printer,
  Save,
  Trash2,
  X,
  Search,
  FileText,
} from 'lucide-react'

// ── Types ─────────────────────────────────────────────────────────────────────

type AngebotPosition = {
  posNr: number
  artikelNr: string
  artikelId: string | null
  bezeichnung: string
  bezeichnung2: string
  menge: number
  einheit: string
  listenpreis: number
  rabatt: number
  nettoPreis: number
  nettoBetrag: number
  ekPreis: number
  mwstProzent: number
  gewicht: number
  gesamtGewicht: number
}

type CurrentPositionDetails = {
  posNr: number
  artikelNr: string
  artikelId: string | null
  bezeichnung: string
  bezeichnung2: string
  menge: number
  einheit: string
  listenpreis: number
  rabatt: number
  einhPreis: number
  betrag: number
  ekPreis: number
  mwstProzent: number
  gewicht: number
}

// ── Helper ────────────────────────────────────────────────────────────────────

import { fetchDocumentNumber } from '@/hooks/useDocumentNumber'
import { CustomerSalesEligibilityBanner } from '@/components/sales/CustomerSalesEligibilityBanner'
import { useCustomerSalesEligibility } from '@/hooks/useCustomerSalesEligibility'
import { buildSalesHandoverPath, parseSalesHandover } from '@/lib/workflow/sales-handover'

type OfferAssistantRole = 'vertrieb' | 'innendienst' | 'auftragsabwicklung' | 'finance' | 'leitung'

const offerAssistantRoles = [
  {
    id: 'vertrieb',
    label: 'Vertrieb',
    description: 'Prueft Kunde, Angebot, Preis und naechstes Nachfassen bis zur Entscheidung.',
  },
  {
    id: 'innendienst',
    label: 'Innendienst',
    description: 'Haelt Stammdaten, Positionen, Druck und Anlagen sauber, damit nichts im Folgeauftrag fehlt.',
  },
  {
    id: 'auftragsabwicklung',
    label: 'Auftragsabwicklung',
    description: 'Achtet darauf, ob das Angebot vollstaendig und gespeichert ist, bevor daraus ein Auftrag wird.',
  },
  {
    id: 'finance',
    label: 'Finance',
    description: 'Prueft Wert, Rabatt, Steuer und spaetere Faktura-Folgen.',
  },
  {
    id: 'leitung',
    label: 'Leitung',
    description: 'Sieht Abschlussreife, offene Stopper und den naechsten Verantwortungswechsel.',
  },
] satisfies Array<{ id: OfferAssistantRole; label: string; description: string }>

let _angebotNrCache: string | null = null
function generateAngebotNr(): string {
  if (!_angebotNrCache) {
    const year = new Date().getFullYear()
    _angebotNrCache = `A${year}-DRAFT`
    fetchDocumentNumber('angebot').then(nr => { _angebotNrCache = nr }).catch(() => {})
  }
  return _angebotNrCache
}

function emptyPosition(posNr: number): CurrentPositionDetails {
  return {
    posNr,
    artikelNr: '',
    artikelId: null,
    bezeichnung: '',
    bezeichnung2: '',
    menge: 0,
    einheit: '',
    listenpreis: 0,
    rabatt: 0,
    einhPreis: 0,
    betrag: 0,
    ekPreis: 0,
    mwstProzent: 19,
    gewicht: 0,
  }
}

function getErrorMessage(error: unknown): string {
  if (error && typeof error === 'object') {
    const response = 'response' in error ? (error as { response?: { data?: { detail?: string } } }).response : undefined
    if (response?.data?.detail) {
      return response.data.detail
    }
    if ('message' in error && typeof (error as { message?: unknown }).message === 'string') {
      return (error as { message: string }).message
    }
  }
  return 'Unbekannter Fehler'
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function AngebotErstellenPage(): JSX.Element {
  const { push } = useToast()
  const navigate = useNavigate()
  const { id: routeOfferId } = useParams<{ id?: string }>()
  const [searchParams] = useSearchParams()
  const handover = useMemo(() => parseSalesHandover(searchParams), [searchParams])
  const [isDirty, setIsDirty] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [isLoadingOffer, setIsLoadingOffer] = useState(false)
  const [roleFocus, setRoleFocus] = useState<OfferAssistantRole>('vertrieb')

  // ── Angebot-Kopf ──────────────────────────────────────────────────────────
  const [angebotNr, setAngebotNr] = useState(() => generateAngebotNr())
  const [datum, setDatum] = useState(() => new Date().toISOString().split('T')[0])
  const [gueltigBis, setGueltigBis] = useState('')
  const [status, setStatus] = useState('Offen')
  const [isPauschale, setIsPauschale] = useState(false)
  const [kontakt, setKontakt] = useState('')
  const [customer, setCustomer] = useState<Customer | null>(null)
  const { data: salesEligibility } = useCustomerSalesEligibility(customer?.id)

  useEffect(() => {
    const customerNumber = handover.customerNumber
    const customerId = handover.customerId ?? customerNumber
    if (!customerId || customer) return
    setCustomer({
      id: customerId,
      customerNumber: customerNumber ?? customerId,
      name: handover.customerName ?? customerNumber ?? customerId,
      debitorAccount: customerNumber ?? customerId,
    })
  }, [customer, handover.customerId, handover.customerName, handover.customerNumber])

  // ── Dialoge ───────────────────────────────────────────────────────────────
  const [showAngebotAuswahl, setShowAngebotAuswahl] = useState(false) // öffnet nur per Button
  const [showCustomerDialog, setShowCustomerDialog] = useState(false)
  const [showArticleDialog, setShowArticleDialog] = useState(false)
  const [showPrintDialog, setShowPrintDialog] = useState(false)
  const [showAttachmentDialog, setShowAttachmentDialog] = useState(false)
  const [angebotId, setAngebotId] = useState<string | null>(null)
  const [sucheText, setSucheText] = useState('')

  useEffect(() => {
    if (!routeOfferId || routeOfferId === 'neu') return

    let cancelled = false
    setIsLoadingOffer(true)
    apiClient.get<SalesOffer>(`/api/v1/sales/offers/${encodeURIComponent(routeOfferId)}`)
      .then((offer) => {
        if (cancelled) return
        setAngebotId(offer.id)
        setAngebotNr(offer.offer_number)
        setDatum((offer.created_at || new Date().toISOString()).slice(0, 10))
        setGueltigBis(offer.valid_until?.slice(0, 10) || '')
        setStatus(offer.status)
        setIsPauschale(offer.is_pauschale)
        setKontakt(offer.contact_person || '')
        setCustomer(offer.customer_id ? {
          id: offer.customer_id,
          customerNumber: offer.customer_id,
          name: offer.customer_name || offer.customer_id,
          debitorAccount: offer.customer_id,
        } : null)
        setPositionen(offer.items.map((item) => ({
          posNr: item.line_number,
          artikelNr: item.article_number,
          artikelId: null,
          bezeichnung: item.description || '',
          bezeichnung2: '',
          menge: item.quantity,
          einheit: item.unit,
          listenpreis: item.unit_price,
          rabatt: item.discount_percent,
          nettoPreis: item.quantity > 0 ? item.line_total / item.quantity : item.unit_price,
          nettoBetrag: item.line_total,
          ekPreis: item.ek_price || 0,
          mwstProzent: 19,
          gewicht: 0,
          gesamtGewicht: 0,
        })))
        setIsDirty(false)
      })
      .catch((error: unknown) => {
        if (!cancelled) push(`Angebot konnte nicht geladen werden: ${getErrorMessage(error)}`)
      })
      .finally(() => {
        if (!cancelled) setIsLoadingOffer(false)
      })

    return () => {
      cancelled = true
    }
  }, [push, routeOfferId])

  // ── Positionen ────────────────────────────────────────────────────────────
  const [positionen, setPositionen] = useState<AngebotPosition[]>([])
  const [aktivePositionIndex, setAktivePositionIndex] = useState<number | null>(null)

  // ── Aktuelle Eingabe-Position ─────────────────────────────────────────────
  const [currentPosition, setCurrentPosition] = useState<CurrentPositionDetails>(() => emptyPosition(10))

  // ── Angebote-Liste (Auswahl-Dialog) ──────────────────────────────────────
  const { data: angebote = [], isLoading } = useAngebote()
  const filteredAngebote = angebote.filter(
    (a) =>
      a.nummer.toLowerCase().includes(sucheText.toLowerCase()) ||
      a.kunde.toLowerCase().includes(sucheText.toLowerCase()),
  )

  // ── Preis automatisch berechnen ───────────────────────────────────────────
  useEffect(() => {
    const einhPreis = currentPosition.listenpreis * (1 - currentPosition.rabatt / 100)
    const betrag = einhPreis * currentPosition.menge
    setCurrentPosition((prev) => ({ ...prev, einhPreis, betrag }))
  }, [currentPosition.listenpreis, currentPosition.rabatt, currentPosition.menge])

  // ── Summen ────────────────────────────────────────────────────────────────
  const summen = useMemo(() => {
    const netto = positionen.reduce((s, p) => s + p.nettoBetrag, 0)
    const mwst = positionen.reduce((s, p) => s + (p.nettoBetrag * p.mwstProzent) / 100, 0)
    const brutto = netto + mwst
    const gewicht = positionen.reduce((s, p) => s + (p.gesamtGewicht || 0), 0)
    return { netto, mwst, brutto, gewicht }
  }, [positionen])
  const customerAllowed = !customer || !salesEligibility || salesEligibility.allowed_order
  const canConvertToOrder = Boolean(angebotId && customer && positionen.length > 0 && customerAllowed && !isDirty)
  const offerBlockers = [
    !customer ? 'Kunde auswaehlen' : null,
    positionen.length === 0 ? 'mindestens eine Position erfassen' : null,
    !angebotId ? 'Angebot speichern' : null,
    isDirty ? 'Aenderungen speichern' : null,
    !customerAllowed ? 'Kundenfreigabe klaeren' : null,
  ].filter((item): item is string => Boolean(item))
  const offerNextAction = !customer
    ? 'Kunde auswaehlen, damit Preis, Kontakt und Auftragsfreigabe geprueft werden koennen.'
    : positionen.length === 0
      ? 'Position erfassen und Menge/Preis pruefen.'
      : !angebotId || isDirty
        ? 'Angebot speichern, bevor Druck, DMS-Anhang oder Auftragserzeugung genutzt werden.'
        : !customerAllowed
          ? 'Kundenfreigabe im Stammdatensatz klaeren, bevor daraus ein Auftrag wird.'
          : 'Angebot ist uebergabereif: Druck/Nachweis erstellen oder in Auftrag uebernehmen.'

  // ── Handler ───────────────────────────────────────────────────────────────

  function handleAngebotAuswaehlen(angebot: Angebot) {
    setAngebotId(angebot.id)
    setAngebotNr(angebot.nummer)
    setDatum(angebot.datum)
    setStatus(angebot.status)
    setShowAngebotAuswahl(false)
    setIsDirty(false)
  }

  function handleCustomerSelect(c: Customer) {
    setCustomer(c)
    if (c.representative) setKontakt(c.representative)
    setIsDirty(true)
  }

  function handleArticleSelect(article: Article) {
    const pricing = article as Article & {
      sales_price?: number
      salesPrice?: number
      purchase_price?: number
      purchasePrice?: number
      weight?: number
      gewicht?: number
      mehrwertsteuer_prozent?: number
      mwstProzent?: number
    }
    const listenpreis = pricing.sales_price || pricing.salesPrice || 0
    const ekPreis = pricing.purchase_price || pricing.purchasePrice || 0
    const gewicht = pricing.weight || pricing.gewicht || 0
    const mwstProzent = Number(pricing.mehrwertsteuer_prozent || pricing.mwstProzent || 19)
    setCurrentPosition((prev) => ({
      ...prev,
      artikelNr: article.article_number || article.articleNumber || '',
      artikelId: article.id || null,
      bezeichnung: article.name || article.description || '',
      bezeichnung2: article.description2 || '',
      einheit: article.unit || 'Stk',
      listenpreis,
      ekPreis,
      mwstProzent,
      gewicht,
    }))
  }

  function renumberPositionen(items: AngebotPosition[]): AngebotPosition[] {
    return items.map((p, i) => ({ ...p, posNr: i + 1 }))
  }

  function handlePositionOK() {
    if (!currentPosition.artikelNr || !currentPosition.menge) return

    const nettoPreis = currentPosition.listenpreis * (1 - currentPosition.rabatt / 100)
    const nettoBetrag = nettoPreis * currentPosition.menge
    const gesamtGewicht = currentPosition.gewicht * currentPosition.menge

    const newPos: AngebotPosition = {
      posNr: currentPosition.posNr,
      artikelNr: currentPosition.artikelNr,
      artikelId: currentPosition.artikelId,
      bezeichnung: currentPosition.bezeichnung,
      bezeichnung2: currentPosition.bezeichnung2,
      menge: currentPosition.menge,
      einheit: currentPosition.einheit,
      listenpreis: currentPosition.listenpreis,
      rabatt: currentPosition.rabatt,
      nettoPreis,
      nettoBetrag,
      ekPreis: currentPosition.ekPreis,
      mwstProzent: currentPosition.mwstProzent,
      gewicht: currentPosition.gewicht,
      gesamtGewicht,
    }

    setPositionen((prev) => {
      let next: AngebotPosition[]
      if (aktivePositionIndex !== null && aktivePositionIndex >= 0 && aktivePositionIndex < prev.length) {
        next = [...prev.slice(0, aktivePositionIndex), newPos, ...prev.slice(aktivePositionIndex + 1)]
      } else {
        next = [...prev, newPos]
      }
      return renumberPositionen(next)
    })
    setAktivePositionIndex(null)
    const nextPosNr = positionen.length + (aktivePositionIndex !== null ? 0 : 1) + 1
    setCurrentPosition(emptyPosition(nextPosNr))
    setIsDirty(true)
  }

  function handlePositionDelete(idx: number) {
    setPositionen((prev) => renumberPositionen(prev.filter((_, i) => i !== idx)))
    setAktivePositionIndex(null)
    setCurrentPosition(emptyPosition(10))
    setIsDirty(true)
  }

  function handleMovePositionUp(idx: number) {
    if (idx <= 0) return
    setPositionen((prev) => {
      const next = [...prev]
      ;[next[idx - 1], next[idx]] = [next[idx], next[idx - 1]]
      return renumberPositionen(next)
    })
    setAktivePositionIndex((prev) => (prev === idx ? idx - 1 : prev === idx - 1 ? idx : prev))
    setIsDirty(true)
  }

  function handleMovePositionDown(idx: number) {
    if (idx >= positionen.length - 1) return
    setPositionen((prev) => {
      const next = [...prev]
      ;[next[idx], next[idx + 1]] = [next[idx + 1], next[idx]]
      return renumberPositionen(next)
    })
    setAktivePositionIndex((prev) => (prev === idx ? idx + 1 : prev === idx + 1 ? idx : prev))
    setIsDirty(true)
  }

  // ── Build API payload (header + items) ────────────────────────────────────
  function buildOfferPayload() {
    const items = positionen.map((p) => ({
      article_number: p.artikelNr,
      description: [p.bezeichnung, p.bezeichnung2].filter(Boolean).join(' ') || undefined,
      quantity: p.menge,
      unit: p.einheit || 'Stk',
      unit_price: p.listenpreis,
      discount_percent: p.rabatt,
      ek_price: p.ekPreis ?? undefined,
    }))
    const total_amount = positionen.reduce((s, p) => s + p.nettoBetrag, 0)
    return {
      offer_number: angebotNr,
      customer_id: customer?.id ?? null,
      customer_name: customer?.name ?? null,
      subject: `Angebot ${angebotNr}`,
      description: '',
      total_amount,
      currency: 'EUR',
      status: status.toLowerCase(),
      contact_person: kontakt || null,
      valid_until: gueltigBis || null,
      is_pauschale: isPauschale,
      items,
    }
  }

  const handleSave = useCallback(async () => {
    if (customer && salesEligibility && !salesEligibility.allowed_order) {
      push(
        salesEligibility.reasons.join(' ') ||
          'Kunde ist für Angebote/Aufträge nicht freigegeben (Stammdaten).',
      )
      return
    }
    const payload = buildOfferPayload()
    setIsSaving(true)
    try {
      const id = angebotId
      if (id) {
        const updated = await apiClient.patch<{
          id: string
          offer_number: string
          status?: string
        }>(`/api/v1/sales/offers/${id}`, payload)
        setAngebotId(updated.id)
        if (updated.offer_number) setAngebotNr(updated.offer_number)
        push('Angebot gespeichert')
      } else {
        const created = await apiClient.post<{ id: string; offer_number: string }>(
          '/api/v1/sales/offers/',
          payload,
        )
        setAngebotId(created.id)
        if (created.offer_number) setAngebotNr(created.offer_number)
        push('Angebot erstellt')
      }
      setIsDirty(false)
    } catch (err: unknown) {
      push(`Fehler beim Speichern: ${getErrorMessage(err)}`)
    } finally {
      setIsSaving(false)
    }
  }, [
    angebotId,
    angebotNr,
    customer,
    gueltigBis,
    isPauschale,
    kontakt,
    positionen,
    status,
    push,
    salesEligibility,
    customer,
  ])

  const handleConvertToOrder = useCallback(async () => {
    const id = angebotId
    if (!id) {
      push('Bitte zuerst Angebot speichern')
      return
    }
    if (customer && salesEligibility && !salesEligibility.allowed_order) {
      push(
        salesEligibility.reasons.join(' ') ||
          'Übernahme in Auftrag nicht möglich — Kunde gesperrt (Stammdaten).',
      )
      return
    }
    try {
      const converted = await apiClient.post<{
        created_order_id: string
        created_order_number: string
      }>(`/api/v1/sales/offers/${id}/convert-to-order`)
      push('Angebot in Auftrag übernommen')
      navigate(buildSalesHandoverPath(`/sales/order-editor/${converted.created_order_id}`, {
        customerId: customer?.id,
        customerNumber: customer?.customerNumber || customer?.debitorAccount,
        customerName: customer?.name,
        entryMode: handover.entryMode ?? 'offer-conversion',
        sourceOfferId: id,
        sourceOrderId: converted.created_order_id,
      }))
    } catch (err: unknown) {
      push(`Fehler: ${getErrorMessage(err)}`)
    }
  }, [angebotId, push, navigate, customer, salesEligibility, handover.entryMode])

  const handleDelete = useCallback(async () => {
    const id = angebotId
    if (!id) {
      push('Kein gespeichertes Angebot zum Löschen')
      return
    }
    try {
      await apiClient.delete(`/api/v1/sales/offers/${id}`)
      push('Angebot gelöscht')
      navigate('/sales/angebote')
    } catch (err: unknown) {
      push(`Fehler beim Löschen: ${getErrorMessage(err)}`)
    }
  }, [angebotId, push, navigate])

  const handleBeenden = useCallback(() => {
    if (isDirty) {
      if (window.confirm('Es gibt ungespeicherte Änderungen. Wirklich verlassen?')) {
        navigate('/sales/angebote')
      }
    } else {
      navigate('/sales/angebote')
    }
  }, [isDirty, navigate])

  function handlePositionRowClick(pos: AngebotPosition, idx: number) {
    setAktivePositionIndex(idx)
    setCurrentPosition({
      posNr: pos.posNr,
      artikelNr: pos.artikelNr,
      artikelId: pos.artikelId,
      bezeichnung: pos.bezeichnung,
      bezeichnung2: pos.bezeichnung2,
      menge: pos.menge,
      einheit: pos.einheit,
      listenpreis: pos.listenpreis,
      rabatt: pos.rabatt,
      einhPreis: pos.nettoPreis,
      betrag: pos.nettoBetrag,
      ekPreis: pos.ekPreis,
      mwstProzent: pos.mwstProzent,
      gewicht: pos.gewicht,
    })
  }

  // ── Druck ─────────────────────────────────────────────────────────────────

  const handlePrint = async (options: PrintOptions): Promise<void> => {
    try {
      let id = angebotId
      if (!id) {
        // Angebot speichern, um ID zu erhalten
        const saved = await apiClient.post<{ id: string }>('/api/v1/sales/quotations', {
          nummer: angebotNr,
          datum,
          gueltig_bis: gueltigBis || null,
          status,
          ist_pauschal: isPauschale,
          customer_id: customer?.id || null,
          kontakt,
          positionen: positionen.map((p) => ({
            pos_nr: p.posNr,
            artikel_id: p.artikelId,
            artikel_nr: p.artikelNr,
            bezeichnung: p.bezeichnung,
            menge: p.menge,
            einheit: p.einheit,
            listenpreis: p.listenpreis,
            rabatt: p.rabatt,
            netto_preis: p.nettoPreis,
            netto_betrag: p.nettoBetrag,
            mwst_prozent: p.mwstProzent,
          })),
        })
        id = saved.id
        setAngebotId(id)
      }

      const params = new URLSearchParams()
      params.append('template', options.formatvorlage)
      params.append('copies', String(options.anzahlDrucke))
      await apiClient.post(`/api/v1/sales/quotations/${id}/print?${params.toString()}`)
      await apiClient.post(`/api/v1/sales/quotations/${id}/post`)

      push('Angebot erfolgreich gedruckt und gebucht')
      setShowPrintDialog(false)

      // Formular zurücksetzen
      setAngebotNr(generateAngebotNr())
      setDatum(new Date().toISOString().split('T')[0])
      setGueltigBis('')
      setStatus('Offen')
      setIsPauschale(false)
      setKontakt('')
      setCustomer(null)
      setPositionen([])
      setAktivePositionIndex(null)
      setCurrentPosition(emptyPosition(10))
      setAngebotId(null)
    } catch (error: unknown) {
      push(`Fehler beim Drucken: ${getErrorMessage(error)}`)
    }
  }

  // ── JSX ──────────────────────────────────────────────────────────────────

  return (
    <div className="h-screen flex flex-col bg-gray-50" data-offer-id={angebotId ?? undefined} aria-busy={isLoadingOffer}>
      {/* Header */}
      <div className="bg-amber-500 text-white px-4 py-2">
        <h1 className="text-lg font-bold">ANGEBOT-ERFASSUNG</h1>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {customer ? (
          <CustomerSalesEligibilityBanner crmCustomerId={customer.id} modus="auftrag" />
        ) : null}

        {/* ── Kopf-Bereich ─────────────────────────────────────────────── */}
        <div className="mb-4 space-y-4">
          <RoleFocusBar
            roles={offerAssistantRoles}
            value={roleFocus}
            onChange={setRoleFocus}
            visibleCount={positionen.length}
            totalCount={positionen.length}
            title="Wer fuehrt das Angebot weiter?"
          />

          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
            <ManagementDecisionPanel
              decision={{
                allowed: canConvertToOrder,
                allowedLabel: 'Uebergabe bereit',
                blockedLabel: 'Noch nicht uebergabereif',
                summary: canConvertToOrder
                  ? `Das Angebot ${angebotNr} ist gespeichert, hat einen freigegebenen Kunden und ${positionen.length} Position(en). Es kann in den Auftrag uebernommen werden.`
                  : `Vor der Auftragsuebergabe fehlen noch: ${offerBlockers.join(', ')}.`,
                blockerCount: offerBlockers.length,
                nextFocus: canConvertToOrder ? 'Auftrag erzeugen oder Nachweis drucken' : offerBlockers[0] ?? 'Angebot vervollstaendigen',
                template: { label: 'Angebots- und Auftragsuebergabe', href: '/docs/sales/angebot-auftrag-uebergabe.md' },
              }}
            />
            <div className="space-y-4">
              <NextActionPanel action={offerNextAction} tone={canConvertToOrder ? 'emerald' : 'amber'} />
              <EvidenceTemplateLink link={{ label: 'Angebotsnachweis im DMS ablegen', href: '/docs/sales/angebotsnachweis.md' }} />
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <OperationalTaskPlan
              title="Uebergabeplan Angebot zu Auftrag"
              items={[
                { label: 'Kunde auswaehlen', done: Boolean(customer), hint: customer ? `${customer.name} ist ausgewaehlt.` : 'Ohne Kunde ist keine saubere Auftragsuebergabe moeglich.' },
                { label: 'Positionen erfassen', done: positionen.length > 0, hint: positionen.length > 0 ? `${positionen.length} Position(en), ${summen.brutto.toFixed(2)} EUR brutto.` : 'Artikel, Menge, Preis und Rabatt erfassen.' },
                { label: 'Angebot speichern', done: Boolean(angebotId) && !isDirty, hint: angebotId && !isDirty ? 'Gespeicherter Stand ist Grundlage fuer Druck und Auftrag.' : 'Vor Druck, DMS und Auftragserzeugung speichern.' },
                { label: 'Kundenfreigabe pruefen', done: customerAllowed, hint: customerAllowed ? 'Keine Sperre aus den Stammdaten sichtbar.' : salesEligibility?.reasons.join(' ') ?? 'Kundenfreigabe offen.' },
                { label: 'Nachweis oder Auftrag erzeugen', done: canConvertToOrder, hint: canConvertToOrder ? 'Druck, DMS-Anhang oder Auftragserzeugung sind jetzt fachlich sinnvoll.' : 'Erst die offenen Punkte abschliessen.' },
              ]}
            />
            <CrudCapabilityChecklist
              capabilities={[
                { key: 'create', label: 'Angebot anlegen', available: true, hint: 'Neues Angebot wird ueber die Erfassungsmaske erstellt.' },
                { key: 'read', label: 'Bestehendes Angebot laden', available: true, hint: 'Suchdialog oeffnet vorhandene Angebote.' },
                { key: 'update', label: 'Aenderungen speichern', available: true, hint: 'Kopf, Kunde und Positionen koennen gespeichert werden.' },
                { key: 'delete', label: 'Angebot loeschen', available: Boolean(angebotId), hint: 'Loeschen ist erst nach Speicherung technisch moeglich.' },
                { key: 'evidence', label: 'DMS-Anhang', available: Boolean(angebotId), hint: 'Anlagen gehoeren an ein gespeichertes Angebot.' },
                { key: 'approve', label: 'In Auftrag uebernehmen', available: canConvertToOrder, hint: 'Uebergabe erst nach Kunde, Position, Speicherung und Kundenfreigabe.' },
              ]}
            />
          </div>
        </div>

        <Card className="mb-4 p-4">
          <div className="grid grid-cols-3 gap-6">

            {/* Linke Spalte */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm whitespace-nowrap shrink-0">Angebot-Nr.:</Label>
                <Input
                  value={angebotNr}
                  onChange={(e) => {
                    setAngebotNr(e.target.value)
                    setIsDirty(true)
                  }}
                  className="flex-1 h-8 text-sm"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  title="Bestehendes Angebot suchen"
                  onClick={() => setShowAngebotAuswahl(true)}
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Datum:</Label>
                <Input
                  type="date"
                  value={datum}
                  onChange={(e) => {
                    setDatum(e.target.value)
                    setIsDirty(true)
                  }}
                  className="flex-1 h-8 text-sm"
                />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm whitespace-nowrap shrink-0">Gültig bis:</Label>
                <Input
                  type="date"
                  value={gueltigBis}
                  onChange={(e) => {
                    setGueltigBis(e.target.value)
                    setIsDirty(true)
                  }}
                  className="flex-1 h-8 text-sm"
                />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Status:</Label>
                <Input value={status} readOnly className="flex-1 h-8 text-sm bg-muted" />
              </div>
              <div className="flex items-center gap-2 pt-1">
                <Checkbox
                  id="pauschale"
                  checked={isPauschale}
                  onCheckedChange={(c) => {
                    setIsPauschale(c === true)
                    setIsDirty(true)
                  }}
                />
                <Label htmlFor="pauschale" className="text-sm cursor-pointer">
                  Pauschal-Angebot
                </Label>
              </div>
            </div>

            {/* Mittlere Spalte — leer / für spätere Felder */}
            <div />

            {/* Rechte Spalte — Kunde */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Kunde:</Label>
                <Input
                  value={customer?.name || ''}
                  readOnly
                  placeholder="Kein Kunde gewählt"
                  className="flex-1 h-8 text-sm"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  title="Kunden suchen"
                  onClick={() => setShowCustomerDialog(true)}
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
              {customer && (
                <div className="text-xs text-muted-foreground space-y-0.5 pl-[7.5rem]">
                  <div>Kd-Nr.: {customer.customerNumber}</div>
                  {(customer.postalCode || customer.city) && (
                    <div>{[customer.postalCode, customer.city].filter(Boolean).join(' ')}</div>
                  )}
                  {customer.phone && <div>Tel.: {customer.phone}</div>}
                </div>
              )}
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm whitespace-nowrap shrink-0">Ansprechpartner:</Label>
                <Input
                  value={kontakt}
                  onChange={(e) => {
                    setKontakt(e.target.value)
                    setIsDirty(true)
                  }}
                  className="flex-1 h-8 text-sm"
                />
              </div>
            </div>
          </div>
        </Card>

        {/* ── Positionen-Grid ──────────────────────────────────────────── */}
        <Card className="mb-4 p-4">
          <h2 className="mb-2 font-semibold text-sm">Positionen</h2>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="text-xs">
                  <TableHead className="w-16">Pos.-Nr.</TableHead>
                  <TableHead className="w-24">Artikel-Nr.</TableHead>
                  <TableHead className="w-40">Bezeichnung</TableHead>
                  <TableHead className="w-36">Bezeichnung 2</TableHead>
                  <TableHead className="w-20 text-right">Menge</TableHead>
                  <TableHead className="w-16">Einheit</TableHead>
                  <TableHead className="w-24 text-right">Listenpreis</TableHead>
                  <TableHead className="w-20 text-right">Rabatt %</TableHead>
                  <TableHead className="w-24 text-right">Netto-Pr.</TableHead>
                  <TableHead className="w-24 text-right">Netto-Be.</TableHead>
                  <TableHead className="w-24 text-right">EK-Preis</TableHead>
                  <TableHead className="w-16 text-right">MwSt %</TableHead>
                  <TableHead className="w-28 text-right">Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {positionen.map((pos, idx) => (
                  <TableRow
                    key={idx}
                    className={`cursor-pointer text-xs ${
                      aktivePositionIndex === idx ? 'bg-amber-100' : 'hover:bg-muted/50'
                    }`}
                    onClick={() => handlePositionRowClick(pos, idx)}
                  >
                    <TableCell>{pos.posNr}</TableCell>
                    <TableCell>{pos.artikelNr}</TableCell>
                    <TableCell>{pos.bezeichnung}</TableCell>
                    <TableCell>{pos.bezeichnung2}</TableCell>
                    <TableCell className="text-right">{pos.menge}</TableCell>
                    <TableCell>{pos.einheit}</TableCell>
                    <TableCell className="text-right">{pos.listenpreis.toFixed(2)}</TableCell>
                    <TableCell className="text-right">{pos.rabatt}%</TableCell>
                    <TableCell className="text-right">{pos.nettoPreis.toFixed(2)}</TableCell>
                    <TableCell className="text-right">{pos.nettoBetrag.toFixed(2)}</TableCell>
                    <TableCell className="text-right">{pos.ekPreis.toFixed(2)}</TableCell>
                    <TableCell className="text-right">{pos.mwstProzent}</TableCell>
                    <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-0.5">
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          title="Hoch"
                          onClick={() => handleMovePositionUp(idx)}
                          disabled={idx <= 0}
                        >
                          <ChevronUp className="h-4 w-4" />
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          title="Runter"
                          onClick={() => handleMovePositionDown(idx)}
                          disabled={idx >= positionen.length - 1}
                        >
                          <ChevronDown className="h-4 w-4" />
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-red-600 hover:text-red-700"
                          title="Position löschen"
                          onClick={() => handlePositionDelete(idx)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
                {positionen.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={14} className="text-center text-xs text-muted-foreground py-4">
                      Noch keine Positionen — Artikel im Bereich unten eingeben
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </Card>

        {/* ── Positions-Details ────────────────────────────────────────── */}
        <Card className="mb-4 p-4">
          <h2 className="mb-2 font-semibold text-sm">Positions-Details</h2>
          <div className="grid grid-cols-6 gap-4">

            {/* Pos.-Nr. */}
            <div className="space-y-1">
              <Label className="text-xs">Pos.-Nr.:</Label>
              <Input value={currentPosition.posNr} readOnly className="h-8 text-sm" />
            </div>

            {/* Artikel-Nr. + Suche */}
            <div className="space-y-1">
              <Label className="text-xs">Artikel-Nr.:</Label>
              <div className="flex gap-1">
                <Input
                  value={currentPosition.artikelNr}
                  readOnly
                  className="flex-1 h-8 text-sm"
                  placeholder="—"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  title="Artikel suchen"
                  onClick={() => setShowArticleDialog(true)}
                >
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Bezeichnung (2 Spalten) */}
            <div className="space-y-1 col-span-2">
              <Label className="text-xs">Bezeichnung:</Label>
              <Input value={currentPosition.bezeichnung} readOnly className="h-8 text-sm" />
              <Input value={currentPosition.bezeichnung2} readOnly className="h-8 text-sm" placeholder="Bezeichnung 2" />
            </div>

            {/* Menge */}
            <div className="space-y-1">
              <Label className="text-xs">Menge:</Label>
              <Input
                type="number"
                min="0"
                step="0.001"
                value={currentPosition.menge === 0 ? '' : currentPosition.menge}
                onChange={(e) =>
                  setCurrentPosition((prev) => ({ ...prev, menge: Number(e.target.value) }))
                }
                className="h-8 text-sm"
              />
            </div>

            {/* Einheit */}
            <div className="space-y-1">
              <Label className="text-xs">Einheit:</Label>
              <Input value={currentPosition.einheit} readOnly className="h-8 text-sm" />
            </div>

            {/* Listenpreis */}
            <div className="space-y-1">
              <Label className="text-xs">Listenpreis:</Label>
              <Input
                type="number"
                step="0.01"
                value={currentPosition.listenpreis === 0 ? '' : currentPosition.listenpreis}
                onChange={(e) =>
                  setCurrentPosition((prev) => ({ ...prev, listenpreis: Number(e.target.value) }))
                }
                className="h-8 text-sm"
              />
            </div>

            {/* Rabatt */}
            <div className="space-y-1">
              <Label className="text-xs">Rabatt %:</Label>
              <Input
                type="number"
                min="0"
                max="100"
                step="0.1"
                value={currentPosition.rabatt === 0 ? '' : currentPosition.rabatt}
                onChange={(e) =>
                  setCurrentPosition((prev) => ({ ...prev, rabatt: Number(e.target.value) }))
                }
                className="h-8 text-sm"
              />
            </div>

            {/* Einh.-Preis (berechnet) */}
            <div className="space-y-1">
              <Label className="text-xs">Einh.-Preis:</Label>
              <Input
                value={currentPosition.einhPreis.toFixed(2)}
                readOnly
                className="h-8 text-sm bg-muted"
              />
            </div>

            {/* Betrag (berechnet) */}
            <div className="space-y-1">
              <Label className="text-xs">Betrag:</Label>
              <Input
                value={currentPosition.betrag.toFixed(2)}
                readOnly
                className="h-8 text-sm bg-muted"
              />
            </div>

            {/* EK-Preis */}
            <div className="space-y-1">
              <Label className="text-xs">EK-Preis:</Label>
              <Input
                type="number"
                step="0.01"
                value={currentPosition.ekPreis === 0 ? '' : currentPosition.ekPreis}
                onChange={(e) =>
                  setCurrentPosition((prev) => ({ ...prev, ekPreis: Number(e.target.value) }))
                }
                className="h-8 text-sm"
              />
            </div>

            {/* MwSt. */}
            <div className="space-y-1">
              <Label className="text-xs">MwSt. %:</Label>
              <Input
                type="number"
                value={currentPosition.mwstProzent}
                onChange={(e) =>
                  setCurrentPosition((prev) => ({ ...prev, mwstProzent: Number(e.target.value) }))
                }
                className="h-8 text-sm"
              />
            </div>

            {/* Zeile OK */}
            <div className="flex items-end">
              <Button
                onClick={handlePositionOK}
                disabled={!currentPosition.artikelNr || !currentPosition.menge}
                className="h-8 gap-1 bg-amber-500 hover:bg-amber-600 text-white text-sm"
              >
                <Check className="h-4 w-4" />
                Zeile OK
              </Button>
            </div>
          </div>
        </Card>

        {/* ── Summen ──────────────────────────────────────────────────── */}
        <Card className="mb-4 p-4">
          <div className="grid grid-cols-5 gap-4">
            <div className="space-y-1">
              <Label className="text-xs">Gewicht:</Label>
              <Input value={`${summen.gewicht.toFixed(2)} kg`} readOnly className="h-8 text-sm" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Netto:</Label>
              <Input value={summen.netto.toFixed(2)} readOnly className="h-8 text-sm" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">MwSt.:</Label>
              <Input value={summen.mwst.toFixed(2)} readOnly className="h-8 text-sm" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs font-semibold">Brutto:</Label>
              <Input value={summen.brutto.toFixed(2)} readOnly className="h-8 text-sm font-semibold" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Währung:</Label>
              <Input value="EUR" readOnly className="h-8 text-sm" />
            </div>
          </div>
        </Card>
      </div>

      {/* ── Bottom-Toolbar ─────────────────────────────────────────────── */}
      <div className="border-t bg-white px-4 py-2 flex items-center justify-between">
        <div className="flex gap-2">
          <Button size="sm" className="h-7 text-xs gap-1" onClick={handleSave} disabled={isSaving}>
            <Save className="h-3 w-3" /> Speichern
          </Button>
          <Button variant="outline" size="sm" className="h-7 text-xs gap-1" onClick={() => setShowPrintDialog(true)}>
            <Printer className="h-3 w-3" /> Drucken
          </Button>
          <Button variant="outline" size="sm" className="h-7 text-xs gap-1" onClick={() => setShowAttachmentDialog(true)}>
            <FileText className="h-3 w-3" /> Unterlagen
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-7 text-xs gap-1"
            onClick={handleConvertToOrder}
            data-action-id="sales.offer.convert-to-order"
          >
            <FileText className="h-3 w-3" /> In Auftrag wandeln
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-7 text-xs gap-1 text-destructive hover:text-destructive"
            onClick={() => {
              if (!angebotId) {
                push('Kein gespeichertes Angebot zum Löschen')
                return
              }
              if (window.confirm('Angebot wirklich löschen?')) void handleDelete()
            }}
          >
            <Trash2 className="h-3 w-3" /> Löschen
          </Button>
        </div>
        <Button variant="ghost" size="sm" className="h-7 text-xs gap-1" onClick={handleBeenden}>
          <X className="h-3 w-3" /> Beenden
        </Button>
      </div>

      {/* ── Dialoge ──────────────────────────────────────────────────────── */}

      {/* Auswahl bestehendes Angebot — öffnet nur per ... Button */}
      <Dialog open={showAngebotAuswahl} onOpenChange={setShowAngebotAuswahl}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Verkaufs-Angebote</DialogTitle>
          </DialogHeader>

          <div className="flex items-center gap-2 mb-3">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Input
              value={sucheText}
              onChange={(e) => setSucheText(e.target.value)}
              placeholder="Angebot-Nr. oder Kunde suchen..."
              className="h-8 text-sm"
              autoFocus
            />
          </div>

          <div className="border rounded-md overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted text-xs">
                  <TableHead className="py-1 w-28">Angebot-Nr.</TableHead>
                  <TableHead className="py-1 w-24">Datum</TableHead>
                  <TableHead className="py-1">Kunde</TableHead>
                  <TableHead className="py-1 w-20 text-right">Betrag</TableHead>
                  <TableHead className="py-1 w-20">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-sm text-muted-foreground py-6">
                      Lade Angebote…
                    </TableCell>
                  </TableRow>
                ) : filteredAngebote.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-sm text-muted-foreground py-6">
                      Keine Angebote gefunden
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredAngebote.map((a, idx) => (
                    <TableRow
                      key={a.id}
                      className={`text-xs cursor-pointer ${
                        idx === 0 ? 'bg-primary text-primary-foreground' : 'hover:bg-muted/50'
                      }`}
                      onDoubleClick={() => handleAngebotAuswaehlen(a)}
                    >
                      <TableCell className="py-1 font-mono">{a.nummer}</TableCell>
                      <TableCell className="py-1">{a.datum}</TableCell>
                      <TableCell className="py-1">{a.kunde}</TableCell>
                      <TableCell className="py-1 text-right">
                        {a.betrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €
                      </TableCell>
                      <TableCell className="py-1">{a.status}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          <DialogFooter className="mt-2">
            <Button variant="outline" size="sm" onClick={() => setShowAngebotAuswahl(false)}>
              Abbrechen
            </Button>
            <Button
              size="sm"
              onClick={() => filteredAngebote[0] && handleAngebotAuswaehlen(filteredAngebote[0])}
            >
              Übernehmen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Kunden-Auswahl */}
      <CustomerSelectionDialog
        open={showCustomerDialog}
        onClose={() => setShowCustomerDialog(false)}
        onSelect={handleCustomerSelect}
      />

      {/* Artikel-Suche */}
      <ArtikelSuchDialog
        open={showArticleDialog}
        onClose={() => setShowArticleDialog(false)}
        onSelect={handleArticleSelect}
      />

      {/* Druck-Dialog */}
      <LieferscheinDruckDialog
        open={showPrintDialog}
        onClose={() => setShowPrintDialog(false)}
        onConfirm={handlePrint}
        title="ANGEBOT DRUCKEN"
      />
      <DmsAnhangDialog
        open={showAttachmentDialog}
        onClose={() => setShowAttachmentDialog(false)}
        businessObjectType="quotation"
        businessObjectId={angebotId}
        title="UNTERLAGEN / DATEIEN — ANGEBOT"
      />
    </div>
  )
}
