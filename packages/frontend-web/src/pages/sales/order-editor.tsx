/**
 * Auftrags-Erfassung (Verkauf)
 * Im Stil der Lieferschein-Erfassung — einheitliches ERP-Look & Feel
 */

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { useAuftraege, type Auftrag } from '@/lib/api/sales'
import { ChevronLeft, ChevronRight, MoreHorizontal, Printer, Save, Trash2, X, Search, FileText, Truck } from 'lucide-react'

type Position = {
  abs: string
  zeile: string
  pos: string
  artikelNr: string
  bezeichnung: string
  menge: string
  einheit: string
  preis: string
  betrag: string
  ekPreis: string
}

export default function SalesOrderEditorPage(): JSX.Element {
  const [auftragNr, setAuftragNr] = useState('')
  const [datum, setDatum] = useState(new Date().toLocaleDateString('de-DE'))
  const [liefertermin, setLiefertermin] = useState('')
  const [kunde, setKunde] = useState('')
  const [status, setStatus] = useState('Offen')
  const [isPauschale, setIsPauschale] = useState(false)
  const [kontakt, setKontakt] = useState('')
  const [zahlungsbedingung, setZahlungsbedingung] = useState('')
  const [versandart, setVersandart] = useState('')
  const [selectedPosition, setSelectedPosition] = useState<number | null>(null)
  const [auswahlOffen, setAuswahlOffen] = useState(true)
  const [sucheText, setSucheText] = useState('')

  const { data: auftraege = [], isLoading } = useAuftraege()

  const filtered = auftraege.filter(
    (a) =>
      a.nummer.toLowerCase().includes(sucheText.toLowerCase()) ||
      a.kunde.toLowerCase().includes(sucheText.toLowerCase()),
  )

  const [positionen] = useState<Position[]>([
    { abs: '10', zeile: '20', pos: '10', artikelNr: '', bezeichnung: '', menge: '', einheit: 'kg', preis: '', betrag: '', ekPreis: '' },
  ])

  function handleAuswaehlen(auftrag: Auftrag) {
    setAuftragNr(auftrag.nummer)
    setDatum(auftrag.datum)
    setKunde(auftrag.kunde)
    setStatus(auftrag.status)
    setLiefertermin(auftrag.liefertermin)
    setAuswahlOffen(false)
  }

  const selectedPos = selectedPosition !== null ? positionen[selectedPosition] : null

  return (
    <div className="flex flex-col h-full">

      {/* Titelbalken */}
      <div className="bg-green-700 px-4 py-2">
        <h1 className="text-white font-bold text-sm tracking-wide uppercase">Auftragserfassung</h1>
      </div>

      {/* Kopfbereich */}
      <Card className="m-3 p-3 rounded-md shadow-sm">
        <div className="grid grid-cols-[auto_1fr_auto_1fr_auto_1fr] items-center gap-x-3 gap-y-2 text-sm">

          {/* Zeile 1 */}
          <Label className="text-right whitespace-nowrap">Auftrag-Nr.:</Label>
          <div className="flex gap-1 items-center">
            <Input value={auftragNr} onChange={(e) => setAuftragNr(e.target.value)} className="h-7 text-sm" />
            <Button variant="outline" size="icon" className="h-7 w-7" onClick={() => setAuswahlOffen(true)}>
              <MoreHorizontal className="h-3 w-3" />
            </Button>
            <Button variant="outline" size="icon" className="h-7 w-7"><ChevronLeft className="h-3 w-3" /></Button>
            <Button variant="outline" size="icon" className="h-7 w-7"><ChevronRight className="h-3 w-3" /></Button>
          </div>

          <Label className="text-right whitespace-nowrap">Datum:</Label>
          <Input value={datum} onChange={(e) => setDatum(e.target.value)} className="h-7 text-sm" />

          <Label className="text-right whitespace-nowrap">Liefertermin:</Label>
          <Input value={liefertermin} onChange={(e) => setLiefertermin(e.target.value)} placeholder="TT.MM.JJJJ" className="h-7 text-sm" />

          {/* Zeile 2 */}
          <Label className="text-right whitespace-nowrap">Kunde:</Label>
          <div className="flex gap-1 items-center col-span-3">
            <Input value={kunde} onChange={(e) => setKunde(e.target.value)} className="h-7 text-sm flex-1" />
            <Button variant="outline" size="icon" className="h-7 w-7">
              <MoreHorizontal className="h-3 w-3" />
            </Button>
          </div>

          <Label className="text-right whitespace-nowrap">Status:</Label>
          <Input value={status} readOnly className="h-7 text-sm bg-muted" />

          {/* Zeile 3 */}
          <Label className="text-right whitespace-nowrap">Ansprechpartner:</Label>
          <Input value={kontakt} onChange={(e) => setKontakt(e.target.value)} className="h-7 text-sm" />

          <Label className="text-right whitespace-nowrap">Zahlungsbedingung:</Label>
          <Input value={zahlungsbedingung} onChange={(e) => setZahlungsbedingung(e.target.value)} className="h-7 text-sm" />

          <Label className="text-right whitespace-nowrap">Versandart:</Label>
          <Input value={versandart} onChange={(e) => setVersandart(e.target.value)} className="h-7 text-sm" />

          {/* Zeile 4 */}
          <Label className="text-right whitespace-nowrap">Pauschal-Auftrag:</Label>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={isPauschale}
              onChange={(e) => setIsPauschale(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300"
            />
          </div>
          <span /><span /><span /><span />
        </div>
      </Card>

      {/* Positionen */}
      <Card className="mx-3 mb-2 rounded-md shadow-sm overflow-hidden flex-1">
        <div className="overflow-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted text-xs">
                <TableHead className="w-10 py-1">Abs.</TableHead>
                <TableHead className="w-12 py-1">Zeile</TableHead>
                <TableHead className="w-12 py-1">Pos.</TableHead>
                <TableHead className="w-24 py-1">Artikel</TableHead>
                <TableHead className="py-1">Bezeichnung</TableHead>
                <TableHead className="w-20 py-1 text-right">Menge</TableHead>
                <TableHead className="w-14 py-1">Einh.</TableHead>
                <TableHead className="w-24 py-1 text-right">Einh.-Preis</TableHead>
                <TableHead className="w-24 py-1 text-right">Netto-Betr.</TableHead>
                <TableHead className="w-22 py-1 text-right">EK-Preis</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {positionen.map((pos, idx) => (
                <TableRow
                  key={idx}
                  className={`text-xs cursor-pointer ${selectedPosition === idx ? 'bg-primary text-primary-foreground' : 'hover:bg-muted/50'}`}
                  onClick={() => setSelectedPosition(idx)}
                >
                  <TableCell className="py-1">{pos.abs}</TableCell>
                  <TableCell className="py-1">{pos.zeile}</TableCell>
                  <TableCell className="py-1">{pos.pos}</TableCell>
                  <TableCell className="py-1">{pos.artikelNr}</TableCell>
                  <TableCell className="py-1">{pos.bezeichnung}</TableCell>
                  <TableCell className="py-1 text-right">{pos.menge}</TableCell>
                  <TableCell className="py-1">{pos.einheit}</TableCell>
                  <TableCell className="py-1 text-right">{pos.preis}</TableCell>
                  <TableCell className="py-1 text-right">{pos.betrag}</TableCell>
                  <TableCell className="py-1 text-right">{pos.ekPreis}</TableCell>
                </TableRow>
              ))}
              {/* Eingabezeile */}
              <TableRow className="text-xs bg-blue-50">
                <TableCell className="py-1"><Input className="h-5 text-xs p-0 px-1 border-0 bg-transparent" /></TableCell>
                <TableCell className="py-1"><Input className="h-5 text-xs p-0 px-1 border-0 bg-transparent" /></TableCell>
                <TableCell className="py-1"><Input className="h-5 text-xs p-0 px-1 border-0 bg-transparent" /></TableCell>
                <TableCell className="py-1"><Input className="h-5 text-xs p-0 px-1" /></TableCell>
                <TableCell className="py-1"><Input className="h-5 text-xs p-0 px-1" /></TableCell>
                <TableCell className="py-1"><Input className="h-5 text-xs p-0 px-1 text-right" /></TableCell>
                <TableCell className="py-1"><Input className="h-5 text-xs p-0 px-1" /></TableCell>
                <TableCell className="py-1"><Input className="h-5 text-xs p-0 px-1 text-right" /></TableCell>
                <TableCell className="py-1 text-right text-muted-foreground">0,00</TableCell>
                <TableCell className="py-1"><Input className="h-5 text-xs p-0 px-1 text-right" /></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </Card>

      {/* Positions-Details */}
      {selectedPos !== null && (
        <Card className="mx-3 mb-2 p-3 rounded-md shadow-sm">
          <div className="text-xs font-semibold text-muted-foreground mb-2 uppercase tracking-wide">Positions-Details</div>
          <div className="grid grid-cols-[auto_1fr_auto_1fr_auto_1fr_auto_1fr] items-center gap-x-3 gap-y-2 text-sm">
            <Label className="text-right text-xs">Pos.-Nr.:</Label>
            <Input value={selectedPos.pos} readOnly className="h-6 text-xs" />
            <Label className="text-right text-xs">Artikel-Nr.:</Label>
            <Input value={selectedPos.artikelNr} className="h-6 text-xs" />
            <Label className="text-right text-xs">Einh.-Preis:</Label>
            <Input value={selectedPos.preis} className="h-6 text-xs" />
            <Label className="text-right text-xs">Betrag:</Label>
            <Input value={selectedPos.betrag} className="h-6 text-xs" />
            <Button size="sm" variant="outline" className="h-6 text-xs col-span-2">Zeile OK</Button>
          </div>
        </Card>
      )}

      {/* Summen */}
      <Card className="mx-3 mb-2 p-2 rounded-md shadow-sm">
        <div className="flex items-center justify-end gap-6 text-sm">
          <span className="text-muted-foreground text-xs">Gewicht: 0 kg</span>
          <div className="flex items-center gap-2">
            <Label className="text-xs">Netto:</Label>
            <Input value="0,00 €" readOnly className="h-6 w-28 text-xs text-right bg-muted" />
          </div>
          <div className="flex items-center gap-2">
            <Label className="text-xs">MwSt.:</Label>
            <Input value="0,00 €" readOnly className="h-6 w-24 text-xs text-right bg-muted" />
          </div>
          <div className="flex items-center gap-2">
            <Label className="text-xs font-semibold">Brutto:</Label>
            <Input value="0,00 €" readOnly className="h-6 w-28 text-xs text-right font-semibold bg-muted" />
          </div>
        </div>
      </Card>

      {/* Aktionsleiste */}
      <div className="border-t bg-muted/30 px-3 py-2 flex items-center justify-between gap-2">
        <div className="flex gap-2 flex-wrap">
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
            <Truck className="h-3 w-3" /> Lieferschein erstellen
          </Button>
          <Button variant="outline" size="sm" className="h-7 text-xs gap-1">
            <FileText className="h-3 w-3" /> Rechnung erstellen
          </Button>
          <Button variant="outline" size="sm" className="h-7 text-xs gap-1 text-destructive hover:text-destructive">
            <Trash2 className="h-3 w-3" /> Löschen
          </Button>
        </div>
        <Button variant="ghost" size="sm" className="h-7 text-xs gap-1">
          <X className="h-3 w-3" /> Beenden
        </Button>
      </div>

      {/* Auswahl-Dialog */}
      <Dialog open={auswahlOffen} onOpenChange={setAuswahlOffen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Verkaufs-Aufträge</DialogTitle>
          </DialogHeader>

          <div className="flex items-center gap-2 mb-3">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Input
              value={sucheText}
              onChange={(e) => setSucheText(e.target.value)}
              placeholder="Auftrag-Nr. oder Kunde suchen..."
              className="h-8 text-sm"
              autoFocus
            />
          </div>

          <div className="border rounded-md overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted text-xs">
                  <TableHead className="py-1 w-28">Auftrag-Nr.</TableHead>
                  <TableHead className="py-1 w-24">Datum</TableHead>
                  <TableHead className="py-1">Kunde</TableHead>
                  <TableHead className="py-1 w-24">Liefertermin</TableHead>
                  <TableHead className="py-1 w-24 text-right">Betrag</TableHead>
                  <TableHead className="py-1 w-20">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-sm text-muted-foreground py-6">
                      Lade Aufträge...
                    </TableCell>
                  </TableRow>
                ) : filtered.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-sm text-muted-foreground py-6">
                      Keine Aufträge gefunden
                    </TableCell>
                  </TableRow>
                ) : (
                  filtered.map((a, idx) => (
                    <TableRow
                      key={a.id}
                      className={`text-xs cursor-pointer ${idx === 0 ? 'bg-primary text-primary-foreground' : 'hover:bg-muted/50'}`}
                      onDoubleClick={() => handleAuswaehlen(a)}
                      onClick={() => {}}
                    >
                      <TableCell className="py-1 font-mono">{a.nummer}</TableCell>
                      <TableCell className="py-1">{a.datum}</TableCell>
                      <TableCell className="py-1">{a.kunde}</TableCell>
                      <TableCell className="py-1">{a.liefertermin}</TableCell>
                      <TableCell className="py-1 text-right">{a.betrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €</TableCell>
                      <TableCell className="py-1">{a.status}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          <DialogFooter className="mt-2">
            <Button variant="outline" size="sm" onClick={() => setAuswahlOffen(false)}>Abbrechen</Button>
            <Button size="sm" onClick={() => filtered[0] && handleAuswaehlen(filtered[0])}>
              Übernehmen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
