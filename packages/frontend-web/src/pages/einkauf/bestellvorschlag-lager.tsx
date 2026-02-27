/**
 * Bestell-Vorschläge aus Bestand/Lager
 * 1:1 Nachbau der zvoove BESTELL-VORSCHLÄGE-Maske (Lager-Variante)
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useToast } from '@/components/ui/toast-provider'
import { apiClient } from '@/lib/axios'
import { MoreHorizontal, RefreshCw, Plus, Trash2, Calculator } from 'lucide-react'

type ArtikelZeile = {
  id: string
  artikelNr: string
  bezeichnung: string
  verfBestand: number
  bestandMin: number
  bestandMax: number
  vorschlagMenge: number
  einheit: string
  lagerhalle: string
  niederlassung: string
}

type Lieferant = {
  liefNr: string
  name: string
}

type Kontrakt = {
  kontraktNr: string
  lieferant: string
  restMenge: number
  einhPreis: number
  einheit: string
}

type LetzterEinkauf = {
  belegNr: string
  liefNr: string
  name: string
  menge: number
  einhPreis: number
  netto: number
  datum: string
  liefArt: string
}

type BestellVorschlag = {
  id: string
  liefNr: string
  name: string
  artikelNr: string
  liefArt: string
  menge: number
  einheit: string
  einhPreis: number
  preisEi: string
  betrag: number
  kontraktNr: string
  niederlassung: string
  lagerhalle: string
  bediener: string
  datum: string
}

export default function BestellvorschlagLagerPage(): JSX.Element {
  const navigate = useNavigate()
  const { push } = useToast()

  const [filterNiederlassung, setFilterNiederlassung] = useState('')
  const [filterArtikelGruppe, setFilterArtikelGruppe] = useState('')
  const [filterArtikelNr, setFilterArtikelNr] = useState('')

  const [artikel, setArtikel] = useState<ArtikelZeile[]>([])
  const [selectedArtikel, setSelectedArtikel] = useState<string | null>(null)
  const [lieferanten, setLieferanten] = useState<Lieferant[]>([])
  const [kontrakte, setKontrakte] = useState<Kontrakt[]>([])
  const [letzteEinkaeufe, setLetzteEinkaeufe] = useState<LetzterEinkauf[]>([])
  const [vorschlaege, setVorschlaege] = useState<BestellVorschlag[]>([])
  const [selectedVorschlag, setSelectedVorschlag] = useState<string | null>(null)
  const [vorschlagFilter, setVorschlagFilter] = useState<'alle' | 'lieferant'>('alle')

  const [lieferantText, setLieferantText] = useState('')
  const [gebindeMenge, setGebindeMenge] = useState('')
  const [preisJe1, setPreisJe1] = useState('')
  const [bestellMenge, setBestellMenge] = useState('')
  const [bestellWert, setBestellWert] = useState('')

  const [loading, setLoading] = useState(false)

  const loadData = async (): Promise<void> => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (filterNiederlassung) params['niederlassung'] = filterNiederlassung
      if (filterArtikelGruppe) params['artikel_gruppe'] = filterArtikelGruppe
      if (filterArtikelNr) params['artikel_nr'] = filterArtikelNr

      const data = await apiClient.get<any[]>('/api/v1/einkauf/bestellvorschlaege/lager', { params })
      const rows = (data || []).map((r: any) => ({
        id: r.id,
        artikelNr: r.artikel_nr || '',
        bezeichnung: r.bezeichnung || '',
        verfBestand: parseFloat(r.verf_bestand || '0'),
        bestandMin: parseFloat(r.bestand_min || '0'),
        bestandMax: parseFloat(r.bestand_max || '0'),
        vorschlagMenge: parseFloat(r.vorschlag_menge || '0'),
        einheit: r.einheit || '',
        lagerhalle: r.lagerhalle || '',
        niederlassung: r.niederlassung || '',
      }))
      setArtikel(rows)
    } catch {
      setArtikel([])
    } finally {
      setLoading(false)
    }
  }

  const loadArtikelDetails = async (id: string): Promise<void> => {
    try {
      const [liefData, kontData, kaufData] = await Promise.all([
        apiClient.get<any[]>(`/api/v1/einkauf/bestellvorschlaege/lager/${id}/lieferanten`).catch(() => []),
        apiClient.get<any[]>(`/api/v1/einkauf/bestellvorschlaege/lager/${id}/kontrakte`).catch(() => []),
        apiClient.get<any[]>(`/api/v1/einkauf/bestellvorschlaege/lager/${id}/letzte-einkaeufe`).catch(() => []),
      ])
      setLieferanten((liefData || []).map((r: any) => ({ liefNr: r.lief_nr || '', name: r.name || '' })))
      setKontrakte((kontData || []).map((r: any) => ({
        kontraktNr: r.kontrakt_nr || '',
        lieferant: r.lieferant || '',
        restMenge: parseFloat(r.rest_menge || '0'),
        einhPreis: parseFloat(r.einh_preis || '0'),
        einheit: r.einheit || '',
      })))
      setLetzteEinkaeufe((kaufData || []).map((r: any) => ({
        belegNr: r.beleg_nr || '',
        liefNr: r.lief_nr || '',
        name: r.name || '',
        menge: parseFloat(r.menge || '0'),
        einhPreis: parseFloat(r.einh_preis || '0'),
        netto: parseFloat(r.netto || '0'),
        datum: r.datum || '',
        liefArt: r.lief_art || '',
      })))
    } catch {
      /* ignore */
    }
  }

  useEffect(() => {
    if (selectedArtikel) {
      void loadArtikelDetails(selectedArtikel)
    }
  }, [selectedArtikel])

  const handleVorschlagUebernehmen = (): void => {
    if (!selectedArtikel) { push('Bitte einen Artikel auswählen'); return }
    const art = artikel.find((a) => a.id === selectedArtikel)
    if (!art) return
    const newVorschlag: BestellVorschlag = {
      id: crypto.randomUUID(),
      liefNr: lieferantText,
      name: '',
      artikelNr: art.artikelNr,
      liefArt: '',
      menge: parseFloat(bestellMenge || String(art.vorschlagMenge)),
      einheit: art.einheit,
      einhPreis: parseFloat(preisJe1 || '0'),
      preisEi: art.einheit,
      betrag: parseFloat(bestellWert || '0'),
      kontraktNr: '',
      niederlassung: art.niederlassung,
      lagerhalle: art.lagerhalle,
      bediener: '',
      datum: new Date().toISOString().substring(0, 10),
    }
    setVorschlaege((prev) => [...prev, newVorschlag])
    push('Vorschlag übernommen')
  }

  const handleBestellungErstellen = (): void => {
    if (vorschlaege.length === 0) { push('Keine Vorschläge vorhanden'); return }
    push('Bestellung erstellen: nicht implementiert')
  }

  const filteredVorschlaege = vorschlagFilter === 'alle'
    ? vorschlaege
    : vorschlaege.filter((v) => v.liefNr === lieferantText)

  const gesamtBestWert = filteredVorschlaege.reduce((s, v) => s + v.betrag, 0)

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <div className="bg-gray-700 text-white px-4 py-2">
        <h1 className="text-lg font-bold">BESTELL-VORSCHLÄGE AUS LAGER</h1>
      </div>

      <div className="flex-1 overflow-auto p-3 space-y-3">
        {/* Filter-Bereich */}
        <Card className="p-3">
          <div className="flex flex-wrap gap-4 items-end">
            <div className="flex items-center gap-2">
              <Label className="w-28 text-sm shrink-0">Niederlassung:</Label>
              <Input value={filterNiederlassung} onChange={(e) => setFilterNiederlassung(e.target.value)}
                className="w-32 h-8" placeholder="Alle" />
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Label className="w-28 text-sm shrink-0">Artikel-Gruppe:</Label>
              <Input value={filterArtikelGruppe} onChange={(e) => setFilterArtikelGruppe(e.target.value)}
                className="w-28 h-8" placeholder="Alle" />
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Label className="w-24 text-sm shrink-0">Artikel-Nr.:</Label>
              <Input value={filterArtikelNr} onChange={(e) => setFilterArtikelNr(e.target.value)}
                className="w-28 h-8" />
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
            <Button onClick={() => void loadData()} disabled={loading} size="sm" className="gap-2">
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Aufbereiten
            </Button>
          </div>
        </Card>

        {/* Artikel-Liste */}
        <Card className="p-3">
          <h2 className="font-semibold text-sm mb-2">
            Artikel unter Mindestbestand
            {artikel.length > 0 && <span className="text-muted-foreground font-normal ml-2">({artikel.length})</span>}
          </h2>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-28">Artikel-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead className="w-28 text-right">verf. Bestand</TableHead>
                  <TableHead className="w-24 text-right">Min.</TableHead>
                  <TableHead className="w-24 text-right">Max.</TableHead>
                  <TableHead className="w-28 text-right">Vorschl.-Me.</TableHead>
                  <TableHead className="w-16">Einh.</TableHead>
                  <TableHead className="w-28">Lagerhalle</TableHead>
                  <TableHead className="w-28">Niederlassung</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {artikel.length === 0 && !loading && (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center text-muted-foreground py-6">
                      Filter setzen und „Aufbereiten" klicken.
                    </TableCell>
                  </TableRow>
                )}
                {artikel.map((a) => (
                  <TableRow key={a.id}
                    className={`cursor-pointer ${selectedArtikel === a.id ? 'bg-blue-100' : 'hover:bg-muted/50'}`}
                    onClick={() => setSelectedArtikel(a.id)}>
                    <TableCell className="font-mono text-xs">{a.artikelNr}</TableCell>
                    <TableCell>{a.bezeichnung}</TableCell>
                    <TableCell className="text-right">{a.verfBestand.toFixed(3)}</TableCell>
                    <TableCell className="text-right">{a.bestandMin.toFixed(3)}</TableCell>
                    <TableCell className="text-right">{a.bestandMax.toFixed(3)}</TableCell>
                    <TableCell className="text-right font-medium">{a.vorschlagMenge.toFixed(3)}</TableCell>
                    <TableCell>{a.einheit}</TableCell>
                    <TableCell>{a.lagerhalle}</TableCell>
                    <TableCell>{a.niederlassung}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>

        {/* 3-Panel Mitte */}
        <div className="grid grid-cols-3 gap-3">
          {/* Lieferanten */}
          <Card className="p-3">
            <h3 className="font-semibold text-xs mb-2 text-muted-foreground uppercase tracking-wide">Lieferanten</h3>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">Lief.-Nr.</TableHead>
                  <TableHead>Name</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {lieferanten.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={2} className="text-center text-muted-foreground py-4 text-xs">
                      Artikel auswählen
                    </TableCell>
                  </TableRow>
                )}
                {lieferanten.map((l, i) => (
                  <TableRow key={i} className="cursor-pointer hover:bg-muted/50"
                    onClick={() => setLieferantText(l.liefNr)}>
                    <TableCell className="font-mono text-xs">{l.liefNr}</TableCell>
                    <TableCell className="text-sm">{l.name}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>

          {/* Kontrakte */}
          <Card className="p-3">
            <h3 className="font-semibold text-xs mb-2 text-muted-foreground uppercase tracking-wide">Kontrakte</h3>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-24">Kontrakt-Nr.</TableHead>
                  <TableHead>Lieferant</TableHead>
                  <TableHead className="w-20 text-right">Rest-Me.</TableHead>
                  <TableHead className="w-20 text-right">Einh.-Preis</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {kontrakte.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center text-muted-foreground py-4 text-xs">
                      Artikel auswählen
                    </TableCell>
                  </TableRow>
                )}
                {kontrakte.map((k, i) => (
                  <TableRow key={i} className="cursor-pointer hover:bg-muted/50">
                    <TableCell className="font-mono text-xs">{k.kontraktNr}</TableCell>
                    <TableCell className="text-sm">{k.lieferant}</TableCell>
                    <TableCell className="text-right text-sm">{k.restMenge.toFixed(3)}</TableCell>
                    <TableCell className="text-right text-sm">{k.einhPreis.toFixed(4)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>

          {/* Letzte Einkäufe */}
          <Card className="p-3">
            <h3 className="font-semibold text-xs mb-2 text-muted-foreground uppercase tracking-wide">Letzte Einkäufe</h3>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">Beleg-Nr.</TableHead>
                  <TableHead className="w-16">Lief.-Nr.</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead className="w-20 text-right">Menge</TableHead>
                  <TableHead className="w-20 text-right">Einh.-Pr.</TableHead>
                  <TableHead className="w-20">Datum</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {letzteEinkaeufe.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground py-4 text-xs">
                      Artikel auswählen
                    </TableCell>
                  </TableRow>
                )}
                {letzteEinkaeufe.map((e, i) => (
                  <TableRow key={i} className="cursor-pointer hover:bg-muted/50">
                    <TableCell className="font-mono text-xs">{e.belegNr}</TableCell>
                    <TableCell className="font-mono text-xs">{e.liefNr}</TableCell>
                    <TableCell className="text-sm">{e.name}</TableCell>
                    <TableCell className="text-right text-sm">{e.menge.toFixed(3)}</TableCell>
                    <TableCell className="text-right text-sm">{e.einhPreis.toFixed(4)}</TableCell>
                    <TableCell className="text-sm">{e.datum}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </div>

        {/* Eingabe-Zeile: Vorschlag übernehmen */}
        <Card className="p-3">
          <div className="flex flex-wrap gap-3 items-end">
            <div className="flex items-center gap-2">
              <Label className="text-sm shrink-0">Lieferant:</Label>
              <Input value={lieferantText} onChange={(e) => setLieferantText(e.target.value)}
                className="w-28 h-8" placeholder="Lief.-Nr." />
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Label className="text-sm shrink-0">Gebinde-Menge:</Label>
              <Input value={gebindeMenge} onChange={(e) => setGebindeMenge(e.target.value)}
                className="w-24 h-8 text-right" />
            </div>
            <div className="flex items-center gap-2">
              <Label className="text-sm shrink-0">Preis je 1:</Label>
              <Input value={preisJe1} onChange={(e) => setPreisJe1(e.target.value)}
                className="w-24 h-8 text-right" />
              <span className="text-sm text-muted-foreground">EUR</span>
            </div>
            <div className="flex items-center gap-2">
              <Label className="text-sm shrink-0">Bestell-Menge:</Label>
              <Input value={bestellMenge} onChange={(e) => setBestellMenge(e.target.value)}
                className="w-24 h-8 text-right" />
            </div>
            <div className="flex items-center gap-2">
              <Label className="text-sm shrink-0">Bestell-Wert:</Label>
              <Input value={bestellWert} onChange={(e) => setBestellWert(e.target.value)}
                className="w-24 h-8 text-right" readOnly />
              <span className="text-sm text-muted-foreground">EUR</span>
            </div>
            <Button onClick={handleVorschlagUebernehmen} size="sm" className="gap-2">
              ↓ Vorschlag übernehmen
            </Button>
          </div>
        </Card>

        {/* Bestell-Vorschläge Grid */}
        <Card className="p-3">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-semibold text-sm">
              Bestell-Vorschläge
              {filteredVorschlaege.length > 0 && (
                <span className="text-muted-foreground font-normal ml-2">({filteredVorschlaege.length})</span>
              )}
            </h2>
            <div className="flex gap-4">
              <label className="flex items-center gap-1 text-sm cursor-pointer">
                <input type="radio" name="vorschlag-filter-lager" value="alle"
                  checked={vorschlagFilter === 'alle'}
                  onChange={() => setVorschlagFilter('alle')} />
                alle
              </label>
              <label className="flex items-center gap-1 text-sm cursor-pointer">
                <input type="radio" name="vorschlag-filter-lager" value="lieferant"
                  checked={vorschlagFilter === 'lieferant'}
                  onChange={() => setVorschlagFilter('lieferant')} />
                nur zu Lieferant
              </label>
            </div>
          </div>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">Lief.-Nr.</TableHead>
                  <TableHead className="w-36">Name</TableHead>
                  <TableHead className="w-28">Artikel-Nr.</TableHead>
                  <TableHead className="w-28">Lief.-Art.</TableHead>
                  <TableHead className="w-24 text-right">Menge</TableHead>
                  <TableHead className="w-16">Einh.</TableHead>
                  <TableHead className="w-24 text-right">Einh.-Pr.</TableHead>
                  <TableHead className="w-16">Preis-Ei.</TableHead>
                  <TableHead className="w-24 text-right">Betrag</TableHead>
                  <TableHead className="w-24">Kontrakt-Nr.</TableHead>
                  <TableHead className="w-24">Niederla.</TableHead>
                  <TableHead className="w-24">Lagerhalle</TableHead>
                  <TableHead className="w-20">Bedie.</TableHead>
                  <TableHead className="w-24">Datum</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredVorschlaege.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={14} className="text-center text-muted-foreground py-6">
                      Keine Vorschläge. Artikel auswählen und „Vorschlag übernehmen" klicken.
                    </TableCell>
                  </TableRow>
                )}
                {filteredVorschlaege.map((v) => (
                  <TableRow key={v.id}
                    className={`cursor-pointer ${selectedVorschlag === v.id ? 'bg-blue-100' : 'hover:bg-muted/50'}`}
                    onClick={() => setSelectedVorschlag(v.id)}>
                    <TableCell className="font-mono text-xs">{v.liefNr}</TableCell>
                    <TableCell>{v.name}</TableCell>
                    <TableCell className="font-mono text-xs">{v.artikelNr}</TableCell>
                    <TableCell>{v.liefArt}</TableCell>
                    <TableCell className="text-right">{v.menge.toFixed(3)}</TableCell>
                    <TableCell>{v.einheit}</TableCell>
                    <TableCell className="text-right">{v.einhPreis.toFixed(4)}</TableCell>
                    <TableCell>{v.preisEi}</TableCell>
                    <TableCell className="text-right">{v.betrag.toFixed(2)}</TableCell>
                    <TableCell>{v.kontraktNr}</TableCell>
                    <TableCell>{v.niederlassung}</TableCell>
                    <TableCell>{v.lagerhalle}</TableCell>
                    <TableCell>{v.bediener}</TableCell>
                    <TableCell>{v.datum}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          {/* Summen-Zeile */}
          {filteredVorschlaege.length > 0 && (
            <div className="flex justify-end gap-8 mt-2 text-sm border-t pt-2">
              <span className="text-muted-foreground">min. Best.-Wert:</span>
              <span className="font-medium w-24 text-right">–</span>
              <span className="text-muted-foreground">Ges.Best.:</span>
              <span className="font-bold w-24 text-right">{gesamtBestWert.toFixed(2)} EUR</span>
            </div>
          )}
        </Card>
      </div>

      {/* Bottom Toolbar */}
      <div className="border-t bg-white px-4 py-2 flex items-center gap-3">
        <Button variant="outline" size="sm" className="gap-2"
          onClick={() => void loadData()} disabled={loading}>
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Aufbereiten
        </Button>
        <Button variant="outline" size="sm" className="gap-2"
          onClick={() => {
            if (!selectedVorschlag) { push('Bitte einen Vorschlag auswählen'); return }
            setVorschlaege((prev) => prev.filter((v) => v.id !== selectedVorschlag))
            setSelectedVorschlag(null)
          }}>
          <Trash2 className="h-4 w-4" />
          Pos. löschen
        </Button>
        <Button variant="outline" size="sm" className="gap-2"
          onClick={() => push('Manuelle Pos.: nicht implementiert')}>
          <Plus className="h-4 w-4" />
          Manuelle Pos.
        </Button>
        <Button variant="outline" size="sm" className="gap-2"
          onClick={() => push('Calc: nicht implementiert')}>
          <Calculator className="h-4 w-4" />
          Calc
        </Button>
        <Button variant="default" size="sm" className="gap-2"
          onClick={handleBestellungErstellen}>
          Bestellung erstellen
        </Button>
        <Button variant="outline" size="sm"
          onClick={() => push('Anfrage erstellen: nicht implementiert')}>
          Anfrage erstellen
        </Button>
        <div className="ml-auto">
          <Button variant="outline" onClick={() => navigate('/einkauf')} size="sm">
            Schließen
          </Button>
        </div>
      </div>
    </div>
  )
}
