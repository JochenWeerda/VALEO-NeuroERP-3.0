/**
 * Einkauf-Rechnung-Eingang-Erfassung
 * 1:1 Nachbau der zvoove EINKAUF-RECHNUNG-Maske
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
import { useToast } from '@/components/ui/toast-provider'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { DmsAnhangDialog } from '@/components/dms/DmsAnhangDialog'
import { ArtikelSuchDialog } from '@/components/sales/ArtikelSuchDialog'
import { apiClient } from '@/lib/api-client'
import { useAuth } from '@/hooks/useAuth'
import { useGlobalShortcutsWithVoice } from '@/features/ki-usability'
import { ShortcutHintButton } from '@/components/shortcuts/ShortcutHelpPanel'
import {
  ChevronLeft, ChevronRight, ChevronUp, ChevronDown, MoreHorizontal, Check, Printer,
  Save, Trash2, FileText, Folder, Search, BookOpen,
} from 'lucide-react'

// ==================== Types ====================

type Lieferant = {
  id: string; name: string; kreditorAccount: string
  address?: { street?: string; postalCode?: string; city?: string; phone?: string }
}

type RechnungPosition = {
  posNr: number
  lieferscheinNr: string
  artikelNr: string
  artikelId: string | null
  lieferantArtikelNr: string
  bezeichnung: string
  bezeichnung2: string
  gebindeNr: string
  gebinde: number
  menge: number
  einheit: string
  einhPreis: number
  bruttoEinzel: number
  nettoBetrag: number
  mwstProzent: number
  bruttoBetrag: number
  niederlassung: string
  lagerhalle: string
  lagerfach: string
  chargenNr: string
  anerkennung: string
  serienNr: string
  kontraktNr: string
  streckeNr: string
  naBio: string
  kostenstelle: string
}

type RechnungState = {
  id: string | null
  belegNr: string
  rechnungNr: string
  rechnDatum: string
  buchDatum: string
  niederlassung: string
  kostenstelle: string
  bediener: string
  erledigt: boolean
  lieferant: Lieferant | null
  // Zahlungsbedingungen
  skonto1Tage: string; skonto1Prozent: string; skonto1FaelligAb: string
  skonto2Tage: string; skonto2Prozent: string; skonto2ValutaDatum: string
  nettoKasseTage: string
  positionen: RechnungPosition[]
  aktivePositionIndex: number | null
}

type CurrentRechnungPos = {
  posNr: number
  lieferscheinNr: string
  artikelNr: string
  artikelId: string | null
  lieferantArtikelNr: string
  artikelBezeichnung: string
  gebinde: number
  menge: number
  einheit: string
  mwstProzent: number
  niederlassung: string
  lagerhalle: string
  listenpreis: number
  rabatt: number
  nettoPreis: number
  nettoBetrag: number
  bruttoPreis: number
  bruttoBetrag: number
  kontraktNr: string
}

// ==================== Lieferant-Suche Dialog ====================

function LieferantSuchDialog({ open, onClose, onSelect }: {
  open: boolean; onClose: () => void; onSelect: (l: Lieferant) => void
}): JSX.Element {
  const [search, setSearch] = useState('')
  const [results, setResults] = useState<Lieferant[]>([])
  const [loading, setLoading] = useState(false)
  const doSearch = async (): Promise<void> => {
    if (!search.trim()) return
    setLoading(true)
    try {
      const data = await apiClient.get<any[]>('/api/v1/crm/customers', { params: { search: search.trim(), limit: 30 } })
      setResults((data || []).map((c: any) => ({
        id: c.id, name: c.company_name || c.name || '',
        kreditorAccount: c.customer_number || '', address: c.address,
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
                <TableHead>Name</TableHead><TableHead>Ort</TableHead>
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
        <DialogFooter><Button variant="outline" onClick={onClose}>Abbrechen</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ==================== Main Component ====================

export default function RechnungEingangErfassungPage(): JSX.Element {
  const navigate = useNavigate()
  const { push } = useToast()
  const { user } = useAuth()
  const { id: rechnungId } = useParams<{ id?: string }>()

  const today = (): string => {
    const d = new Date()
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }
  const generateBelegNr = (): string =>
    `RG-${new Date().getFullYear()}-${Date.now().toString(36).toUpperCase().slice(-5)}`

  const getBediener = (): string => {
    if (!user) return 'SY'
    return user.name?.split(' ').map((n) => n[0]).join('').toUpperCase().substring(0, 2) || 'SY'
  }

  const emptyState = (): RechnungState => ({
    id: null, belegNr: generateBelegNr(), rechnungNr: '', rechnDatum: today(), buchDatum: today(),
    niederlassung: '', kostenstelle: '', bediener: getBediener(), erledigt: false, lieferant: null,
    skonto1Tage: '', skonto1Prozent: '', skonto1FaelligAb: '',
    skonto2Tage: '', skonto2Prozent: '', skonto2ValutaDatum: '', nettoKasseTage: '',
    positionen: [], aktivePositionIndex: null,
  })

  const emptyPos = (nr: number): CurrentRechnungPos => ({
    posNr: nr, lieferscheinNr: '', artikelNr: '', artikelId: null, lieferantArtikelNr: '',
    artikelBezeichnung: '', gebinde: 0, menge: 0, einheit: '', mwstProzent: 19,
    niederlassung: '', lagerhalle: '', listenpreis: 0, rabatt: 0, nettoPreis: 0,
    nettoBetrag: 0, bruttoPreis: 0, bruttoBetrag: 0, kontraktNr: '',
  })

  const [state, setState] = useState<RechnungState>(emptyState)
  const [currentPos, setCurrentPos] = useState<CurrentRechnungPos>(emptyPos(10))
  const [headerTab, setHeaderTab] = useState<'lieferant' | 'zahlungsbed'>('lieferant')
  const [showLieferantDialog, setShowLieferantDialog] = useState(false)
  const [showArticleDialog, setShowArticleDialog] = useState(false)
  const [showAttachmentDialog, setShowAttachmentDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    if (user) setState((p) => ({ ...p, bediener: getBediener() }))
  }, [user])

  // Brutto/Netto neu berechnen
  useEffect(() => {
    const nettoPreis = currentPos.listenpreis * (1 - currentPos.rabatt / 100)
    const nettoBetrag = nettoPreis * currentPos.menge
    const bruttoPreis = nettoPreis * (1 + currentPos.mwstProzent / 100)
    const bruttoBetrag = bruttoPreis * currentPos.menge
    setCurrentPos((p) => ({ ...p, nettoPreis, nettoBetrag, bruttoPreis, bruttoBetrag }))
  }, [currentPos.listenpreis, currentPos.rabatt, currentPos.menge, currentPos.mwstProzent])

  const summen = useMemo(() => {
    const netto = state.positionen.reduce((s, p) => s + p.nettoBetrag, 0)
    const brutto = state.positionen.reduce((s, p) => s + p.bruttoBetrag, 0)
    const mwst1 = state.positionen.filter(p => p.mwstProzent === 19).reduce((s, p) => s + (p.bruttoBetrag - p.nettoBetrag), 0)
    const mwst2 = state.positionen.filter(p => p.mwstProzent !== 19).reduce((s, p) => s + (p.bruttoBetrag - p.nettoBetrag), 0)
    return { netto, mwst1, mwst2, brutto }
  }, [state.positionen])

  const handleArticleSelect = (article: any): void => {
    const ep = article.purchase_price || article.sales_price || 0
    setCurrentPos((p) => ({
      ...p, artikelNr: article.article_number || '', artikelId: article.id || null,
      artikelBezeichnung: article.name || '', einheit: article.unit || 'Stk',
      listenpreis: ep, mwstProzent: article.mehrwertsteuer_prozent || 19,
    }))
  }

  const handlePositionOK = (): void => {
    if (!currentPos.artikelNr || !currentPos.menge) { push('Bitte Artikel und Menge eingeben'); return }
    const pos: RechnungPosition = {
      posNr: currentPos.posNr, lieferscheinNr: currentPos.lieferscheinNr,
      artikelNr: currentPos.artikelNr, artikelId: currentPos.artikelId,
      lieferantArtikelNr: currentPos.lieferantArtikelNr,
      bezeichnung: currentPos.artikelBezeichnung, bezeichnung2: '',
      gebindeNr: '', gebinde: currentPos.gebinde,
      menge: currentPos.menge, einheit: currentPos.einheit,
      einhPreis: currentPos.listenpreis, bruttoEinzel: currentPos.bruttoPreis,
      nettoBetrag: currentPos.nettoBetrag, mwstProzent: currentPos.mwstProzent,
      bruttoBetrag: currentPos.bruttoBetrag, niederlassung: currentPos.niederlassung,
      lagerhalle: currentPos.lagerhalle, lagerfach: '', chargenNr: '', anerkennung: '',
      serienNr: '', kontraktNr: currentPos.kontraktNr, streckeNr: '', naBio: '', kostenstelle: '',
    }
    setState((p) => ({ ...p, positionen: [...p.positionen, pos], aktivePositionIndex: p.positionen.length }))
    setCurrentPos(emptyPos(currentPos.posNr + 10))
  }

  const renumberPosNr = (positionen: RechnungPosition[]): RechnungPosition[] =>
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
    setState((prev) => ({ ...prev, positionen: renumbered, aktivePositionIndex: newAktive }))
  }

  const handleMovePositionUp = (idx: number): void => {
    if (idx <= 0) return
    const newPositionen = [...state.positionen]
    ;[newPositionen[idx - 1], newPositionen[idx]] = [newPositionen[idx], newPositionen[idx - 1]]
    const renumbered = renumberPosNr(newPositionen)
    const newAktive = state.aktivePositionIndex === idx ? idx - 1 : state.aktivePositionIndex === idx - 1 ? idx : state.aktivePositionIndex
    setState((prev) => ({ ...prev, positionen: renumbered, aktivePositionIndex: newAktive }))
  }

  const handleMovePositionDown = (idx: number): void => {
    if (idx >= state.positionen.length - 1) return
    const newPositionen = [...state.positionen]
    ;[newPositionen[idx], newPositionen[idx + 1]] = [newPositionen[idx + 1], newPositionen[idx]]
    const renumbered = renumberPosNr(newPositionen)
    const newAktive = state.aktivePositionIndex === idx ? idx + 1 : state.aktivePositionIndex === idx + 1 ? idx : state.aktivePositionIndex
    setState((prev) => ({ ...prev, positionen: renumbered, aktivePositionIndex: newAktive }))
  }

  const handleSave = async (): Promise<string | null> => {
    if (!state.lieferant) { push('Bitte Lieferant auswählen'); return null }
    if (!state.rechnungNr) { push('Bitte Rechnungs-Nr. eingeben'); return null }
    try {
      const payload = {
        beleg_nr: state.belegNr, rechnung_nr: state.rechnungNr,
        rechn_datum: state.rechnDatum, buch_datum: state.buchDatum,
        niederlassung: state.niederlassung || null, bediener: state.bediener,
        lieferant_id: state.lieferant.id, lieferant_name: state.lieferant.name,
        erledigt: state.erledigt,
        netto_betrag: summen.netto.toFixed(2),
        mwst_betrag: (summen.mwst1 + summen.mwst2).toFixed(2),
        brutto_betrag: summen.brutto.toFixed(2),
        positionen: state.positionen.map((p) => ({
          pos_nr: p.posNr, lieferschein_nr: p.lieferscheinNr || null,
          artikel_nr: p.artikelNr, lieferant_artikel_nr: p.lieferantArtikelNr || null,
          bezeichnung: p.bezeichnung, menge: p.menge, einheit: p.einheit,
          einh_preis: p.einhPreis, netto_betrag: p.nettoBetrag,
          mwst_prozent: p.mwstProzent, brutto_betrag: p.bruttoBetrag,
          kontrakt_nr: p.kontraktNr || null,
        })),
      }
      let resp: any
      if (state.id) {
        resp = await apiClient.patch(`/api/v1/einkauf/rechnungen/${state.id}`, payload)
      } else {
        resp = await apiClient.post('/api/v1/einkauf/rechnungen', payload)
      }
      setState((p) => ({ ...p, id: resp.id, belegNr: resp.beleg_nr || p.belegNr }))
      push('Rechnung gespeichert')
      return resp.id
    } catch (err: any) {
      push(`Fehler: ${err.response?.data?.detail || err.message}`)
      return null
    }
  }

  const handleDelete = async (): Promise<void> => {
    if (!state.id) { setState(emptyState()); setCurrentPos(emptyPos(10)); setShowDeleteDialog(false); return }
    try {
      await apiClient.delete(`/api/v1/einkauf/rechnungen/${state.id}`)
      push('Rechnung gelöscht'); setShowDeleteDialog(false); navigate('/einkauf')
    } catch (err: any) { push(`Fehler: ${err.response?.data?.detail || err.message}`) }
  }

  /** Beleg drucken und buchen: Speichern, dann Workflow Prüfen → Freigeben → Verbuchen. */
  const handleSaveClick = async (): Promise<void> => {
    setIsSaving(true)
    try {
      await handleSave()
    } finally {
      setIsSaving(false)
    }
  }

  const handlePrintAndBook = async (): Promise<void> => {
    setIsSaving(true)
    try {
      const id = await handleSave()
      if (!id) return
      const base = '/api/v1/einkauf/rechnungseingaenge'
      await apiClient.post(`${base}/${encodeURIComponent(id)}/pruefen`)
      await apiClient.post(`${base}/${encodeURIComponent(id)}/freigeben`)
      await apiClient.post(`${base}/${encodeURIComponent(id)}/verbuchen`)
      push('Beleg verbucht.')
    } catch (err: any) {
      push(`Buchung: ${err.response?.data?.detail || err.message}`)
    } finally {
      setIsSaving(false)
    }
  }

  useGlobalShortcutsWithVoice({
    'open-customer-selection': () => setShowLieferantDialog(true),
    'open-article-selection': () => setShowArticleDialog(true),
    'confirm-position': () => handlePositionOK(),
    'save-document': () => void handleSaveClick(),
    'delete-document': () => setShowDeleteDialog(true),
    'close-document': () => navigate(-1),
    cancel: () => { setShowLieferantDialog(false); setShowArticleDialog(false) },
  })

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <div className="bg-green-600 text-white px-4 py-2">
        <h1 className="text-lg font-bold">EINKAUF-RECHNUNG</h1>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {/* Header */}
        <Card className="mb-4 p-4">
          <div className="grid grid-cols-3 gap-6">
            {/* Links: Tabs LIEFERANT / ZAHLUNGSBEDINGUNGEN */}
            <div className="col-span-2">
              <Tabs value={headerTab} onValueChange={(v) => setHeaderTab(v as typeof headerTab)}>
                <TabsList className="mb-3">
                  <TabsTrigger value="lieferant">LIEFERANT</TabsTrigger>
                  <TabsTrigger value="zahlungsbed">ZAHLUNGSBEDINGUNGEN</TabsTrigger>
                </TabsList>

                <TabsContent value="lieferant">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Label className="w-28 text-sm shrink-0">Kreditor-Kto.:</Label>
                        <Input value={state.lieferant?.kreditorAccount || ''} readOnly
                          className="flex-1 h-8 bg-green-50" />
                        <ShortcutHintButton shortcut="Strg+F1">
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0"
                            onClick={() => setShowLieferantDialog(true)}>
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </ShortcutHintButton>
                      </div>
                      <div className="border rounded p-2 min-h-[80px] text-sm">
                        {state.lieferant ? (
                          <>
                            <div className="font-medium">{state.lieferant.name}</div>
                            {state.lieferant.address?.street && <div>{state.lieferant.address.street}</div>}
                            {(state.lieferant.address?.postalCode || state.lieferant.address?.city) && (
                              <div>{[state.lieferant.address.postalCode, state.lieferant.address.city].filter(Boolean).join(' ')}</div>
                            )}
                          </>
                        ) : <div className="text-muted-foreground italic text-xs">Kein Lieferant</div>}
                      </div>
                      <a href="#" className="text-sm text-blue-600 underline hover:text-blue-800"
                        onClick={async (e) => {
                          e.preventDefault()
                          try {
                            const items: any[] = await apiClient.get<any[]>('/api/v1/einkauf/rechnungen')
                            const idx = rechnungId ? items.findIndex((r: any) => r.id === rechnungId) : -1
                            if (idx + 1 < items.length) navigate(`/einkauf/rechnungen/${items[idx + 1].id}`)
                            else push('Kein vorheriger Beleg vorhanden.')
                          } catch { push('Rechnungen konnten nicht geladen werden.') }
                        }}>
                        wie vorh. RG (F11)
                      </a>
                      <br />
                      <a href="#" className="text-sm text-blue-600 underline hover:text-blue-800"
                        onClick={(e) => {
                          e.preventDefault()
                          if (state.lieferant) {
                            navigate(`/einkauf/lieferant/${state.lieferant.id}`)
                          } else {
                            setShowLieferantDialog(true)
                          }
                        }}>
                        Lieferanten-Stamm
                      </a>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Label className="w-28 text-sm shrink-0">Niederlassung:</Label>
                        <Input value={state.niederlassung}
                          onChange={(e) => setState((p) => ({ ...p, niederlassung: e.target.value }))}
                          className="flex-1 h-8" />
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><MoreHorizontal className="h-4 w-4" /></Button>
                      </div>
                      <div className="flex items-center gap-2">
                        <Label className="w-28 text-sm shrink-0">Kostenstelle:</Label>
                        <Input value={state.kostenstelle} readOnly className="flex-1 h-8 bg-muted" />
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><MoreHorizontal className="h-4 w-4" /></Button>
                      </div>
                      <div className="flex items-center gap-2">
                        <Label className="w-28 text-sm shrink-0">Bediener:</Label>
                        <Input value={state.bediener} readOnly className="flex-1 h-8" />
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><MoreHorizontal className="h-4 w-4" /></Button>
                      </div>
                      <div className="flex items-center gap-2 pt-1">
                        <Checkbox checked={state.erledigt}
                          onCheckedChange={(v) => setState((p) => ({ ...p, erledigt: v === true }))} />
                        <Label className="text-sm">Erledigt</Label>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="zahlungsbed">
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <Input value={state.skonto1Tage}
                        onChange={(e) => setState((p) => ({ ...p, skonto1Tage: e.target.value }))}
                        placeholder="Tage" className="w-16 h-8" />
                      <Input value={state.skonto1Prozent}
                        onChange={(e) => setState((p) => ({ ...p, skonto1Prozent: e.target.value }))}
                        placeholder="% Skonto" className="w-20 h-8" />
                      <Label className="text-sm">Fällig ab:</Label>
                      <Input type="date" value={state.skonto1FaelligAb}
                        onChange={(e) => setState((p) => ({ ...p, skonto1FaelligAb: e.target.value }))}
                        className="flex-1 h-8" />
                    </div>
                    <div className="flex items-center gap-3">
                      <Input value={state.skonto2Tage}
                        onChange={(e) => setState((p) => ({ ...p, skonto2Tage: e.target.value }))}
                        placeholder="Tage" className="w-16 h-8" />
                      <Input value={state.skonto2Prozent}
                        onChange={(e) => setState((p) => ({ ...p, skonto2Prozent: e.target.value }))}
                        placeholder="% Skonto" className="w-20 h-8" />
                      <Label className="text-sm">Festes Valuta-Datum:</Label>
                      <Input type="date" value={state.skonto2ValutaDatum}
                        onChange={(e) => setState((p) => ({ ...p, skonto2ValutaDatum: e.target.value }))}
                        className="flex-1 h-8" />
                    </div>
                    <div className="flex items-center gap-3">
                      <Input value={state.nettoKasseTage}
                        onChange={(e) => setState((p) => ({ ...p, nettoKasseTage: e.target.value }))}
                        placeholder="Tage" className="w-16 h-8" />
                      <Label className="text-sm">Tage netto Kasse</Label>
                    </div>
                    <a href="#" className="text-sm text-blue-600 underline hover:text-blue-800"
                      onClick={(e) => {
                        e.preventDefault()
                        navigate('/einkauf/zahlungsbedingungen')
                      }}>
                      Auswahl aus ZB-Stamm
                    </a>
                    <div className="mt-4 space-y-2">
                      <div className="flex items-center gap-2">
                        <Label className="w-28 text-sm shrink-0">Niederlassung:</Label>
                        <Input value={state.niederlassung} readOnly className="flex-1 h-8" />
                      </div>
                      <div className="flex items-center gap-2">
                        <Label className="w-28 text-sm shrink-0">Bediener:</Label>
                        <Input value={state.bediener} readOnly className="flex-1 h-8" />
                      </div>
                      <div className="flex items-center gap-2">
                        <Checkbox checked={state.erledigt}
                          onCheckedChange={(v) => setState((p) => ({ ...p, erledigt: v === true }))} />
                        <Label className="text-sm">Erledigt</Label>
                      </div>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>

            {/* Rechts: Beleg-Nr. etc. */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-24 text-sm shrink-0">Beleg-Nr.:</Label>
                <Input value={state.belegNr} readOnly className="flex-1 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><MoreHorizontal className="h-4 w-4" /></Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><ChevronLeft className="h-4 w-4" /></Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><ChevronRight className="h-4 w-4" /></Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-24 text-sm shrink-0">Rechnung-Nr.:</Label>
                <Input value={state.rechnungNr}
                  onChange={(e) => setState((p) => ({ ...p, rechnungNr: e.target.value }))}
                  className="flex-1 h-8" placeholder="Rechnungs-Nr. des Lieferanten" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-24 text-sm shrink-0">Rechn.-Datum:</Label>
                <Input type="date" value={state.rechnDatum}
                  onChange={(e) => setState((p) => ({ ...p, rechnDatum: e.target.value }))}
                  className="flex-1 h-8" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-24 text-sm shrink-0">Buch.-Datum:</Label>
                <Input type="date" value={state.buchDatum}
                  onChange={(e) => setState((p) => ({ ...p, buchDatum: e.target.value }))}
                  className="flex-1 h-8" />
              </div>
            </div>
          </div>
        </Card>

        {/* Rechnungs-Summen + Positions-Grid */}
        <Card className="mb-4 p-4">
          {/* → Lieferschein-Auswahl + Rechn.-Summen */}
          <div className="flex items-center gap-6 mb-3 flex-wrap">
            <a href="#" className="text-sm text-blue-600 underline hover:text-blue-800 font-medium"
              onClick={async (e) => {
                e.preventDefault()
                if (!state.lieferant) { push('Bitte zuerst einen Lieferanten auswählen.'); return }
                try {
                  const res: any[] = await apiClient.get<any[]>('/api/v1/einkauf/lieferscheine', {
                    params: { lieferant_id: state.lieferant.id, status: 'offen' }
                  })
                  const lsList = Array.isArray(res) ? res : []
                  if (lsList.length === 0) { push('Keine offenen Lieferscheine für diesen Lieferanten.'); return }
                  // Übernimmt Positionen des ersten gefundenen Lieferscheins
                  const ls = lsList[0]
                  if (ls.positionen?.length) {
                    setState((prev) => ({
                      ...prev,
                      positionen: ls.positionen.map((p: any, i: number) => ({
                      id: crypto.randomUUID(), posNr: i + 1, liefArt: 'frei',
                      artikelNr: p.artikel_nr ?? '', lieferantArtikelNr: '',
                      artikelBezeichnung: p.bezeichnung ?? '', artikelBezeichnung2: '',
                      einheit: p.einheit ?? 'kg', menge: p.menge ?? 0,
                      einhPreis: p.einzelpreis ?? 0, betrag: (p.menge ?? 0) * (p.einzelpreis ?? 0),
                      mwstKz: '1', mwstSatz: 19, rabatt: 0, lager: '', lagerhalle: '', lagerfach: '', info: ''
                      }))
                    }))
                    push(`${lsList.length} Lieferschein(e) gefunden — LS ${ls.ls_nummer ?? ls.id} übernommen.`)
                  }
                } catch (e: any) { push(`Fehler: ${e.response?.data?.detail ?? e.message}`) }
              }}>
              → Lieferschein-Auswahl
            </a>
            <div className="flex items-center gap-2 ml-auto flex-wrap">
              <span className="text-sm font-medium">Rechn.-Summen:</span>
              <div className="flex items-center gap-1">
                <Label className="text-xs">netto</Label>
                <Input value={summen.netto.toFixed(2)} readOnly className="h-7 w-24 text-right" />
              </div>
              <div className="flex items-center gap-1">
                <Label className="text-xs">MWSt.1</Label>
                <Input value={summen.mwst1.toFixed(2)} readOnly className="h-7 w-24 text-right" />
              </div>
              <div className="flex items-center gap-1">
                <Label className="text-xs">MWSt.2</Label>
                <Input value={summen.mwst2.toFixed(2)} readOnly className="h-7 w-24 text-right" />
              </div>
              <div className="flex items-center gap-1">
                <Label className="text-xs">brutto</Label>
                <Input value={summen.brutto.toFixed(2)} readOnly className="h-7 w-28 text-right font-semibold" />
              </div>
              <span className="text-sm font-medium">EUR</span>
            </div>
          </div>

          {/* Positionen */}
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-14">Pos.-Nr.</TableHead>
                  <TableHead className="w-24">Lief.-LS-Nr.</TableHead>
                  <TableHead className="w-24">Artikel-Nr.</TableHead>
                  <TableHead className="w-24">Lief.-Arti.</TableHead>
                  <TableHead className="w-32">Bezeichn.</TableHead>
                  <TableHead className="w-32">Bezeichn.2</TableHead>
                  <TableHead className="w-20">Geb.-Nr.</TableHead>
                  <TableHead className="w-16">Gebinde</TableHead>
                  <TableHead className="w-20">Menge</TableHead>
                  <TableHead className="w-16">Einheit</TableHead>
                  <TableHead className="w-24">Einh.Preis</TableHead>
                  <TableHead className="w-24">Brutto-Ei.</TableHead>
                  <TableHead className="w-24">Netto-Betr.</TableHead>
                  <TableHead className="w-16">MWSt.</TableHead>
                  <TableHead className="w-24">Brutto-Betr.</TableHead>
                  <TableHead className="w-20">Niederlas.</TableHead>
                  <TableHead className="w-20">Lagerhalle</TableHead>
                  <TableHead className="w-20">Lagerfach</TableHead>
                  <TableHead className="w-24">Chargen-Nr.</TableHead>
                  <TableHead className="w-20">Anerken.</TableHead>
                  <TableHead className="w-20">Serien-Nr.</TableHead>
                  <TableHead className="w-24">Kontrakt-Nr.</TableHead>
                  <TableHead className="w-20">Strecke-Nr.</TableHead>
                  <TableHead className="w-16">Na.-Bio.</TableHead>
                  <TableHead className="w-24">Kosten/S.</TableHead>
                  <TableHead className="w-24">Kostenstelle</TableHead>
                  <TableHead className="w-24 text-right">Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {state.positionen.map((pos, idx) => (
                  <TableRow key={idx}
                    className={state.aktivePositionIndex === idx ? 'bg-green-100' : 'cursor-pointer hover:bg-muted/50'}
                    onClick={() => setState((p) => ({ ...p, aktivePositionIndex: idx }))}>
                    <TableCell>{pos.posNr}</TableCell>
                    <TableCell>{pos.lieferscheinNr}</TableCell>
                    <TableCell>{pos.artikelNr}</TableCell>
                    <TableCell>{pos.lieferantArtikelNr}</TableCell>
                    <TableCell>{pos.bezeichnung}</TableCell>
                    <TableCell>{pos.bezeichnung2}</TableCell>
                    <TableCell>{pos.gebindeNr}</TableCell>
                    <TableCell>{pos.gebinde || ''}</TableCell>
                    <TableCell>{pos.menge}</TableCell>
                    <TableCell>{pos.einheit}</TableCell>
                    <TableCell>{pos.einhPreis.toFixed(2)}</TableCell>
                    <TableCell>{pos.bruttoEinzel.toFixed(2)}</TableCell>
                    <TableCell>{pos.nettoBetrag.toFixed(2)}</TableCell>
                    <TableCell>{pos.mwstProzent}%</TableCell>
                    <TableCell>{pos.bruttoBetrag.toFixed(2)}</TableCell>
                    <TableCell>{pos.niederlassung}</TableCell>
                    <TableCell>{pos.lagerhalle}</TableCell>
                    <TableCell>{pos.lagerfach}</TableCell>
                    <TableCell>{pos.chargenNr}</TableCell>
                    <TableCell>{pos.anerkennung}</TableCell>
                    <TableCell>{pos.serienNr}</TableCell>
                    <TableCell>{pos.kontraktNr}</TableCell>
                    <TableCell>{pos.streckeNr}</TableCell>
                    <TableCell>{pos.naBio}</TableCell>
                    <TableCell></TableCell>
                    <TableCell>{pos.kostenstelle}</TableCell>
                    <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-0.5">
                        <Button type="button" variant="ghost" size="icon" className="h-7 w-7" title="Hoch"
                          onClick={() => handleMovePositionUp(idx)} disabled={idx <= 0}>
                          <ChevronUp className="h-4 w-4" />
                        </Button>
                        <Button type="button" variant="ghost" size="icon" className="h-7 w-7" title="Runter"
                          onClick={() => handleMovePositionDown(idx)} disabled={idx >= state.positionen.length - 1}>
                          <ChevronDown className="h-4 w-4" />
                        </Button>
                        <Button type="button" variant="ghost" size="icon" className="h-7 w-7 text-red-600 hover:text-red-700" title="Position löschen"
                          onClick={() => handleDeletePosition(idx)}>
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

        {/* Verfügb. Bestand + Gewicht + Summen-Zeile */}
        <div className="flex items-center gap-6 mb-2 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground">verfügb. Bestand:</span>
            <Input value="0,00 kg" readOnly className="h-7 w-24" />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-muted-foreground">Gewicht</span>
            <Input value="0,00" readOnly className="h-7 w-20" />
            <span className="text-muted-foreground">kg</span>
          </div>
          <div className="flex items-center gap-4 ml-auto">
            <div className="flex items-center gap-1">
              <span className="text-muted-foreground text-xs">Summe: netto</span>
              <Input value={summen.netto.toFixed(2)} readOnly className="h-7 w-24 text-right" />
            </div>
            <div className="flex items-center gap-1">
              <span className="text-muted-foreground text-xs">MWSt.</span>
              <Input value={(summen.mwst1 + summen.mwst2).toFixed(2)} readOnly className="h-7 w-20 text-right" />
            </div>
            <div className="flex items-center gap-1">
              <span className="text-muted-foreground text-xs">brutto</span>
              <Input value={summen.brutto.toFixed(2)} readOnly className="h-7 w-24 text-right font-semibold" />
            </div>
            <span className="font-medium">EUR</span>
          </div>
        </div>

        {/* Positions-Details */}
        <Card className="mb-4 p-4">
          <h2 className="mb-2 font-semibold text-sm">Positions-Details</h2>
          <div className="grid grid-cols-8 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">Pos.-Nr.:</Label>
              <Input value={currentPos.posNr} readOnly className="h-8" />
              <Label className="text-xs text-muted-foreground">Uhrzeit</Label>
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
              <Label className="text-xs text-muted-foreground">Lief.-Art.-Nr.</Label>
              <Input value={currentPos.lieferantArtikelNr}
                onChange={(e) => setCurrentPos((p) => ({ ...p, lieferantArtikelNr: e.target.value }))}
                className="h-8" />
            </div>
            <div className="space-y-1 col-span-2">
              <Label className="text-xs">Artikel-Bezeichnung:</Label>
              <Input value={currentPos.artikelBezeichnung} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Menge:</Label>
              <Input type="number" value={currentPos.menge}
                onChange={(e) => setCurrentPos((p) => ({ ...p, menge: Number(e.target.value) }))}
                className="h-8" />
              <Label className="text-xs text-muted-foreground">Gebinde</Label>
              <Input type="number" value={currentPos.gebinde}
                onChange={(e) => setCurrentPos((p) => ({ ...p, gebinde: Number(e.target.value) }))}
                className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Einheit:</Label>
              <Input value={currentPos.einheit} readOnly className="h-8" />
              <Label className="text-xs text-muted-foreground">MWSt</Label>
              <div className="flex items-center gap-1">
                <Input type="number" value={currentPos.mwstProzent}
                  onChange={(e) => setCurrentPos((p) => ({ ...p, mwstProzent: Number(e.target.value) }))}
                  className="h-8 flex-1" />
                <span className="text-xs">%</span>
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Niederl./Lagerhalle:</Label>
              <Input value={currentPos.niederlassung}
                onChange={(e) => setCurrentPos((p) => ({ ...p, niederlassung: e.target.value }))}
                className="h-8" />
              <Input value={currentPos.lagerhalle}
                onChange={(e) => setCurrentPos((p) => ({ ...p, lagerhalle: e.target.value }))}
                className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Listenpreis / Rabatt:</Label>
              <Input type="number" step="0.01" value={currentPos.listenpreis}
                onChange={(e) => setCurrentPos((p) => ({ ...p, listenpreis: Number(e.target.value) }))}
                className="h-8" />
              <Input type="number" value={currentPos.rabatt}
                onChange={(e) => setCurrentPos((p) => ({ ...p, rabatt: Number(e.target.value) }))}
                className="h-8" />
            </div>
            {/* Netto-Preis / Brutto-Preis */}
            <div className="space-y-1 col-span-2">
              <Label className="text-xs">Netto-Preis:</Label>
              <Input value={currentPos.nettoPreis.toFixed(2)} readOnly className="h-8" />
              <Label className="text-xs">Brutto-Preis:</Label>
              <Input value={currentPos.bruttoPreis.toFixed(2)} readOnly className="h-8" />
            </div>
            <div className="space-y-1 col-span-2">
              <Label className="text-xs">Netto-Betrag:</Label>
              <Input value={currentPos.nettoBetrag.toFixed(2)} readOnly className="h-8" />
              <Label className="text-xs">Brutto-Betrag:</Label>
              <Input value={currentPos.bruttoBetrag.toFixed(2)} readOnly className="h-8 font-semibold" />
            </div>

            {/* Buttons-Leiste */}
            <div className="col-span-8 flex items-center gap-2 pt-1 flex-wrap">
              <Button variant="outline" size="sm" className="h-8">PopUp</Button>
              <Button variant="outline" size="sm" className="h-8"
                onClick={() => push('Aktualisieren')}>Aktualisieren</Button>
              <div className="flex items-center gap-1 border rounded px-2 h-8">
                <span className="text-xs">Kontrakt-Nr. ---</span>
              </div>
              <div className="flex items-center gap-1">
                <Checkbox />
                <Label className="text-xs">skontierfähig</Label>
              </div>
              <Button variant="outline" size="sm" className="h-8">↔ Niederlassung usw.</Button>
              <Button variant="outline" size="sm" className="h-8">⚡ Chargen-/Serien-Nr.</Button>
              <ShortcutHintButton shortcut="Strg+F3">
                <Button onClick={handlePositionOK} className="h-8 gap-1">
                  <Check className="h-4 w-4" />Zeile OK
                </Button>
              </ShortcutHintButton>
            </div>
          </div>
        </Card>
      </div>

      {/* Bottom Toolbar */}
      <div className="border-t bg-white px-4 py-2 flex items-center justify-between">
        <div className="flex gap-2 flex-wrap">
          <Button variant="outline" size="sm" className="gap-2"
            disabled={isSaving}
            onClick={() => void handlePrintAndBook()}>
            <Printer className="h-4 w-4" />Beleg drucken und buchen
          </Button>
          <Button variant="outline" size="sm" className="gap-2"
            onClick={() => setShowAttachmentDialog(true)}>
            <FileText className="h-4 w-4" />Unterlagen
          </Button>
          <Button variant="outline" size="sm" className="gap-2"
            onClick={() => setShowAttachmentDialog(true)}>
            <Folder className="h-4 w-4" />Dateien
          </Button>
          <Button variant="outline" size="sm" className="gap-2 text-red-600"
            onClick={() => setShowDeleteDialog(true)}>
            <Trash2 className="h-4 w-4" />Rechnung löschen
          </Button>
          <Button variant="outline" size="sm" className="gap-2" onClick={() => { setShowAttachmentDialog(true); push('Unterlagen geöffnet. Hier können Sie die Originalrechnung hochladen.'); }} title="Originalrechnung anzeigen/hochladen">
            <BookOpen className="h-4 w-4" />Originalrechnung ▼
          </Button>
        </div>
        <div className="flex gap-2">
          <ShortcutHintButton shortcut="Strg+F4">
            <Button onClick={() => void handleSaveClick()} disabled={isSaving} size="sm" className="gap-2">
              <Save className="h-4 w-4" />Speichern
            </Button>
          </ShortcutHintButton>
          <Button variant="outline" onClick={() => navigate('/einkauf')} size="sm">Schließen</Button>
        </div>
      </div>

      {/* Dialoge */}
      <LieferantSuchDialog open={showLieferantDialog} onClose={() => setShowLieferantDialog(false)}
        onSelect={(l) => setState((p) => ({ ...p, lieferant: l }))} />
      <ArtikelSuchDialog open={showArticleDialog} onClose={() => setShowArticleDialog(false)}
        onSelect={handleArticleSelect} />
      <DmsAnhangDialog open={showAttachmentDialog} onClose={() => setShowAttachmentDialog(false)}
        businessObjectType="einkauf_rechnung" businessObjectId={state.id}
        title="UNTERLAGEN / DATEIEN — EINKAUF-RECHNUNG" />
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="max-w-sm">
          <DialogHeader><DialogTitle>Rechnung löschen?</DialogTitle></DialogHeader>
          <div className="py-2 text-sm">
            {state.id ? <>Rechnung <strong>{state.rechnungNr || state.belegNr}</strong> wird gelöscht.</> : 'Formular wird geleert.'}
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
