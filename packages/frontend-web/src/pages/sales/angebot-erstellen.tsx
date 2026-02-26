/**
 * Angebot-Erfassung (Verkauf)
 * Im Stil der Lieferschein-Erfassung — einheitliches ERP-Look & Feel
 */

import { useState, useEffect, useMemo } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Card } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { CustomerSelectionDialog, type Customer } from '@/components/sales/CustomerSelectionDialog'
import { ArtikelSuchDialog } from '@/components/sales/ArtikelSuchDialog'
import { useAngebote, type Angebot } from '@/lib/api/sales'
import {
  ChevronLeft,
  ChevronRight,
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

function generateAngebotNr(): string {
  const year = new Date().getFullYear()
  const random = Math.floor(Math.random() * 100000)
  return `A${year}-${String(random).padStart(5, '0')}`
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

// ── Component ─────────────────────────────────────────────────────────────────

export default function AngebotErstellenPage(): JSX.Element {
  // ── Angebot-Kopf ──────────────────────────────────────────────────────────
  const [angebotNr, setAngebotNr] = useState(() => generateAngebotNr())
  const [datum, setDatum] = useState(() => new Date().toISOString().split('T')[0])
  const [gueltigBis, setGueltigBis] = useState('')
  const [status, setStatus] = useState('Offen')
  const [isPauschale, setIsPauschale] = useState(false)
  const [kontakt, setKontakt] = useState('')
  const [customer, setCustomer] = useState<Customer | null>(null)

  // ── Dialoge ───────────────────────────────────────────────────────────────
  const [showAngebotAuswahl, setShowAngebotAuswahl] = useState(false) // öffnet nur per Button
  const [showCustomerDialog, setShowCustomerDialog] = useState(false)
  const [showArticleDialog, setShowArticleDialog] = useState(false)
  const [sucheText, setSucheText] = useState('')

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPosition.listenpreis, currentPosition.rabatt, currentPosition.menge])

  // ── Summen ────────────────────────────────────────────────────────────────
  const summen = useMemo(() => {
    const netto = positionen.reduce((s, p) => s + p.nettoBetrag, 0)
    const mwst = positionen.reduce((s, p) => s + (p.nettoBetrag * p.mwstProzent) / 100, 0)
    const brutto = netto + mwst
    const gewicht = positionen.reduce((s, p) => s + (p.gesamtGewicht || 0), 0)
    return { netto, mwst, brutto, gewicht }
  }, [positionen])

  // ── Handler ───────────────────────────────────────────────────────────────

  function handleAngebotAuswaehlen(angebot: Angebot) {
    setAngebotNr(angebot.nummer)
    setDatum(angebot.datum)
    setStatus(angebot.status)
    setShowAngebotAuswahl(false)
  }

  function handleCustomerSelect(c: Customer) {
    setCustomer(c)
    if (c.representative) setKontakt(c.representative)
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

    setPositionen((prev) => [...prev, newPos])
    setAktivePositionIndex(positionen.length)
    setCurrentPosition(emptyPosition(currentPosition.posNr + 10))
  }

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

  // ── JSX ──────────────────────────────────────────────────────────────────

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-amber-500 text-white px-4 py-2">
        <h1 className="text-lg font-bold">ANGEBOT-ERFASSUNG</h1>
      </div>

      <div className="flex-1 overflow-auto p-4">

        {/* ── Kopf-Bereich ─────────────────────────────────────────────── */}
        <Card className="mb-4 p-4">
          <div className="grid grid-cols-3 gap-6">

            {/* Linke Spalte */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm whitespace-nowrap shrink-0">Angebot-Nr.:</Label>
                <Input
                  value={angebotNr}
                  onChange={(e) => setAngebotNr(e.target.value)}
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
                  onChange={(e) => setDatum(e.target.value)}
                  className="flex-1 h-8 text-sm"
                />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm whitespace-nowrap shrink-0">Gültig bis:</Label>
                <Input
                  type="date"
                  value={gueltigBis}
                  onChange={(e) => setGueltigBis(e.target.value)}
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
                  onCheckedChange={(c) => setIsPauschale(c === true)}
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
                  onChange={(e) => setKontakt(e.target.value)}
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
                  </TableRow>
                ))}
                {positionen.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={12} className="text-center text-xs text-muted-foreground py-4">
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
          <Button size="sm" className="h-7 text-xs gap-1">
            <Save className="h-3 w-3" /> Speichern
          </Button>
          <Button variant="outline" size="sm" className="h-7 text-xs gap-1">
            <Printer className="h-3 w-3" /> Drucken
          </Button>
          <Button variant="outline" size="sm" className="h-7 text-xs gap-1">
            <FileText className="h-3 w-3" /> Unterlagen
          </Button>
          <Button variant="outline" size="sm" className="h-7 text-xs gap-1">
            <FileText className="h-3 w-3" /> In Auftrag wandeln
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-7 text-xs gap-1 text-destructive hover:text-destructive"
          >
            <Trash2 className="h-3 w-3" /> Löschen
          </Button>
        </div>
        <Button variant="ghost" size="sm" className="h-7 text-xs gap-1">
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
    </div>
  )
}
