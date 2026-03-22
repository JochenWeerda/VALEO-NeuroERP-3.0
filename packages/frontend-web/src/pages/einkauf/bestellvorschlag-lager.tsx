/**
 * Bestell-Vorschläge aus Bestand/Lager
 * 1:1 Nachbau der zvoove BESTELL-VORSCHLÄGE-Maske (Lager-Variante)
 */

import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useToast } from '@/components/ui/toast-provider'
import { apiClient } from '@/lib/axios'
import { MoreHorizontal, RefreshCw, Plus, Trash2, Calculator } from 'lucide-react'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AgentProcessPanel, AgentSuggestionBadge } from '@/components/agent'

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
  // aus Engine-Response
  lieferant_name?: string
  lieferant_id?: string
  letzter_preis?: number
  letzter_kauf_datum?: string
  bedarf?: number
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
  const filterRef = useRef<HTMLInputElement | null>(null)

  const shortcuts = buildCoreMaskShortcuts({
    onRefresh: () => { void loadData() },
    onSearch: () => filterRef.current?.focus(),
    onCancel: () => navigate('/einkauf'),
  })
  useKeyboardShortcuts(shortcuts)

  const loadData = async (): Promise<void> => {
    setLoading(true)
    try {
      const p = new URLSearchParams()
      if (filterNiederlassung) p.set('niederlassung_id', filterNiederlassung)
      if (filterArtikelGruppe) p.set('artikelgruppe', filterArtikelGruppe)
      if (filterArtikelNr) p.set('artikelNr', filterArtikelNr)
      p.set('nur_unter_meldebestand', 'false')
      const qs = p.toString() ? `?${p.toString()}` : ''
      const data = await apiClient.get<any[]>(`/api/v1/einkauf/bestellvorschlaege/lager${qs}`)
      const rows = (data || []).map((r: any) => ({
        id: r.article_id,
        artikelNr: r.artikel_nr || '',
        bezeichnung: r.artikel_bezeichnung || '',
        verfBestand: r.ist_bestand ?? 0,
        bestandMin: r.mindestbestand ?? 0,
        bestandMax: r.maximalbestand ?? 0,
        vorschlagMenge: r.vorschlag_menge ?? 0,
        einheit: r.einheit || '',
        lagerhalle: '',
        niederlassung: '',
        // Für Detailpanel
        lieferant_name: r.lieferant_name,
        lieferant_id: r.lieferant_id,
        letzter_preis: r.letzter_preis,
        letzter_kauf_datum: r.letzter_kauf_datum,
        bedarf: r.bedarf ?? 0,
      }))
      setArtikel(rows)
    } catch {
      setArtikel([])
    } finally {
      setLoading(false)
    }
  }

  const loadArtikelDetails = async (id: string): Promise<void> => {
    // Details werden aus der Hauptliste befüllt (lieferant_name, letzter_preis, etc.)
    const selected = artikel.find(a => a.id === id)
    if (selected) {
      setLieferanten(selected.lieferant_name
        ? [{ liefNr: selected.lieferant_id || '', name: selected.lieferant_name }]
        : [])
      setKontrakte([])
      setLetzteEinkaeufe(selected.letzter_kauf_datum ? [{
        belegNr: '',
        liefNr: selected.lieferant_id || '',
        name: selected.lieferant_name || '',
        menge: selected.vorschlagMenge,
        einhPreis: selected.letzter_preis ?? 0,
        netto: 0,
        datum: selected.letzter_kauf_datum,
        liefArt: '',
      }] : [])
      // Kontrakte nachladen
      try {
        const data = await apiClient.get<any[]>(
          `/api/v1/einkauf/kontrakte?lieferant_id=${encodeURIComponent(selected.lieferant_id || '')}&status=aktiv`
        )
        setKontrakte((data || []).map((k: any) => ({
          kontraktNr: k.kontraktnummer || '',
          lieferant: k.lieferant_id || '',
          restMenge: k.offene_menge ?? 0,
          einhPreis: 0,
          einheit: 't',
        })))
      } catch { /* ignore */ }
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

  const handleBestellungErstellen = async (): Promise<void> => {
    if (vorschlaege.length === 0) { push('Keine Vorschläge vorhanden'); return }
    // Vorschläge nach Lieferant gruppieren → eine Bestellung pro Lieferant
    const byLieferant = vorschlaege.reduce<Record<string, BestellVorschlag[]>>((acc, v) => {
      const key = v.liefNr || 'unbekannt'
      ;(acc[key] = acc[key] || []).push(v)
      return acc
    }, {})
    try {
      const created: string[] = []
      for (const [liefNr, positionen] of Object.entries(byLieferant)) {
        const res = await apiClient.post<{ bestellnummer?: string }>('/api/v1/einkauf/bestellungen', {
          lieferant_id: liefNr,
          lieferant_name: positionen[0].name,
          positionen: positionen.map((v) => ({
            artikel_nr: v.artikelNr,
            menge: v.menge,
            einheit: v.einheit,
            einzelpreis: v.einhPreis,
            kontrakt_nr: v.kontraktNr || null,
          })),
          niederlassung: positionen[0].niederlassung,
          bestelldatum: new Date().toISOString().slice(0, 10),
        })
        created.push(res.bestellnummer ?? liefNr)
      }
      push(`${created.length} Bestellung(en) erstellt: ${created.join(', ')}`)
      setVorschlaege([])
    } catch (e: any) {
      push(`Fehler beim Erstellen: ${e.response?.data?.detail ?? e.message}`)
    }
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
        <AgentProcessPanel domain="einkauf" />
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
              <Input ref={filterRef} value={filterArtikelNr} onChange={(e) => setFilterArtikelNr(e.target.value)}
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

        {/* Agent-Vorschlag: Bestellvorschlag-Assistent */}
        {selectedArtikel && (
          <AgentSuggestionBadge<{ lieferant?: string; menge?: number }>
            capabilityKey="bestellvorschlag_assistant"
            parameters={{
              artikel_id: selectedArtikel,
              artikel_nr: artikel.find((a) => a.id === selectedArtikel)?.artikelNr,
              bezeichnung: artikel.find((a) => a.id === selectedArtikel)?.bezeichnung,
            }}
            label="Bestellvorschlag analysieren"
            renderSuggestion={(s) => (
              <span>Lieferant: <strong>{s.lieferant ?? '—'}</strong> / Menge: <strong>{s.menge ?? '—'}</strong></span>
            )}
            onAccept={(s) => {
              if (s.lieferant) setLieferantText(s.lieferant)
              if (s.menge) setBestellMenge(String(s.menge))
            }}
          />
        )}

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
          onClick={() => {
            const artNr = prompt('Artikelnummer:')
            if (!artNr) return
            const menge = parseFloat(prompt('Menge:') ?? '0')
            if (!menge) return
            setVorschlaege((prev) => [...prev, {
              id: crypto.randomUUID(), liefNr: '', name: 'Manuell', artikelNr: artNr,
              liefArt: 'frei', menge, einheit: 'kg', einhPreis: 0, preisEi: 'kg',
              betrag: 0, kontraktNr: '', niederlassung: '', lagerhalle: '', bediener: '', datum: new Date().toISOString().slice(0,10)
            }])
            push('Manuelle Position hinzugefügt')
          }}>
          <Plus className="h-4 w-4" />
          Manuelle Pos.
        </Button>
        <Button variant="outline" size="sm" className="gap-2"
          onClick={() => {
            const sel = vorschlaege.find((v) => v.id === selectedVorschlag)
            if (!sel) { push('Bitte Position auswählen'); return }
            const neu = parseFloat(prompt(`Menge für ${sel.artikelNr} (aktuell: ${sel.menge}):`) ?? '')
            if (!isNaN(neu) && neu > 0) {
              setVorschlaege((prev) => prev.map((v) => v.id === selectedVorschlag ? { ...v, menge: neu, betrag: neu * v.einhPreis } : v))
            }
          }}>
          <Calculator className="h-4 w-4" />
          Calc
        </Button>
        <Button variant="default" size="sm" className="gap-2"
          onClick={handleBestellungErstellen}>
          Bestellung erstellen
        </Button>
        <Button variant="outline" size="sm"
          onClick={async () => {
            if (vorschlaege.length === 0) { push('Keine Vorschläge vorhanden'); return }
            try {
              await apiClient.post('/api/v1/einkauf/anfragen', {
                positionen: vorschlaege.map((v) => ({ artikel_nr: v.artikelNr, menge: v.menge, einheit: v.einheit })),
                anfragedatum: new Date().toISOString().slice(0, 10),
              })
              push('Anfrage erstellt und an Lieferanten weitergeleitet.')
            } catch (e: any) {
              push(`Fehler: ${(e as any).response?.data?.detail ?? (e as any).message}`)
            }
          }}>
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
