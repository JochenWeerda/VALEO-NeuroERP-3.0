/**
 * Einkauf-Anfrage-Erfassung
 * 1:1 Nachbau der zvoove ANFRAGE-Maske
 */

import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Card } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { DmsAnhangDialog } from '@/components/dms/DmsAnhangDialog'
import { ArtikelSuchDialog } from '@/components/sales/ArtikelSuchDialog'
import { apiClient } from '@/lib/api-client'
import { useAuth } from '@/hooks/useAuth'
import { useGlobalShortcutsWithVoice } from '@/features/ki-usability'
import { ShortcutHintButton } from '@/components/shortcuts/ShortcutHelpPanel'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { isRecord, numberValue, recordArrayFromResponse, stringValue } from '@/lib/record-utils'
import {
  ChevronLeft, ChevronRight, MoreHorizontal, Check, Printer,
  Save, Trash2, FileText, Folder, Search, Send,
} from 'lucide-react'

// ==================== Types ====================

type Lieferant = {
  id: string
  lieferantNr: string
  name: string
  kreditorAccount: string
  address?: { street?: string; postalCode?: string; city?: string; phone?: string }
}

type AnfragePosition = {
  posNr: number
  artikelNr: string
  artikelId: string | null
  lieferantArtikelNr: string
  bezeichnung: string
  bezeichnung2: string
  gebindeMenge: number
  gebindeEinheit: string
  bestellMenge: number
  einheit: string
  einhPreis: number
  preisEinheit: number
  bestellWert: number
  kontraktNr: string
  lager: string
  lagerhalle: string
  lagerfach: string
  info: string
}

type AnfrageState = {
  id: string | null
  anfrageNr: string
  anfrageDat: string
  bediener: string
  bemerkung: string
  niederlassung: string
  kostenstelle: string
  kommission: string
  geplLieferDatum: string
  ladeTerminAb: string
  ladeDatum: string
  erledigt: boolean
  lieferant: Lieferant | null
  positionen: AnfragePosition[]
  aktivePositionIndex: number | null
}

type CurrentAnfragePos = {
  posNr: number
  artikelNr: string
  artikelId: string | null
  lieferantArtikelNr: string
  artikelBezeichnung: string
  artikelBezeichnung2: string
  gebindeMenge: number
  gebindeEinheit: string
  bestellMenge: number
  einheit: string
  einhPreis: number
  preisEinheit: number
  kontraktNr: string
  lager: string
}

// ==================== Lieferant-Suche Dialog (inline) ====================

function LieferantSuchDialog({
  open, onClose, onSelect,
}: {
  open: boolean; onClose: () => void; onSelect: (l: Lieferant) => void
}): JSX.Element {
  const [search, setSearch] = useState('')
  const [results, setResults] = useState<Lieferant[]>([])
  const [loading, setLoading] = useState(false)

  const doSearch = async (): Promise<void> => {
    if (!search.trim()) return
    setLoading(true)
    try {
      const response = await apiClient.get<Record<string, unknown>[]>('/api/v1/crm/customers/', {
        params: { search: search.trim(), limit: 30 },
      })
      setResults(recordArrayFromResponse(response.data).map(c => ({
        id: stringValue(c.id),
        lieferantNr: stringValue(c.customer_number),
        name: stringValue(c.company_name, stringValue(c.name)),
        kreditorAccount: stringValue(c.customer_number),
        address: isRecord(c.address) ? c.address : undefined,
      })))
    } catch { setResults([]) }
    finally { setLoading(false) }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader><DialogTitle>Lieferant suchen</DialogTitle></DialogHeader>
        <div className="flex gap-2 mb-3">
          <Input value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Name oder Kreditor-Kto. ..." className="flex-1"
            onKeyDown={(e) => e.key === 'Enter' && void doSearch()} autoFocus />
          <Button onClick={() => void doSearch()} disabled={loading} className="gap-1">
            <Search className="h-4 w-4" />Suchen
          </Button>
        </div>
        <div className="max-h-72 overflow-y-auto border rounded">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-28">Kreditor-Kto.</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Ort</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {results.length === 0 && (
                <TableRow><TableCell colSpan={3} className="text-center text-muted-foreground py-4">
                  {search ? 'Keine Ergebnisse' : 'Suchbegriff eingeben'}
                </TableCell></TableRow>
              )}
              {results.map((l) => (
                <TableRow key={l.id} className="cursor-pointer hover:bg-muted"
                  onClick={() => { onSelect(l); onClose() }}>
                  <TableCell className="font-mono">{l.kreditorAccount}</TableCell>
                  <TableCell>{l.name}</TableCell>
                  <TableCell>{l.address?.city || '—'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Abbrechen</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ==================== Main Component ====================

export default function AnfrageErfassungPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const push = (msg: string) => toast({ title: msg })
  const { user } = useAuth()
  const { id: anfrageId } = useParams<{ id?: string }>()

  const today = (): string => {
    const d = new Date()
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }

  const generateAnfrageNr = (): string => {
    const y = new Date().getFullYear()
    return `ANF-${y}-${Date.now().toString(36).toUpperCase().slice(-5)}`
  }

  const getBediener = (): string => {
    if (!user) return 'SYSTEM'
    return user.name?.split(' ').map((n) => n[0]).join('').toUpperCase().substring(0, 2) || 'SY'
  }

  const [state, setState] = useState<AnfrageState>({
    id: null, anfrageNr: generateAnfrageNr(), anfrageDat: today(),
    bediener: getBediener(), bemerkung: '', niederlassung: '', kostenstelle: '', kommission: '',
    geplLieferDatum: today(), ladeTerminAb: today(), ladeDatum: today(),
    erledigt: false, lieferant: null, positionen: [], aktivePositionIndex: null,
  })

  const [currentPos, setCurrentPos] = useState<CurrentAnfragePos>({
    posNr: 10, artikelNr: '', artikelId: null, lieferantArtikelNr: '',
    artikelBezeichnung: '', artikelBezeichnung2: '', gebindeMenge: 0,
    gebindeEinheit: '', bestellMenge: 0, einheit: '', einhPreis: 0,
    preisEinheit: 1, kontraktNr: '', lager: '',
  })

  const [posTab, setPosTab] = useState<'positionen' | 'angebot' | 'zahlungsbed' | 'zusatz'>('positionen')
  const [showLieferantDialog, setShowLieferantDialog] = useState(false)
  const [showArticleDialog, setShowArticleDialog] = useState(false)
  const [showAttachmentDialog, setShowAttachmentDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (user) setState((p) => ({ ...p, bediener: getBediener() }))
  }, [user])

  useEffect(() => {
    if (!anfrageId) return
    void (async () => {
      try {
        const response = await apiClient.get<Record<string, unknown>>(`/api/v1/einkauf/anfragen/${anfrageId}`)
        const data = response.data
        setState((p) => ({
          ...p, id: stringValue(data.id) || null, anfrageNr: stringValue(data.anfrage_nr),
          anfrageDat: stringValue(data.anfrage_datum).substring(0, 10) || today(),
          niederlassung: stringValue(data.niederlassung),
          erledigt: data.erledigt === true,
          lieferant: data.lieferant_id
            ? { id: stringValue(data.lieferant_id), lieferantNr: stringValue(data.lieferant_id), name: stringValue(data.lieferant_name), kreditorAccount: stringValue(data.lieferant_id) }
            : null,
        }))
        push('Anfrage geladen')
      } catch (_rawErr: unknown) {
        const err = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        push(`Fehler beim Laden: ${err.response?.data?.detail || err.message}`)
      }
    })()
  }, [anfrageId])

  const summen = useMemo(() => {
    const gesamt = state.positionen.reduce((s, p) => s + p.bestellWert, 0)
    const gewicht = 0
    return { gesamt, gewicht }
  }, [state.positionen])

  const handleArticleSelect = (article: Record<string, unknown>): void => {
    setCurrentPos((p) => ({
      ...p,
      artikelNr: stringValue(article.article_number, stringValue(article.articleNumber)),
      artikelId: stringValue(article.id) || null,
      artikelBezeichnung: stringValue(article.name),
      artikelBezeichnung2: stringValue(article.description),
      einheit: stringValue(article.unit, 'Stk'),
      einhPreis: numberValue(article.purchase_price, numberValue(article.sales_price)),
    }))
  }

  const handlePositionOK = (): void => {
    if (!currentPos.artikelNr || !currentPos.bestellMenge) {
      push('Bitte Artikel und Bestellmenge eingeben')
      return
    }
    const bestellWert = currentPos.einhPreis * currentPos.bestellMenge
    const pos: AnfragePosition = {
      posNr: currentPos.posNr, artikelNr: currentPos.artikelNr,
      artikelId: currentPos.artikelId, lieferantArtikelNr: currentPos.lieferantArtikelNr,
      bezeichnung: currentPos.artikelBezeichnung, bezeichnung2: currentPos.artikelBezeichnung2,
      gebindeMenge: currentPos.gebindeMenge, gebindeEinheit: currentPos.gebindeEinheit,
      bestellMenge: currentPos.bestellMenge, einheit: currentPos.einheit,
      einhPreis: currentPos.einhPreis, preisEinheit: currentPos.preisEinheit,
      bestellWert, kontraktNr: currentPos.kontraktNr, lager: currentPos.lager,
      lagerhalle: '', lagerfach: '', info: '',
    }
    setState((p) => ({ ...p, positionen: [...p.positionen, pos], aktivePositionIndex: p.positionen.length }))
    setCurrentPos((p) => ({
      ...p, posNr: p.posNr + 10, artikelNr: '', artikelId: null,
      artikelBezeichnung: '', artikelBezeichnung2: '', bestellMenge: 0, einhPreis: 0,
    }))
  }

  const handleSave = async (): Promise<string | null> => {
    if (!state.lieferant) { push('Bitte Lieferant auswählen'); return null }
    setLoading(true)
    try {
      const payload = {
        anfrage_nr: state.anfrageNr,
        anfrage_datum: state.anfrageDat,
        niederlassung: state.niederlassung || null,
        kostenstelle: state.kostenstelle || null,
        kommission: state.kommission || null,
        gepl_liefer_datum: state.geplLieferDatum,
        lade_termin_ab: state.ladeTerminAb,
        lade_datum: state.ladeDatum,
        erledigt: state.erledigt,
        bediener: state.bediener,
        lieferant_id: state.lieferant.id,
        lieferant_name: state.lieferant.name,
        positionen: state.positionen.map((p) => ({
          pos_nr: p.posNr, artikel_nr: p.artikelNr,
          lieferant_artikel_nr: p.lieferantArtikelNr || null,
          bezeichnung: p.bezeichnung, gebinde_menge: p.gebindeMenge,
          gebinde_einheit: p.gebindeEinheit || null,
          bestell_menge: p.bestellMenge, einheit: p.einheit,
          einh_preis: p.einhPreis, bestell_wert: p.bestellWert,
          kontrakt_nr: p.kontraktNr || null,
        })),
      }
      let resp: Record<string, unknown>
      if (state.id) {
        resp = (await apiClient.patch<Record<string, unknown>>(`/api/v1/einkauf/anfragen/${state.id}`, payload)).data
      } else {
        resp = (await apiClient.post<Record<string, unknown>>('/api/v1/einkauf/anfragen', payload)).data
      }
      setState((p) => ({ ...p, id: stringValue(resp.id) || null, anfrageNr: stringValue(resp.anfrage_nr, p.anfrageNr) }))
      push('Anfrage gespeichert')
      return stringValue(resp.id) || null
    } catch (_rawErr: unknown) {
        const err = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      push(`Fehler: ${err.response?.data?.detail || err.message}`)
      return null
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (): Promise<void> => {
    if (!state.id) {
      setState((p) => ({ ...p, id: null, anfrageNr: generateAnfrageNr(), positionen: [], aktivePositionIndex: null, lieferant: null }))
      setShowDeleteDialog(false)
      return
    }
    try {
      await apiClient.delete(`/api/v1/einkauf/anfragen/${state.id}`)
      push('Anfrage gelöscht')
      setShowDeleteDialog(false)
      navigate('/einkauf')
    } catch (_rawErr: unknown) {
        const err = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      push(`Fehler: ${err.response?.data?.detail || err.message}`)
    }
  }

  useGlobalShortcutsWithVoice({
    'open-customer-selection': () => setShowLieferantDialog(true),
    'open-article-selection': () => setShowArticleDialog(true),
    'confirm-position': () => handlePositionOK(),
    'save-document': () => void handleSave(),
    'delete-document': () => setShowDeleteDialog(true),
    'close-document': () => navigate(-1),
    cancel: () => { setShowLieferantDialog(false); setShowArticleDialog(false) },
  })

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <div className="bg-green-600 text-white px-4 py-2">
        <h1 className="text-lg font-bold">ANFRAGE</h1>
      </div>
      <ModuleToolbar backTarget="/einkauf" closeTarget="/einkauf" title="Anfrage" />
      <div className="flex-1 overflow-auto p-4">
        {/* Header-Bereich */}
        <Card className="mb-4 p-4">
          <div className="grid grid-cols-3 gap-6">
            {/* Linke Spalte: Lieferant */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-24 text-sm shrink-0">Kreditor-Kto.:</Label>
                <Input value={state.lieferant?.kreditorAccount || ''} readOnly className="flex-1 h-8 bg-green-50" />
                <ShortcutHintButton shortcut="Strg+F1">
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"
                    onClick={() => setShowLieferantDialog(true)}>
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </ShortcutHintButton>
              </div>
              {/* Adress-Block */}
              <div className="border rounded p-2 min-h-[80px] text-sm space-y-0.5">
                {state.lieferant ? (
                  <>
                    <div className="font-medium">{state.lieferant.name}</div>
                    {state.lieferant.address?.street && <div>{state.lieferant.address.street}</div>}
                    {(state.lieferant.address?.postalCode || state.lieferant.address?.city) && (
                      <div>{[state.lieferant.address.postalCode, state.lieferant.address.city].filter(Boolean).join(' ')}</div>
                    )}
                  </>
                ) : (
                  <div className="text-muted-foreground italic text-xs">Kein Lieferant</div>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-24 text-sm shrink-0">Lieferant-Nr.:</Label>
                <Input value={state.lieferant?.lieferantNr || ''} readOnly className="flex-1 h-8" />
              </div>
              <div className="flex items-center gap-2 pt-1">
                <a href="#" className="text-sm text-blue-600 underline hover:text-blue-800"
                  onClick={async (e) => {
                    e.preventDefault()
                    try {
                      const items = await apiClient.get<{ id: string }[]>('/api/v1/einkauf/anfragen')
                      const idx = anfrageId ? items.findIndex(a => a.id === anfrageId) : -1
                      if (idx + 1 < items.length) {
                        navigate(`/einkauf/anfragen/${items[idx + 1].id}`)
                      } else {
                        push('Kein vorheriger Auftrag vorhanden.')
                      }
                    } catch { push('Anfragen konnten nicht geladen werden.') }
                  }}>
                  &gt;&gt; wie vorh. Best. (F11)
                </a>
              </div>
              <div className="flex items-center gap-2">
                <a href="#" className="text-sm text-blue-600 underline hover:text-blue-800"
                  onClick={(e) => {
                    e.preventDefault()
                    if (state.lieferant?.id) navigate(`/crm/lieferanten/stamm/${state.lieferant.id}`)
                    else push('Bitte zuerst einen Lieferanten auswählen.')
                  }}>
                  Lieferanten-Stamm
                </a>
              </div>
            </div>

            {/* Mittlere Spalte */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">Niederlassung:</Label>
                <Input value={state.niederlassung}
                  onChange={(e) => setState((p) => ({ ...p, niederlassung: e.target.value }))}
                  className="flex-1 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">Kostenstelle:</Label>
                <Input value={state.kostenstelle}
                  onChange={(e) => setState((p) => ({ ...p, kostenstelle: e.target.value }))}
                  className="flex-1 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">Kommission:</Label>
                <Input value={state.kommission}
                  onChange={(e) => setState((p) => ({ ...p, kommission: e.target.value }))}
                  className="flex-1 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">gepl. Liefer-Datum:</Label>
                <Input type="date" value={state.geplLieferDatum}
                  onChange={(e) => setState((p) => ({ ...p, geplLieferDatum: e.target.value }))}
                  className="flex-1 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">Lade-Termin ab:</Label>
                <Input type="date" value={state.ladeTerminAb}
                  onChange={(e) => setState((p) => ({ ...p, ladeTerminAb: e.target.value }))}
                  className="flex-1 h-8" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">Lade-Datum:</Label>
                <Input type="date" value={state.ladeDatum}
                  onChange={(e) => setState((p) => ({ ...p, ladeDatum: e.target.value }))}
                  className="flex-1 h-8" />
              </div>
            </div>

            {/* Rechte Spalte */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Anfrage-Nr.:</Label>
                <Input value={state.anfrageNr} readOnly className="flex-1 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><MoreHorizontal className="h-4 w-4" /></Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><ChevronLeft className="h-4 w-4" /></Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><ChevronRight className="h-4 w-4" /></Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Anfrage-Dat.:</Label>
                <Input type="date" value={state.anfrageDat}
                  onChange={(e) => setState((p) => ({ ...p, anfrageDat: e.target.value }))}
                  className="flex-1 h-8" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Bediener:</Label>
                <Input value={state.bediener} readOnly className="flex-1 h-8" />
              </div>
              <div className="flex items-center gap-2 pt-1">
                <Checkbox checked={state.erledigt}
                  onCheckedChange={(v) => setState((p) => ({ ...p, erledigt: v === true }))} />
                <Label className="text-sm">Erledigt</Label>
              </div>
            </div>
          </div>
        </Card>

        {/* Positions-Tabs */}
        <Card className="mb-4 p-4">
          <Tabs value={posTab} onValueChange={(v) => setPosTab(v as typeof posTab)}>
            <TabsList className="mb-3">
              <TabsTrigger value="positionen">POSITIONEN</TabsTrigger>
              <TabsTrigger value="angebot">ANFRAGE / ANGEBOT</TabsTrigger>
              <TabsTrigger value="zahlungsbed">ZAHLUNGSBEDINGUNGEN</TabsTrigger>
              <TabsTrigger value="zusatz">ZUSÄTZLICHE ANGABEN</TabsTrigger>
            </TabsList>

            <TabsContent value="positionen">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-14">Pos.-Nr.</TableHead>
                      <TableHead className="w-24">Artikel-Nr.</TableHead>
                      <TableHead className="w-24">Lief.-Artikel</TableHead>
                      <TableHead className="w-36">Bezeichnung 1</TableHead>
                      <TableHead className="w-36">Bezeichnung 2</TableHead>
                      <TableHead className="w-20">Geb.-Menge</TableHead>
                      <TableHead className="w-16">Geb.-Ei.</TableHead>
                      <TableHead className="w-24">Best.-Menge</TableHead>
                      <TableHead className="w-16">Einheit</TableHead>
                      <TableHead className="w-24">Einh.-Pr.</TableHead>
                      <TableHead className="w-20">Preis-Ei.</TableHead>
                      <TableHead className="w-28">Bestell-Wert</TableHead>
                      <TableHead className="w-24">Kontrakt-Nr.</TableHead>
                      <TableHead className="w-16">Lager</TableHead>
                      <TableHead className="w-20">Lagerhalle</TableHead>
                      <TableHead className="w-20">Lagerfach</TableHead>
                      <TableHead className="w-20">Info</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {state.positionen.map((pos, idx) => (
                      <TableRow key={idx}
                        className={state.aktivePositionIndex === idx ? 'bg-green-100' : 'cursor-pointer hover:bg-muted/50'}
                        onClick={() => setState((p) => ({ ...p, aktivePositionIndex: idx }))}>
                        <TableCell>{pos.posNr}</TableCell>
                        <TableCell>{pos.artikelNr}</TableCell>
                        <TableCell>{pos.lieferantArtikelNr}</TableCell>
                        <TableCell>{pos.bezeichnung}</TableCell>
                        <TableCell>{pos.bezeichnung2}</TableCell>
                        <TableCell>{pos.gebindeMenge || ''}</TableCell>
                        <TableCell>{pos.gebindeEinheit}</TableCell>
                        <TableCell>{pos.bestellMenge}</TableCell>
                        <TableCell>{pos.einheit}</TableCell>
                        <TableCell>{pos.einhPreis.toFixed(2)}</TableCell>
                        <TableCell>{pos.preisEinheit}</TableCell>
                        <TableCell>{pos.bestellWert.toFixed(2)}</TableCell>
                        <TableCell>{pos.kontraktNr}</TableCell>
                        <TableCell>{pos.lager}</TableCell>
                        <TableCell>{pos.lagerhalle}</TableCell>
                        <TableCell>{pos.lagerfach}</TableCell>
                        <TableCell>{pos.info}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>

            <TabsContent value="angebot">
              <div className="py-4 space-y-3 text-sm">
                {state.positionen.length === 0 ? (
                  <p className="text-muted-foreground">Noch keine Positionen erfasst — Angebots-Vergleich wird nach Positionserfassung verfügbar.</p>
                ) : (
                  <>
                  <div className="flex items-center gap-2 mb-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        if (state.id) {
                          navigate(`/einkauf/rfq-bids/${state.id}`)
                        } else {
                          push('Bitte zuerst Anfrage speichern, dann Angebots-Vergleich öffnen.')
                        }
                      }}
                    >
                      Angebots-Vergleich öffnen
                    </Button>
                  </div>
                  <table className="w-full text-xs border-collapse">
                    <thead><tr className="bg-gray-100">
                      <th className="border px-2 py-1 text-left">Pos.</th>
                      <th className="border px-2 py-1 text-left">Artikel</th>
                      <th className="border px-2 py-1 text-right">Menge</th>
                      <th className="border px-2 py-1 text-right">Einh.-Preis</th>
                      <th className="border px-2 py-1 text-right">Gesamt</th>
                    </tr></thead>
                    <tbody>{state.positionen.map((p) => (
                      <tr key={p.posNr}>
                        <td className="border px-2 py-1">{p.posNr}</td>
                        <td className="border px-2 py-1">{p.bezeichnung || p.artikelNr}</td>
                        <td className="border px-2 py-1 text-right">{p.bestellMenge} {p.einheit}</td>
                        <td className="border px-2 py-1 text-right">{p.einhPreis.toFixed(2)} €</td>
                        <td className="border px-2 py-1 text-right">{p.bestellWert.toFixed(2)} €</td>
                      </tr>
                    ))}</tbody>
                  </table>
                  </>
                )}
              </div>
            </TabsContent>

            <TabsContent value="zahlungsbed">
              <div className="grid grid-cols-3 gap-4 text-sm pt-2">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Input placeholder="Tage" className="w-16 h-8" />
                    <Input placeholder="% Skonto" className="w-20 h-8" />
                    <Label className="text-xs">Fällig ab</Label>
                    <Input type="date" className="flex-1 h-8" />
                  </div>
                  <div className="flex items-center gap-2">
                    <Input placeholder="Tage" className="w-16 h-8" />
                    <Input placeholder="% Skonto" className="w-20 h-8" />
                    <Label className="text-xs">Festes Valuta:</Label>
                    <Input type="date" className="flex-1 h-8" />
                  </div>
                  <div className="flex items-center gap-2">
                    <Input placeholder="Tage" className="w-16 h-8" />
                    <Label className="text-xs">netto Kasse</Label>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="zusatz">
              <div className="grid grid-cols-2 gap-4 text-sm pt-2">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label className="w-36 text-xs shrink-0">Auftragstext:</Label>
                    <textarea className="flex-1 border rounded p-1 text-xs h-16"
                      value={state.bemerkung ?? ''}
                      onChange={(e) => setState((p) => ({ ...p, bemerkung: e.target.value }))} />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="w-36 text-xs shrink-0">Interne Notiz:</Label>
                    <textarea className="flex-1 border rounded p-1 text-xs h-16" />
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label className="w-36 text-xs shrink-0">Ihr Zeichen:</Label>
                    <Input className="flex-1 h-8" />
                  </div>
                  <div className="flex items-center gap-2">
                    <Label className="w-36 text-xs shrink-0">Unser Zeichen:</Label>
                    <Input className="flex-1 h-8" />
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </Card>

        {/* Positions-Details Eingabe */}
        <Card className="mb-4 p-4">
          <h2 className="mb-2 font-semibold text-sm">Positions-Eingabe</h2>
          <div className="grid grid-cols-6 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">Pos.-Nr.:</Label>
              <Input value={currentPos.posNr} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Artikel-Nr.:</Label>
              <div className="flex gap-1">
                <Input value={currentPos.artikelNr} readOnly className="flex-1 h-8" />
                <ShortcutHintButton shortcut="Strg+F2">
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0"
                    onClick={() => setShowArticleDialog(true)}>
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </ShortcutHintButton>
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Lief.-Artikel-Nr.:</Label>
              <Input value={currentPos.lieferantArtikelNr}
                onChange={(e) => setCurrentPos((p) => ({ ...p, lieferantArtikelNr: e.target.value }))}
                className="h-8" />
            </div>
            <div className="space-y-1 col-span-2">
              <Label className="text-xs">Bezeichnung:</Label>
              <Input value={currentPos.artikelBezeichnung} readOnly className="h-8" />
              <Input value={currentPos.artikelBezeichnung2} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Gebinde-Menge:</Label>
              <Input type="number" value={currentPos.gebindeMenge}
                onChange={(e) => setCurrentPos((p) => ({ ...p, gebindeMenge: Number(e.target.value) }))}
                className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Best.-Menge:</Label>
              <Input type="number" value={currentPos.bestellMenge}
                onChange={(e) => setCurrentPos((p) => ({ ...p, bestellMenge: Number(e.target.value) }))}
                className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Einheit:</Label>
              <Input value={currentPos.einheit} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Einh.-Preis:</Label>
              <Input type="number" step="0.01" value={currentPos.einhPreis}
                onChange={(e) => setCurrentPos((p) => ({ ...p, einhPreis: Number(e.target.value) }))}
                className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Preis je:</Label>
              <Input type="number" value={currentPos.preisEinheit}
                onChange={(e) => setCurrentPos((p) => ({ ...p, preisEinheit: Number(e.target.value) }))}
                className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Kontrakt-Nr.:</Label>
              <Input value={currentPos.kontraktNr}
                onChange={(e) => setCurrentPos((p) => ({ ...p, kontraktNr: e.target.value }))}
                className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Lager:</Label>
              <Input value={currentPos.lager}
                onChange={(e) => setCurrentPos((p) => ({ ...p, lager: e.target.value }))}
                className="h-8" />
            </div>
            <div className="col-span-6 flex justify-end">
              <ShortcutHintButton shortcut="Strg+F3">
                <Button onClick={handlePositionOK} className="h-8 gap-1">
                  <Check className="h-4 w-4" />Zeile OK
                </Button>
              </ShortcutHintButton>
            </div>
          </div>
        </Card>

        {/* Summen-Zeile */}
        <Card className="mb-4 p-4">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2">
              <Label className="text-xs">Summe Gewicht:</Label>
              <Input value={`${summen.gewicht.toFixed(2)} kg`} readOnly className="h-8 w-28" />
            </div>
            <div className="flex items-center gap-2 ml-auto">
              <Label className="text-xs">Anfrage-Summe:</Label>
              <Input value={summen.gesamt.toFixed(2)} readOnly className="h-8 w-32" />
              <span className="text-sm font-medium">EUR</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Bottom Toolbar */}
      <div className="border-t bg-white px-4 py-2 flex items-center justify-between">
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="gap-2"
            onClick={async () => {
              if (!state.lieferant) { push('Bitte zuerst einen Lieferanten auswählen.'); return }
              if (state.positionen.length === 0) { push('Bitte zuerst Positionen erfassen.'); return }
              try {
                const payload = {
                  lieferant_id: state.lieferant.id,
                  lieferant_name: state.lieferant.name,
                  positionen: state.positionen.map((p) => ({ artikel_nr: p.artikelNr, bezeichnung: p.bezeichnung, menge: p.bestellMenge, einheit: p.einheit })),
                  anfragedatum: state.anfrageDat,
                }
                const resp = state.id
                  ? await apiClient.patch(`/api/v1/einkauf/anfragen/${state.id}`, payload)
                  : await apiClient.post('/api/v1/einkauf/anfragen', payload)
                push(`Lieferanten-Angebot gesendet (${String((resp as Record<string, unknown>)?.anfrageNr ?? 'OK')})`)
              } catch (_rawErr: unknown) {
                const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
                push(`Fehler: ${e.response?.data?.detail ?? e.message}`)
              }
            }}>
            <Send className="h-4 w-4" />Lieferanten-Angebot
          </Button>
          <Button variant="outline" size="sm" className="gap-2"
            onClick={() => window.print()}>
            <Printer className="h-4 w-4" />Drucken
          </Button>
          <Button variant="outline" size="sm" className="gap-2"
            onClick={() => setShowAttachmentDialog(true)}>
            <FileText className="h-4 w-4" />Unterlagen
          </Button>
          <Button variant="outline" size="sm" className="gap-2"
            onClick={() => setShowAttachmentDialog(true)}>
            <Folder className="h-4 w-4" />Dateien
          </Button>
          <Button variant="outline" size="sm" className="gap-2 text-status-error"
            onClick={() => setShowDeleteDialog(true)}>
            <Trash2 className="h-4 w-4" />Anfrage löschen
          </Button>
        </div>
        <div className="flex gap-2">
          <ShortcutHintButton shortcut="Strg+F4">
            <Button onClick={() => void handleSave()} size="sm" className="gap-2" disabled={loading}>
              <Save className="h-4 w-4" />Speichern
            </Button>
          </ShortcutHintButton>
          <Button variant="outline" onClick={() => navigate('/einkauf')} size="sm">
            Schließen
          </Button>
        </div>
      </div>

      {/* Dialoge */}
      <LieferantSuchDialog open={showLieferantDialog} onClose={() => setShowLieferantDialog(false)}
        onSelect={(l) => setState((p) => ({ ...p, lieferant: l }))} />
      <ArtikelSuchDialog open={showArticleDialog} onClose={() => setShowArticleDialog(false)}
        onSelect={handleArticleSelect} />
      <DmsAnhangDialog open={showAttachmentDialog} onClose={() => setShowAttachmentDialog(false)}
        businessObjectType="einkauf_anfrage" businessObjectId={state.id}
        title="UNTERLAGEN / DATEIEN — ANFRAGE" />
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="max-w-sm">
          <DialogHeader><DialogTitle>Anfrage löschen?</DialogTitle></DialogHeader>
          <div className="py-2 text-sm">
            {state.id
              ? <>Anfrage <strong>{state.anfrageNr}</strong> wird gelöscht.</>
              : 'Formular wird geleert.'}
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


