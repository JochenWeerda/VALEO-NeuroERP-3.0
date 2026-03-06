/**
 * Auftrags-Erfassung (Verkauf)
 * 1:1 Struktur nach Lieferschein-Erfassung — Gewohnheits-Prinzip
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
import { BelegfolgePositionenDialog, type BelegfolgePosition } from '@/components/sales/BelegfolgePositionenDialog'
import { useAuftraege, type Auftrag } from '@/lib/api/sales'
import { apiClient } from '@/lib/axios'
import { useAuth } from '@/hooks/useAuth'
import { globalShortcutManager } from '@/lib/shortcuts/global-shortcuts'
import { useGlobalShortcutsWithVoice } from '@/features/ki-usability'
import { ShortcutHintButton } from '@/components/shortcuts/ShortcutHelpPanel'
import {
  ChevronLeft, ChevronRight, ChevronUp, ChevronDown, MoreHorizontal, Check, Printer, Save,
  FileText, Folder, FileCheck, Link as LinkIcon, Receipt, Trash2, Search,
} from 'lucide-react'

// â”€â”€ API Response Type â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

type AuftragResponse = {
  id: string
  order_number: string
  customer_id: string | null
  subject: string | null
  description: string | null
  total_amount: number
  currency: string
  status: string
  contact_person: string | null
  delivery_date: string | null
  delivery_address: string | null
  shipping_method: string | null
  payment_terms: string | null
  created_at: string
  updated_at: string
  items: Array<{
    id: string
    article_number: string
    description: string
    quantity: number
    unit_price: number
    discount_percent: number
  }>
}

// â”€â”€ Types â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

export type Position = {
  posNr: number
  artikelNr: string
  artikelId: string | null
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
  gefPunkt: string
  gefahrgutPunkte: number
  gesamtGefahrgutPunkte: number
  naBio: string
  musterNr: string
  strecke: string
  zusBeleg: string
  anerken: string
  erloskonto: string
  mwstProzent: number
  gewicht: number
  gesamtGewicht: number
  kontraktNr: string
  skontierf: boolean
  fremdware: boolean
  ekPreis: number
}

type AuftragState = {
  id: string | null
  auftragNr: string
  niederlassung: number
  vertreter: string
  bediener: string
  auftragDatum: string
  uhrzeit: string
  liefertermin: string
  kostenstelle: number
  versandart: string
  angebotNrBezug: string
  statusGedruckt: boolean
  statusBestaetigt: boolean
  lieferscheinNr: string   // readonly — wird nach LS-Erstellung gesetzt
  selbstabholung: boolean
  pauschalAuftrag: boolean
  betreff: string
  notizen: string
  customer: Customer | null
  positionen: Position[]
  aktivePositionIndex: number | null
}

type CurrentPositionDetails = {
  posNr: number
  artikelNr: string
  artikelId: string | null
  artikelBezeichnung: string
  artikelBezeichnung2: string
  mengeGebinde: number
  einheit: string
  listenpreis: number
  rabatt: number
  einhPreis: number
  betrag: number
  ekPreis: number
  mwstProzent: number
  verfuegbar: number
  kontraktNr: string
  skontierf: boolean
  fremdware: boolean
  artikelGewicht: number
  artikelGefahrgutPunkte: number
}

type Angebot = {
  id: string
  angebotNr: string
  datum: string
}

// â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

function generateAuftragNr(): string {
  const year = new Date().getFullYear()
  const random = Math.floor(Math.random() * 100000)
  return `AU${year}-${String(random).padStart(5, '0')}`
}

function formatDateForInput(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function emptyCurrentPosition(posNr: number): CurrentPositionDetails {
  return {
    posNr, artikelNr: '', artikelId: null, artikelBezeichnung: '', artikelBezeichnung2: '',
    mengeGebinde: 0, einheit: '', listenpreis: 0, rabatt: 0, einhPreis: 0,
    betrag: 0, ekPreis: 0, mwstProzent: 19, verfuegbar: 0, kontraktNr: '',
    skontierf: false, fremdware: false, artikelGewicht: 0, artikelGefahrgutPunkte: 0,
  }
}

function mapResponseItemsToPositionen(items: AuftragResponse['items']): Position[] {
  return items.map((item, idx) => {
    const nettoPreis = item.unit_price * (1 - item.discount_percent / 100)
    return {
      posNr: (idx + 1) * 10,
      artikelNr: item.article_number,
      artikelId: null,
      bezeichnung: item.description,
      bezeichnung2: '',
      menge: item.quantity,
      einheit: 'Stk',
      listenpreis: item.unit_price,
      rabatt: item.discount_percent,
      art: '',
      nettoPreis,
      nettoBetrag: nettoPreis * item.quantity,
      niederlassung: '',
      lagerhalle: '', lagerfach: '', charge: '', serienNr: '', gefPunkt: '',
      gefahrgutPunkte: 0, gesamtGefahrgutPunkte: 0,
      naBio: '', musterNr: '', strecke: '', zusBeleg: '', anerken: '', erloskonto: '',
      mwstProzent: 19,
      gewicht: 0, gesamtGewicht: 0,
      kontraktNr: '', skontierf: false, fremdware: false, ekPreis: 0,
    }
  })
}

// â”€â”€ Component â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

export default function SalesOrderEditorPage(): JSX.Element {
  const navigate = useNavigate()
  const { id: routeId } = useParams<{ id?: string }>()
  const { push } = useToast()
  const { user } = useAuth()

  const getUserShortName = (): string => {
    if (!user) return 'SYS'
    const name = user.name?.split(' ').map((n) => n[0]).join('').toUpperCase() ||
      user.sub?.substring(0, 2).toUpperCase() || 'SYS'
    return name.length > 2 ? name.substring(0, 2) : name
  }

  // â”€â”€ Haupt-State â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  const [state, setState] = useState<AuftragState>({
    id: null,
    auftragNr: generateAuftragNr(),
    niederlassung: 0,
    vertreter: '',
    bediener: getUserShortName(),
    auftragDatum: formatDateForInput(new Date()),
    uhrzeit: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
    liefertermin: '',
    kostenstelle: 0,
    versandart: '',
    angebotNrBezug: '',
    statusGedruckt: false,
    statusBestaetigt: false,
    lieferscheinNr: '',
    selbstabholung: false,
    pauschalAuftrag: false,
    betreff: '',
    notizen: '',
    customer: null,
    positionen: [],
    aktivePositionIndex: null,
  })

  const [currentPosition, setCurrentPosition] = useState<CurrentPositionDetails>(
    () => emptyCurrentPosition(10),
  )
  const [customerTab, setCustomerTab] = useState<string>('kunde')
  const [angebote, setAngebote] = useState<Angebot[]>([])
  const [showBelegfolgeDialog, setShowBelegfolgeDialog] = useState(false)
  const [vorgaengerCount, setVorgaengerCount] = useState(0)

  // Dialog-States
  const [showAuftragAuswahl, setShowAuftragAuswahl] = useState(!routeId)
  const [showCustomerDialog, setShowCustomerDialog] = useState(false)
  const [showArticleDialog, setShowArticleDialog] = useState(false)
  const [showPrintDialog, setShowPrintDialog] = useState(false)
  const [showAttachmentDialog, setShowAttachmentDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showAttestationDialog, setShowAttestationDialog] = useState(false)
  const [showInformationDialog, setShowInformationDialog] = useState(false)
  const [pendingPrintOptions, setPendingPrintOptions] = useState<PrintOptions | null>(null)
  const [pendingAction, setPendingAction] = useState<'print' | 'modify' | 'cancel' | 'post' | 'reopen' | null>(null)
  const [sucheText, setSucheText] = useState('')
  const [showNiederlassungDialog, setShowNiederlassungDialog] = useState(false)
  const [showVertreterDialog, setShowVertreterDialog] = useState(false)
  const [vertreterInput, setVertreterInput] = useState('')
  const [branchesList, setBranchesList] = useState<Array<{ id: string; branch_number: number; name: string }>>([])

  // Auftrags-Auswahl-Liste
  const { data: auftraege = [], isLoading } = useAuftraege()
  const filteredAuftraege = auftraege.filter(
    (a) =>
      a.nummer.toLowerCase().includes(sucheText.toLowerCase()) ||
      a.kunde.toLowerCase().includes(sucheText.toLowerCase()),
  )

  // Bediener aus Session aktualisieren
  useEffect(() => {
    if (user) setState((prev) => ({ ...prev, bediener: getUserShortName() }))
  }, [user])

  // Bestehenden Auftrag laden wenn ID in URL (Kunde per customer_id aus API)
  useEffect(() => {
    if (!routeId) return
    const load = async (): Promise<void> => {
      try {
        const res = await apiClient.get<AuftragResponse>(`/api/v1/sales/orders/${routeId}`)
        const response = (res as any)?.data ?? res
        let customer: Customer | null = null
        if (response?.customer_id) {
          try {
            const cr = await apiClient.get<any>(`/api/v1/crm/customers/${response.customer_id}`)
            const cd = (cr as any)?.data ?? cr
            customer = {
              id: cd.id,
              customerNumber: cd.customer_number ?? cd.customerNumber ?? '',
              name: cd.company_name ?? cd.name ?? '',
              debitorAccount: cd.customer_number ?? cd.customerNumber ?? '',
              representative: cd.contact_person ?? cd.representative,
              postalCode: cd.postal_code ?? cd.postalCode,
              city: cd.city,
              creditLimit: cd.credit_limit?.toString(),
              address: cd.address,
              phone: cd.phone,
              email: cd.email,
              chefanweisung: cd.chefanweisung ?? cd.executive_note,
              paymentTerms: cd.payment_terms,
            }
          } catch { /* ignore */ }
        }
        setState((prev) => ({
          ...prev,
          id: response?.id,
          auftragNr: response?.order_number ?? prev.auftragNr,
          auftragDatum: response?.created_at?.split('T')[0] ?? formatDateForInput(new Date()),
          liefertermin: response?.delivery_date?.split('T')[0] ?? '',
          versandart: response?.shipping_method ?? '',
          betreff: response?.subject ?? '',
          notizen: response?.description ?? '',
          vertreter: response?.contact_person ?? '',
          customer,
          positionen: mapResponseItemsToPositionen(response?.items ?? []),
        }))
      } catch (error: any) {
        push(`Fehler beim Laden: ${error.response?.data?.detail || error.message}`)
      }
    }
    void load()
  }, [routeId])

  // Preis automatisch berechnen
  useEffect(() => {
    const einhPreis = currentPosition.listenpreis * (1 - currentPosition.rabatt / 100)
    const betrag = einhPreis * currentPosition.mengeGebinde
    setCurrentPosition((prev) => ({ ...prev, einhPreis, betrag }))
  }, [currentPosition.listenpreis, currentPosition.rabatt, currentPosition.mengeGebinde])

  // Summen
  const summen = useMemo(() => {
    const netto = state.positionen.reduce((s, p) => s + p.nettoBetrag, 0)
    const mwst = state.positionen.reduce((s, p) => s + (p.nettoBetrag * p.mwstProzent) / 100, 0)
    const brutto = netto + mwst
    const gewicht = state.positionen.reduce((s, p) => s + p.gesamtGewicht, 0)
    const gefahrgutPunkte = state.positionen.reduce((s, p) => s + p.gesamtGefahrgutPunkte, 0)
    return { netto, mwst, brutto, gesamt: brutto, gewicht, gefahrgutPunkte }
  }, [state.positionen])

  // â”€â”€ Handler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  async function handleCustomerSelect(c: Customer): Promise<void> {
    setState((prev) => ({
      ...prev,
      customer: c,
      vertreter: c.representative || prev.vertreter,
    }))
    // Angebote für Kunden laden
    try {
      const offers = await apiClient.get<any[]>(`/api/v1/sales/quotes?customer_id=${c.id}`)
      const mapped = (offers || []).map((o) => ({
        id: o.id,
        angebotNr: o.quote_number || o.number || o.id,
        datum: o.created_at?.split('T')[0] || '',
      }))
      setAngebote(mapped)
      setVorgaengerCount(mapped.length)
    } catch {
      setAngebote([])
      setVorgaengerCount(0)
    }
  }

  function handleAuftragAuswaehlen(auftrag: Auftrag) {
    navigate(`/sales/order-editor/${auftrag.id}`)
    setShowAuftragAuswahl(false)
  }

  function handleAuftragPrev() {
    const idx = state.id ? auftraege.findIndex((a) => a.id === state.id) : -1
    if (idx > 0 && auftraege[idx - 1]) {
      navigate(`/sales/order-editor/${auftraege[idx - 1].id}`)
    } else {
      push('Kein vorheriger Auftrag')
    }
  }
  function handleAuftragNext() {
    const idx = state.id ? auftraege.findIndex((a) => a.id === state.id) : -1
    if (idx >= 0 && idx < auftraege.length - 1 && auftraege[idx + 1]) {
      navigate(`/sales/order-editor/${auftraege[idx + 1].id}`)
    } else {
      push('Kein nächster Auftrag')
    }
  }
  const handleNiederlassungOpen = async (): Promise<void> => {
    try {
      const list = await apiClient.get<Array<{ id: string; branch_number: number; name: string }>>('/api/v1/admin/branches', { params: { active_only: true } })
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

  function handleArticleSelect(article: any) {
    const listenpreis = article.sales_price || article.salesPrice || 0
    const ekPreis = article.purchase_price || article.purchasePrice || 0
    const artikelGewicht = article.weight || article.gewicht || 0
    const artikelGefahrgutPunkte =
      article.gefahrgut_punkte || article.gefahrgutPunkte ||
      (article.gefahrgutklasse ? parseFloat(article.gefahrgutklasse) || 0 : 0)
    const mwstProzent = Number(article.mehrwertsteuer_prozent || article.mwstProzent || 19)
    setCurrentPosition((prev) => ({
      ...prev,
      artikelNr: article.article_number || article.articleNumber || '',
      artikelId: article.id || null,
      artikelBezeichnung: article.name || article.description || '',
      artikelBezeichnung2: article.description2 || '',
      einheit: article.unit || 'Stk',
      listenpreis,
      ekPreis,
      mwstProzent,
      artikelGewicht,
      artikelGefahrgutPunkte,
    }))
  }

  function handlePositionOK() {
    if (!currentPosition.artikelNr || !currentPosition.mengeGebinde) return
    const nettoPreis = currentPosition.listenpreis * (1 - currentPosition.rabatt / 100)
    const nettoBetrag = nettoPreis * currentPosition.mengeGebinde
    const gesamtGewicht = currentPosition.artikelGewicht * currentPosition.mengeGebinde
    const gesamtGefahrgutPunkte = currentPosition.artikelGefahrgutPunkte * currentPosition.mengeGebinde

    const newPos: Position = {
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
      lagerhalle: '', lagerfach: '', charge: '', serienNr: '',
      gefPunkt: currentPosition.artikelGefahrgutPunkte > 0
        ? currentPosition.artikelGefahrgutPunkte.toString() : '',
      gefahrgutPunkte: currentPosition.artikelGefahrgutPunkte,
      gesamtGefahrgutPunkte,
      naBio: '', musterNr: '', strecke: '', zusBeleg: '', anerken: '', erloskonto: '',
      mwstProzent: currentPosition.mwstProzent,
      gewicht: currentPosition.artikelGewicht,
      gesamtGewicht,
      kontraktNr: currentPosition.kontraktNr,
      skontierf: currentPosition.skontierf,
      fremdware: currentPosition.fremdware,
      ekPreis: currentPosition.ekPreis,
    }

    const activeIdx = state.aktivePositionIndex
    setState((prev) => ({
      ...prev,
      positionen: activeIdx !== null
        ? prev.positionen.map((p, i) => (i === activeIdx ? newPos : p))
        : [...prev.positionen, newPos],
      aktivePositionIndex: activeIdx !== null ? activeIdx : prev.positionen.length,
    }))
    setCurrentPosition(emptyCurrentPosition(currentPosition.posNr + 10))
  }

  function handlePositionRowClick(pos: Position, idx: number) {
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
      ekPreis: pos.ekPreis,
      mwstProzent: pos.mwstProzent,
      verfuegbar: 0,
      kontraktNr: pos.kontraktNr,
      skontierf: pos.skontierf,
      fremdware: pos.fremdware,
      artikelGewicht: pos.gewicht,
      artikelGefahrgutPunkte: pos.gefahrgutPunkte,
    })
  }

  // Nur bei Entwurf (nicht bestätigt) Positionen löschen/verschieben erlauben
  const isDraft = !state.statusBestaetigt

  const renumberPosNr = (positionen: Position[]): Position[] =>
    positionen.map((p, i) => ({ ...p, posNr: (i + 1) * 10 }))

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
    if (state.aktivePositionIndex === idx) {
      setCurrentPosition(emptyCurrentPosition(renumbered.length > 0 ? renumbered[renumbered.length - 1].posNr + 10 : 10))
    }
  }

  const handleMovePositionUp = (idx: number): void => {
    if (idx <= 0) return
    const newPositionen = [...state.positionen]
    ;[newPositionen[idx - 1], newPositionen[idx]] = [newPositionen[idx], newPositionen[idx - 1]]
    const renumbered = renumberPosNr(newPositionen)
    const newAktive =
      state.aktivePositionIndex === idx ? idx - 1 : state.aktivePositionIndex === idx - 1 ? idx : state.aktivePositionIndex
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
    const newAktive =
      state.aktivePositionIndex === idx ? idx + 1 : state.aktivePositionIndex === idx + 1 ? idx : state.aktivePositionIndex
    setState((prev) => ({
      ...prev,
      positionen: renumbered,
      aktivePositionIndex: newAktive,
    }))
  }

  // â”€â”€ Speichern â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const handleSave = async (): Promise<string | null> => {
    if (!state.customer) {
      push('Bitte zuerst einen Kunden auswählen')
      return null
    }
    try {
      const payload = {
        order_number: state.auftragNr,
        customer_id: state.customer.id,
        subject: state.betreff || `Auftrag ${state.auftragNr}`,
        description: state.notizen,
        total_amount: summen.netto,
        currency: 'EUR',
        status: state.statusBestaetigt ? 'confirmed' : 'open',
        contact_person: state.vertreter || null,
        delivery_date: state.liefertermin ? new Date(state.liefertermin).toISOString() : null,
        delivery_address: state.customer.address
          ? [state.customer.address.street, state.customer.address.postalCode, state.customer.address.city]
              .filter(Boolean).join(', ')
          : null,
        shipping_method: state.versandart || null,
        payment_terms: state.customer.paymentTerms
          ? `${state.customer.paymentTerms} Tage netto`
          : null,
        items: state.positionen.map((p) => ({
          article_number: p.artikelNr,
          description: p.bezeichnung,
          quantity: p.menge,
          unit_price: p.listenpreis,
          discount_percent: p.rabatt,
        })),
      }

      if (state.id) {
        await apiClient.put(`/api/v1/sales/orders/${state.id}`, payload)
        push('Auftrag gespeichert')
        return state.id
      } else {
        const saved = await apiClient.post<{ id: string }>('/api/v1/sales/orders/', payload)
        setState((prev) => ({ ...prev, id: saved.id }))
        push('Auftrag angelegt')
        return saved.id
      }
    } catch (error: any) {
      push(`Speichern fehlgeschlagen: ${error.response?.data?.detail || error.message}`)
      return null
    }
  }

  // â”€â”€ Drucken â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const handlePrint = async (options: PrintOptions): Promise<void> => {
    if (state.statusGedruckt || state.statusBestaetigt) {
      setPendingPrintOptions(options)
      setPendingAction('print')
      setShowAttestationDialog(true)
      return
    }
    await executePrint(options)
  }

  const handleAttestationConfirm = async (
    reason: string,
    action: 'print' | 'modify' | 'cancel' | 'post' | 'reopen',
  ): Promise<void> => {
    setShowAttestationDialog(false)
    if (action === 'print') {
      const opts: PrintOptions = pendingPrintOptions ?? {
        formatvorlage: 'W00001', anzahlDrucke: 1, sortierung: 'pos-nr',
        druckLieferschein: true, druckAllgemeineAngaben: false, werbetext: '',
      }
      await executePrint(opts, reason)
    }
    setPendingAction(null)
  }

  const executePrint = async (options: PrintOptions, attestation?: string): Promise<void> => {
    try {
      let id = state.id
      if (!id) {
        id = await handleSave()
        if (!id) return
      }
      const params = new URLSearchParams()
      if (attestation) params.append('attestation', attestation)
      params.append('template', options.formatvorlage)
      params.append('copies', String(options.anzahlDrucke))
      await apiClient.post(`/api/v1/sales/orders/${id}/print?${params.toString()}`)
      await apiClient.post(`/api/v1/sales/orders/${id}/post`)
      push('Auftrag erfolgreich gedruckt und gebucht')
      setState((prev) => ({ ...prev, statusGedruckt: true }))
      setShowPrintDialog(false)
    } catch (error: any) {
      push(`Fehler beim Drucken: ${error.response?.data?.detail || error.message}`)
    }
  }

  // â”€â”€ Löschen â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const handleDelete = async (): Promise<void> => {
    if (!state.id) {
      setState((prev) => ({
        ...prev,
        id: null, auftragNr: generateAuftragNr(),
        auftragDatum: formatDateForInput(new Date()), liefertermin: '',
        customer: null, positionen: [], aktivePositionIndex: null,
      }))
      setShowDeleteDialog(false)
      return
    }
    try {
      await apiClient.delete(`/api/v1/sales/orders/${state.id}`)
      push('Auftrag gelöscht')
      setShowDeleteDialog(false)
      navigate('/verkauf')
    } catch (error: any) {
      push(`Löschen fehlgeschlagen: ${error.response?.data?.detail || error.message}`)
    }
  }

  // â”€â”€ Belegfolge-Positionsübernahme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  function handleBelegfolgePositionen(incoming: BelegfolgePosition[]): void {
    const baseNr =
      state.positionen.length > 0
        ? Math.max(...state.positionen.map((p) => p.posNr)) + 10
        : 10
    const newPositionen: Position[] = incoming.map((pos, idx) => {
      const nettoPreis = pos.listenpreis * (1 - pos.rabatt / 100)
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
        nettoBetrag: nettoPreis * pos.menge,
        niederlassung: '',
        lagerhalle: '', lagerfach: '', charge: '', serienNr: '', gefPunkt: '',
        gefahrgutPunkte: 0, gesamtGefahrgutPunkte: 0,
        naBio: '', musterNr: '', strecke: '', zusBeleg: '', anerken: '', erloskonto: '',
        mwstProzent: pos.mwstProzent,
        gewicht: 0, gesamtGewicht: 0,
        kontraktNr: '', skontierf: false, fremdware: false,
        ekPreis: pos.ekPreis,
      }
    })
    setState((prev) => ({ ...prev, positionen: [...prev.positionen, ...newPositionen] }))
    push(`${newPositionen.length} Position${newPositionen.length !== 1 ? 'en' : ''} übernommen`)
  }

  // â”€â”€ In Lieferschein wandeln â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  const handleCreateLieferschein = async (): Promise<void> => {
    const id = state.id || (await handleSave())
    if (!id) return
    navigate(`/verkauf/lieferschein-erfassung?auftrag=${id}`)
  }

  const handleSofortRechnung = async () => {
    let orderId = state.id
    if (!orderId) {
      try { orderId = await handleSave() } catch { return }
    }
    if (!orderId) return
    try {
      const res = await apiClient.post<{
        command: string
        target_doc_id?: string
        status: string
        payload?: { target_doc_number?: string; target_doc_type?: string }
      }>(`/api/v1/docflow/${orderId}/convert`, {
        target_doc_type: 'sales_invoice',
        idempotency_key: crypto.randomUUID(),
      })
      const docNumber = res.payload?.target_doc_number
      if (docNumber) {
        push(`Rechnung ${docNumber} erstellt`)
        const targetId = res.target_doc_id
        if (targetId && typeof navigate === 'function') {
          navigate(`/verkauf/rechnungen/${targetId}`, { replace: false })
        }
      } else {
        push('Rechnung erstellt')
      }
    } catch (e: any) {
      push(`Sofort-Rechnung fehlgeschlagen: ${e.response?.data?.detail ?? e.message}`)
    }
  }

  // â”€â”€ Globale Shortcuts â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  useGlobalShortcutsWithVoice({
    'open-customer-selection': () => setShowCustomerDialog(true),
    'open-article-selection': () => setShowArticleDialog(true),
    'confirm-position': () => handlePositionOK(),
    'save-document': () => void handleSave(),
    'print-document': () => { if (!showPrintDialog) setShowPrintDialog(true) },
    'delete-document': () => setShowDeleteDialog(true),
    'close-document': () => navigate(-1),
    'copy-previous-full': async () => {
      try {
        const response = await apiClient.get<AuftragResponse | null>('/api/v1/sales/orders/last', {
          params: { customer_id: state.customer?.id || undefined },
        })
        if (!response) { push('Kein vorheriger Auftrag gefunden'); return }
        setState((prev) => ({
          ...prev,
          positionen: mapResponseItemsToPositionen(response.items || []),
        }))
        push('Daten vom vorherigen Auftrag übernommen')
      } catch (error: any) {
        push(`Fehler: ${error.response?.data?.detail || error.message}`)
      }
    },
    'create-invoice': () => void handleSofortRechnung(),
    'open-attachments': () => setShowAttachmentDialog(true),
    'show-information': () => {
      if (state.customer) setShowInformationDialog(true)
      else push('Bitte zuerst einen Kunden auswählen')
    },
    cancel: () => {
      setShowCustomerDialog(false)
      setShowArticleDialog(false)
      setShowPrintDialog(false)
      setShowAttestationDialog(false)
    },
  })

  // â”€â”€ JSX â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-green-700 text-white px-4 py-2">
        <h1 className="text-lg font-bold">AUFTRAGS-ERFASSUNG</h1>
      </div>

      {/* Belegfolge-Hinweis */}
      {vorgaengerCount > 0 && state.customer && (
        <div className="bg-amber-50 border-b border-amber-300 px-4 py-1.5 flex items-center gap-3">
          <span className="text-amber-800 text-sm font-medium">
            {vorgaengerCount} offene{vorgaengerCount !== 1 ? ' Angebote' : 's Angebot'} für{' '}
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
            ×
          </Button>
        </div>
      )}

      <div className="flex-1 overflow-auto p-4">

        {/* â”€â”€ Kopf-Bereich (3 Spalten) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
        <Card className="mb-4 p-4">
          <div className="grid grid-cols-3 gap-4">

            {/* Linke Spalte */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Auftrags-Nr.:</Label>
                <Input value={state.auftragNr} readOnly className="flex-1 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0"
                  onClick={() => setShowAuftragAuswahl(true)} title="Auftrag suchen">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={handleAuftragPrev} title="Vorheriger Auftrag">
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={handleAuftragNext} title="Nächster Auftrag">
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Auftrag-Datum:</Label>
                <Input
                  type="date"
                  value={state.auftragDatum}
                  onChange={(e) => setState((prev) => ({ ...prev, auftragDatum: e.target.value }))}
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
                <Label className="w-32 text-sm">Liefertermin:</Label>
                <Input
                  type="date"
                  value={state.liefertermin}
                  onChange={(e) => setState((prev) => ({ ...prev, liefertermin: e.target.value }))}
                  className="flex-1 h-8"
                />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Kostenstelle:</Label>
                <Input
                  type="number"
                  value={state.kostenstelle}
                  onChange={(e) => setState((prev) => ({ ...prev, kostenstelle: Number(e.target.value) }))}
                  className="flex-1 h-8"
                />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm whitespace-nowrap">Angebots-Nr. (Bezug):</Label>
                <Input
                  value={state.angebotNrBezug}
                  onChange={(e) => setState((prev) => ({ ...prev, angebotNrBezug: e.target.value }))}
                  className="flex-1 h-8"
                />
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={state.statusGedruckt}
                  onCheckedChange={(c) => setState((prev) => ({ ...prev, statusGedruckt: c === true }))}
                />
                <Label className="text-sm">gedruckt</Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={state.statusBestaetigt}
                  onCheckedChange={(c) => setState((prev) => ({ ...prev, statusBestaetigt: c === true }))}
                />
                <Label className="text-sm">bestätigt</Label>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm whitespace-nowrap">in LS gewandelt:</Label>
                <Input
                  value={state.lieferscheinNr}
                  readOnly
                  className="flex-1 h-8 bg-muted cursor-not-allowed"
                  placeholder="Wird nach LS-Erstellung zugewiesen"
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
                  onChange={(e) => setState((prev) => ({ ...prev, niederlassung: Number(e.target.value) }))}
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
                <Label className="w-32 text-sm">Versandart:</Label>
                <Input
                  value={state.versandart}
                  onChange={(e) => setState((prev) => ({ ...prev, versandart: e.target.value }))}
                  className="flex-1 h-8"
                />
              </div>
              <div className="flex items-center gap-2">
                <a
                  href="#"
                  className="text-sm text-blue-600 underline hover:text-blue-800"
                  onClick={(e) => {
                    e.preventDefault()
                    void globalShortcutManager.execute('copy-previous-full')
                  }}
                >
                  &gt;&gt; wie vorheriger Auftrag (F11)
                </a>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={state.selbstabholung}
                  onCheckedChange={(c) => setState((prev) => ({ ...prev, selbstabholung: c === true }))}
                />
                <Label className="text-sm">Selbstabholung</Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={state.pauschalAuftrag}
                  onCheckedChange={(c) => setState((prev) => ({ ...prev, pauschalAuftrag: c === true }))}
                />
                <Label className="text-sm">Pauschal-Auftrag</Label>
              </div>
            </div>

            {/* Rechte Spalte — Kunden-Tabs */}
            <div className="space-y-2">
              <Tabs value={customerTab} onValueChange={(v) => setCustomerTab(v)}>
                <TabsList className="grid w-full grid-cols-4 h-auto">
                  <TabsTrigger value="kunde" className="text-xs py-1">KUNDE</TabsTrigger>
                  <TabsTrigger value="lieferanschr" className="text-xs py-1">LIEFER-ANSCHR.</TabsTrigger>
                  <TabsTrigger value="rechnanschrift" className="text-xs py-1">RECHN.-ANSCHRIFT</TabsTrigger>
                  <TabsTrigger value="angebot" className="text-xs py-1">ANGEBOT</TabsTrigger>
                </TabsList>
                <TabsList className="grid w-full grid-cols-4 h-auto mt-1">
                  <TabsTrigger value="rechnung" className="text-xs py-1">RECHNUNG/ZAHLUNGSBED.</TabsTrigger>
                  <TabsTrigger value="texte" className="text-xs py-1">TEXTE</TabsTrigger>
                  <TabsTrigger value="spediteur" className="text-xs py-1">SPEDITEUR</TabsTrigger>
                  <TabsTrigger value="lieferung" className="text-xs py-1">LIEFERUNG</TabsTrigger>
                </TabsList>

                <TabsContent value="kunde" className="mt-2 space-y-1">
                  {state.customer ? (
                    <div className="text-sm space-y-1">
                      <div className="font-semibold">{state.customer.name}</div>
                      {state.customer.address?.street && <div>{state.customer.address.street}</div>}
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
                  ) : (
                    <div className="text-sm text-muted-foreground">Kein Kunde ausgewählt</div>
                  )}
                </TabsContent>

                <TabsContent value="lieferanschr" className="mt-2 space-y-1">
                  {state.customer ? (
                    <div className="text-sm space-y-1">
                      <div className="font-semibold">Lieferanschrift</div>
                      {state.customer.address?.street ? (
                        <>
                          <div>{state.customer.address.street}</div>
                          <div>
                            {[state.customer.address.postalCode, state.customer.address.city]
                              .filter(Boolean).join(' ')}
                          </div>
                          {state.customer.address.phone && (
                            <div className="text-muted-foreground">Tel: {state.customer.address.phone}</div>
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

                <TabsContent value="rechnanschrift" className="mt-2 space-y-1">
                  {state.customer ? (
                    <div className="text-sm space-y-1">
                      <div className="font-semibold">Rechnungsanschrift</div>
                      {state.customer.address?.street ? (
                        <>
                          <div>{state.customer.address.street}</div>
                          <div>
                            {[state.customer.address.postalCode, state.customer.address.city]
                              .filter(Boolean).join(' ')}
                          </div>
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

                <TabsContent value="angebot" className="mt-2 space-y-2">
                  <div className="text-sm space-y-2">
                    {state.customer ? (
                      angebote.length > 0 ? (
                        <>
                          <div className="font-semibold">
                            Zu Angeboten ({String(angebote.length).padStart(2, '0')})
                          </div>
                          <ul className="list-disc pl-5 space-y-1">
                            {angebote.map((a) => (
                              <li key={a.id} className="text-sm">
                                Angebots-Nr: {a.angebotNr} vom {a.datum}
                              </li>
                            ))}
                          </ul>
                          <Button
                            variant="outline"
                            size="sm"
                            className="mt-2"
                            onClick={() => setShowBelegfolgeDialog(true)}
                          >
                            Positionen aus Angebot übernehmen
                          </Button>
                        </>
                      ) : (
                        <div className="text-muted-foreground">Es liegt kein Angebot vor</div>
                      )
                    ) : (
                      <div className="text-muted-foreground">Kein Kunde ausgewählt</div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="rechnung" className="mt-2 space-y-1">
                  {state.customer ? (
                    <div className="text-sm space-y-1.5">
                      <div className="grid grid-cols-[140px_1fr] gap-1">
                        <span className="text-muted-foreground">Zahlungsziel:</span>
                        <span>
                          {state.customer.paymentTerms !== undefined
                            ? `${state.customer.paymentTerms} Tage netto` : '—'}
                        </span>
                        <span className="text-muted-foreground">Kredit-Limit:</span>
                        <span>
                          {state.customer.creditLimit
                            ? Number(state.customer.creditLimit).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
                            : '—'}
                        </span>
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
                      <div className="grid grid-cols-[80px_1fr] gap-1 items-center">
                        <span className="text-muted-foreground">Betreff:</span>
                        <Input
                          value={state.betreff}
                          onChange={(e) => setState((prev) => ({ ...prev, betreff: e.target.value }))}
                          className="h-7 text-xs" placeholder="Auftrags-Betreff"
                        />
                        <span className="text-muted-foreground">Notiz:</span>
                        <Input
                          value={state.notizen}
                          onChange={(e) => setState((prev) => ({ ...prev, notizen: e.target.value }))}
                          className="h-7 text-xs" placeholder="Interne Notizen"
                        />
                      </div>
                      {(state.customer.chefanweisung || state.customer.executiveNote) && (
                        <div>
                          <div className="font-semibold mb-1">Chefanweisung</div>
                          <div className="p-2 bg-amber-50 border border-amber-200 rounded text-xs whitespace-pre-wrap">
                            {state.customer.chefanweisung || state.customer.executiveNote}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground">Kein Kunde ausgewählt</div>
                  )}
                </TabsContent>

                <TabsContent value="spediteur" className="mt-2 space-y-1">
                  {state.customer ? (
                    <div className="text-sm space-y-1.5">
                      <div className="grid grid-cols-[140px_1fr] gap-1">
                        <span className="text-muted-foreground">Spediteur:</span>
                        <span>—</span>
                        <span className="text-muted-foreground">Versandart:</span>
                        <span>{state.versandart || '—'}</span>
                        <span className="text-muted-foreground">Lieferadresse:</span>
                        <span>
                          {[
                            state.customer.address?.street,
                            state.customer.address?.postalCode,
                            state.customer.address?.city,
                          ].filter(Boolean).join(', ') || '—'}
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
                    <div>Liefertermin: {state.liefertermin || '—'}</div>
                    {state.selbstabholung && (
                      <div className="text-muted-foreground">Selbstabholung</div>
                    )}
                    {state.versandart && (
                      <div className="text-muted-foreground">Versandart: {state.versandart}</div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>

              {/* Debitor-Kto. unterhalb der Tabs */}
              <div className="flex items-center gap-2">
                <Label className="w-32 text-sm">Debitor-Kto.:</Label>
                <Input value={state.customer?.debitorAccount || ''} readOnly className="flex-1 h-8" />
                <ShortcutHintButton shortcut="Strg+F1">
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"
                    onClick={() => setShowCustomerDialog(true)}>
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </ShortcutHintButton>
              </div>
              {state.customer && (
                <div className="text-sm space-y-1 pl-32">
                  <div>{state.customer.name}</div>
                  <div className="text-muted-foreground">
                    Kredit-Limit: {state.customer.creditLimit || '—'}
                  </div>
                </div>
              )}
              <div className="flex items-center gap-2 pl-32">
                <a
                  href="#"
                  className="text-sm text-blue-600 hover:text-blue-800 underline"
                  onClick={(e) => {
                    e.preventDefault()
                    if (state.customer) setShowInformationDialog(true)
                    else push('Bitte zuerst einen Kunden auswählen')
                  }}
                >
                  Information
                </a>
              </div>
            </div>
          </div>
        </Card>

        {/* â”€â”€ Positionen-Grid â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
        <Card className="mb-4 p-4">
          <h2 className="mb-2 font-semibold text-sm">Positionen</h2>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-14">Pos.-Nr.</TableHead>
                  <TableHead className="w-24">Artikel-Nr.</TableHead>
                  <TableHead className="w-36">Bezeichn.</TableHead>
                  <TableHead className="w-32">Bezeichn2</TableHead>
                  <TableHead className="w-16">Menge</TableHead>
                  <TableHead className="w-16">Einh.</TableHead>
                  <TableHead className="w-24">Listenpreis</TableHead>
                  <TableHead className="w-16">Rabatt</TableHead>
                  <TableHead className="w-16">Art</TableHead>
                  <TableHead className="w-24">Netto-Pr.</TableHead>
                  <TableHead className="w-24">Netto-Be.</TableHead>
                  <TableHead className="w-20">Niederl.</TableHead>
                  <TableHead className="w-20">Lagerhalle</TableHead>
                  <TableHead className="w-20">Lagerfach</TableHead>
                  <TableHead className="w-20">Charge</TableHead>
                  <TableHead className="w-20">Serien-Nr.</TableHead>
                  <TableHead className="w-20">Gef.-Pun.</TableHead>
                  <TableHead className="w-20">Na.-Bio.</TableHead>
                  <TableHead className="w-20">Muster-Nr.</TableHead>
                  <TableHead className="w-20">Strecke</TableHead>
                  <TableHead className="w-20">Zus.Beleg</TableHead>
                  <TableHead className="w-20">Anerken.</TableHead>
                  <TableHead className="w-24">Erlöskonto</TableHead>
                  <TableHead className="w-28 text-right">Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {state.positionen.map((pos, idx) => (
                  <TableRow
                    key={idx}
                    className={`cursor-pointer text-xs ${state.aktivePositionIndex === idx ? 'bg-green-100' : 'hover:bg-muted/50'}`}
                    onClick={() => handlePositionRowClick(pos, idx)}
                  >
                    <TableCell>{pos.posNr}</TableCell>
                    <TableCell className="font-mono">{pos.artikelNr}</TableCell>
                    <TableCell>{pos.bezeichnung}</TableCell>
                    <TableCell>{pos.bezeichnung2}</TableCell>
                    <TableCell>{pos.menge.toLocaleString('de-DE')}</TableCell>
                    <TableCell>{pos.einheit}</TableCell>
                    <TableCell>{pos.listenpreis.toFixed(2)}</TableCell>
                    <TableCell>{pos.rabatt > 0 ? `${pos.rabatt}%` : ''}</TableCell>
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
                      {isDraft && (
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
                            disabled={idx >= state.positionen.length - 1}
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
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {state.positionen.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={24} className="text-center text-xs text-muted-foreground py-4">
                      Noch keine Positionen — Artikel unten eingeben
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </Card>

        {/* â”€â”€ Positions-Details â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
        <Card className="mb-4 p-4">
          <h2 className="mb-2 font-semibold text-sm">
            {state.aktivePositionIndex !== null
              ? `Position ${state.positionen[state.aktivePositionIndex]?.posNr} bearbeiten`
              : 'Positions-Details'}
          </h2>
          <div className="grid grid-cols-6 gap-4">
            <div className="space-y-1">
              <Label className="text-xs">Pos.-Nr.:</Label>
              <Input value={currentPosition.posNr} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Artikel-Nr.:</Label>
              <div className="flex gap-1">
                <Input value={currentPosition.artikelNr} readOnly className="flex-1 h-8" />
                <ShortcutHintButton shortcut="Strg+F2">
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"
                    onClick={() => setShowArticleDialog(true)}>
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </ShortcutHintButton>
              </div>
            </div>
            <div className="space-y-1 col-span-2">
              <Label className="text-xs">Artikel-Bezeichn.:</Label>
              <Input value={currentPosition.artikelBezeichnung} readOnly className="h-8" />
              <Input value={currentPosition.artikelBezeichnung2} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Menge:</Label>
              <Input
                type="number"
                value={currentPosition.mengeGebinde || ''}
                onChange={(e) => setCurrentPosition((prev) => ({ ...prev, mengeGebinde: Number(e.target.value) }))}
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
                type="number" step="0.01"
                value={currentPosition.listenpreis || ''}
                onChange={(e) => setCurrentPosition((prev) => ({ ...prev, listenpreis: Number(e.target.value) }))}
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Rabatt %:</Label>
              <Input
                type="number"
                value={currentPosition.rabatt || ''}
                onChange={(e) => setCurrentPosition((prev) => ({ ...prev, rabatt: Number(e.target.value) }))}
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Einh.-Preis:</Label>
              <Input value={currentPosition.einhPreis.toFixed(2)} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Betrag:</Label>
              <Input value={currentPosition.betrag.toFixed(2)} readOnly className="h-8 font-semibold" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">MWSt. %:</Label>
              <Input
                type="number"
                value={currentPosition.mwstProzent}
                onChange={(e) => setCurrentPosition((prev) => ({ ...prev, mwstProzent: Number(e.target.value) }))}
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">verfügbar:</Label>
              <Input
                value={`${currentPosition.verfuegbar} ${currentPosition.einheit}`}
                readOnly className="h-8"
              />
            </div>

            <div className="space-y-1">
              <Label className="text-xs">Kontrakt-Nr.:</Label>
              <Input
                value={currentPosition.kontraktNr}
                onChange={(e) => setCurrentPosition((prev) => ({ ...prev, kontraktNr: e.target.value }))}
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">EK-Preis:</Label>
              <Input value={currentPosition.ekPreis.toFixed(2)} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Gewicht (kg):</Label>
              <Input value={currentPosition.artikelGewicht.toFixed(3)} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Gef.-Punkte:</Label>
              <Input value={currentPosition.artikelGefahrgutPunkte.toFixed(0)} readOnly className="h-8" />
            </div>
            <div className="col-span-2 flex items-end gap-3 pb-0.5">
              <div className="flex items-center gap-1">
                <Checkbox
                  checked={currentPosition.fremdware}
                  onCheckedChange={(c) => setCurrentPosition((prev) => ({ ...prev, fremdware: c === true }))}
                />
                <Label className="text-xs">Fremdware</Label>
              </div>
              <div className="flex items-center gap-1">
                <Checkbox
                  checked={currentPosition.skontierf}
                  onCheckedChange={(c) => setCurrentPosition((prev) => ({ ...prev, skontierf: c === true }))}
                />
                <Label className="text-xs">skontierf.</Label>
              </div>
              <ShortcutHintButton shortcut="Strg+F3">
                <Button
                  onClick={handlePositionOK}
                  disabled={!currentPosition.artikelNr || !currentPosition.mengeGebinde}
                  className="h-8 gap-1"
                >
                  <Check className="h-4 w-4" />
                  Zeile OK
                </Button>
              </ShortcutHintButton>
              {state.aktivePositionIndex !== null && (
                <Button
                  variant="outline" size="sm" className="h-8"
                  onClick={() => {
                    setState((prev) => ({ ...prev, aktivePositionIndex: null }))
                    setCurrentPosition(emptyCurrentPosition(currentPosition.posNr + 10))
                  }}
                >
                  Abbrechen
                </Button>
              )}
            </div>
          </div>
        </Card>

        {/* â”€â”€ Summen â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
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
              <Input value={summen.gesamt.toFixed(2)} readOnly className="h-8 font-semibold" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">EUR</Label>
              <Input value="EUR" readOnly className="h-8" />
            </div>
          </div>
        </Card>

      </div>

      {/* â”€â”€ Bottom-Toolbar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}
      <div className="border-t bg-white px-4 py-2 flex items-center justify-between">
        <div className="flex gap-2 flex-wrap">
          <Button onClick={() => setShowPrintDialog(true)} variant="outline" size="sm" className="gap-2">
            <Printer className="h-4 w-4" />
            Auftrag drucken
          </Button>
          <Button variant="outline" size="sm" className="gap-2"
            onClick={() => setShowAttachmentDialog(true)}>
            <FileText className="h-4 w-4" />
            Unterlagen
          </Button>
          <Button variant="outline" size="sm" className="gap-2"
            onClick={() => setShowAttachmentDialog(true)}>
            <Folder className="h-4 w-4" />
            Dateien
          </Button>
          <Button variant="outline" size="sm" className="gap-2" onClick={() => { const q = state.customer?.id ? `?customerId=${state.customer.id}` : ''; navigate(`/contracts${q}`); push('Kontrakte geöffnet.'); }} title="Kontrakte anzeigen/verknüpfen">
            <FileCheck className="h-4 w-4" />
            Kontrakte
          </Button>
          <Button variant="outline" size="sm" className="gap-2"
            onClick={() => void handleCreateLieferschein()}>
            <LinkIcon className="h-4 w-4" />
            In Lieferschein wandeln
          </Button>
          <Button variant="outline" size="sm" className="gap-2" onClick={() => void handleSofortRechnung()} title="Direkt Rechnung aus Auftrag">
            <Receipt className="h-4 w-4" />
            Sofort-Rechnung
          </Button>
          <Button variant="outline" size="sm" className="gap-2 text-red-600"
            onClick={() => setShowDeleteDialog(true)}>
            <Trash2 className="h-4 w-4" />
            Auftrag löschen
          </Button>
        </div>
        <div className="flex gap-2">
          <ShortcutHintButton shortcut="Strg+F4">
            <Button onClick={() => void handleSave()} size="sm" className="gap-2">
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

      {/* â”€â”€ Dialoge â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */}

      {/* Auftrag-Auswahl */}
      <Dialog open={showAuftragAuswahl} onOpenChange={setShowAuftragAuswahl}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Verkaufs-Aufträge</DialogTitle>
          </DialogHeader>
          <div className="flex items-center gap-2 mb-3">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Input
              value={sucheText}
              onChange={(e) => setSucheText(e.target.value)}
              placeholder="Auftrag-Nr. oder Kunde suchen…"
              className="h-8 text-sm"
              autoFocus
            />
          </div>
          <div className="border rounded-md overflow-hidden max-h-80 overflow-y-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted text-xs">
                  <TableHead className="py-1 w-32">Auftrag-Nr.</TableHead>
                  <TableHead className="py-1 w-24">Datum</TableHead>
                  <TableHead className="py-1">Kunde</TableHead>
                  <TableHead className="py-1 w-24">Liefertermin</TableHead>
                  <TableHead className="py-1 w-28 text-right">Betrag</TableHead>
                  <TableHead className="py-1 w-20">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-sm text-muted-foreground py-6">
                      Lade Aufträge…
                    </TableCell>
                  </TableRow>
                ) : filteredAuftraege.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-sm text-muted-foreground py-6">
                      Keine Aufträge gefunden
                    </TableCell>
                  </TableRow>
                ) : filteredAuftraege.map((a, idx) => (
                  <TableRow
                    key={a.id}
                    className={`text-xs cursor-pointer ${idx === 0 ? 'bg-primary/10' : 'hover:bg-muted/50'}`}
                    onDoubleClick={() => handleAuftragAuswaehlen(a)}
                  >
                    <TableCell className="py-1 font-mono">{a.nummer}</TableCell>
                    <TableCell className="py-1">{a.datum}</TableCell>
                    <TableCell className="py-1">{a.kunde}</TableCell>
                    <TableCell className="py-1">{a.liefertermin}</TableCell>
                    <TableCell className="py-1 text-right">
                      {a.betrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })} â‚¬
                    </TableCell>
                    <TableCell className="py-1">{a.status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <DialogFooter className="mt-2">
            <Button variant="outline" size="sm"
              onClick={() => {
                setState((prev) => ({
                  ...prev, id: null, auftragNr: generateAuftragNr(),
                  auftragDatum: formatDateForInput(new Date()), liefertermin: '',
                  customer: null, positionen: [], aktivePositionIndex: null,
                }))
                setShowAuftragAuswahl(false)
              }}>
              Neuer Auftrag
            </Button>
            <Button variant="outline" size="sm" onClick={() => setShowAuftragAuswahl(false)}>
              Abbrechen
            </Button>
            <Button size="sm"
              onClick={() => filteredAuftraege[0] && handleAuftragAuswaehlen(filteredAuftraege[0])}>
              Übernehmen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <CustomerSelectionDialog
        open={showCustomerDialog}
        onClose={() => setShowCustomerDialog(false)}
        onSelect={(c) => { void handleCustomerSelect(c); setShowCustomerDialog(false) }}
      />

      <ArtikelSuchDialog
        open={showArticleDialog}
        onClose={() => setShowArticleDialog(false)}
        onSelect={(a) => { handleArticleSelect(a); setShowArticleDialog(false) }}
        customerId={state.customer?.id}
      />

      <LieferscheinDruckDialog
        open={showPrintDialog}
        onClose={() => setShowPrintDialog(false)}
        onConfirm={handlePrint}
        title="AUFTRAG DRUCKEN"
      />

      <DmsAnhangDialog
        open={showAttachmentDialog}
        onClose={() => setShowAttachmentDialog(false)}
        businessObjectType="sales_order"
        businessObjectId={state.id}
        title="UNTERLAGEN / DATEIEN — AUFTRAG"
      />

      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Auftrag löschen?</DialogTitle>
          </DialogHeader>
          <div className="py-2 text-sm">
            {state.id
              ? <><strong>{state.auftragNr}</strong> wird unwiderruflich gelöscht. Fortfahren?</>
              : 'Das Formular wird geleert. Nicht gespeicherte Daten gehen verloren.'}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>Abbrechen</Button>
            <Button variant="destructive" onClick={() => void handleDelete()}>Löschen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AttestationDialog
        open={showAttestationDialog}
        onClose={() => { setShowAttestationDialog(false); setPendingAction(null) }}
        onConfirm={handleAttestationConfirm}
        action={pendingAction || 'print'}
        entityType="Auftrag"
        entityNumber={state.auftragNr}
      />

      {state.customer && (
        <BelegfolgePositionenDialog
          open={showBelegfolgeDialog}
          onClose={() => setShowBelegfolgeDialog(false)}
          onConfirm={handleBelegfolgePositionen}
          customerId={state.customer.id}
          targetDocType="auftrag"
        />
      )}

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
    </div>
  )
}

