/**
 * Lieferschein-Erfassung (Verkauf)
 * 1:1 Nachbau der zvoove Lieferschein-Erfassungsmaske
 */

import { useState, useEffect, useMemo } from 'react'
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
import { CustomerSelectionDialog, type Customer } from '@/components/sales/CustomerSelectionDialog'
import { ArtikelSuchDialog } from '@/components/sales/ArtikelSuchDialog'
import { LieferscheinDruckDialog, type PrintOptions } from '@/components/sales/LieferscheinDruckDialog'
import { DmsAnhangDialog } from '@/components/dms/DmsAnhangDialog'
import { AttestationDialog } from '@/components/sales/AttestationDialog'
import { apiClient } from '@/lib/axios'
import { useAuth } from '@/hooks/useAuth'
import { useGlobalShortcuts, globalShortcutManager } from '@/lib/shortcuts/global-shortcuts'
import { ShortcutHintButton } from '@/components/shortcuts/ShortcutHelpPanel'
import { ChevronLeft, ChevronRight, MoreHorizontal, Check, Printer, Save, X, FileText, Folder, FileCheck, Link as LinkIcon, Receipt, Trash2 } from 'lucide-react'

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
            // eslint-disable-next-line no-console
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
                // eslint-disable-next-line no-console
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
            // eslint-disable-next-line no-console
            console.warn('Fehler beim Laden der Branch:', error)
          }
        }

        setState({
          id: response.id,
          lieferscheinNr: response.delivery_note_number, // Vom Backend vergeben
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
        // eslint-disable-next-line no-console
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
  const [showAttestationDialog, setShowAttestationDialog] = useState(false)
  const [pendingAction, setPendingAction] = useState<'print' | 'modify' | null>(null)
  const [pendingPrintOptions, setPendingPrintOptions] = useState<PrintOptions | null>(null)
  const [showInformationDialog, setShowInformationDialog] = useState(false)
  const [customerTab, setCustomerTab] = useState<'kunde' | 'lieferanschr' | 'rechnanschrift' | 'bestellung' | 'rechnung' | 'texte' | 'spediteur' | 'lieferung'>('kunde')
  
  // State für Bestellungen
  const [bestellungen, setBestellungen] = useState<Array<{ id: string; bestellNr: string; datum: string }>>([])
  
  // Cache für Branch-Mapping (niederlassung -> branch_id)
  const [branchCache, setBranchCache] = useState<Map<number, string>>(new Map())

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
    
    // Lade Bestellungen für den ausgewählten Kunden vom Backend
    try {
      const response = await apiClient.get<any>('/api/v1/sales/orders', {
        params: {
          customer_id: customer.id,
          limit: 10, // Maximal 10 Bestellungen anzeigen
        },
      })
      
      // Handle PaginatedResponse or direct array
      const orders = response.items || response || []
      setBestellungen(
        orders.map((o: any) => ({
          id: o.id,
          bestellNr: o.order_number || o.orderNumber || '',
          datum: o.created_at 
            ? new Date(o.created_at).toLocaleDateString('de-DE')
            : new Date().toLocaleDateString('de-DE'),
        }))
      )
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn('Fehler beim Laden der Bestellungen:', error)
      setBestellungen([]) // Fallback: Leere Liste
    }
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
          // eslint-disable-next-line no-console
          console.warn('Fehler beim Abrufen des Listenpreises aus Preisliste:', error)
          // Fallback: Verwende bereits gesetzten sales_price
        }
      })()
    }
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
    const neueGesamtGefahrgutPunkte = aktuelleGefahrgutPunkte + gesamtGefahrgutPunkte
    
    if (neueGesamtGefahrgutPunkte > 1000) {
      push(`Fehler: Die maximale Anzahl von 1000 Gefahrgut-Punkten pro Lieferung würde überschritten werden. Aktuell: ${aktuelleGefahrgutPunkte.toFixed(0)}, zusätzlich: ${gesamtGefahrgutPunkte.toFixed(0)}, Gesamt: ${neueGesamtGefahrgutPunkte.toFixed(0)}`)
      return
    }

    const position: Position = {
      posNr: currentPosition.posNr,
      artikelNr: currentPosition.artikelNr,
      artikelId: currentPosition.artikelId, // Artikel-ID für Backend-Mapping
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
      gefPunkt: currentPosition.artikelGefahrgutPunkte > 0 ? currentPosition.artikelGefahrgutPunkte.toString() : '', // Als String für Anzeige
      gefahrgutPunkte: currentPosition.artikelGefahrgutPunkte, // Numerisch pro Einheit
      gesamtGefahrgutPunkte, // Gesamt-Gefahrgut-Punkte (gefahrgutPunkte × menge)
      naBio: '',
      musterNr: '',
      strecke: '',
      zusBeleg: '',
      anerken: '',
      erloskonto: '',
      mwstProzent: currentPosition.mwstProzent,
      gewicht: currentPosition.artikelGewicht, // Gewicht pro Einheit
      gesamtGewicht, // Gesamtgewicht (gewicht × menge)
      kontraktNr: currentPosition.kontraktNr, // Vertragsnummer
      skontierf: currentPosition.skontierf, // Skontierfähig
      fremdware: currentPosition.fremdware, // Fremdware
    }

    setState((prev) => ({
      ...prev,
      positionen: [...prev.positionen, position],
      aktivePositionIndex: prev.positionen.length,
    }))

    // Nächste Position vorbereiten
    setCurrentPosition({
      posNr: currentPosition.posNr + 10,
      artikelNr: '',
      artikelId: null, // Reset Artikel-ID
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

      const payload = {
        customer_id: state.customer.id,
        branch_id: null, // TODO: Map niederlassung to branch_id
        sales_rep_id: null, // TODO: Map vertreter to sales_rep_id
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

      const response = await apiClient.post<DeliveryNoteResponse>('/api/v1/sales/delivery-notes', payload)
      setState((prev) => ({
        ...prev,
        id: response.id, // UUID vom Backend
        lieferscheinNr: response.delivery_note_number,
        fakturiertRechnNr: response.invoice_number || '', // Vom Backend gesetzt nach Fakturierung
      }))
      push('Lieferschein erfolgreich gespeichert')
      return response.id // Return ID for use in executePrint
    } catch (error: any) {
      // eslint-disable-next-line no-console
      console.error('Save error:', error)
      push(`Fehler beim Speichern: ${error.response?.data?.detail || error.message}`)
      return null // Return null on error
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
      // TODO: Handle modify action
      push('Korrektur noch nicht implementiert')
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

      push('Lieferschein erfolgreich gedruckt und gebucht')
      setShowPrintDialog(false)

      // Maske auf neuen leeren Lieferschein zurücksetzen
      setState({
        id: null,
        lieferscheinNr: generateLieferscheinNr(),
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
      // eslint-disable-next-line no-console
      console.error('Print error:', error)
      push(`Fehler beim Drucken: ${error.response?.data?.detail || error.message}`)
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
  useGlobalShortcuts({
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
      // TODO: Implementieren
      push('Löschen-Funktion noch nicht implementiert')
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
            // eslint-disable-next-line no-console
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
                // eslint-disable-next-line no-console
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
        // eslint-disable-next-line no-console
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
        
        if (!response || !response.positionen || response.positionen.length === 0) {
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
                // eslint-disable-next-line no-console
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
        // eslint-disable-next-line no-console
        console.error('Fehler beim Laden der Positionen:', error)
        push(`Fehler: ${error.response?.data?.detail || error.message}`)
      }
    },
    'create-invoice': () => {
      // TODO: Implementieren
      push('Sofort-Rechnung noch nicht implementiert')
    },
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

      <div className="flex-1 overflow-auto p-4">
        {/* Header-Bereich (3 Spalten) */}
        <Card className="mb-4 p-4">
          <div className="grid grid-cols-3 gap-4">
            {/* Linke Spalte */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Liefersch.-Nr.:</Label>
                <Input value={state.lieferscheinNr} readOnly className="flex-1 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
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
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Vertreter:</Label>
                <Input value={state.vertreter} readOnly className="flex-1 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
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
                              onClick={async () => {
                                // TODO: Implementiere "Alle Bestellpositionen übernehmen"
                                // Dies erfordert eine API zum Laden der Bestellpositionen
                                push('Alle Bestellpositionen übernehmen - noch nicht vollständig implementiert')
                              }}
                            >
                              Alle Bestellpositionen übernehmen
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
                    <div className="text-sm space-y-1">
                      <div className="font-semibold">Zahlungsbedingungen</div>
                      {state.customer.creditLimit && (
                        <div>Kredit-Limit: {state.customer.creditLimit}</div>
                      )}
                      <div className="text-muted-foreground">Weitere Zahlungsbedingungen werden hier angezeigt</div>
                      {/* TODO: Zahlungsbedingungen vom Backend laden */}
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground">Kein Kunde ausgewählt</div>
                  )}
                </TabsContent>

                <TabsContent value="texte" className="mt-2 space-y-2">
                  <div className="text-sm space-y-2">
                    <div className="text-muted-foreground">Kunden-Texte und Notizen werden hier angezeigt</div>
                    {/* TODO: Texte vom Backend laden */}
                  </div>
                </TabsContent>

                <TabsContent value="spediteur" className="mt-2 space-y-2">
                  <div className="text-sm space-y-2">
                    <div className="text-muted-foreground">Spediteur-Daten werden hier angezeigt</div>
                    {/* TODO: Spediteur-Daten vom Backend laden */}
                  </div>
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
              <Button variant="outline" size="sm" className="h-8">
                PopUp
              </Button>
              <Button variant="outline" size="sm" className="h-8">
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
          <Button variant="outline" size="sm" className="gap-2">
            <FileCheck className="h-4 w-4" />
            Kontrakte
          </Button>
          <Button variant="outline" size="sm" className="gap-2">
            <LinkIcon className="h-4 w-4" />
            Connect Anwendungen (Schnittstelle zB zum Waagenmodul)
          </Button>
          <Button variant="outline" size="sm" className="gap-2">
            <Receipt className="h-4 w-4" />
            Sofort-Rechnung
          </Button>
          <Button variant="outline" size="sm" className="gap-2 text-red-600">
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
      <DmsAnhangDialog
        open={showAttachmentDialog}
        onClose={() => setShowAttachmentDialog(false)}
        businessObjectType="delivery_note"
        businessObjectId={state.id}
        title="UNTERLAGEN / DATEIEN — LIEFERSCHEIN"
      />
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
    </div>
  )
}

