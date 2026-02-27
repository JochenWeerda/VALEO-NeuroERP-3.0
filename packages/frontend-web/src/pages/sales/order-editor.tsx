/**
 * Auftrags-Erfassung (Verkauf)
 * Einheitliches ERP-Look & Feel — Gewohnheits-Prinzip nach Lieferschein-Erfassung
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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { CustomerSelectionDialog, type Customer } from '@/components/sales/CustomerSelectionDialog'
import { ArtikelSuchDialog } from '@/components/sales/ArtikelSuchDialog'
import { LieferscheinDruckDialog, type PrintOptions } from '@/components/sales/LieferscheinDruckDialog'
import { DmsAnhangDialog } from '@/components/dms/DmsAnhangDialog'
import { useAuftraege, type Auftrag } from '@/lib/api/sales'
import { apiClient } from '@/lib/axios'
import { useToast } from '@/components/ui/toast-provider'
import { useAuth } from '@/hooks/useAuth'
import {
  ChevronLeft,
  ChevronRight,
  MoreHorizontal,
  Printer,
  Save,
  Trash2,
  X,
  Search,
  FileText,
  Truck,
  Receipt,
} from 'lucide-react'

// ── Types ──────────────────────────────────────────────────────────────────────

type AuftragPosition = {
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

// ── Helpers ────────────────────────────────────────────────────────────────────

function generateAuftragNr(): string {
  const year = new Date().getFullYear()
  const random = Math.floor(Math.random() * 100000)
  return `AU${year}-${String(random).padStart(5, '0')}`
}

function emptyPosition(posNr: number): CurrentPositionDetails {
  return {
    posNr, artikelNr: '', artikelId: null, bezeichnung: '', bezeichnung2: '',
    menge: 0, einheit: '', listenpreis: 0, rabatt: 0, einhPreis: 0,
    betrag: 0, ekPreis: 0, mwstProzent: 19, gewicht: 0,
  }
}

function formatEur(val: number): string {
  return val.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €'
}

// ── Component ──────────────────────────────────────────────────────────────────

export default function SalesOrderEditorPage(): JSX.Element {
  const navigate = useNavigate()
  const { id: routeId } = useParams<{ id?: string }>()
  const { push } = useToast()
  const { user } = useAuth()

  // ── Kopf-Daten ─────────────────────────────────────────────────────────────
  const [auftragId, setAuftragId] = useState<string | null>(null)
  const [auftragNr, setAuftragNr] = useState(() => generateAuftragNr())
  const [datum, setDatum] = useState(() => new Date().toISOString().split('T')[0])
  const [liefertermin, setLiefertermin] = useState('')
  const [lieferadresse, setLieferadresse] = useState('')
  const [status, setStatus] = useState('Offen')
  const [isPauschale, setIsPauschale] = useState(false)
  const [kontakt, setKontakt] = useState('')
  const [zahlungsbedingung, setZahlungsbedingung] = useState('')
  const [versandart, setVersandart] = useState('')
  const [notizen, setNotizen] = useState('')
  const [betreff, setBetreff] = useState('')
  const [customer, setCustomer] = useState<Customer | null>(null)

  // ── Dialog-States ──────────────────────────────────────────────────────────
  const [showAuftragAuswahl, setShowAuftragAuswahl] = useState(!routeId)
  const [showCustomerDialog, setShowCustomerDialog] = useState(false)
  const [showArticleDialog, setShowArticleDialog] = useState(false)
  const [showPrintDialog, setShowPrintDialog] = useState(false)
  const [showAttachmentDialog, setShowAttachmentDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [sucheText, setSucheText] = useState('')

  // ── Positionen ─────────────────────────────────────────────────────────────
  const [positionen, setPositionen] = useState<AuftragPosition[]>([])
  const [aktivePositionIndex, setAktivePositionIndex] = useState<number | null>(null)
  const [currentPosition, setCurrentPosition] = useState<CurrentPositionDetails>(() => emptyPosition(10))

  // ── Aufträge-Liste (Auswahl-Dialog) ───────────────────────────────────────
  const { data: auftraege = [], isLoading } = useAuftraege()
  const filteredAuftraege = auftraege.filter(
    (a) =>
      a.nummer.toLowerCase().includes(sucheText.toLowerCase()) ||
      a.kunde.toLowerCase().includes(sucheText.toLowerCase()),
  )

  // ── Preis automatisch berechnen ───────────────────────────────────────────
  useEffect(() => {
    const einhPreis = currentPosition.listenpreis * (1 - currentPosition.rabatt / 100)
    const betrag = einhPreis * currentPosition.menge
    setCurrentPosition((prev) => ({ ...prev, einhPreis, betrag }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPosition.listenpreis, currentPosition.rabatt, currentPosition.menge])

  // ── Summen ─────────────────────────────────────────────────────────────────
  const summen = useMemo(() => {
    const netto = positionen.reduce((s, p) => s + p.nettoBetrag, 0)
    const mwst = positionen.reduce((s, p) => s + (p.nettoBetrag * p.mwstProzent) / 100, 0)
    const brutto = netto + mwst
    const gewicht = positionen.reduce((s, p) => s + (p.gesamtGewicht || 0), 0)
    return { netto, mwst, brutto, gewicht }
  }, [positionen])

  // ── Handlers ───────────────────────────────────────────────────────────────

  function handleAuftragAuswaehlen(auftrag: Auftrag) {
    setAuftragNr(auftrag.nummer)
    setDatum(auftrag.datum)
    setStatus(auftrag.status)
    setLiefertermin(auftrag.liefertermin)
    setCustomer({ id: '', customerNumber: auftrag.nummer, name: auftrag.kunde, debitorAccount: '' })
    setShowAuftragAuswahl(false)
  }

  function handleCustomerSelect(c: Customer) {
    setCustomer(c)
    if (c.representative) setKontakt(c.representative)
    if (c.paymentTerms) setZahlungsbedingung(`${c.paymentTerms} Tage netto`)
    if (c.address) {
      const adr = [c.address.street, c.address.postalCode, c.address.city].filter(Boolean).join(', ')
      if (adr) setLieferadresse(adr)
    }
  }

  function handleArticleSelect(article: any) {
    const listenpreis = article.sales_price || article.salesPrice || 0
    const ekPreis = article.purchase_price || article.purchasePrice || 0
    const gewicht = article.weight || article.gewicht || 0
    const mwstProzent = Number(article.mehrwertsteuer_prozent || article.mwstProzent || 19)
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

  function handlePositionOK() {
    if (!currentPosition.artikelNr || !currentPosition.menge) return

    const nettoPreis = currentPosition.listenpreis * (1 - currentPosition.rabatt / 100)
    const nettoBetrag = nettoPreis * currentPosition.menge
    const gesamtGewicht = currentPosition.gewicht * currentPosition.menge

    const newPos: AuftragPosition = {
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

    if (aktivePositionIndex !== null) {
      setPositionen((prev) => prev.map((p, i) => i === aktivePositionIndex ? newPos : p))
    } else {
      setPositionen((prev) => [...prev, newPos])
    }
    setAktivePositionIndex(null)
    setCurrentPosition(emptyPosition(currentPosition.posNr + 10))
  }

  function handlePositionRowClick(pos: AuftragPosition, idx: number) {
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

  function handlePositionDelete(idx: number) {
    setPositionen((prev) => prev.filter((_, i) => i !== idx))
    if (aktivePositionIndex === idx) {
      setAktivePositionIndex(null)
      setCurrentPosition(emptyPosition(10))
    }
  }

  // ── Speichern ──────────────────────────────────────────────────────────────

  const handleSave = async (): Promise<string | null> => {
    if (!customer) {
      push('Bitte zuerst einen Kunden auswählen')
      return null
    }
    try {
      const payload = {
        order_number: auftragNr,
        customer_id: customer.id,
        subject: betreff || `Auftrag ${auftragNr}`,
        description: notizen,
        total_amount: summen.netto,
        currency: 'EUR',
        status: status.toLowerCase().replace('ö', 'o'),
        contact_person: kontakt || null,
        delivery_date: liefertermin ? new Date(liefertermin).toISOString() : null,
        delivery_address: lieferadresse || null,
        shipping_method: versandart || null,
        payment_terms: zahlungsbedingung || null,
        items: positionen.map((p) => ({
          article_number: p.artikelNr,
          description: p.bezeichnung,
          quantity: p.menge,
          unit_price: p.listenpreis,
          discount_percent: p.rabatt,
        })),
      }

      if (auftragId) {
        await apiClient.put(`/api/v1/sales/orders/${auftragId}`, payload)
        push('Auftrag gespeichert')
        return auftragId
      } else {
        const saved = await apiClient.post<{ id: string }>('/api/v1/sales/orders/', payload)
        setAuftragId(saved.id)
        push('Auftrag angelegt')
        return saved.id
      }
    } catch (error: any) {
      push(`Speichern fehlgeschlagen: ${error.response?.data?.detail || error.message}`)
      return null
    }
  }

  // ── Löschen ────────────────────────────────────────────────────────────────

  const handleDelete = async (): Promise<void> => {
    if (!auftragId) {
      // Noch nicht gespeichert — Formular leeren
      resetForm()
      setShowDeleteDialog(false)
      return
    }
    try {
      await apiClient.delete(`/api/v1/sales/orders/${auftragId}`)
      push('Auftrag gelöscht')
      setShowDeleteDialog(false)
      navigate('/verkauf')
    } catch (error: any) {
      push(`Löschen fehlgeschlagen: ${error.response?.data?.detail || error.message}`)
    }
  }

  function resetForm() {
    setAuftragId(null)
    setAuftragNr(generateAuftragNr())
    setDatum(new Date().toISOString().split('T')[0])
    setLiefertermin('')
    setLieferadresse('')
    setStatus('Offen')
    setIsPauschale(false)
    setKontakt('')
    setZahlungsbedingung('')
    setVersandart('')
    setNotizen('')
    setBetreff('')
    setCustomer(null)
    setPositionen([])
    setAktivePositionIndex(null)
    setCurrentPosition(emptyPosition(10))
  }

  // ── Drucken ────────────────────────────────────────────────────────────────

  const handlePrint = async (options: PrintOptions): Promise<void> => {
    try {
      let id = auftragId || (await handleSave())
      if (!id) return

      const params = new URLSearchParams()
      params.append('template', options.formatvorlage)
      params.append('copies', String(options.anzahlDrucke))
      await apiClient.post(`/api/v1/sales/orders/${id}/print?${params.toString()}`)
      await apiClient.post(`/api/v1/sales/orders/${id}/post`)

      push('Auftrag erfolgreich gedruckt und gebucht')
      setShowPrintDialog(false)
      resetForm()
    } catch (error: any) {
      push(`Fehler beim Drucken: ${error.response?.data?.detail || error.message}`)
    }
  }

  // ── In Lieferschein wandeln ────────────────────────────────────────────────

  const handleCreateLieferschein = async (): Promise<void> => {
    const id = auftragId || (await handleSave())
    if (!id) return
    navigate(`/verkauf/lieferschein-erfassung?auftrag=${id}`)
  }

  // ── JSX ────────────────────────────────────────────────────────────────────

  return (
    <div className="h-screen flex flex-col bg-gray-50">

      {/* Header */}
      <div className="bg-green-700 text-white px-4 py-2">
        <h1 className="text-lg font-bold tracking-wide">AUFTRAGS-ERFASSUNG</h1>
      </div>

      <div className="flex-1 overflow-auto p-3 space-y-3">

        {/* ── Kopf-Bereich ───────────────────────────────────────────────── */}
        <Card className="p-4">
          <div className="grid grid-cols-3 gap-6">

            {/* Linke Spalte — Auftrag-Kopf */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm whitespace-nowrap shrink-0">Auftrag-Nr.:</Label>
                <Input value={auftragNr} onChange={(e) => setAuftragNr(e.target.value)} className="flex-1 h-8 text-sm" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" title="Auftrag suchen" onClick={() => setShowAuftragAuswahl(true)}>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><ChevronLeft className="h-4 w-4" /></Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><ChevronRight className="h-4 w-4" /></Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Datum:</Label>
                <Input type="date" value={datum} onChange={(e) => setDatum(e.target.value)} className="flex-1 h-8 text-sm" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm whitespace-nowrap shrink-0">Liefertermin:</Label>
                <Input type="date" value={liefertermin} onChange={(e) => setLiefertermin(e.target.value)} className="flex-1 h-8 text-sm" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Status:</Label>
                <Input value={status} readOnly className="flex-1 h-8 text-sm bg-muted" />
              </div>
              <div className="flex items-center gap-2 pt-1">
                <Checkbox
                  id="pauschale"
                  checked={isPauschale}
                  onCheckedChange={(v) => setIsPauschale(v === true)}
                />
                <Label htmlFor="pauschale" className="text-sm cursor-pointer">Pauschal-Auftrag</Label>
              </div>
            </div>

            {/* Mittlere Spalte — Kunde */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm whitespace-nowrap shrink-0">Kunde:</Label>
                <Input
                  value={customer?.name || ''}
                  readOnly
                  placeholder="Kunden auswählen…"
                  className="flex-1 h-8 text-sm"
                />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => setShowCustomerDialog(true)}>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
              {customer && (
                <>
                  <div className="flex items-center gap-2">
                    <Label className="w-28 text-sm shrink-0">Kunden-Nr.:</Label>
                    <Input value={customer.customerNumber} readOnly className="flex-1 h-8 text-sm bg-muted" />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="w-28 text-sm shrink-0">Debitor-Kto.:</Label>
                    <Input value={customer.debitorAccount} readOnly className="flex-1 h-8 text-sm bg-muted" />
                  </div>
                </>
              )}
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm whitespace-nowrap shrink-0">Ansprechpartner:</Label>
                <Input value={kontakt} onChange={(e) => setKontakt(e.target.value)} className="flex-1 h-8 text-sm" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Betreff:</Label>
                <Input value={betreff} onChange={(e) => setBetreff(e.target.value)} placeholder="Auftrags-Betreff" className="flex-1 h-8 text-sm" />
              </div>
            </div>

            {/* Rechte Spalte — Kunden-Tabs */}
            <div>
              {customer ? (
                <Tabs defaultValue="rechnung">
                  <TabsList className="h-7 text-xs">
                    <TabsTrigger value="rechnung" className="text-xs py-1 px-2">Rechnung</TabsTrigger>
                    <TabsTrigger value="versand" className="text-xs py-1 px-2">Versand</TabsTrigger>
                    <TabsTrigger value="texte" className="text-xs py-1 px-2">Texte</TabsTrigger>
                  </TabsList>

                  <TabsContent value="rechnung" className="mt-2 space-y-1 text-sm">
                    <div className="grid grid-cols-[120px_1fr] gap-1">
                      <span className="text-muted-foreground">Zahlungsziel:</span>
                      <Input value={zahlungsbedingung} onChange={(e) => setZahlungsbedingung(e.target.value)} className="h-7 text-xs" />
                      <span className="text-muted-foreground">Kredit-Limit:</span>
                      <span className="text-sm">{customer.creditLimit ? formatEur(Number(customer.creditLimit)) : '—'}</span>
                    </div>
                  </TabsContent>

                  <TabsContent value="versand" className="mt-2 space-y-1 text-sm">
                    <div className="grid grid-cols-[120px_1fr] gap-1">
                      <span className="text-muted-foreground">Versandart:</span>
                      <Input value={versandart} onChange={(e) => setVersandart(e.target.value)} className="h-7 text-xs" />
                      <span className="text-muted-foreground">Lieferadresse:</span>
                      <Input value={lieferadresse} onChange={(e) => setLieferadresse(e.target.value)} className="h-7 text-xs" />
                    </div>
                  </TabsContent>

                  <TabsContent value="texte" className="mt-2 text-sm">
                    {(customer.chefanweisung || customer.executiveNote) ? (
                      <div className="p-2 bg-amber-50 border border-amber-200 rounded text-xs whitespace-pre-wrap">
                        {customer.chefanweisung || customer.executiveNote}
                      </div>
                    ) : (
                      <p className="text-muted-foreground text-xs">Keine Kunden-Notizen</p>
                    )}
                  </TabsContent>
                </Tabs>
              ) : (
                <div className="flex items-center justify-center h-full text-sm text-muted-foreground border border-dashed rounded-md p-4">
                  Kunden auswählen für Details
                </div>
              )}
            </div>
          </div>
        </Card>

        {/* ── Positionen-Grid ────────────────────────────────────────────── */}
        <Card className="overflow-hidden">
          <div className="overflow-auto max-h-64">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted text-xs">
                  <TableHead className="w-10 py-1">Pos.</TableHead>
                  <TableHead className="w-24 py-1">Artikel-Nr.</TableHead>
                  <TableHead className="py-1">Bezeichnung</TableHead>
                  <TableHead className="w-20 py-1 text-right">Menge</TableHead>
                  <TableHead className="w-14 py-1">Einh.</TableHead>
                  <TableHead className="w-24 py-1 text-right">Listenpreis</TableHead>
                  <TableHead className="w-16 py-1 text-right">Rab.%</TableHead>
                  <TableHead className="w-24 py-1 text-right">Einh.-Preis</TableHead>
                  <TableHead className="w-28 py-1 text-right">Netto-Betrag</TableHead>
                  <TableHead className="w-8 py-1" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {positionen.map((pos, idx) => (
                  <TableRow
                    key={pos.posNr}
                    className={`text-xs cursor-pointer ${aktivePositionIndex === idx ? 'bg-primary/10' : 'hover:bg-muted/50'}`}
                    onClick={() => handlePositionRowClick(pos, idx)}
                  >
                    <TableCell className="py-1">{pos.posNr}</TableCell>
                    <TableCell className="py-1 font-mono">{pos.artikelNr}</TableCell>
                    <TableCell className="py-1">{pos.bezeichnung}</TableCell>
                    <TableCell className="py-1 text-right">{pos.menge.toLocaleString('de-DE')}</TableCell>
                    <TableCell className="py-1">{pos.einheit}</TableCell>
                    <TableCell className="py-1 text-right">{pos.listenpreis.toLocaleString('de-DE', { minimumFractionDigits: 2 })}</TableCell>
                    <TableCell className="py-1 text-right">{pos.rabatt > 0 ? `${pos.rabatt}%` : ''}</TableCell>
                    <TableCell className="py-1 text-right">{pos.nettoPreis.toLocaleString('de-DE', { minimumFractionDigits: 2 })}</TableCell>
                    <TableCell className="py-1 text-right font-medium">{pos.nettoBetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}</TableCell>
                    <TableCell className="py-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-5 w-5 text-muted-foreground hover:text-destructive"
                        onClick={(e) => { e.stopPropagation(); handlePositionDelete(idx) }}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {positionen.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={10} className="text-center text-xs text-muted-foreground py-4">
                      Noch keine Positionen — Artikel unten eingeben
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </Card>

        {/* ── Positions-Eingabe ──────────────────────────────────────────── */}
        <Card className="p-3">
          <div className="text-xs font-semibold text-muted-foreground mb-2 uppercase tracking-wide">
            {aktivePositionIndex !== null ? `Position ${positionen[aktivePositionIndex]?.posNr} bearbeiten` : 'Neue Position'}
          </div>
          <div className="grid grid-cols-[auto_1fr_auto_1fr_auto_1fr_auto_1fr] items-center gap-x-3 gap-y-2 text-sm">
            <Label className="text-right text-xs whitespace-nowrap">Pos.-Nr.:</Label>
            <Input
              type="number"
              value={currentPosition.posNr}
              onChange={(e) => setCurrentPosition((p) => ({ ...p, posNr: Number(e.target.value) }))}
              className="h-7 text-xs"
            />
            <Label className="text-right text-xs whitespace-nowrap">Artikel-Nr.:</Label>
            <div className="flex gap-1">
              <Input
                value={currentPosition.artikelNr}
                onChange={(e) => setCurrentPosition((p) => ({ ...p, artikelNr: e.target.value }))}
                className="h-7 text-xs flex-1"
              />
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => setShowArticleDialog(true)}>
                <MoreHorizontal className="h-3 w-3" />
              </Button>
            </div>
            <Label className="text-right text-xs">Bezeichnung:</Label>
            <Input
              value={currentPosition.bezeichnung}
              onChange={(e) => setCurrentPosition((p) => ({ ...p, bezeichnung: e.target.value }))}
              className="h-7 text-xs col-span-3"
            />

            <Label className="text-right text-xs">Menge:</Label>
            <Input
              type="number"
              value={currentPosition.menge || ''}
              onChange={(e) => setCurrentPosition((p) => ({ ...p, menge: Number(e.target.value) }))}
              className="h-7 text-xs"
            />
            <Label className="text-right text-xs">Einheit:</Label>
            <Input
              value={currentPosition.einheit}
              onChange={(e) => setCurrentPosition((p) => ({ ...p, einheit: e.target.value }))}
              className="h-7 text-xs"
            />
            <Label className="text-right text-xs whitespace-nowrap">Listenpreis:</Label>
            <Input
              type="number"
              value={currentPosition.listenpreis || ''}
              onChange={(e) => setCurrentPosition((p) => ({ ...p, listenpreis: Number(e.target.value) }))}
              className="h-7 text-xs"
            />
            <Label className="text-right text-xs">Rabatt %:</Label>
            <Input
              type="number"
              value={currentPosition.rabatt || ''}
              onChange={(e) => setCurrentPosition((p) => ({ ...p, rabatt: Number(e.target.value) }))}
              className="h-7 text-xs"
            />

            <Label className="text-right text-xs whitespace-nowrap">Einh.-Preis:</Label>
            <Input value={currentPosition.einhPreis.toLocaleString('de-DE', { minimumFractionDigits: 2 })} readOnly className="h-7 text-xs bg-muted" />
            <Label className="text-right text-xs">Betrag:</Label>
            <Input value={currentPosition.betrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })} readOnly className="h-7 text-xs bg-muted font-semibold" />
            <Label className="text-right text-xs">MwSt.%:</Label>
            <Input
              type="number"
              value={currentPosition.mwstProzent}
              onChange={(e) => setCurrentPosition((p) => ({ ...p, mwstProzent: Number(e.target.value) }))}
              className="h-7 text-xs"
            />
            <div className="col-span-2 flex gap-2 justify-end">
              <Button
                size="sm"
                className="h-7 text-xs"
                onClick={handlePositionOK}
                disabled={!currentPosition.artikelNr || !currentPosition.menge}
              >
                Position übernehmen
              </Button>
              {aktivePositionIndex !== null && (
                <Button
                  size="sm"
                  variant="outline"
                  className="h-7 text-xs"
                  onClick={() => { setAktivePositionIndex(null); setCurrentPosition(emptyPosition(currentPosition.posNr + 10)) }}
                >
                  Abbrechen
                </Button>
              )}
            </div>
          </div>
        </Card>

        {/* ── Summen ────────────────────────────────────────────────────── */}
        <Card className="p-2">
          <div className="flex items-center justify-end gap-6 text-sm">
            <span className="text-muted-foreground text-xs">Gewicht: {summen.gewicht.toLocaleString('de-DE', { maximumFractionDigits: 1 })} kg</span>
            <div className="flex items-center gap-2">
              <Label className="text-xs">Netto:</Label>
              <Input value={formatEur(summen.netto)} readOnly className="h-6 w-32 text-xs text-right bg-muted" />
            </div>
            <div className="flex items-center gap-2">
              <Label className="text-xs">MwSt.:</Label>
              <Input value={formatEur(summen.mwst)} readOnly className="h-6 w-28 text-xs text-right bg-muted" />
            </div>
            <div className="flex items-center gap-2">
              <Label className="text-xs font-semibold">Brutto:</Label>
              <Input value={formatEur(summen.brutto)} readOnly className="h-6 w-32 text-xs text-right font-semibold bg-muted" />
            </div>
          </div>
        </Card>

        {/* ── Notizen ───────────────────────────────────────────────────── */}
        <Card className="p-3">
          <div className="flex items-start gap-2">
            <Label className="w-20 text-sm pt-1 shrink-0">Notizen:</Label>
            <Input value={notizen} onChange={(e) => setNotizen(e.target.value)} placeholder="Interne Notizen zum Auftrag" className="flex-1 h-8 text-sm" />
          </div>
        </Card>
      </div>

      {/* ── Aktionsleiste ─────────────────────────────────────────────────── */}
      <div className="border-t bg-white px-4 py-2 flex items-center justify-between">
        <div className="flex gap-2 flex-wrap">
          <Button size="sm" className="gap-1 h-8" onClick={() => void handleSave()}>
            <Save className="h-3 w-3" /> Speichern
          </Button>
          <Button variant="outline" size="sm" className="gap-1 h-8" onClick={() => setShowPrintDialog(true)}>
            <Printer className="h-3 w-3" /> Drucken
          </Button>
          <Button variant="outline" size="sm" className="gap-1 h-8" onClick={() => setShowAttachmentDialog(true)}>
            <FileText className="h-3 w-3" /> Unterlagen
          </Button>
          <Button variant="outline" size="sm" className="gap-1 h-8" onClick={() => void handleCreateLieferschein()}>
            <Truck className="h-3 w-3" /> In Lieferschein wandeln
          </Button>
          <Button variant="outline" size="sm" className="gap-1 h-8">
            <Receipt className="h-3 w-3" /> Rechnung erstellen
          </Button>
          <Button variant="outline" size="sm" className="gap-1 h-8 text-destructive hover:text-destructive" onClick={() => setShowDeleteDialog(true)}>
            <Trash2 className="h-3 w-3" /> Löschen
          </Button>
        </div>
        <Button variant="ghost" size="sm" className="gap-1 h-8" onClick={() => navigate('/verkauf')}>
          <X className="h-3 w-3" /> Beenden
        </Button>
      </div>

      {/* ── Dialoge ───────────────────────────────────────────────────────── */}

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
          <div className="border rounded-md overflow-hidden max-h-80 overflow-auto">
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
                  <TableRow><TableCell colSpan={6} className="text-center text-sm text-muted-foreground py-6">Lade Aufträge…</TableCell></TableRow>
                ) : filteredAuftraege.length === 0 ? (
                  <TableRow><TableCell colSpan={6} className="text-center text-sm text-muted-foreground py-6">Keine Aufträge gefunden</TableCell></TableRow>
                ) : filteredAuftraege.map((a, idx) => (
                  <TableRow
                    key={a.id}
                    className={`text-xs cursor-pointer ${idx === 0 ? 'bg-primary/10' : 'hover:bg-muted/50'}`}
                    onDoubleClick={() => handleAuftragAuswaehlen(a)}
                    onClick={() => {}}
                  >
                    <TableCell className="py-1 font-mono">{a.nummer}</TableCell>
                    <TableCell className="py-1">{a.datum}</TableCell>
                    <TableCell className="py-1">{a.kunde}</TableCell>
                    <TableCell className="py-1">{a.liefertermin}</TableCell>
                    <TableCell className="py-1 text-right">{a.betrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €</TableCell>
                    <TableCell className="py-1">{a.status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <DialogFooter className="mt-2">
            <Button variant="outline" size="sm" onClick={() => { resetForm(); setShowAuftragAuswahl(false) }}>Neuer Auftrag</Button>
            <Button variant="outline" size="sm" onClick={() => setShowAuftragAuswahl(false)}>Abbrechen</Button>
            <Button size="sm" onClick={() => filteredAuftraege[0] && handleAuftragAuswaehlen(filteredAuftraege[0])}>
              Übernehmen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Kunden-Auswahl */}
      <CustomerSelectionDialog
        open={showCustomerDialog}
        onClose={() => setShowCustomerDialog(false)}
        onSelect={(c) => { handleCustomerSelect(c); setShowCustomerDialog(false) }}
      />

      {/* Artikel-Auswahl */}
      <ArtikelSuchDialog
        open={showArticleDialog}
        onClose={() => setShowArticleDialog(false)}
        onSelect={(a) => { handleArticleSelect(a); setShowArticleDialog(false) }}
        customerId={customer?.id}
      />

      {/* Druck-Dialog */}
      <LieferscheinDruckDialog
        open={showPrintDialog}
        onClose={() => setShowPrintDialog(false)}
        onConfirm={handlePrint}
        title="AUFTRAG DRUCKEN"
      />

      {/* DMS-Anhänge */}
      <DmsAnhangDialog
        open={showAttachmentDialog}
        onClose={() => setShowAttachmentDialog(false)}
        businessObjectType="sales_order"
        businessObjectId={auftragId}
        title="UNTERLAGEN / DATEIEN — AUFTRAG"
      />

      {/* Löschen-Bestätigung */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Auftrag löschen?</DialogTitle>
          </DialogHeader>
          <div className="py-2 text-sm">
            {auftragId
              ? <>Auftrag <strong>{auftragNr}</strong> wird unwiderruflich gelöscht. Fortfahren?</>
              : 'Das Formular wird geleert. Nicht gespeicherte Daten gehen verloren.'}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>Abbrechen</Button>
            <Button variant="destructive" onClick={() => void handleDelete()}>Löschen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
