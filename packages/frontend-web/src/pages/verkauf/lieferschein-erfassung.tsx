/**
 * Lieferschein-Erfassung (Verkauf)
 * 1:1 Nachbau der zvoove Lieferschein-Erfassungsmaske
 */

import { lazy, Suspense, useState, useEffect, useMemo } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Card } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { useToast } from '@/components/ui/toast-provider'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import type { Customer } from '@/components/sales/CustomerSelectionDialog'
import type { PrintOptions } from '@/components/sales/LieferscheinDruckDialog'
import type { BelegfolgePosition } from '@/components/sales/BelegfolgePositionenDialog'
import { apiClient } from '@/lib/axios'
import { useAuth } from '@/hooks/useAuth'
import { useSchlaege } from '@/lib/api/agrar'
import { globalShortcutManager } from '@/lib/shortcuts/global-shortcuts'
import { useGlobalShortcutsWithVoice } from '@/features/ki-usability'
import { ShortcutHintButton } from '@/components/shortcuts/ShortcutHelpPanel'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { NativeSelect } from '@/components/ui/native-select'
import { ChevronLeft, ChevronRight, ChevronUp, ChevronDown, MoreHorizontal, Check, Printer, Save, X, FileText, Folder, FileCheck, Link as LinkIcon, Receipt, Trash2 } from 'lucide-react'

const CustomerSelectionDialog = lazy(() =>
  import('@/components/sales/CustomerSelectionDialog').then((m) => ({ default: m.CustomerSelectionDialog }))
)
const ArtikelSuchDialog = lazy(() =>
  import('@/components/sales/ArtikelSuchDialog').then((m) => ({ default: m.ArtikelSuchDialog }))
)
const LieferscheinDruckDialog = lazy(() =>
  import('@/components/sales/LieferscheinDruckDialog').then((m) => ({ default: m.LieferscheinDruckDialog }))
)
const DmsAnhangDialog = lazy(() =>
  import('@/components/dms/DmsAnhangDialog').then((m) => ({ default: m.DmsAnhangDialog }))
)
const AttestationDialog = lazy(() =>
  import('@/components/sales/AttestationDialog').then((m) => ({ default: m.AttestationDialog }))
)
const BelegfolgePositionenDialog = lazy(() =>
  import('@/components/sales/BelegfolgePositionenDialog').then((m) => ({ default: m.BelegfolgePositionenDialog }))
)

function LazyDialogBoundary({ children }: { children: JSX.Element }) {
  return <Suspense fallback={null}>{children}</Suspense>
}

// API Response Type
type DeliveryNoteResponse = {
  id: string
  tenant_id: string
  delivery_note_number: string
  customer_id: string | null
  branch_id: string | null
  sales_rep_id: string | null
  operator_id: string | null
  delivery_date: string
  delivery_time: string | null
  cost_center_id: string | null
  truck_number: number | null
  is_credit_note: boolean
  is_self_pickup: boolean
  is_early_payment: boolean
  reference_invoice_number: string | null
  status: string
  is_printed: boolean
  is_delivered: boolean
  invoice_number: string | null
  totals: { netto: number; mwst: number; brutto: number } | null
  created_at: string
  updated_at: string
  created_by: string | null
  updated_by: string | null
  positionen: Array<{
    id: string
    delivery_note_id: string
    pos_nr: number
    artikel_id: string | null
    artikel_nr: string | null
    bezeichnung: string | null
    bezeichnung2: string | null
    menge: number
    einheit: string | null
    listenpreis: number | null
    rabatt: number
    art: string | null
    netto_preis: number | null
    netto_betrag: number | null
    niederlassung: number | null
    lagerhalle: string | null
    lagerfach: string | null
    charge: string | null
    serien_nr: string | null
    erloskonto: string | null
    mwst_prozent: number
    kontrakt_nr: string | null
    skontierf: boolean
    fremdware: boolean
    gef_punkt: string | null
    na_bio: string | null
    muster_nr: string | null
    strecke: string | null
    zus_beleg: string | null
    anerken: string | null
    created_at: string
    updated_at: string
  }>
}

export type Position = {
  posNr: number
  artikelNr: string
  artikelId: string | null // Artikel-ID (UUID) für Backend-Mapping
  bezeichnung: string
  bezeichnung2: string
  menge: number
  einheit: string
  listenpreis: number
  rabatt: number
  art: string
  nettoPreis: number
  nettoBetrag: number
  niederlassung: string
  lagerhalle: string
  lagerfach: string
  charge: string
  serienNr: string
  gefPunkt: string // Gefahrgut-Punkte als String (für Anzeige)
  gefahrgutPunkte: number // Gefahrgut-Punkte pro Einheit (numerisch, aus Artikel)
  gesamtGefahrgutPunkte: number // Gesamt-Gefahrgut-Punkte (gefahrgutPunkte × menge)
  naBio: string
  musterNr: string
  strecke: string
  zusBeleg: string
  anerken: string
  erloskonto: string
  mwstProzent: number
  gewicht: number // Gewicht pro Einheit (aus Artikel)
  gesamtGewicht: number // Gesamtgewicht (gewicht × menge)
  kontraktNr: string // Vertragsnummer
  skontierf: boolean // Skontierfähig
  fremdware: boolean // Fremdware
}

type LieferscheinState = {
  id: string | null // UUID vom Backend
  lieferscheinNr: string
  status: string // draft | posted | printed | delivered (nur bei draft Positionen änderbar)
  niederlassung: number
  vertreter: string
  bediener: string
  lieferDatum: string
  uhrzeit: string
  kostenstelle: number
  lkwNr: number
  gutschriftKennz: boolean
  selbstabholung: boolean
  fruehbezugRechnung: boolean
  reNrBezug: string
  statusGedruckt: boolean
  statusAusgeliefert: boolean
  fakturiertRechnNr: string
  customer: Customer | null
  positionen: Position[]
  aktivePositionIndex: number | null
}

type CurrentPositionDetails = {
  posNr: number
  artikelNr: string
  artikelId: string | null // Artikel-ID (UUID) für Backend-Mapping
  artikelBezeichnung: string
  artikelBezeichnung2: string
  mengeGebinde: number
  einheit: string
  listenpreis: number
  rabatt: number
  einhPreis: number
  betrag: number
  mwstProzent: number
  verfuegbar: number
  kontraktNr: string
  skontierf: boolean
  fremdware: boolean
  artikelGewicht: number // Gewicht pro Einheit (aus Artikel)
  artikelGefahrgutPunkte: number // Gefahrgut-Punkte pro Einheit (aus Artikel)
}

export default function LieferscheinErfassungPage(): JSX.Element {
  const navigate = useNavigate()
  const { push } = useToast()
  const { user } = useAuth()
  const { id: deliveryNoteId } = useParams<{ id?: string }>() // URL-Parameter für bestehenden Lieferschein

  // Auto-generiere Lieferschein-Nummer (später vom Backend)
  const generateLieferscheinNr = (): string => {
    const year = new Date().getFullYear()
    const random = Math.floor(Math.random() * 1000000)
    return `${year}${String(random).padStart(6, '0')}`
  }

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
    // Versuche verschiedene Felder: username, name, sub
    const shortName = user.name?.split(' ').map(n => n[0]).join('').toUpperCase() || 
                     user.sub?.substring(0, 2).toUpperCase() || 
                     'USER'
    return shortName.length > 2 ? shortName.substring(0, 2) : shortName
  }

  const [state, setState] = useState<LieferscheinState>({
    id: null, // Wird beim Speichern vom Backend gesetzt
    lieferscheinNr: generateLieferscheinNr(),
    status: 'draft',
    niederlassung: 0,
    vertreter: '', // Wird beim Kundenauswahl gesetzt
    bediener: getUserShortName(), // Aus Session
    lieferDatum: formatDateForInput(new Date()),
    uhrzeit: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
    kostenstelle: 0,
    lkwNr: 0,
    gutschriftKennz: false,
    selbstabholung: false,
    fruehbezugRechnung: false,
    reNrBezug: '',
    statusGedruckt: false,
    statusAusgeliefert: false,
    fakturiertRechnNr: '',
    customer: null,
    positionen: [],
    aktivePositionIndex: null,
  })

  // Bediener aus Session aktualisieren, wenn User geladen wird
  useEffect(() => {
    if (user) {
      setState((prev) => ({
        ...prev,
        bediener: getUserShortName(),
      }))
    }
  }, [user])

  // Lade bestehenden Lieferschein, wenn ID in URL vorhanden
  useEffect(() => {
    const loadDeliveryNote = async (): Promise<void> => {
      if (!deliveryNoteId) return

      try {
        const response = await apiClient.get<DeliveryNoteResponse>(`/api/v1/sales/delivery-notes/${deliveryNoteId}`)
        
        // Lade Kunde, falls vorhanden
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
          } catch (err) {
            console.warn('Kunde konnte nicht geladen werden:', err)
          }
        }

        // Mappe Positionen
        const positionen: Position[] = await Promise.all(
          response.positionen.map(async (pos) => {
            // Lade Artikel-Gewicht und Gefahrgut-Punkte, falls artikel_id vorhanden
            let artikelGewicht = 0
            let artikelGefahrgutPunkte = 0
            if (pos.artikel_id) {
              try {
                const artikelResponse = await apiClient.get<any>(`/api/v1/articles/${pos.artikel_id}`)
                artikelGewicht = artikelResponse.weight || artikelResponse.gewicht || 0
                artikelGefahrgutPunkte = artikelResponse.gefahrgut_punkte || artikelResponse.gefahrgutpunkte || 
                  artikelResponse.gefahrgutPunkte || (artikelResponse.gefahrgutklasse ? parseFloat(artikelResponse.gefahrgutklasse) || 0 : 0)
              } catch (err) {
                console.warn(`Artikel-Daten konnten nicht geladen werden für Artikel ${pos.artikel_id}:`, err)
              }
            }
            const gesamtGewicht = artikelGewicht * pos.menge
            const gesamtGefahrgutPunkte = artikelGefahrgutPunkte * pos.menge

            return {
              posNr: pos.pos_nr,
              artikelNr: pos.artikel_nr || '',
              artikelId: pos.artikel_id || null, // Artikel-ID aus Backend
              bezeichnung: pos.bezeichnung || '',
              bezeichnung2: pos.bezeichnung2 || '',
              menge: pos.menge,
              einheit: pos.einheit || '',
              listenpreis: pos.listenpreis || 0,
              rabatt: pos.rabatt,
              art: pos.art || '',
              nettoPreis: pos.netto_preis || 0,
              nettoBetrag: pos.netto_betrag || 0,
              niederlassung: String(pos.niederlassung || ''),
              lagerhalle: pos.lagerhalle || '',
              lagerfach: pos.lagerfach || '',
              charge: pos.charge || '',
              serienNr: pos.serien_nr || '',
              gefPunkt: pos.gef_punkt || (artikelGefahrgutPunkte > 0 ? artikelGefahrgutPunkte.toString() : ''),
              gefahrgutPunkte: artikelGefahrgutPunkte,
              gesamtGefahrgutPunkte,
              naBio: pos.na_bio || '',
              musterNr: pos.muster_nr || '',
              strecke: pos.strecke || '',
              zusBeleg: pos.zus_beleg || '',
              anerken: pos.anerken || '',
              erloskonto: pos.erloskonto || '',
              mwstProzent: pos.mwst_prozent,
              gewicht: artikelGewicht,
              gesamtGewicht,
              kontraktNr: pos.kontrakt_nr || '', // Vertragsnummer aus Backend
              skontierf: pos.skontierf || false, // Skontierfähig aus Backend
              fremdware: pos.fremdware || false, // Fremdware aus Backend
            }
          })
        )

        // Parse delivery_date
        const deliveryDate = response.delivery_date ? formatDateForInput(new Date(response.delivery_date)) : formatDateForInput(new Date())
        
        // Parse delivery_time
        const deliveryTime = response.delivery_time 
          ? response.delivery_time.substring(0, 5) // HH:MM
          : new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })

        // Mappe branch_id zu niederlassung (branch_number)
        let niederlassung = 0
        const branchId = response.branch_id
        if (branchId) {
          try {
            const branch = await apiClient.get<any>(`/api/v1/admin/branches/${branchId}`)
            niederlassung = branch.branch_number || 0
            // Cache speichern
            setBranchCache((prev) => new Map(prev).set(niederlassung, branchId))
          } catch (error) {
            console.warn('Fehler beim Laden der Branch:', error)
          }
        }

        setState({
          id: response.id,
          lieferscheinNr: response.delivery_note_number, // Vom Backend vergeben
          status: response.status || 'draft',
          niederlassung, // Gemappt von branch_id
          vertreter: customer?.representative || '', // Vertreter aus Kunden-Stammdaten
          bediener: getUserShortName(),
          lieferDatum: deliveryDate,
          uhrzeit: deliveryTime,
          kostenstelle: response.cost_center_id ? Number(response.cost_center_id) : 0,
          lkwNr: response.truck_number || 0,
          gutschriftKennz: response.is_credit_note,
          selbstabholung: response.is_self_pickup,
          fruehbezugRechnung: response.is_early_payment,
          reNrBezug: response.reference_invoice_number || '',
          statusGedruckt: response.is_printed,
          statusAusgeliefert: response.is_delivered,
          fakturiertRechnNr: response.invoice_number || '', // Vom Backend vergeben
          customer,
          positionen,
          aktivePositionIndex: null,
        })

        push('Lieferschein geladen')
      } catch (error: any) {
        console.error('Fehler beim Laden des Lieferscheins:', error)
        push(`Fehler beim Laden: ${error.response?.data?.detail || error.message}`)
      }
    }

    void loadDeliveryNote()
  }, [deliveryNoteId, user, push])

  const [currentPosition, setCurrentPosition] = useState<CurrentPositionDetails>({
    posNr: 10,
    artikelNr: '',
    artikelId: null, // Artikel-ID für Backend-Mapping
    artikelBezeichnung: '',
    artikelBezeichnung2: '',
    mengeGebinde: 0,
    einheit: '',
    listenpreis: 0,
    rabatt: 0,
    einhPreis: 0,
    betrag: 0,
    mwstProzent: 19,
    verfuegbar: 0,
    kontraktNr: '',
    skontierf: false,
    fremdware: false,
    artikelGewicht: 0, // Gewicht pro Einheit
    artikelGefahrgutPunkte: 0, // Gefahrgut-Punkte pro Einheit
  })

  const [showCustomerDialog, setShowCustomerDialog] = useState(false)
  const [showArticleDialog, setShowArticleDialog] = useState(false)
  const [showPrintDialog, setShowPrintDialog] = useState(false)
  const [showAttachmentDialog, setShowAttachmentDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showAttestationDialog, setShowAttestationDialog] = useState(false)
  const [pendingAction, setPendingAction] = useState<'print' | 'modify' | null>(null)
  const [pendingPrintOptions, setPendingPrintOptions] = useState<PrintOptions | null>(null)
  const [showInformationDialog, setShowInformationDialog] = useState(false)
  const [customerTab, setCustomerTab] = useState<'kunde' | 'lieferanschr' | 'rechnanschrift' | 'bestellung' | 'rechnung' | 'texte' | 'spediteur' | 'lieferung'>('kunde')
  
  // State für Bestellungen
  const [bestellungen, setBestellungen] = useState<Array<{ id: string; bestellNr: string; datum: string }>>([])
  const [showBelegfolgeDialog, setShowBelegfolgeDialog] = useState(false)
  const [vorgaengerCount, setVorgaengerCount] = useState(0)
  const [showLieferscheinSuchenDialog, setShowLieferscheinSuchenDialog] = useState(false)
  const [lsList, setLsList] = useState<Array<{ id: string; delivery_note_number: string; customer_id?: string; delivery_date?: string }>>([])
  const [showNiederlassungDialog, setShowNiederlassungDialog] = useState(false)
  const [showVertreterDialog, setShowVertreterDialog] = useState(false)
  const [showPositionPopUpDialog, setShowPositionPopUpDialog] = useState(false)
  const [showPositionDetailsDialog, setShowPositionDetailsDialog] = useState(false)
  const [vertreterInput, setVertreterInput] = useState('')
  const [branchesList, setBranchesList] = useState<Array<{ id: string; branch_number: number; name: string }>>([])

  // Cache für Branch-Mapping (niederlassung -> branch_id)
  const [, setBranchCache] = useState<Map<number, string>>(new Map())

  // PSM-Dienstleistung: Schlag-Auswahl für Feldbuch-Eintrag
  const [psmSchlagId, setPsmSchlagId] = useState<string>('')
  const [psmFlaeche, setPsmFlaeche] = useState<string>('')
  const customerId = state.customer?.id
  const { data: schlaege = [] } = useSchlaege(customerId)

  // Berechne Summen
  const summen = useMemo(() => {
    const netto = state.positionen.reduce((sum, pos) => sum + pos.nettoBetrag, 0)
    // MWSt. wird pro Position berechnet (unterschiedliche MWSt.-Sätze möglich)
    const mwst = state.positionen.reduce((sum, pos) => {
      const mwstBetrag = (pos.nettoBetrag * pos.mwstProzent) / 100
      return sum + mwstBetrag
    }, 0)
    const brutto = netto + mwst
    // Gesamtgewicht berechnen (gewicht × menge für jede Position)
    const gesamtGewicht = state.positionen.reduce((sum, pos) => sum + (pos.gesamtGewicht || 0), 0)
    // Gesamt-Gefahrgut-Punkte berechnen (gefahrgutPunkte × menge für jede Position)
    const gesamtGefahrgutPunkte = state.positionen.reduce((sum, pos) => sum + (pos.gesamtGefahrgutPunkte || 0), 0)
    return { netto, mwst, brutto, gesamt: brutto, gewicht: gesamtGewicht, gefahrgutPunkte: gesamtGefahrgutPunkte }
  }, [state.positionen])

  // Kunde auswählen
  const handleCustomerSelect = async (customer: Customer): Promise<void> => {
    setState((prev) => ({
      ...prev,
      customer,
      // Vertreter aus Kunden-Stammdaten setzen
      vertreter: customer.representative || prev.vertreter || '',
    }))
    
    // Lade Vorgänger-Belege für den ausgewählten Kunden (Angebote + Aufträge + Portal-Bestellungen)
    try {
      const [ordersResp, quotesResp, portalResp] = await Promise.allSettled([
        apiClient.get<any>('/api/v1/sales/orders', { params: { customer_id: customer.id, limit: 20 } }),
        apiClient.get<any>('/api/v1/sales/quotes', { params: { customer_id: customer.id, limit: 20 } }),
        apiClient.get<any>('/api/v1/portal/bestellungen', { params: { customer_id: customer.id, status: 'bestellt', limit: 20 } }),
      ])

      const orders = ordersResp.status === 'fulfilled' ? (ordersResp.value.items || ordersResp.value || []) : []
      const mapped = orders.map((o: any) => ({
        id: o.id,
        bestellNr: o.order_number || o.orderNumber || '',
        datum: o.created_at
          ? new Date(o.created_at).toLocaleDateString('de-DE')
          : new Date().toLocaleDateString('de-DE'),
      }))
      setBestellungen(mapped)

      const quotesCount = quotesResp.status === 'fulfilled'
        ? (quotesResp.value.items || quotesResp.value || []).length
        : 0
      const portalCount = portalResp.status === 'fulfilled'
        ? (Array.isArray(portalResp.value) ? portalResp.value : (portalResp.value.items || portalResp.value.data || [])).length
        : 0
      setVorgaengerCount(mapped.length + quotesCount + portalCount)
    } catch (error) {
      console.warn('Fehler beim Laden der Vorgänger-Belege:', error)
      setBestellungen([])
      setVorgaengerCount(0)
    }
  }

  // Belegfolge-Positionsübernahme
  function handleBelegfolgePositionen(incoming: BelegfolgePosition[]): void {
    const baseNr =
      state.positionen.length > 0
        ? Math.max(...state.positionen.map((p) => p.posNr)) + 10
        : 10
    const newPositionen = incoming.map((pos, idx) => {
      const nettoPreis = pos.listenpreis * (1 - pos.rabatt / 100)
      const nettoBetrag = nettoPreis * pos.menge
      return {
        posNr: baseNr + idx * 10,
        artikelNr: pos.artikelNr,
        artikelId: pos.artikelId,
        bezeichnung: pos.bezeichnung,
        bezeichnung2: pos.bezeichnung2,
        menge: pos.menge,
        einheit: pos.einheit,
        listenpreis: pos.listenpreis,
        rabatt: pos.rabatt,
        art: '',
        nettoPreis,
        nettoBetrag,
        niederlassung: String(state.niederlassung),
        lagerhalle: '', lagerfach: '', charge: '', serienNr: '', gefPunkt: '',
        gefahrgutPunkte: 0, gesamtGefahrgutPunkte: 0,
        naBio: '', musterNr: '', strecke: '', zusBeleg: '', anerken: '', erloskonto: '',
        mwstProzent: pos.mwstProzent,
        gewicht: 0, gesamtGewicht: 0,
        kontraktNr: '', skontierf: false, fremdware: false,
      }
    })
    setState((prev) => ({
      ...prev,
      positionen: [...prev.positionen, ...newPositionen],
    }))
    push(`${newPositionen.length} Position${newPositionen.length !== 1 ? 'en' : ''} übernommen`)
  }

  // Artikel auswählen
  const handleArticleSelect = (article: any): void => {
    // API gibt zurück: article_number, name, description, sales_price, mehrwertsteuer_prozent, unit
    const mwstProzent = article.mehrwertsteuer_prozent || article.mwstProzent || 19
    const articleId = article.id
    
    // Standardwerte (Fallback falls Pricing-API nicht verfügbar)
    const fallbackListenpreis = article.sales_price || article.salesPrice || 0
    
    // Setze zunächst Standardwerte
    const artikelGewicht = article.weight || article.gewicht || 0
    // Gefahrgut-Punkte aus Artikel laden (kann direkt als Zahl oder aus gefahrgutklasse berechnet werden)
    const artikelGefahrgutPunkte = article.gefahrgut_punkte || article.gefahrgutpunkte || article.gefahrgutPunkte || 
      (article.gefahrgutklasse ? parseFloat(article.gefahrgutklasse) || 0 : 0)
    setCurrentPosition((prev) => ({
      ...prev,
      artikelNr: article.article_number || article.articleNumber || '',
      artikelId: article.id || articleId || null, // Artikel-ID für Backend-Mapping
      artikelBezeichnung: article.name || article.description || '',
      artikelBezeichnung2: article.description || article.description2 || '',
      einheit: article.unit || 'Stk',
      listenpreis: fallbackListenpreis,
      einhPreis: fallbackListenpreis, // Wird bei Preisberechnung aktualisiert
      mwstProzent: Number(mwstProzent) || 19,
      artikelGewicht, // Gewicht pro Einheit aus Artikel
      artikelGefahrgutPunkte, // Gefahrgut-Punkte pro Einheit aus Artikel
    }))
    
    // Hole Listenpreis aus Preisliste (mit Mengenstaffel-Berücksichtigung) asynchron
    // Verwende Standardmenge 1 für initiale Preisermittlung
    if (articleId && state.customer?.id) {
      void (async () => {
        try {
          const pricingResponse = await apiClient.get<{
            list_price: number
            discount: number
            net_price: number
            source: string
          }>('/api/v1/pricing/calculate', {
            params: {
              article_id: articleId,
              customer_id: state.customer?.id,
              quantity: currentPosition.mengeGebinde || 1, // Verwende aktuelle Menge oder 1
            },
          })
          
          if (pricingResponse.list_price) {
            setCurrentPosition((prev) => ({
              ...prev,
              listenpreis: pricingResponse.list_price,
              einhPreis: pricingResponse.list_price * (1 - (currentPosition.rabatt / 100)),
            }))
          }
        } catch (error) {
          console.warn('Fehler beim Abrufen des Listenpreises aus Preisliste:', error)
          // Fallback: Verwende bereits gesetzten sales_price
        }
      })()
    }
  }

  // Hilfsfunktion: pos_nr auf 10, 20, 30 … setzen
  const renumberPosNr = (positionen: Position[]): Position[] =>
    positionen.map((p, i) => ({ ...p, posNr: (i + 1) * 10 }))

  // Position löschen
  const handleDeletePosition = (idx: number): void => {
    const newPositionen = state.positionen.filter((_, i) => i !== idx)
    const renumbered = renumberPosNr(newPositionen)
    const newAktive =
      state.aktivePositionIndex === idx
        ? null
        : idx < (state.aktivePositionIndex ?? -1)
          ? (state.aktivePositionIndex ?? 0) - 1
          : state.aktivePositionIndex
    setState((prev) => ({
      ...prev,
      positionen: renumbered,
      aktivePositionIndex: newAktive,
    }))
  }

  // Position nach oben / unten verschieben
  const handleMovePositionUp = (idx: number): void => {
    if (idx <= 0) return
    const newPositionen = [...state.positionen]
    ;[newPositionen[idx - 1], newPositionen[idx]] = [newPositionen[idx], newPositionen[idx - 1]]
    const renumbered = renumberPosNr(newPositionen)
    const newAktive = state.aktivePositionIndex === idx ? idx - 1 : state.aktivePositionIndex === idx - 1 ? idx : state.aktivePositionIndex
    setState((prev) => ({
      ...prev,
      positionen: renumbered,
      aktivePositionIndex: newAktive,
    }))
  }

  const handleMovePositionDown = (idx: number): void => {
    if (idx >= state.positionen.length - 1) return
    const newPositionen = [...state.positionen]
    ;[newPositionen[idx], newPositionen[idx + 1]] = [newPositionen[idx + 1], newPositionen[idx]]
    const renumbered = renumberPosNr(newPositionen)
    const newAktive = state.aktivePositionIndex === idx ? idx + 1 : state.aktivePositionIndex === idx + 1 ? idx : state.aktivePositionIndex
    setState((prev) => ({
      ...prev,
      positionen: renumbered,
      aktivePositionIndex: newAktive,
    }))
  }

  // Position aus state.positionen[idx] in currentPosition (CurrentPositionDetails) füllen
  const selectPositionForEdit = (idx: number): void => {
    const pos = state.positionen[idx]
    if (!pos) return
    setState((prev) => ({ ...prev, aktivePositionIndex: idx }))
    setCurrentPosition({
      posNr: pos.posNr,
      artikelNr: pos.artikelNr,
      artikelId: pos.artikelId,
      artikelBezeichnung: pos.bezeichnung,
      artikelBezeichnung2: pos.bezeichnung2,
      mengeGebinde: pos.menge,
      einheit: pos.einheit,
      listenpreis: pos.listenpreis,
      rabatt: pos.rabatt,
      einhPreis: pos.nettoPreis,
      betrag: pos.nettoBetrag,
      mwstProzent: pos.mwstProzent,
      verfuegbar: 0,
      kontraktNr: pos.kontraktNr,
      skontierf: pos.skontierf,
      fremdware: pos.fremdware,
      artikelGewicht: pos.gewicht,
      artikelGefahrgutPunkte: pos.gefahrgutPunkte,
    })
  }

  // Position OK
  const handlePositionOK = (): void => {
    if (!currentPosition.artikelNr || !currentPosition.mengeGebinde) {
      push('Bitte Artikel und Menge eingeben')
      return
    }

    const nettoPreis = currentPosition.einhPreis * (1 - currentPosition.rabatt / 100)
    const nettoBetrag = nettoPreis * currentPosition.mengeGebinde
    const gesamtGewicht = currentPosition.artikelGewicht * currentPosition.mengeGebinde
    const gesamtGefahrgutPunkte = currentPosition.artikelGefahrgutPunkte * currentPosition.mengeGebinde

    // Validierung: Maximal 1000 Gefahrgut-Punkte pro Lieferung
    const aktuelleGefahrgutPunkte = state.positionen.reduce((sum, pos) => sum + (pos.gesamtGefahrgutPunkte || 0), 0)
    const neueGesamtGefahrgutPunkte = state.aktivePositionIndex !== null
      ? aktuelleGefahrgutPunkte - (state.positionen[state.aktivePositionIndex]?.gesamtGefahrgutPunkte || 0) + gesamtGefahrgutPunkte
      : aktuelleGefahrgutPunkte + gesamtGefahrgutPunkte

    if (neueGesamtGefahrgutPunkte > 1000) {
      push(`Fehler: Die maximale Anzahl von 1000 Gefahrgut-Punkten pro Lieferung würde überschritten werden. Aktuell: ${aktuelleGefahrgutPunkte.toFixed(0)}, zusätzlich: ${gesamtGefahrgutPunkte.toFixed(0)}, Gesamt: ${neueGesamtGefahrgutPunkte.toFixed(0)}`)
      return
    }

    const position: Position = {
      posNr: currentPosition.posNr,
      artikelNr: currentPosition.artikelNr,
      artikelId: currentPosition.artikelId,
      bezeichnung: currentPosition.artikelBezeichnung,
      bezeichnung2: currentPosition.artikelBezeichnung2,
      menge: currentPosition.mengeGebinde,
      einheit: currentPosition.einheit,
      listenpreis: currentPosition.listenpreis,
      rabatt: currentPosition.rabatt,
      art: '',
      nettoPreis,
      nettoBetrag,
      niederlassung: String(state.niederlassung),
      lagerhalle: '',
      lagerfach: '',
      charge: '',
      serienNr: '',
      gefPunkt: currentPosition.artikelGefahrgutPunkte > 0 ? currentPosition.artikelGefahrgutPunkte.toString() : '',
      gefahrgutPunkte: currentPosition.artikelGefahrgutPunkte,
      gesamtGefahrgutPunkte,
      naBio: '',
      musterNr: '',
      strecke: '',
      zusBeleg: '',
      anerken: '',
      erloskonto: '',
      mwstProzent: currentPosition.mwstProzent,
      gewicht: currentPosition.artikelGewicht,
      gesamtGewicht,
      kontraktNr: currentPosition.kontraktNr,
      skontierf: currentPosition.skontierf,
      fremdware: currentPosition.fremdware,
    }

    if (state.aktivePositionIndex !== null) {
      // Ersetzen an Index, dann durchnummerieren und zurücksetzen
      const newPositionen = [...state.positionen]
      newPositionen[state.aktivePositionIndex] = position
      const renumbered = renumberPosNr(newPositionen)
      const nextPosNr = (renumbered.length + 1) * 10
      setState((prev) => ({
        ...prev,
        positionen: renumbered,
        aktivePositionIndex: null,
      }))
      setCurrentPosition({
        posNr: nextPosNr,
        artikelNr: '',
        artikelId: null,
        artikelBezeichnung: '',
        artikelBezeichnung2: '',
        mengeGebinde: 0,
        einheit: '',
        listenpreis: 0,
        rabatt: 0,
        einhPreis: 0,
        betrag: 0,
        mwstProzent: 19,
        verfuegbar: 0,
        kontraktNr: '',
        skontierf: false,
        fremdware: false,
        artikelGewicht: 0,
        artikelGefahrgutPunkte: 0,
      })
      return
    }

    // Anhängen (wie bisher)
    setState((prev) => ({
      ...prev,
      positionen: [...prev.positionen, position],
      aktivePositionIndex: prev.positionen.length,
    }))
    setCurrentPosition({
      posNr: currentPosition.posNr + 10,
      artikelNr: '',
      artikelId: null,
      artikelBezeichnung: '',
      artikelBezeichnung2: '',
      mengeGebinde: 0,
      einheit: '',
      listenpreis: 0,
      rabatt: 0,
      einhPreis: 0,
      betrag: 0,
      mwstProzent: 19,
      verfuegbar: 0,
      kontraktNr: '',
      skontierf: false,
      fremdware: false,
      artikelGewicht: 0,
      artikelGefahrgutPunkte: 0,
    })
  }

  // Lieferschein speichern
  const handleSave = async (): Promise<string | null> => {
    try {
      if (!state.customer) {
        push('Bitte wählen Sie einen Kunden aus')
        return null
      }

      const [hours, minutes] = state.uhrzeit.split(':')
      const deliveryTime = `${hours}:${minutes}:00`

      const branch = branchesList.find((b) => b.branch_number === state.niederlassung)
      const payload = {
        customer_id: state.customer.id,
        branch_id: branch?.id ?? null,
        sales_rep_id: null,
        operator_id: user?.sub || null,
        delivery_date: state.lieferDatum,
        delivery_time: deliveryTime,
        cost_center_id: state.kostenstelle > 0 ? String(state.kostenstelle) : null,
        truck_number: state.lkwNr > 0 ? state.lkwNr : null,
        is_credit_note: state.gutschriftKennz,
        is_self_pickup: state.selbstabholung,
        is_early_payment: state.fruehbezugRechnung,
        reference_invoice_number: state.reNrBezug || null,
        status: 'draft',
        is_printed: state.statusGedruckt,
        is_delivered: state.statusAusgeliefert,
        // invoice_number wird NICHT vom Frontend gesetzt - nur vom Backend nach Fakturierung
        // invoice_number: state.fakturiertRechnNr || null,
        positionen: state.positionen.map((pos) => ({
          pos_nr: pos.posNr,
          artikel_id: pos.artikelId || null, // Artikel-ID aus Position
          artikel_nr: pos.artikelNr,
          bezeichnung: pos.bezeichnung,
          bezeichnung2: pos.bezeichnung2,
          menge: pos.menge,
          einheit: pos.einheit,
          listenpreis: pos.listenpreis,
          rabatt: pos.rabatt,
          art: pos.art,
          netto_preis: pos.nettoPreis,
          netto_betrag: pos.nettoBetrag,
          niederlassung: state.niederlassung,
          lagerhalle: pos.lagerhalle || null,
          lagerfach: pos.lagerfach || null,
          charge: pos.charge || null,
          serien_nr: pos.serienNr || null,
          erloskonto: pos.erloskonto || null,
          mwst_prozent: pos.mwstProzent,
          kontrakt_nr: pos.kontraktNr || null, // Vertragsnummer aus Position
          skontierf: pos.skontierf, // Skontierfähig aus Position
          fremdware: pos.fremdware, // Fremdware aus Position
          gef_punkt: pos.gefPunkt || null,
          na_bio: pos.naBio || null,
          muster_nr: pos.musterNr || null,
          strecke: pos.strecke || null,
          zus_beleg: pos.zusBeleg || null,
          anerken: pos.anerken || null,
        })),
      }

      let response: DeliveryNoteResponse
      if (state.id) {
        response = await apiClient.put<DeliveryNoteResponse>(`/api/v1/sales/delivery-notes/${state.id}`, payload)
      } else {
        response = await apiClient.post<DeliveryNoteResponse>('/api/v1/sales/delivery-notes', payload)
      }
      setState((prev) => ({
        ...prev,
        id: response.id, // UUID vom Backend
        lieferscheinNr: response.delivery_note_number,
        status: response.status || prev.status,
        fakturiertRechnNr: response.invoice_number || '', // Vom Backend gesetzt nach Fakturierung
      }))
      push('Lieferschein erfolgreich gespeichert')
      return response.id // Return ID for use in executePrint
    } catch (error: any) {
      console.error('Save error:', error)
      push(`Fehler beim Speichern: ${error.response?.data?.detail || error.message}`)
      return null // Return null on error
    }
  }

  // Lieferschein suchen / vorheriger / nächster
  const loadLsList = async (): Promise<Array<{ id: string; delivery_note_number: string; customer_id?: string; delivery_date?: string }>> => {
    const list = await apiClient.get<Array<{ id: string; delivery_note_number: string; customer_id?: string; delivery_date?: string }>>(
      '/api/v1/sales/delivery-notes',
      { params: { limit: 100 } }
    )
    return Array.isArray(list) ? list : (list as any)?.data ?? []
  }
  const handleLieferscheinSuchenOpen = async (): Promise<void> => {
    try {
      const list = await loadLsList()
      setLsList(list)
      setShowLieferscheinSuchenDialog(true)
    } catch (e: any) {
      push(`Fehler: ${e.response?.data?.detail ?? e.message}`)
    }
  }
  const handleLieferscheinPrev = async (): Promise<void> => {
    try {
      const list = await loadLsList()
      const idx = state.id ? list.findIndex((l) => l.id === state.id) : -1
      if (idx > 0 && list[idx - 1]) {
        navigate(`/verkauf/lieferschein-erfassung/${list[idx - 1].id}`)
      } else {
        push('Kein vorheriger Lieferschein')
      }
    } catch (e: any) {
      push(`Fehler: ${e.response?.data?.detail ?? e.message}`)
    }
  }
  const handleLieferscheinNext = async (): Promise<void> => {
    try {
      const list = await loadLsList()
      const idx = state.id ? list.findIndex((l) => l.id === state.id) : -1
      if (idx >= 0 && idx < list.length - 1 && list[idx + 1]) {
        navigate(`/verkauf/lieferschein-erfassung/${list[idx + 1].id}`)
      } else {
        push('Kein nächster Lieferschein')
      }
    } catch (e: any) {
      push(`Fehler: ${e.response?.data?.detail ?? e.message}`)
    }
  }
  // Branches beim Mount laden, damit branch_id beim Speichern aus niederlassung gemappt werden kann
  useEffect(() => {
    let cancelled = false
    apiClient.get<Array<{ id: string; branch_number: number; name: string }>>('/api/v1/admin/branches', { params: { active_only: true } })
      .then((res) => {
        const list = (res as any)?.data ?? res
        if (!cancelled && Array.isArray(list)) setBranchesList(list)
      })
      .catch(() => {})
    return () => { cancelled = true }
  }, [])

  const handleNiederlassungOpen = async (): Promise<void> => {
    try {
      const res = await apiClient.get<Array<{ id: string; branch_number: number; name: string }>>('/api/v1/admin/branches', { params: { active_only: true } })
      const list = (res as any)?.data ?? res
      setBranchesList(Array.isArray(list) ? list : [])
      setShowNiederlassungDialog(true)
    } catch (e: any) {
      push(`Fehler: ${e.response?.data?.detail ?? e.message}`)
    }
  }
  const handleVertreterOpen = (): void => {
    setVertreterInput(state.vertreter)
    setShowVertreterDialog(true)
  }
  const handleVertreterConfirm = (): void => {
    setState((prev) => ({ ...prev, vertreter: vertreterInput }))
    setShowVertreterDialog(false)
  }

  // Sofort-Rechnung: Lieferschein speichern, dann per Docflow in Rechnung umwandeln
  const handleCreateInvoice = async (): Promise<void> => {
    try {
      const savedId = await handleSave()
      if (!savedId) {
        push('Lieferschein muss zuerst gespeichert werden.')
        return
      }
      if (savedId && !state.id) setState((prev) => ({ ...prev, id: savedId }))
      const lsId = savedId
      const idempotencyKey = crypto.randomUUID()
      const res = await apiClient.post<{
        command: string
        target_doc_id?: string
        status: string
        payload?: { target_doc_number?: string; target_doc_type?: string }
      }>(`/api/v1/docflow/${lsId}/convert`, {
        target_doc_type: 'sales_invoice',
        idempotency_key: idempotencyKey,
      })
      const docNumber = res.payload?.target_doc_number
      if (docNumber) {
        push(`Rechnung ${docNumber} erstellt`)
        setState((prev) => ({ ...prev, fakturiertRechnNr: docNumber }))
        const targetId = res.target_doc_id
        if (targetId && typeof navigate === 'function') {
          navigate(`/verkauf/rechnungen/${targetId}`, { replace: false })
        }
      } else {
        push('Rechnung erstellt')
      }
    } catch (error: any) {
      push(`Sofort-Rechnung fehlgeschlagen: ${error.response?.data?.detail || error.message}`)
    }
  }

  // Lieferschein drucken und buchen
  const handlePrint = async (options: PrintOptions): Promise<void> => {
    // Wenn bereits gebucht, Attestierung erforderlich
    if (state.statusGedruckt || state.statusAusgeliefert) {
      setPendingPrintOptions(options)
      setPendingAction('print')
      setShowAttestationDialog(true)
      return
    }

    await executePrint(options)
  }

  // Attestierung bestätigt
  const handleAttestationConfirm = async (reason: string, action: 'print' | 'modify' | 'cancel' | 'post' | 'reopen'): Promise<void> => {
    setShowAttestationDialog(false)
    
    if (action === 'print') {
      const opts: PrintOptions = pendingPrintOptions ?? {
        formatvorlage: 'W00005', anzahlDrucke: 1, sortierung: 'pos-nr',
        druckLieferschein: true, druckAllgemeineAngaben: false, werbetext: '',
      }
      await executePrint(opts, reason)
    } else if (action === 'modify') {
      // Korrektur: setzt Status zurück auf 'offen' damit der LS editierbar wird
      if (!state.id) { push('Kein Lieferschein geöffnet'); return }
      try {
        await apiClient.patch(`/api/v1/sales/delivery-notes/${state.id}`, { status: 'offen', is_printed: false })
        dispatch({ type: 'SET_FIELD', field: 'statusGedruckt', value: false })
        push('Lieferschein zur Korrektur geöffnet — Änderungen vornehmen und erneut speichern.')
      } catch (e: any) {
        push(`Korrektur fehlgeschlagen: ${e.response?.data?.detail ?? e.message}`)
      }
    }
    // Other actions (cancel, post, reopen) are not handled yet
  }

  // Druck ausführen
  const executePrint = async (options: PrintOptions, attestation?: string): Promise<void> => {
    try {
      // Wenn noch nicht gespeichert (keine ID), erst speichern
      let lsId = state.id
      if (!lsId) {
        try {
          lsId = await handleSave()
          // Update state with new ID
          if (lsId) {
            setState((prev) => ({ ...prev, id: lsId }))
          }
        } catch (error) {
          push('Fehler: Lieferschein konnte nicht gespeichert werden. Bitte erneut versuchen.')
          return
        }
      }

      // Prüfe nochmal
      if (!lsId) {
        push('Fehler: Lieferschein-ID fehlt. Bitte erneut versuchen.')
        return
      }

      // API erwartet UUID (id), nicht delivery_note_number

      // Drucken via API
      const params = new URLSearchParams()
      if (attestation) {
        params.append('attestation', attestation)
      }
      params.append('template', options.formatvorlage)
      params.append('copies', String(options.anzahlDrucke))

      await apiClient.post(
        `/api/v1/sales/delivery-notes/${lsId}/print?${params.toString()}`
      )

      // Buchen
      await apiClient.post(`/api/v1/sales/delivery-notes/${lsId}/post`)

      // Feldbuch-Eintrag anlegen wenn Schlag ausgewählt
      if (psmSchlagId && state.customer?.id) {
        const psm_artikel = state.positionen[0]?.bezeichnung || 'PSM-Dienstleistung'
        const psm_menge = state.positionen[0]?.menge ?? 0
        const psm_einheit = state.positionen[0]?.einheit ?? 'l/ha'
        try {
          await apiClient.post('/api/v1/agrar/feldbuch/massnahmen/from-lieferschein', {
            lieferschein_id: lsId,
            lieferschein_datum: state.lieferDatum || new Date().toISOString(),
            customer_id: state.customer.id,
            schlag_id: psmSchlagId,
            artikel_name: psm_artikel,
            menge: psm_menge,
            einheit: psm_einheit,
            flaeche: psmFlaeche ? parseFloat(psmFlaeche) : 0,
            anwender: 'VALEO NeuroERP',
          })
          push('Maßnahme im Feldbuch angelegt')
        } catch {
          // Feldbuch-Fehler nicht blockierend
          push('Hinweis: Feldbuch-Eintrag konnte nicht erstellt werden')
        }
        setPsmSchlagId('')
        setPsmFlaeche('')
      }

      push('Lieferschein erfolgreich gedruckt und gebucht')
      setShowPrintDialog(false)

      // Maske auf neuen leeren Lieferschein zurücksetzen
      setState({
        id: null,
        lieferscheinNr: generateLieferscheinNr(),
        status: 'draft',
        niederlassung: 0,
        vertreter: '',
        bediener: getUserShortName(),
        lieferDatum: formatDateForInput(new Date()),
        uhrzeit: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
        kostenstelle: 0,
        lkwNr: 0,
        gutschriftKennz: false,
        selbstabholung: false,
        fruehbezugRechnung: false,
        reNrBezug: '',
        statusGedruckt: false,
        statusAusgeliefert: false,
        fakturiertRechnNr: '',
        customer: null,
        positionen: [],
        aktivePositionIndex: null,
      })
      setCurrentPosition({
        posNr: 10,
        artikelNr: '',
        artikelId: null,
        artikelBezeichnung: '',
        artikelBezeichnung2: '',
        mengeGebinde: 0,
        einheit: '',
        listenpreis: 0,
        rabatt: 0,
        einhPreis: 0,
        betrag: 0,
        mwstProzent: 19,
        verfuegbar: 0,
        kontraktNr: '',
        skontierf: false,
        fremdware: false,
        artikelGewicht: 0,
        artikelGefahrgutPunkte: 0,
      })
      setBestellungen([])
    } catch (error: any) {
      console.error('Print error:', error)
      push(`Fehler beim Drucken: ${error.response?.data?.detail || error.message}`)
    }
  }

  // Lieferschein löschen
  const handleDelete = async (): Promise<void> => {
    const lsId = state.id
    if (!lsId) {
      // Noch nie gespeichert — Formular einfach leeren
      setState({
        id: null,
        lieferscheinNr: generateLieferscheinNr(),
        status: 'draft',
        niederlassung: 0,
        vertreter: '',
        bediener: getUserShortName(),
        lieferDatum: formatDateForInput(new Date()),
        uhrzeit: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
        kostenstelle: 0,
        lkwNr: 0,
        gutschriftKennz: false,
        selbstabholung: false,
        fruehbezugRechnung: false,
        reNrBezug: '',
        statusGedruckt: false,
        statusAusgeliefert: false,
        fakturiertRechnNr: '',
        customer: null,
        positionen: [],
        aktivePositionIndex: null,
      })
      setCurrentPosition({
        posNr: 10, artikelNr: '', artikelId: null, artikelBezeichnung: '',
        artikelBezeichnung2: '', mengeGebinde: 0, einheit: '', listenpreis: 0,
        rabatt: 0, einhPreis: 0, betrag: 0, mwstProzent: 19, verfuegbar: 0,
        kontraktNr: '', skontierf: false, fremdware: false, artikelGewicht: 0,
        artikelGefahrgutPunkte: 0,
      })
      setBestellungen([])
      setShowDeleteDialog(false)
      return
    }

    try {
      await apiClient.delete(`/api/v1/sales/delivery-notes/${lsId}`)
      push('Lieferschein erfolgreich gelöscht')
      setShowDeleteDialog(false)
      navigate('/verkauf')
    } catch (error: any) {
      push(`Löschen fehlgeschlagen: ${error.response?.data?.detail || error.message}`)
    }
  }

  // Berechne Einh.-Preis und Betrag bei Änderung
  useEffect(() => {
    const nettoPreis = currentPosition.listenpreis * (1 - currentPosition.rabatt / 100)
    const betrag = nettoPreis * currentPosition.mengeGebinde
    setCurrentPosition((prev) => ({
      ...prev,
      einhPreis: nettoPreis,
      betrag,
    }))
  }, [currentPosition.listenpreis, currentPosition.rabatt, currentPosition.mengeGebinde])

  // Globale Shortcuts registrieren
  useGlobalShortcutsWithVoice({
    'open-customer-selection': () => setShowCustomerDialog(true),
    'open-article-selection': () => setShowArticleDialog(true),
    'confirm-position': () => handlePositionOK(),
    'save-document': () => void handleSave(),
    'print-document': () => {
      if (!showPrintDialog) {
        setShowPrintDialog(true)
      }
    },
    'delete-document': () => {
      setShowDeleteDialog(true)
    },
    'close-document': () => navigate(-1),
    'copy-previous-full': async () => {
      // F11: Kopiert ALLE Daten vom vorherigen Beleg (Kunde + Positionen)
      try {
        const response = await apiClient.get<DeliveryNoteResponse | null>('/api/v1/sales/delivery-notes/last', {
          params: {
            operator_id: user?.sub || undefined,
            customer_id: state.customer?.id || undefined,
          },
        })
        
        if (!response) {
          push('Kein vorheriger Beleg gefunden')
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
              creditLimit: customerData.credit_limit?.toString(),
              address: customerData.address,
              phone: customerData.phone,
              email: customerData.email,
              chefanweisung: customerData.chefanweisung || customerData.executive_note,
            }
          } catch (err) {
            console.warn('Kunde konnte nicht geladen werden:', err)
          }
        }
        
        // Mappe Positionen
        const positionen: Position[] = await Promise.all(
          response.positionen.map(async (pos) => {
            // Lade Artikel-Daten für Gewicht und Gefahrgut-Punkte
            let artikelGewicht = 0
            let artikelGefahrgutPunkte = 0
            if (pos.artikel_id) {
              try {
                const artikelResponse = await apiClient.get<any>(`/api/v1/articles/${pos.artikel_id}`)
                artikelGewicht = artikelResponse.weight || artikelResponse.gewicht || 0
                artikelGefahrgutPunkte = artikelResponse.gefahrgut_punkte || artikelResponse.gefahrgutpunkte || 
                  artikelResponse.gefahrgutPunkte || (artikelResponse.gefahrgutklasse ? parseFloat(artikelResponse.gefahrgutklasse) || 0 : 0)
              } catch (err) {
                console.warn(`Artikel-Daten konnten nicht geladen werden für Artikel ${pos.artikel_id}:`, err)
              }
            }
            const gesamtGewicht = artikelGewicht * pos.menge
            const gesamtGefahrgutPunkte = artikelGefahrgutPunkte * pos.menge
            
            return {
              posNr: pos.pos_nr,
              artikelNr: pos.artikel_nr || '',
              artikelId: pos.artikel_id || null,
              bezeichnung: pos.bezeichnung || '',
              bezeichnung2: pos.bezeichnung2 || '',
              menge: pos.menge,
              einheit: pos.einheit || '',
              listenpreis: pos.listenpreis || 0,
              rabatt: pos.rabatt,
              art: pos.art || '',
              nettoPreis: pos.netto_preis || 0,
              nettoBetrag: pos.netto_betrag || 0,
              niederlassung: String(pos.niederlassung || ''),
              lagerhalle: pos.lagerhalle || '',
              lagerfach: pos.lagerfach || '',
              charge: pos.charge || '',
              serienNr: pos.serien_nr || '',
              gefPunkt: pos.gef_punkt || (artikelGefahrgutPunkte > 0 ? artikelGefahrgutPunkte.toString() : ''),
              gefahrgutPunkte: artikelGefahrgutPunkte,
              gesamtGefahrgutPunkte,
              naBio: pos.na_bio || '',
              musterNr: pos.muster_nr || '',
              strecke: pos.strecke || '',
              zusBeleg: pos.zus_beleg || '',
              anerken: pos.anerken || '',
              erloskonto: pos.erloskonto || '',
              mwstProzent: pos.mwst_prozent,
              gewicht: artikelGewicht,
              gesamtGewicht,
              kontraktNr: pos.kontrakt_nr || '',
              skontierf: pos.skontierf || false,
              fremdware: pos.fremdware || false,
            }
          })
        )
        
        // Setze alle Daten
        const deliveryDate = response.delivery_date ? formatDateForInput(new Date(response.delivery_date)) : formatDateForInput(new Date())
        const deliveryTime = response.delivery_time 
          ? response.delivery_time.substring(0, 5)
          : new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
        
        setState((prev) => ({
          ...prev,
          customer,
          vertreter: customer?.representative || prev.vertreter || '',
          lieferDatum: deliveryDate,
          uhrzeit: deliveryTime,
          kostenstelle: response.cost_center_id ? Number(response.cost_center_id) : prev.kostenstelle,
          lkwNr: response.truck_number || prev.lkwNr,
          gutschriftKennz: response.is_credit_note,
          selbstabholung: response.is_self_pickup,
          fruehbezugRechnung: response.is_early_payment,
          reNrBezug: response.reference_invoice_number || '',
          positionen,
          aktivePositionIndex: null,
        }))
        
        // Lade auch Bestellungen für den Kunden
        if (customer) {
          await handleCustomerSelect(customer)
        }
        
        push('Daten vom vorherigen Beleg übernommen')
      } catch (error: any) {
        console.error('Fehler beim Laden des vorherigen Belegs:', error)
        push(`Fehler: ${error.response?.data?.detail || error.message}`)
      }
    },
    'copy-previous-positions': async () => {
      // Strg+F8: Kopiert nur Positionen (aktuell ausgewählter Kunde bleibt erhalten)
      if (!state.customer) {
        push('Bitte wählen Sie zuerst einen Kunden aus')
        return
      }
      
      try {
        const response = await apiClient.get<DeliveryNoteResponse | null>('/api/v1/sales/delivery-notes/last', {
          params: {
            operator_id: user?.sub || undefined,
            customer_id: state.customer.id, // Nur Positionen vom gleichen Kunden
          },
        })
        
        if (!response?.positionen || response.positionen.length === 0) {
          push('Keine Positionen im vorherigen Beleg gefunden')
          return
        }
        
        // Mappe nur Positionen
        const positionen: Position[] = await Promise.all(
          response.positionen.map(async (pos) => {
            // Lade Artikel-Daten für Gewicht und Gefahrgut-Punkte
            let artikelGewicht = 0
            let artikelGefahrgutPunkte = 0
            if (pos.artikel_id) {
              try {
                const artikelResponse = await apiClient.get<any>(`/api/v1/articles/${pos.artikel_id}`)
                artikelGewicht = artikelResponse.weight || artikelResponse.gewicht || 0
                artikelGefahrgutPunkte = artikelResponse.gefahrgut_punkte || artikelResponse.gefahrgutpunkte || 
                  artikelResponse.gefahrgutPunkte || (artikelResponse.gefahrgutklasse ? parseFloat(artikelResponse.gefahrgutklasse) || 0 : 0)
              } catch (err) {
                console.warn(`Artikel-Daten konnten nicht geladen werden für Artikel ${pos.artikel_id}:`, err)
              }
            }
            const gesamtGewicht = artikelGewicht * pos.menge
            const gesamtGefahrgutPunkte = artikelGefahrgutPunkte * pos.menge
            
            return {
              posNr: state.positionen.length > 0 
                ? Math.max(...state.positionen.map(p => p.posNr)) + 10 
                : pos.pos_nr,
              artikelNr: pos.artikel_nr || '',
              artikelId: pos.artikel_id || null,
              bezeichnung: pos.bezeichnung || '',
              bezeichnung2: pos.bezeichnung2 || '',
              menge: pos.menge,
              einheit: pos.einheit || '',
              listenpreis: pos.listenpreis || 0,
              rabatt: pos.rabatt,
              art: pos.art || '',
              nettoPreis: pos.netto_preis || 0,
              nettoBetrag: pos.netto_betrag || 0,
              niederlassung: String(pos.niederlassung || state.niederlassung),
              lagerhalle: pos.lagerhalle || '',
              lagerfach: pos.lagerfach || '',
              charge: pos.charge || '',
              serienNr: pos.serien_nr || '',
              gefPunkt: pos.gef_punkt || (artikelGefahrgutPunkte > 0 ? artikelGefahrgutPunkte.toString() : ''),
              gefahrgutPunkte: artikelGefahrgutPunkte,
              gesamtGefahrgutPunkte,
              naBio: pos.na_bio || '',
              musterNr: pos.muster_nr || '',
              strecke: pos.strecke || '',
              zusBeleg: pos.zus_beleg || '',
              anerken: pos.anerken || '',
              erloskonto: pos.erloskonto || '',
              mwstProzent: pos.mwst_prozent,
              gewicht: artikelGewicht,
              gesamtGewicht,
              kontraktNr: pos.kontrakt_nr || '',
              skontierf: pos.skontierf || false,
              fremdware: pos.fremdware || false,
            }
          })
        )
        
        // Füge Positionen hinzu (nicht ersetzen)
        setState((prev) => ({
          ...prev,
          positionen: [...prev.positionen, ...positionen],
          aktivePositionIndex: prev.positionen.length,
        }))
        
        push(`${positionen.length} Positionen vom vorherigen Beleg übernommen`)
      } catch (error: any) {
        console.error('Fehler beim Laden der Positionen:', error)
        push(`Fehler: ${error.response?.data?.detail || error.message}`)
      }
    },
    'create-invoice': () => void handleCreateInvoice(),
    'open-attachments': () => {
      setShowAttachmentDialog(true)
    },
      'show-information': () => {
        if (state.customer) {
          setShowInformationDialog(true)
        } else {
          push('Bitte wählen Sie zuerst einen Kunden aus')
        }
      },
    cancel: () => {
      // Schließe offene Dialoge
      setShowCustomerDialog(false)
      setShowArticleDialog(false)
      setShowPrintDialog(false)
      setShowAttestationDialog(false)
    },
  })

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header: LIEFERSCHEIN-ERFASSUNG */}
      <div className="bg-green-600 text-white px-4 py-2">
        <h1 className="text-lg font-bold">LIEFERSCHEIN-ERFASSUNG</h1>
      </div>
      <ModuleToolbar backTarget="/verkauf" closeTarget="/verkauf" title="Lieferschein-Erfassung" />
      {/* Belegfolge-Hinweis */}
      {vorgaengerCount > 0 && state.customer && (
        <div className="bg-amber-50 border-b border-amber-300 px-4 py-1.5 flex items-center gap-3">
          <span className="text-amber-800 text-sm font-medium">
            {vorgaengerCount} offene{vorgaengerCount !== 1 ? ' Vorgänger-Belege' : 'r Vorgänger-Beleg'} für{' '}
            <strong>{state.customer.name}</strong> vorhanden
          </span>
          <Button
            size="sm"
            variant="outline"
            className="h-6 text-xs border-amber-400 text-amber-800 hover:bg-amber-100"
            onClick={() => setShowBelegfolgeDialog(true)}
          >
            Positionen übernehmen
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="h-6 w-6 p-0 text-amber-600 ml-auto"
            onClick={() => setVorgaengerCount(0)}
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      )}

      <div className="flex-1 overflow-auto p-4">
        {/* Header-Bereich (3 Spalten) */}
        <Card className="mb-4 p-4">
          <div className="grid grid-cols-3 gap-4">
            {/* Linke Spalte */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Liefersch.-Nr.:</Label>
                <Input value={state.lieferscheinNr} readOnly className="flex-1 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => void handleLieferscheinSuchenOpen()} title="Lieferschein suchen">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => void handleLieferscheinPrev()} title="Vorheriger Lieferschein">
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => void handleLieferscheinNext()} title="Nächster Lieferschein">
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Liefer-Datum:</Label>
                <Input
                  type="date"
                  value={state.lieferDatum}
                  onChange={(e) =>
                    setState((prev) => ({
                      ...prev,
                      lieferDatum: e.target.value,
                    }))
                  }
                  className="flex-1 h-8"
                />
                <Input
                  type="time"
                  value={state.uhrzeit}
                  onChange={(e) => setState((prev) => ({ ...prev, uhrzeit: e.target.value }))}
                  className="w-20 h-8"
                />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Kostenstelle:</Label>
                <Input
                  type="number"
                  value={state.kostenstelle}
                  onChange={(e) =>
                    setState((prev) => ({ ...prev, kostenstelle: Number(e.target.value) }))
                  }
                  className="flex-1 h-8"
                />
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={state.gutschriftKennz}
                  onCheckedChange={(checked) =>
                    setState((prev) => ({ ...prev, gutschriftKennz: checked === true }))
                  }
                />
                <Label className="text-sm">Gutschrift kennzeichnen</Label>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Re.-Nr. (Bezug):</Label>
                <Input
                  value={state.reNrBezug}
                  onChange={(e) => setState((prev) => ({ ...prev, reNrBezug: e.target.value }))}
                  className="flex-1 h-8"
                />
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={state.statusGedruckt}
                  onCheckedChange={(checked) =>
                    setState((prev) => ({ ...prev, statusGedruckt: checked === true }))
                  }
                />
                <Label className="text-sm">gedruckt</Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={state.statusAusgeliefert}
                  onCheckedChange={(checked) =>
                    setState((prev) => ({ ...prev, statusAusgeliefert: checked === true }))
                  }
                />
                <Label className="text-sm">ausgeliefert</Label>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">fakturiert: Rechn.-Nr.:</Label>
                <Input
                  value={state.fakturiertRechnNr}
                  readOnly
                  className="flex-1 h-8 bg-muted cursor-not-allowed"
                  placeholder={state.fakturiertRechnNr ? undefined : "Wird automatisch zugewiesen nach Fakturierung"}
                  title={state.fakturiertRechnNr ? `Rechnungsnummer: ${state.fakturiertRechnNr}` : "Wird automatisch vom System zugewiesen, wenn der Lieferschein in eine Rechnung umgewandelt wurde"}
                />
              </div>
            </div>

            {/* Mittlere Spalte */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Niederlassung:</Label>
                <Input
                  type="number"
                  value={state.niederlassung}
                  onChange={(e) =>
                    setState((prev) => ({ ...prev, niederlassung: Number(e.target.value) }))
                  }
                  className="flex-1 h-8"
                />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => void handleNiederlassungOpen()} title="Niederlassung auswählen">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Vertreter:</Label>
                <Input value={state.vertreter} readOnly className="flex-1 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={handleVertreterOpen} title="Vertreter eingeben">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Bediener:</Label>
                <Input value={state.bediener} readOnly className="flex-1 h-8" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Lkw-Nr.:</Label>
                <Input
                  type="number"
                  value={state.lkwNr}
                  onChange={(e) => setState((prev) => ({ ...prev, lkwNr: Number(e.target.value) }))}
                  className="flex-1 h-8"
                />
              </div>
              <div className="flex items-center gap-2">
                <a
                  href="#"
                  className="text-sm text-blue-600 underline hover:text-blue-800"
                  onClick={(e) => {
                    e.preventDefault()
                    // F11: Kopiert ALLE Daten (Kunde + Positionen)
                    void globalShortcutManager.execute('copy-previous-full')
                  }}
                >
                  &gt;&gt; wie vorheriger Beleg (F11)
                </a>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={state.selbstabholung}
                  onCheckedChange={(checked) =>
                    setState((prev) => ({ ...prev, selbstabholung: checked === true }))
                  }
                />
                <Label className="text-sm">Selbstabholung</Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={state.fruehbezugRechnung}
                  onCheckedChange={(checked) =>
                    setState((prev) => ({ ...prev, fruehbezugRechnung: checked === true }))
                  }
                />
                <Label className="text-sm">Frühbezug-Rechnung</Label>
              </div>
            </div>

            {/* Rechte Spalte - Kunde */}
            <div className="space-y-2">
              <Tabs value={customerTab} onValueChange={(v) => setCustomerTab(v as typeof customerTab)}>
                <TabsList className="grid w-full grid-cols-4 h-auto">
                  <TabsTrigger value="kunde" className="text-xs py-1">KUNDE</TabsTrigger>
                  <TabsTrigger value="lieferanschr" className="text-xs py-1">LIEFER-ANSCHR.</TabsTrigger>
                  <TabsTrigger value="rechnanschrift" className="text-xs py-1">RECHN.-ANSCHRIFT</TabsTrigger>
                  <TabsTrigger value="bestellung" className="text-xs py-1">BESTELLUNG</TabsTrigger>
                </TabsList>
                <TabsList className="grid w-full grid-cols-4 h-auto mt-1">
                  <TabsTrigger value="rechnung" className="text-xs py-1">RECHNUNG/ZAHLUNGSBED.</TabsTrigger>
                  <TabsTrigger value="texte" className="text-xs py-1">TEXTE</TabsTrigger>
                  <TabsTrigger value="spediteur" className="text-xs py-1">SPEDITEUR</TabsTrigger>
                  <TabsTrigger value="lieferung" className="text-xs py-1">LIEFERUNG</TabsTrigger>
                </TabsList>

                {/* Tab-Inhalte */}
                <TabsContent value="kunde" className="mt-2 space-y-2">
                  {state.customer ? (
                    <>
                      <div className="text-sm space-y-1">
                        <div className="font-semibold">{state.customer.name}</div>
                        {state.customer.address?.street && (
                          <div>{state.customer.address.street}</div>
                        )}
                        {(state.customer.postalCode || state.customer.city) && (
                          <div>{[state.customer.postalCode, state.customer.city].filter(Boolean).join(' ')}</div>
                        )}
                        {state.customer.phone && (
                          <div className="text-muted-foreground">Tel: {state.customer.phone}</div>
                        )}
                        {state.customer.email && (
                          <div className="text-muted-foreground">E-Mail: {state.customer.email}</div>
                        )}
                        {state.customer.representative && (
                          <div className="text-muted-foreground">Ansprechpartner: {state.customer.representative}</div>
                        )}
                      </div>
                    </>
                  ) : (
                    <div className="text-sm text-muted-foreground">Kein Kunde ausgewählt</div>
                  )}
                </TabsContent>

                <TabsContent value="lieferanschr" className="mt-2 space-y-2">
                  {state.customer ? (
                    <div className="text-sm space-y-1">
                      <div className="font-semibold">Lieferanschrift</div>
                      {state.customer.address?.street ? (
                        <>
                          <div>{state.customer.address.street}</div>
                          <div>{[state.customer.address.postalCode, state.customer.address.city].filter(Boolean).join(' ')}</div>
                          {state.customer.address.phone && (
                            <div className="text-muted-foreground">Tel: {state.customer.address.phone}</div>
                          )}
                          {state.customer.address.fax && (
                            <div className="text-muted-foreground">Fax: {state.customer.address.fax}</div>
                          )}
                        </>
                      ) : (
                        <div className="text-muted-foreground">Keine Lieferanschrift hinterlegt</div>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground">Kein Kunde ausgewählt</div>
                  )}
                </TabsContent>

                <TabsContent value="rechnanschrift" className="mt-2 space-y-2">
                  {state.customer ? (
                    <div className="text-sm space-y-1">
                      <div className="font-semibold">Rechnungsanschrift</div>
                      {state.customer.address?.street ? (
                        <>
                          <div>{state.customer.address.street}</div>
                          <div>{[state.customer.address.postalCode, state.customer.address.city].filter(Boolean).join(' ')}</div>
                          {state.customer.phone && (
                            <div className="text-muted-foreground">Tel: {state.customer.phone}</div>
                          )}
                          {state.customer.email && (
                            <div className="text-muted-foreground">E-Mail: {state.customer.email}</div>
                          )}
                        </>
                      ) : (
                        <div className="text-muted-foreground">Keine Rechnungsanschrift hinterlegt</div>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground">Kein Kunde ausgewählt</div>
                  )}
                </TabsContent>

                <TabsContent value="bestellung" className="mt-2 space-y-2">
                  <div className="text-sm space-y-2">
                    {state.customer ? (
                      <>
                        {bestellungen.length > 0 ? (
                          <>
                            <div className="font-semibold">
                              Zu Bestellungen (01-{String(bestellungen.length).padStart(2, '0')})
                            </div>
                            <ul className="list-disc pl-5 space-y-1">
                              {bestellungen.map((order) => (
                                <li key={order.id} className="text-sm">
                                  Bestell-Nr: {order.bestellNr} vom {order.datum}
                                </li>
                              ))}
                            </ul>
                            <Button
                              variant="outline"
                              size="sm"
                              className="mt-2"
                              onClick={() => setShowBelegfolgeDialog(true)}
                            >
                              Positionen aus Auftrag übernehmen
                            </Button>
                          </>
                        ) : (
                          <div className="text-muted-foreground">
                            Es liegt keine Bestellung vor
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="text-muted-foreground">Kein Kunde ausgewählt</div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="rechnung" className="mt-2 space-y-2">
                  {state.customer ? (
                    <div className="text-sm space-y-1.5">
                      <div className="grid grid-cols-[140px_1fr] gap-1">
                        <span className="text-muted-foreground">Zahlungsziel:</span>
                        <span>
                          {state.customer.paymentTerms !== undefined
                            ? `${state.customer.paymentTerms} Tage netto`
                            : '—'}
                        </span>
                        <span className="text-muted-foreground">Kredit-Limit:</span>
                        <span>{state.customer.creditLimit ? `${Number(state.customer.creditLimit).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}` : '—'}</span>
                        <span className="text-muted-foreground">Debitor-Kto.:</span>
                        <span>{state.customer.debitorAccount || '—'}</span>
                        <span className="text-muted-foreground">Kunden-Nr.:</span>
                        <span>{state.customer.customerNumber || '—'}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground">Kein Kunde ausgewählt</div>
                  )}
                </TabsContent>

                <TabsContent value="texte" className="mt-2 space-y-2">
                  {state.customer ? (
                    <div className="text-sm space-y-2">
                      {(state.customer.chefanweisung || state.customer.executiveNote) ? (
                        <div>
                          <div className="font-semibold mb-1">Chefanweisung</div>
                          <div className="p-2 bg-amber-50 border border-amber-200 rounded whitespace-pre-wrap">
                            {state.customer.chefanweisung || state.customer.executiveNote}
                          </div>
                        </div>
                      ) : (
                        <div className="text-muted-foreground">Keine Kunden-Notizen vorhanden</div>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground">Kein Kunde ausgewählt</div>
                  )}
                </TabsContent>

                <TabsContent value="spediteur" className="mt-2 space-y-2">
                  {state.customer ? (
                    <div className="text-sm space-y-1.5">
                      <div className="grid grid-cols-[140px_1fr] gap-1">
                        <span className="text-muted-foreground">Spediteur:</span>
                        <span>—</span>
                        <span className="text-muted-foreground">Lieferadresse:</span>
                        <span>
                          {[
                            state.customer.address?.street,
                            state.customer.address?.postalCode,
                            state.customer.address?.city,
                          ].filter(Boolean).join(', ') || state.customer.address?.city || '—'}
                        </span>
                        <span className="text-muted-foreground">Telefon:</span>
                        <span>{state.customer.address?.phone || state.customer.phone || '—'}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground">Kein Kunde ausgewählt</div>
                  )}
                </TabsContent>

                <TabsContent value="lieferung" className="mt-2 space-y-2">
                  <div className="text-sm space-y-2">
                    <div className="font-semibold">Lieferdaten</div>
                    <div>Liefer-Datum: {state.lieferDatum}</div>
                    <div>Uhrzeit: {state.uhrzeit}</div>
                    {state.selbstabholung && (
                      <div className="text-muted-foreground">Selbstabholung</div>
                    )}
                    {state.lkwNr > 0 && (
                      <div className="text-muted-foreground">Lkw-Nr.: {state.lkwNr}</div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>
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
                  <div className="text-muted-foreground">Kredit-Limit: {state.customer.creditLimit || '-'}</div>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Kredit-Limit:</Label>
                <Input
                  value={state.customer?.creditLimit || ''}
                  readOnly
                  className="flex-1 h-8"
                />
              </div>
              <div className="flex items-center gap-2 pl-32">
                <a
                  href="#"
                  className="text-sm text-blue-600 hover:text-blue-800 underline"
                  onClick={(e) => {
                    e.preventDefault()
                    if (state.customer) {
                      setShowInformationDialog(true)
                    } else {
                      push('Bitte wählen Sie zuerst einen Kunden aus')
                    }
                  }}
                >
                  Information
                </a>
              </div>
            </div>
          </div>
        </Card>

        {/* Positionen-Grid */}
        <Card className="mb-4 p-4">
          <h2 className="mb-2 font-semibold text-sm">Positionen</h2>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16">Pos.-Nr.</TableHead>
                  <TableHead className="w-24">Artikel-Nr.</TableHead>
                  <TableHead className="w-32">Bezeichn.</TableHead>
                  <TableHead className="w-32">Bezeichn...</TableHead>
                  <TableHead className="w-20">Menge</TableHead>
                  <TableHead className="w-20">Einheit</TableHead>
                  <TableHead className="w-24">Listenpreis</TableHead>
                  <TableHead className="w-20">Rabatt</TableHead>
                  <TableHead className="w-20">Art</TableHead>
                  <TableHead className="w-24">Netto-Pr.</TableHead>
                  <TableHead className="w-24">Netto-Be.</TableHead>
                  <TableHead className="w-20">Niederlas.</TableHead>
                  <TableHead className="w-20">Lagerhalle</TableHead>
                  <TableHead className="w-20">Lagerfach</TableHead>
                  <TableHead className="w-20">Chargen...</TableHead>
                  <TableHead className="w-20">Serien-Nr.</TableHead>
                  <TableHead className="w-20">Gef.-Pun.</TableHead>
                  <TableHead className="w-20">Na.-Bio.</TableHead>
                  <TableHead className="w-20">Muster-Nr.</TableHead>
                  <TableHead className="w-20">Strecke-...</TableHead>
                  <TableHead className="w-20">Zus. Bele...</TableHead>
                  <TableHead className="w-20">Anerken...</TableHead>
                  <TableHead className="w-20">Erlöskonto</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {state.positionen.map((pos, idx) => (
                  <TableRow
                    key={idx}
                    className={state.aktivePositionIndex === idx ? 'bg-green-100' : ''}
                    onClick={() => selectPositionForEdit(idx)}
                  >
                    <TableCell>{pos.posNr}</TableCell>
                    <TableCell>{pos.artikelNr}</TableCell>
                    <TableCell>{pos.bezeichnung}</TableCell>
                    <TableCell>{pos.bezeichnung2}</TableCell>
                    <TableCell>{pos.menge}</TableCell>
                    <TableCell>{pos.einheit}</TableCell>
                    <TableCell>{pos.listenpreis.toFixed(2)}</TableCell>
                    <TableCell>{pos.rabatt}%</TableCell>
                    <TableCell>{pos.art}</TableCell>
                    <TableCell>{pos.nettoPreis.toFixed(2)}</TableCell>
                    <TableCell>{pos.nettoBetrag.toFixed(2)}</TableCell>
                    <TableCell>{pos.niederlassung}</TableCell>
                    <TableCell>{pos.lagerhalle}</TableCell>
                    <TableCell>{pos.lagerfach}</TableCell>
                    <TableCell>{pos.charge}</TableCell>
                    <TableCell>{pos.serienNr}</TableCell>
                    <TableCell>{pos.gefPunkt}</TableCell>
                    <TableCell>{pos.naBio}</TableCell>
                    <TableCell>{pos.musterNr}</TableCell>
                    <TableCell>{pos.strecke}</TableCell>
                    <TableCell>{pos.zusBeleg}</TableCell>
                    <TableCell>{pos.anerken}</TableCell>
                    <TableCell>{pos.erloskonto}</TableCell>
                    <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-0.5">
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          title="Hoch"
                          onClick={() => handleMovePositionUp(idx)}
                          disabled={state.status !== 'draft' || idx <= 0}
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
                          disabled={state.status !== 'draft' || idx >= state.positionen.length - 1}
                        >
                          <ChevronDown className="h-4 w-4" />
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 text-red-600 hover:text-red-700"
                          title="Position löschen"
                          onClick={() => handleDeletePosition(idx)}
                          disabled={state.status !== 'draft'}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>

        {/* Positions-Details */}
        <Card className="mb-4 p-4">
          <h2 className="mb-2 font-semibold text-sm">Positions-Details</h2>
          <div className="grid grid-cols-6 gap-4">
            <div className="space-y-1">
              <Label className="text-xs">Pos.-Nr.:</Label>
              <Input value={currentPosition.posNr} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Artikel-Nr.:</Label>
              <div className="flex gap-1">
                <Input
                  value={currentPosition.artikelNr}
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
            <div className="space-y-1 col-span-2">
              <Label className="text-xs">Artikel-Bezeichn:</Label>
              <Input value={currentPosition.artikelBezeichnung} readOnly className="h-8" />
              <Input value={currentPosition.artikelBezeichnung2} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Menge/Gebinde:</Label>
              <Input
                type="number"
                value={currentPosition.mengeGebinde}
                onChange={(e) =>
                  setCurrentPosition((prev) => ({
                    ...prev,
                    mengeGebinde: Number(e.target.value),
                  }))
                }
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Einheit:</Label>
              <Input value={currentPosition.einheit} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Listenpreis:</Label>
              <Input
                type="number"
                step="0.01"
                value={currentPosition.listenpreis}
                onChange={(e) =>
                  setCurrentPosition((prev) => ({
                    ...prev,
                    listenpreis: Number(e.target.value),
                  }))
                }
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Rabatt:</Label>
              <Input
                type="number"
                value={currentPosition.rabatt}
                onChange={(e) =>
                  setCurrentPosition((prev) => ({
                    ...prev,
                    rabatt: Number(e.target.value),
                  }))
                }
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Einh.-Preis:</Label>
              <Input value={currentPosition.einhPreis.toFixed(2)} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Betrag:</Label>
              <Input value={currentPosition.betrag.toFixed(2)} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">MWSt. %:</Label>
              <Input
                type="number"
                value={currentPosition.mwstProzent}
                onChange={(e) =>
                  setCurrentPosition((prev) => ({
                    ...prev,
                    mwstProzent: Number(e.target.value),
                  }))
                }
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">verfügbar:</Label>
              <Input value={`${currentPosition.verfuegbar} ${currentPosition.einheit}`} readOnly className="h-8" />
            </div>
            <div className="flex items-end gap-2">
              <Button variant="outline" size="sm" className="h-8" onClick={() => setShowPositionPopUpDialog(true)} title="Zusatzinfos zur Position">
                PopUp
              </Button>
              <Button variant="outline" size="sm" className="h-8" onClick={() => setShowPositionDetailsDialog(true)} title="Details zur Position">
                Details
              </Button>
              <div className="flex items-center gap-1">
                <Checkbox
                  checked={currentPosition.fremdware}
                  onCheckedChange={(checked) =>
                    setCurrentPosition((prev) => ({ ...prev, fremdware: checked === true }))
                  }
                />
                <Label className="text-xs">Fremdware</Label>
              </div>
              <div className="flex items-center gap-1">
                <Checkbox
                  checked={currentPosition.skontierf}
                  onCheckedChange={(checked) =>
                    setCurrentPosition((prev) => ({ ...prev, skontierf: checked === true }))
                  }
                />
                <Label className="text-xs">skontierf.</Label>
              </div>
              <ShortcutHintButton shortcut="Strg+F3">
                <Button onClick={handlePositionOK} className="h-8 gap-1">
                  <Check className="h-4 w-4" />
                  Zeile OK
                </Button>
              </ShortcutHintButton>
            </div>
          </div>
        </Card>

        {/* PSM-Dienstleistung: Schlag-Auswahl für Feldbuch */}
        {schlaege.length > 0 && (
          <Card className="mb-4 p-4 border-amber-200 bg-amber-50">
            <h2 className="mb-2 font-semibold text-sm text-amber-800">PSM-Dienstleistung → Feldbuch</h2>
            <div className="grid grid-cols-4 gap-4">
              <div className="space-y-1 col-span-2">
                <Label className="text-xs">Schlag (Feldbuch):</Label>
                <Select value={psmSchlagId} onValueChange={setPsmSchlagId}>
                  <SelectTrigger className="h-8">
                    <SelectValue placeholder="Schlag wählen (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Kein Schlag</SelectItem>
                    {schlaege.map(s => (
                      <SelectItem key={s.id} value={s.id}>{s.name} ({s.flaeche} ha)</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Fläche (ha):</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={psmFlaeche}
                  onChange={e => setPsmFlaeche(e.target.value)}
                  placeholder="z.B. 12.5"
                  className="h-8"
                />
              </div>
              <div className="flex items-end">
                <p className="text-xs text-amber-700">
                  Nach dem Drucken wird automatisch ein Feldbuch-Eintrag erstellt.
                </p>
              </div>
            </div>
          </Card>
        )}

        {/* Summen */}
        <Card className="mb-4 p-4">
          <div className="grid grid-cols-7 gap-4">
            <div className="space-y-1">
              <Label className="text-xs">Gewicht:</Label>
              <Input value={`${summen.gewicht.toFixed(2)} kg`} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Gef.-Pun.:</Label>
              <Input 
                value={summen.gefahrgutPunkte.toFixed(0)} 
                readOnly 
                className={`h-8 ${summen.gefahrgutPunkte > 1000 ? 'bg-red-100 border-red-500' : summen.gefahrgutPunkte > 800 ? 'bg-yellow-100 border-yellow-500' : ''}`}
                title={summen.gefahrgutPunkte > 1000 ? 'Warnung: Maximal 1000 Gefahrgut-Punkte erlaubt!' : ''}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Netto:</Label>
              <Input value={summen.netto.toFixed(2)} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">MWSt.:</Label>
              <Input value={summen.mwst.toFixed(2)} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Brutto:</Label>
              <Input value={summen.brutto.toFixed(2)} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Gesamt:</Label>
              <Input value={summen.gesamt.toFixed(2)} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">EUR</Label>
              <Input value="EUR" readOnly className="h-8" />
            </div>
          </div>
        </Card>
      </div>

      {/* Bottom-Toolbar */}
      <div className="border-t bg-white px-4 py-2 flex items-center justify-between">
        <div className="flex gap-2">
          <Button onClick={() => setShowPrintDialog(true)} variant="outline" size="sm" className="gap-2">
            <Printer className="h-4 w-4" />
            LS drucken
          </Button>
          <Button variant="outline" size="sm" className="gap-2" onClick={() => setShowAttachmentDialog(true)}>
            <FileText className="h-4 w-4" />
            Unterlagen
          </Button>
          <Button variant="outline" size="sm" className="gap-2" onClick={() => setShowAttachmentDialog(true)}>
            <Folder className="h-4 w-4" />
            Dateien
          </Button>
          <Button variant="outline" size="sm" className="gap-2" onClick={() => { const q = state.customer?.id ? `?customerId=${state.customer.id}` : ''; navigate(`/contracts${q}`); push('Kontrakte geöffnet.'); }} title="Kontrakte anzeigen/verknüpfen">
            <FileCheck className="h-4 w-4" />
            Kontrakte
          </Button>
          <Button variant="outline" size="sm" className="gap-2" onClick={() => { navigate('/waage'); push('Waagenmodul geöffnet. Connect-Einstellungen dort konfigurierbar.'); }} title="Schnittstellen (z. B. Waage)">
            <LinkIcon className="h-4 w-4" />
            Connect Anwendungen (Schnittstelle zB zum Waagenmodul)
          </Button>
          <Button variant="outline" size="sm" className="gap-2" onClick={() => void handleCreateInvoice()}>
            <Receipt className="h-4 w-4" />
            Sofort-Rechnung
          </Button>
          <Button variant="outline" size="sm" className="gap-2 text-red-600" onClick={() => setShowDeleteDialog(true)}>
            <Trash2 className="h-4 w-4" />
            LS löschen
          </Button>
        </div>
        <div className="flex gap-2">
          <ShortcutHintButton shortcut="Strg+F4">
            <Button onClick={handleSave} size="sm" className="gap-2">
              <Save className="h-4 w-4" />
              Speichern
            </Button>
          </ShortcutHintButton>
          <ShortcutHintButton shortcut="Strg+F7">
            <Button variant="outline" onClick={() => navigate('/verkauf')} size="sm">
              Schließen
            </Button>
          </ShortcutHintButton>
        </div>
      </div>

      {/* Dialoge */}
      {(showCustomerDialog || showArticleDialog || showPrintDialog) && (
        <LazyDialogBoundary>
          <>
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
            <LieferscheinDruckDialog
              open={showPrintDialog}
              onClose={() => setShowPrintDialog(false)}
              onConfirm={handlePrint}
            />
          </>
        </LazyDialogBoundary>
      )}
      {/* Löschen-Bestätigung */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Lieferschein löschen?</DialogTitle>
          </DialogHeader>
          <div className="py-2 text-sm">
            {state.id
              ? <>Lieferschein <strong>{state.lieferscheinNr}</strong> wird unwiderruflich gelöscht. Fortfahren?</>
              : 'Das Formular wird geleert. Nicht gespeicherte Daten gehen verloren.'}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>Abbrechen</Button>
            <Button variant="destructive" onClick={() => void handleDelete()}>Löschen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <DmsAnhangDialog
        open={showAttachmentDialog}
        onClose={() => setShowAttachmentDialog(false)}
        businessObjectType="delivery_note"
        businessObjectId={state.id}
        title="UNTERLAGEN / DATEIEN — LIEFERSCHEIN"
      />

      {/* Lieferschein suchen */}
      <Dialog open={showLieferscheinSuchenDialog} onOpenChange={setShowLieferscheinSuchenDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>Lieferschein suchen</DialogTitle>
          </DialogHeader>
          <div className="overflow-auto flex-1 min-h-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Liefersch.-Nr.</TableHead>
                  <TableHead>Kunde-ID</TableHead>
                  <TableHead>Lieferdatum</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {lsList.map((row) => (
                  <TableRow
                    key={row.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => {
                      navigate(`/verkauf/lieferschein-erfassung/${row.id}`)
                      setShowLieferscheinSuchenDialog(false)
                    }}
                  >
                    <TableCell>{row.delivery_note_number}</TableCell>
                    <TableCell>{row.customer_id ?? '—'}</TableCell>
                    <TableCell>{row.delivery_date ?? '—'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLieferscheinSuchenDialog(false)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Niederlassung auswählen */}
      <Dialog open={showNiederlassungDialog} onOpenChange={setShowNiederlassungDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Niederlassung auswählen</DialogTitle>
          </DialogHeader>
          <div className="space-y-2 max-h-60 overflow-auto">
            {branchesList.map((b) => (
              <div
                key={b.id}
                className="flex items-center justify-between p-2 rounded border cursor-pointer hover:bg-muted/50"
                onClick={() => {
                  setState((prev) => ({ ...prev, niederlassung: b.branch_number }))
                  setShowNiederlassungDialog(false)
                }}
              >
                <span className="font-medium">{b.branch_number}</span>
                <span className="text-sm text-muted-foreground">{b.name}</span>
              </div>
            ))}
            {branchesList.length === 0 && (
              <p className="text-sm text-muted-foreground">Keine Niederlassungen geladen. Bitte manuell eintragen.</p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNiederlassungDialog(false)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Vertreter eingeben */}
      <Dialog open={showVertreterDialog} onOpenChange={setShowVertreterDialog}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Vertreter</DialogTitle>
          </DialogHeader>
          <div className="py-2">
            <Label className="text-sm">Vertreter</Label>
            <Input
              value={vertreterInput}
              onChange={(e) => setVertreterInput(e.target.value)}
              className="mt-1"
              placeholder="Name oder Nr."
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowVertreterDialog(false)}>Abbrechen</Button>
            <Button onClick={handleVertreterConfirm}>Übernehmen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {(showBelegfolgeDialog || showAttestationDialog) && (
        <LazyDialogBoundary>
          <>
            {state.customer && (
              <BelegfolgePositionenDialog
                open={showBelegfolgeDialog}
                onClose={() => setShowBelegfolgeDialog(false)}
                onConfirm={handleBelegfolgePositionen}
                customerId={state.customer.id}
                targetDocType="lieferschein"
              />
            )}
            <AttestationDialog
              open={showAttestationDialog}
              onClose={() => {
                setShowAttestationDialog(false)
                setPendingAction(null)
              }}
              onConfirm={handleAttestationConfirm}
              action={pendingAction || 'print'}
              entityType="Lieferschein"
              entityNumber={state.lieferscheinNr}
            />
          </>
        </LazyDialogBoundary>
      )}

      {/* Information Dialog für Chefanweisung */}
      <Dialog open={showInformationDialog} onOpenChange={setShowInformationDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Kunden-Information</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {state.customer && (
              <>
                <div>
                  <h3 className="font-semibold mb-2">{state.customer.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    Kunden-Nr.: {state.customer.customerNumber}
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Chefanweisung</h4>
                  {state.customer.chefanweisung || state.customer.executiveNote ? (
                    <div className="p-3 bg-amber-50 border border-amber-200 rounded text-sm whitespace-pre-wrap">
                      {state.customer.chefanweisung || state.customer.executiveNote}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground italic">
                      Keine Chefanweisung für diesen Kunden hinterlegt.
                    </p>
                  )}
                </div>
              </>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowInformationDialog(false)}>
              Schließen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showPositionPopUpDialog} onOpenChange={setShowPositionPopUpDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Zusatzinfos Position</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-2 text-sm py-2">
            <span className="text-muted-foreground">Pos.-Nr.:</span><span>{currentPosition.posNr}</span>
            <span className="text-muted-foreground">Artikel:</span><span>{currentPosition.artikelNr}</span>
            <span className="text-muted-foreground">Bezeichnung:</span><span className="col-span-2">{currentPosition.artikelBezeichnung || '–'}</span>
            <span className="text-muted-foreground">Menge:</span><span>{currentPosition.mengeGebinde} {currentPosition.einheit}</span>
            <span className="text-muted-foreground">Listenpreis:</span><span>{currentPosition.listenpreis.toFixed(2)} â‚¬</span>
            <span className="text-muted-foreground">Rabatt:</span><span>{currentPosition.rabatt} %</span>
            <span className="text-muted-foreground">Verfügbar:</span><span>{currentPosition.verfuegbar} {currentPosition.einheit}</span>
            <span className="text-muted-foreground">Kontrakt-Nr.:</span><span>{currentPosition.kontraktNr || '–'}</span>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPositionPopUpDialog(false)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showPositionDetailsDialog} onOpenChange={setShowPositionDetailsDialog}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Positions-Details (erweiterte Felder)</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-2 text-sm py-2">
            <span className="text-muted-foreground">Pos.-Nr.:</span><span>{currentPosition.posNr}</span>
            <span className="text-muted-foreground">Artikel-ID:</span><span>{currentPosition.artikelId || '–'}</span>
            <span className="text-muted-foreground">Artikel:</span><span>{currentPosition.artikelNr}</span>
            <span className="text-muted-foreground">Bezeichnung 2:</span><span>{currentPosition.artikelBezeichnung2 || '–'}</span>
            <span className="text-muted-foreground">Menge (Gebinde):</span><span>{currentPosition.mengeGebinde}</span>
            <span className="text-muted-foreground">Einheit:</span><span>{currentPosition.einheit}</span>
            <span className="text-muted-foreground">Listenpreis:</span><span>{currentPosition.listenpreis.toFixed(2)} â‚¬</span>
            <span className="text-muted-foreground">Einh.-Preis:</span><span>{currentPosition.einhPreis.toFixed(2)} â‚¬</span>
            <span className="text-muted-foreground">Rabatt:</span><span>{currentPosition.rabatt} %</span>
            <span className="text-muted-foreground">Betrag (Netto):</span><span>{currentPosition.betrag.toFixed(2)} â‚¬</span>
            <span className="text-muted-foreground">MWSt.:</span><span>{currentPosition.mwstProzent} %</span>
            <span className="text-muted-foreground">Gewicht/Einh.:</span><span>{currentPosition.artikelGewicht} kg</span>
            <span className="text-muted-foreground">Gefahrgut-Pkte.:</span><span>{currentPosition.artikelGefahrgutPunkte}</span>
            <span className="text-muted-foreground">Skontierf.:</span><span>{currentPosition.skontierf ? 'Ja' : 'Nein'}</span>
            <span className="text-muted-foreground">Fremdware:</span><span>{currentPosition.fremdware ? 'Ja' : 'Nein'}</span>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPositionDetailsDialog(false)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

