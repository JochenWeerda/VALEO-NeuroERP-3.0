/**
 * Einkauf-Lieferschein-Erfassung
 * 1:1 Nachbau der zvoove EINKAUF-LIEFERSCHEIN-Maske
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
import { DmsAnhangDialog } from '@/components/dms/DmsAnhangDialog'
import { ArtikelSuchDialog } from '@/components/sales/ArtikelSuchDialog'
import { LieferscheinDruckDialog, type PrintOptions } from '@/components/sales/LieferscheinDruckDialog'
import { apiClient } from '@/lib/axios'
import { useAuth } from '@/hooks/useAuth'
import { useGlobalShortcutsWithVoice } from '@/features/ki-usability'
import { ShortcutHintButton } from '@/components/shortcuts/ShortcutHelpPanel'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import {
  ChevronLeft, ChevronRight, ChevronUp, ChevronDown, MoreHorizontal, Check, Printer, Save,
  FileText, Folder, Trash2, Search,
} from 'lucide-react'

// ==================== Types ====================

type Lieferant = {
  id: string
  lieferantNr: string
  name: string
  kreditorAccount: string
  address?: { street?: string; postalCode?: string; city?: string; phone?: string; fax?: string }
  zahlungsbedingung?: string
  kontaktperson?: string
}

type EinkaufLSResponse = {
  id: string
  tenant_id: string
  lieferschein_nr: string
  liefer_nr: string | null
  lieferschein_datum: string
  niederlassung: string | null
  bediener: string | null
  lieferant_id: string | null
  lieferant_name: string | null
  zahlungsbedingung: string | null
  texte: string | null
  zwischenhaendler: string | null
  wie_vom_ls: boolean
  erledigt: boolean
  netto_betrag: string | null
  mwst_betrag: string | null
  brutto_betrag: string | null
  summe_gewicht: string | null
  created_at: string
  updated_at: string
  positionen: Array<{
    id: string
    pos_nr: number
    artikel_nr: string | null
    lieferant_artikel_nr: string | null
    bezeichnung: string | null
    gebinde_nr: string | null
    gebinde: string | null
    menge: string
    einheit: string | null
    einzelpreis: string | null
    nettobetrag: string | null
    lagerhalle: string | null
    lagerfach: string | null
    charge: string | null
    serien_nr: string | null
    kontakt: string | null
    prozent: string | null
    master_nr: string | null
  }>
}

export type EinkaufPosition = {
  posNr: number
  artikelNr: string
  artikelId: string | null
  lieferantArtikelNr: string
  bezeichnung: string
  bezeichnung2: string
  gebindeNr: string
  gebinde: number
  menge: number
  einheit: string
  einzelpreis: number
  nettoBetrag: number
  mwstProzent: number
  bruttoPreis: number
  bruttoBetrag: number
  niederlassung: string
  lagerhalle: string
  lagerfach: string
  charge: string
  serienNr: string
  kontraktNr: string
  streckeNr: string
  naBio: string
  musterNr: string
  prozent: number
  skontierf: boolean
}

type EinkaufLSState = {
  id: string | null
  lieferscheinNr: string
  lieferNr: string
  lieferDatum: string
  niederlassung: string
  bediener: string
  erledigt: boolean
  lieferant: Lieferant | null
  zahlungsbedingung: string
  texte: string
  zwischenhaendler: string
  positionen: EinkaufPosition[]
  aktivePositionIndex: number | null
  positionCharge: string
  positionSerienNr: string
}

type CurrentEinkaufPosition = {
  posNr: number
  artikelNr: string
  artikelId: string | null
  lieferantArtikelNr: string
  artikelBezeichnung: string
  artikelBezeichnung2: string
  gebindeNr: string
  gebinde: number
  menge: number
  einheit: string
  einzelpreis: number
  prozent: number
  bruttoPreis: number
  bruttoBetrag: number
  mwstProzent: number
  kostenstelle: string
  kontraktNr: string
  skontierf: boolean
}

// ==================== Lieferant-Suche Dialog ====================

function LieferantSuchDialog({
  open,
  onClose,
  onSelect,
}: {
  open: boolean
  onClose: () => void
  onSelect: (lieferant: Lieferant) => void
}): JSX.Element {
  const [search, setSearch] = useState('')
  const [results, setResults] = useState<Lieferant[]>([])
  const [loading, setLoading] = useState(false)

  const handleSearch = async (): Promise<void> => {
    if (!search.trim()) return
    setLoading(true)
    try {
      const data = await apiClient.get<any[]>('/api/v1/crm/customers', {
        params: { search: search.trim(), limit: 30 },
      })
      const mapped: Lieferant[] = (data || []).map((c: any) => ({
        id: c.id,
        lieferantNr: c.customer_number || c.customerNumber || '',
        name: c.company_name || c.name || '',
        kreditorAccount: c.customer_number || c.customerNumber || '',
        address: c.address || undefined,
        zahlungsbedingung: c.payment_terms || undefined,
        kontaktperson: c.contact_person || undefined,
      }))
      setResults(mapped)
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Lieferant suchen</DialogTitle>
        </DialogHeader>
        <div className="flex gap-2 mb-3">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Name oder Kreditor-Kto. eingeben..."
            className="flex-1"
            onKeyDown={(e) => e.key === 'Enter' && void handleSearch()}
            autoFocus
          />
          <Button onClick={() => void handleSearch()} disabled={loading} className="gap-2">
            <Search className="h-4 w-4" />
            Suchen
          </Button>
        </div>
        <div className="max-h-80 overflow-y-auto border rounded">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-28">Kreditor-Kto.</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Ort</TableHead>
                <TableHead className="w-20"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {results.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground py-4">
                    {search ? 'Keine Ergebnisse' : 'Suchbegriff eingeben'}
                  </TableCell>
                </TableRow>
              )}
              {results.map((l) => (
                <TableRow
                  key={l.id}
                  className="cursor-pointer hover:bg-muted"
                  onClick={() => { onSelect(l); onClose() }}
                >
                  <TableCell className="font-mono">{l.kreditorAccount}</TableCell>
                  <TableCell>{l.name}</TableCell>
                  <TableCell>{l.address?.city || '—'}</TableCell>
                  <TableCell>
                    <Button size="sm" variant="outline" className="h-6 text-xs">
                      Übernehmen
                    </Button>
                  </TableCell>
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

export default function EinkaufLieferscheinErfassungPage(): JSX.Element {
  const navigate = useNavigate()
  const { push } = useToast()
  const { user } = useAuth()
  const { id: lsId } = useParams<{ id?: string }>()

  const generateLsNr = (): string => {
    const year = new Date().getFullYear()
    const rand = Math.floor(Math.random() * 1000000)
    return `E${year}${String(rand).padStart(6, '0')}`
  }

  const formatDate = (d: Date): string => {
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${y}-${m}-${day}`
  }

  const getBediener = (): string => {
    if (!user) return 'SYSTEM'
    return user.name?.split(' ').map((n) => n[0]).join('').toUpperCase().substring(0, 2) ||
      user.sub?.substring(0, 2).toUpperCase() || 'SY'
  }

  const emptyState = (): EinkaufLSState => ({
    id: null,
    lieferscheinNr: generateLsNr(),
    lieferNr: '',
    lieferDatum: formatDate(new Date()),
    niederlassung: '',
    bediener: getBediener(),
    erledigt: false,
    lieferant: null,
    zahlungsbedingung: '',
    texte: '',
    zwischenhaendler: '',
    positionen: [],
    aktivePositionIndex: null,
    positionCharge: '',
    positionSerienNr: '',
  })

  const emptyPosition = (posNr: number): CurrentEinkaufPosition => ({
    posNr,
    artikelNr: '',
    artikelId: null,
    lieferantArtikelNr: '',
    artikelBezeichnung: '',
    artikelBezeichnung2: '',
    gebindeNr: '',
    gebinde: 0,
    menge: 0,
    einheit: '',
    einzelpreis: 0,
    prozent: 0,
    bruttoPreis: 0,
    bruttoBetrag: 0,
    mwstProzent: 19,
    kostenstelle: '',
    kontraktNr: '',
    skontierf: false,
  })

  const [state, setState] = useState<EinkaufLSState>(emptyState)
  const [currentPos, setCurrentPos] = useState<CurrentEinkaufPosition>(emptyPosition(10))

  const [showLieferantDialog, setShowLieferantDialog] = useState(false)
  const [showArticleDialog, setShowArticleDialog] = useState(false)
  const [showPrintDialog, setShowPrintDialog] = useState(false)
  const [showAttachmentDialog, setShowAttachmentDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showPopUpDialog, setShowPopUpDialog] = useState(false)
  const [showNiederlassungDialog, setShowNiederlassungDialog] = useState(false)
  const [showChargenSerienDialog, setShowChargenSerienDialog] = useState(false)
  const [branchesList, setBranchesList] = useState<Array<{ id: string; branch_number: number; name: string }>>([])
  const [lieferantTab, setLieferantTab] = useState<'lieferant' | 'zahlungsbed' | 'texte' | 'zwhaendler'>('lieferant')
  const [showImportBestellungDialog, setShowImportBestellungDialog] = useState(false)
  const [bestellungenList, setBestellungenList] = useState<Array<{ id: string; bestellnummer: string; bestelldatum: string | null; status: string; positionen_anz: number }>>([])
  const [selectedBestellungId, setSelectedBestellungId] = useState<string | null>(null)
  const [loadingBestellungen, setLoadingBestellungen] = useState(false)

  // Bediener aus Session aktualisieren
  useEffect(() => {
    if (user) {
      setState((prev) => ({ ...prev, bediener: getBediener() }))
    }
  }, [user])

  // Niederlassungen laden wenn Dialog geöffnet
  useEffect(() => {
    if (!showNiederlassungDialog) return
    let cancelled = false
    apiClient.get<Array<{ id: string; branch_number: number; name: string }>>('/api/v1/admin/branches', { params: { active_only: true } })
      .then((list) => { if (!cancelled) setBranchesList(Array.isArray(list) ? list : []) })
      .catch(() => { if (!cancelled) setBranchesList([]) })
    return () => { cancelled = true }
  }, [showNiederlassungDialog])

  // Bestellungen des Lieferanten laden wenn Import-Dialog geöffnet
  useEffect(() => {
    if (!showImportBestellungDialog || !state.lieferant) {
      setBestellungenList([])
      setSelectedBestellungId(null)
      return
    }
    let cancelled = false
    setLoadingBestellungen(true)
    apiClient.get<Array<{ id: string; bestellnummer: string; bestelldatum: string | null; status: string; positionen_anz?: number }>>('/api/v1/einkauf/bestellungen', {
      params: { lieferant_id: state.lieferant.id },
    })
      .then((list) => {
        if (cancelled) return
        const items = Array.isArray(list) ? list : []
        setBestellungenList(items.map((b) => ({ id: b.id, bestellnummer: b.bestellnummer, bestelldatum: b.bestelldatum ?? null, status: b.status, positionen_anz: b.positionen_anz ?? 0 })))
        setSelectedBestellungId(null)
      })
      .catch(() => { if (!cancelled) setBestellungenList([]) })
      .finally(() => { if (!cancelled) setLoadingBestellungen(false) })
    return () => { cancelled = true }
  }, [showImportBestellungDialog, state.lieferant?.id])

  // Bestehenden Lieferschein laden
  useEffect(() => {
    if (!lsId) return
    const load = async (): Promise<void> => {
      try {
        const data = await apiClient.get<EinkaufLSResponse>(`/api/v1/einkauf/lieferscheine/${lsId}`)
        const positionen: EinkaufPosition[] = (data.positionen || []).map((pos) => {
          const ep = parseFloat(pos.einzelpreis || '0')
          const mwst = 19
          const bruttoPreis = ep * (1 + mwst / 100)
          const menge = parseFloat(pos.menge || '0')
          return {
            posNr: pos.pos_nr,
            artikelNr: pos.artikel_nr || '',
            artikelId: null,
            lieferantArtikelNr: pos.lieferant_artikel_nr || '',
            bezeichnung: pos.bezeichnung || '',
            bezeichnung2: '',
            gebindeNr: pos.gebinde_nr || '',
            gebinde: parseFloat(pos.gebinde || '0'),
            menge,
            einheit: pos.einheit || '',
            einzelpreis: ep,
            nettoBetrag: parseFloat(pos.nettobetrag || '0'),
            mwstProzent: mwst,
            bruttoPreis,
            bruttoBetrag: bruttoPreis * menge,
            niederlassung: '',
            lagerhalle: pos.lagerhalle || '',
            lagerfach: pos.lagerfach || '',
            charge: pos.charge || '',
            serienNr: pos.serien_nr || '',
            kontraktNr: pos.kontakt || '',
            streckeNr: '',
            naBio: '',
            musterNr: pos.master_nr || '',
            prozent: parseFloat(pos.prozent || '0'),
            skontierf: false,
          }
        })

        // Lieferant aus Daten zusammensetzen
        const lieferant: Lieferant | null = data.lieferant_id
          ? {
              id: data.lieferant_id,
              lieferantNr: data.lieferant_id,
              name: data.lieferant_name || '',
              kreditorAccount: data.lieferant_id,
            }
          : null

        setState({
          id: data.id,
          lieferscheinNr: data.lieferschein_nr,
          lieferNr: data.liefer_nr || '',
          lieferDatum: data.lieferschein_datum
            ? formatDate(new Date(data.lieferschein_datum))
            : formatDate(new Date()),
          niederlassung: data.niederlassung || '',
          bediener: data.bediener || getBediener(),
          erledigt: data.erledigt,
          lieferant,
          zahlungsbedingung: data.zahlungsbedingung || '',
          texte: data.texte || '',
          zwischenhaendler: data.zwischenhaendler || '',
          positionen,
          aktivePositionIndex: null,
          positionCharge: '',
          positionSerienNr: '',
        })
        push('Lieferschein geladen')
      } catch (err: any) {
        push(`Fehler beim Laden: ${err.response?.data?.detail || err.message}`)
      }
    }
    void load()
  }, [lsId, push])

  // Brutto-Preis/Betrag neu berechnen
  useEffect(() => {
    const bruttoPreis = currentPos.einzelpreis * (1 + currentPos.mwstProzent / 100)
    const bruttoBetrag = bruttoPreis * currentPos.menge
    setCurrentPos((prev) => ({ ...prev, bruttoPreis, bruttoBetrag }))
  }, [currentPos.einzelpreis, currentPos.mwstProzent, currentPos.menge])

  // Summen berechnen
  const summen = useMemo(() => {
    const netto = state.positionen.reduce((s, p) => s + p.nettoBetrag, 0)
    const brutto = state.positionen.reduce((s, p) => s + p.bruttoBetrag, 0)
    const mwst = brutto - netto
    return { netto, mwst, brutto }
  }, [state.positionen])

  // Lieferant ausgewählt
  const handleLieferantSelect = (lieferant: Lieferant): void => {
    setState((prev) => ({
      ...prev,
      lieferant,
      zahlungsbedingung: lieferant.zahlungsbedingung || prev.zahlungsbedingung,
    }))
  }

  // Artikel ausgewählt
  const handleArticleSelect = (article: any): void => {
    const ep = article.purchase_price || article.purchasePrice || article.sales_price || 0
    setCurrentPos((prev) => ({
      ...prev,
      artikelNr: article.article_number || article.articleNumber || '',
      artikelId: article.id || null,
      artikelBezeichnung: article.name || article.description || '',
      artikelBezeichnung2: article.description || '',
      einheit: article.unit || 'Stk',
      einzelpreis: ep,
      mwstProzent: article.mehrwertsteuer_prozent || article.mwstProzent || 19,
    }))
  }

  // Position bestätigen
  const handlePositionOK = (): void => {
    if (!currentPos.artikelNr || !currentPos.menge) {
      push('Bitte Artikel und Menge eingeben')
      return
    }
    const nettoBetrag = currentPos.einzelpreis * currentPos.menge * (1 - currentPos.prozent / 100)
    const bruttoPreis = currentPos.einzelpreis * (1 + currentPos.mwstProzent / 100)
    const bruttoBetrag = bruttoPreis * currentPos.menge

    const pos: EinkaufPosition = {
      posNr: currentPos.posNr,
      artikelNr: currentPos.artikelNr,
      artikelId: currentPos.artikelId,
      lieferantArtikelNr: currentPos.lieferantArtikelNr,
      bezeichnung: currentPos.artikelBezeichnung,
      bezeichnung2: currentPos.artikelBezeichnung2,
      gebindeNr: currentPos.gebindeNr,
      gebinde: currentPos.gebinde,
      menge: currentPos.menge,
      einheit: currentPos.einheit,
      einzelpreis: currentPos.einzelpreis,
      nettoBetrag,
      mwstProzent: currentPos.mwstProzent,
      bruttoPreis,
      bruttoBetrag,
      niederlassung: state.niederlassung,
      lagerhalle: '',
      lagerfach: '',
      charge: state.positionCharge,
      serienNr: state.positionSerienNr,
      kontraktNr: currentPos.kontraktNr,
      streckeNr: '',
      naBio: '',
      musterNr: '',
      prozent: currentPos.prozent,
      skontierf: currentPos.skontierf,
    }

    setState((prev) => ({
      ...prev,
      positionen: [...prev.positionen, pos],
      aktivePositionIndex: prev.positionen.length,
      positionCharge: '',
      positionSerienNr: '',
    }))
    setCurrentPos(emptyPosition(currentPos.posNr + 10))
  }

  const renumberPosNr = (positionen: EinkaufPosition[]): EinkaufPosition[] =>
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
  }

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

  const handleImportBestellungPositionen = async (): Promise<void> => {
    if (!selectedBestellungId) {
      push('Bitte wählen Sie eine Bestellung aus.')
      return
    }
    try {
      const data = await apiClient.get<{ positionen: Array<{
        pos_nr: number
        artikel_nr: string | null
        lieferanten_artnr: string | null
        artikel_bezeichnung: string | null
        menge: number
        einheit: string | null
        einzelpreis: number | null
        netto_betrag: number | null
      }> }>(`/api/v1/einkauf/bestellungen/${selectedBestellungId}`)
      const posList = data.positionen || []
      const mwst = 19
      const mapped: EinkaufPosition[] = posList.map((p) => {
        const ep = p.einzelpreis ?? 0
        const menge = p.menge ?? 0
        const bruttoPreis = ep * (1 + mwst / 100)
        return {
          posNr: 0,
          artikelNr: p.artikel_nr ?? '',
          artikelId: null,
          lieferantArtikelNr: p.lieferanten_artnr ?? '',
          bezeichnung: p.artikel_bezeichnung ?? '',
          bezeichnung2: '',
          gebindeNr: '',
          gebinde: 0,
          menge,
          einheit: p.einheit ?? '',
          einzelpreis: ep,
          nettoBetrag: p.netto_betrag ?? ep * menge,
          mwstProzent: mwst,
          bruttoPreis,
          bruttoBetrag: bruttoPreis * menge,
          niederlassung: '',
          lagerhalle: '',
          lagerfach: '',
          charge: '',
          serienNr: '',
          kontraktNr: '',
          streckeNr: '',
          naBio: '',
          musterNr: '',
          prozent: 0,
          skontierf: false,
        }
      })
      const combined = renumberPosNr([...state.positionen, ...mapped])
      setState((prev) => ({ ...prev, positionen: combined }))
      setShowImportBestellungDialog(false)
      push(`${mapped.length} Position(en) aus Bestellung übernommen.`)
    } catch (err: any) {
      push(`Fehler beim Laden der Bestellung: ${err.response?.data?.detail ?? err.message}`)
    }
  }

  // Lieferschein speichern
  const handleSave = async (): Promise<string | null> => {
    if (!state.lieferant) {
      push('Bitte wählen Sie einen Lieferanten aus')
      return null
    }
    try {
      const payload = {
        lieferschein_nr: state.lieferscheinNr,
        liefer_nr: state.lieferNr || null,
        lieferschein_datum: state.lieferDatum,
        niederlassung: state.niederlassung || null,
        lieferant_id: state.lieferant.id,
        lieferant_name: state.lieferant.name,
        zahlungsbedingung: state.zahlungsbedingung || null,
        texte: state.texte || null,
        zwischenhaendler: state.zwischenhaendler || null,
        bediener: state.bediener || null,
        erledigt: state.erledigt,
        netto_betrag: summen.netto.toFixed(2),
        mwst_betrag: summen.mwst.toFixed(2),
        brutto_betrag: summen.brutto.toFixed(2),
        positionen: state.positionen.map((p) => ({
          pos_nr: p.posNr,
          artikel_nr: p.artikelNr || null,
          lieferant_artikel_nr: p.lieferantArtikelNr || null,
          bezeichnung: p.bezeichnung || null,
          gebinde_nr: p.gebindeNr || null,
          gebinde: p.gebinde || null,
          menge: p.menge,
          einheit: p.einheit || null,
          einzelpreis: p.einzelpreis,
          nettobetrag: p.nettoBetrag,
          lagerhalle: p.lagerhalle || null,
          lagerfach: p.lagerfach || null,
          charge: p.charge || null,
          serien_nr: p.serienNr || null,
          kontakt: p.kontraktNr || null,
          prozent: p.prozent || null,
          master_nr: p.musterNr || null,
        })),
      }

      let response: EinkaufLSResponse
      if (state.id) {
        response = await apiClient.patch<EinkaufLSResponse>(
          `/api/v1/einkauf/lieferscheine/${state.id}`,
          payload
        )
      } else {
        response = await apiClient.post<EinkaufLSResponse>(
          '/api/v1/einkauf/lieferscheine',
          payload
        )
      }

      setState((prev) => ({ ...prev, id: response.id, lieferscheinNr: response.lieferschein_nr }))
      push('Lieferschein erfolgreich gespeichert')
      return response.id
    } catch (err: any) {
      push(`Fehler beim Speichern: ${err.response?.data?.detail || err.message}`)
      return null
    }
  }

  // Drucken
  const handlePrint = async (options: PrintOptions): Promise<void> => {
    try {
      let id = state.id
      if (!id) {
        id = await handleSave()
        if (!id) return
      }
      const params = new URLSearchParams({
        template: options.formatvorlage,
        copies: String(options.anzahlDrucke),
      })
      await apiClient.post(`/api/v1/einkauf/lieferscheine/${id}/print?${params.toString()}`)
      push('Lieferschein erfolgreich gedruckt')
      setShowPrintDialog(false)
    } catch (err: any) {
      push(`Fehler beim Drucken: ${err.response?.data?.detail || err.message}`)
    }
  }

  // Löschen
  const handleDelete = async (): Promise<void> => {
    const id = state.id
    if (!id) {
      setState(emptyState())
      setCurrentPos(emptyPosition(10))
      setShowDeleteDialog(false)
      return
    }
    try {
      await apiClient.delete(`/api/v1/einkauf/lieferscheine/${id}`)
      push('Lieferschein erfolgreich gelöscht')
      setShowDeleteDialog(false)
      navigate('/einkauf')
    } catch (err: any) {
      push(`Löschen fehlgeschlagen: ${err.response?.data?.detail || err.message}`)
    }
  }

  // Globale Shortcuts
  useGlobalShortcutsWithVoice({
    'open-customer-selection': () => setShowLieferantDialog(true),
    'open-article-selection': () => setShowArticleDialog(true),
    'confirm-position': () => handlePositionOK(),
    'save-document': () => void handleSave(),
    'print-document': () => { if (!showPrintDialog) setShowPrintDialog(true) },
    'delete-document': () => setShowDeleteDialog(true),
    'close-document': () => navigate(-1),
    cancel: () => {
      setShowLieferantDialog(false)
      setShowArticleDialog(false)
      setShowPrintDialog(false)
    },
  })

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-green-600 text-white px-4 py-2">
        <h1 className="text-lg font-bold">EINKAUF-LIEFERSCHEIN</h1>
      </div>
      <ModuleToolbar
        backTarget="/einkauf"
        closeTarget="/einkauf"
        title="Einkauf Lieferschein"
      />

      <div className="flex-1 overflow-auto p-4">
        {/* Header-Bereich (3 Spalten) */}
        <Card className="mb-4 p-4">
          <div className="grid grid-cols-3 gap-4">

            {/* Linke Spalte */}
            <div className="space-y-2">
              {/* int.Liefersch.-Nr. */}
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">int.Liefersch.-Nr.:</Label>
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
              {/* Lieferschein-Nr. (Lieferant) */}
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">Lieferschein-Nr.:</Label>
                <Input
                  value={state.lieferNr}
                  onChange={(e) => setState((p) => ({ ...p, lieferNr: e.target.value }))}
                  className="flex-1 h-8"
                  placeholder="Nummer des Lieferanten"
                />
              </div>
              {/* Liefer-Datum */}
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">Liefer-Datum:</Label>
                <Input
                  type="date"
                  value={state.lieferDatum}
                  onChange={(e) => setState((p) => ({ ...p, lieferDatum: e.target.value }))}
                  className="flex-1 h-8"
                />
              </div>
              {/* Erledigt */}
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={state.erledigt}
                  onCheckedChange={(v) => setState((p) => ({ ...p, erledigt: v === true }))}
                />
                <Label className="text-sm">Erledigt</Label>
              </div>
            </div>

            {/* Mittlere Spalte */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Niederlassung:</Label>
                <Input
                  value={state.niederlassung}
                  onChange={(e) => setState((p) => ({ ...p, niederlassung: e.target.value }))}
                  className="flex-1 h-8"
                />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Kostenstelle:</Label>
                <Input value="" readOnly className="flex-1 h-8 bg-muted" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Bediener:</Label>
                <Input
                  value={state.bediener}
                  onChange={(e) => setState((p) => ({ ...p, bediener: e.target.value }))}
                  className="flex-1 h-8"
                />
              </div>
              <div className="flex items-center gap-2 pt-1">
                <a
                  href="#"
                  className="text-sm text-blue-600 underline hover:text-blue-800"
                  onClick={async (e) => {
                    e.preventDefault()
                    try {
                      const params: Record<string, string> = {}
                      if (state.lieferant?.id) params.lieferant_id = state.lieferant.id
                      const data = await apiClient.get<EinkaufLSResponse | null>(
                        '/api/v1/einkauf/lieferscheine/last',
                        { params }
                      )
                      if (!data?.id) {
                        push('Kein vorheriger Lieferschein gefunden.')
                        return
                      }
                      const positionen: EinkaufPosition[] = (data.positionen || []).map((pos) => {
                        const ep = parseFloat(pos.einzelpreis || '0')
                        const mwst = 19
                        const bruttoPreis = ep * (1 + mwst / 100)
                        const menge = parseFloat(pos.menge || '0')
                        return {
                          posNr: pos.pos_nr,
                          artikelNr: pos.artikel_nr || '',
                          artikelId: null,
                          lieferantArtikelNr: pos.lieferant_artikel_nr || '',
                          bezeichnung: pos.bezeichnung || '',
                          bezeichnung2: '',
                          gebindeNr: pos.gebinde_nr || '',
                          gebinde: parseFloat(pos.gebinde || '0'),
                          menge,
                          einheit: pos.einheit || '',
                          einzelpreis: ep,
                          nettoBetrag: parseFloat(pos.nettobetrag || '0'),
                          mwstProzent: mwst,
                          bruttoPreis,
                          bruttoBetrag: bruttoPreis * menge,
                          niederlassung: '',
                          lagerhalle: pos.lagerhalle || '',
                          lagerfach: pos.lagerfach || '',
                          charge: pos.charge || '',
                          serienNr: pos.serien_nr || '',
                          kontraktNr: pos.kontakt || '',
                          streckeNr: '',
                          naBio: '',
                          musterNr: pos.master_nr || '',
                          prozent: parseFloat(pos.prozent || '0'),
                          skontierf: false,
                        }
                      })
                      const lieferant: Lieferant | null = data.lieferant_id
                        ? {
                            id: data.lieferant_id,
                            lieferantNr: data.lieferant_id,
                            name: data.lieferant_name || '',
                            kreditorAccount: data.lieferant_id,
                          }
                        : state.lieferant
                      setState((prev) => ({
                        ...prev,
                        id: null,
                        lieferscheinNr: generateLsNr(),
                        lieferNr: data.liefer_nr || '',
                        lieferDatum: data.lieferschein_datum
                          ? formatDate(new Date(data.lieferschein_datum))
                          : prev.lieferDatum,
                        niederlassung: data.niederlassung ?? prev.niederlassung,
                        bediener: getBediener(),
                        lieferant,
                        zahlungsbedingung: data.zahlungsbedingung ?? prev.zahlungsbedingung,
                        texte: data.texte ?? prev.texte,
                        zwischenhaendler: data.zwischenhaendler ?? prev.zwischenhaendler,
                        positionen,
                        aktivePositionIndex: null,
                        positionCharge: '',
                        positionSerienNr: '',
                      }))
                      push('Daten vom vorherigen Lieferschein übernommen.')
                    } catch (err: any) {
                      push(`Fehler: ${err.response?.data?.detail ?? err.message}`)
                    }
                  }}
                >
                  wie vorh. LS (F11)
                </a>
                <span className="text-muted-foreground text-sm mx-1">|</span>
                <a
                  href="#"
                  className="text-sm text-blue-600 underline hover:text-blue-800"
                  onClick={(e) => {
                    e.preventDefault()
                    if (state.lieferant) {
                      push(`Öffne Lieferanten-Stamm: ${state.lieferant.name}`)
                    } else {
                      setShowLieferantDialog(true)
                    }
                  }}
                >
                  Lieferanten-Stamm
                </a>
              </div>
            </div>

            {/* Rechte Spalte — Lieferant Tabs */}
            <div className="space-y-2">
              <Tabs
                value={lieferantTab}
                onValueChange={(v) => setLieferantTab(v as typeof lieferantTab)}
              >
                <TabsList className="grid w-full grid-cols-4 h-auto">
                  <TabsTrigger value="lieferant" className="text-xs py-1">LIEFERANT</TabsTrigger>
                  <TabsTrigger value="zahlungsbed" className="text-xs py-1">ZAHLUNGSBED.</TabsTrigger>
                  <TabsTrigger value="texte" className="text-xs py-1">TEXTE</TabsTrigger>
                  <TabsTrigger value="zwhaendler" className="text-xs py-1">ZW-HÄNDLER</TabsTrigger>
                </TabsList>

                <TabsContent value="lieferant" className="mt-2 space-y-1 min-h-[80px]">
                  {state.lieferant ? (
                    <div className="text-sm space-y-1">
                      <div className="font-semibold">{state.lieferant.name}</div>
                      {state.lieferant.address?.street && (
                        <div>{state.lieferant.address.street}</div>
                      )}
                      {(state.lieferant.address?.postalCode || state.lieferant.address?.city) && (
                        <div>
                          {[state.lieferant.address.postalCode, state.lieferant.address.city]
                            .filter(Boolean)
                            .join(' ')}
                        </div>
                      )}
                      {state.lieferant.address?.phone && (
                        <div className="text-muted-foreground">
                          Tel: {state.lieferant.address.phone}
                        </div>
                      )}
                      {state.lieferant.kontaktperson && (
                        <div className="text-muted-foreground">
                          Kp.: {state.lieferant.kontaktperson}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-muted-foreground">
                      Kein Lieferant ausgewählt
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="zahlungsbed" className="mt-2 min-h-[80px]">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label className="text-xs w-32">Zahlungsbedingung:</Label>
                      <Input
                        value={state.zahlungsbedingung}
                        onChange={(e) =>
                          setState((p) => ({ ...p, zahlungsbedingung: e.target.value }))
                        }
                        className="flex-1 h-8 text-sm"
                        placeholder="z.B. 30 Tage netto"
                      />
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="texte" className="mt-2 min-h-[80px]">
                  <div className="space-y-2">
                    <Label className="text-xs">Texte / Hinweise:</Label>
                    <textarea
                      value={state.texte}
                      onChange={(e) => setState((p) => ({ ...p, texte: e.target.value }))}
                      className="w-full h-16 text-sm border rounded p-2 resize-none focus:outline-none focus:ring-1 focus:ring-ring"
                      placeholder="Freitext..."
                    />
                  </div>
                </TabsContent>

                <TabsContent value="zwhaendler" className="mt-2 min-h-[80px]">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label className="text-xs w-32">Zwischenhändler:</Label>
                      <Input
                        value={state.zwischenhaendler}
                        onChange={(e) =>
                          setState((p) => ({ ...p, zwischenhaendler: e.target.value }))
                        }
                        className="flex-1 h-8 text-sm"
                      />
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>

              {/* Kreditor-Kto. unter den Tabs */}
              <div className="flex items-center gap-2">
                <Label className="w-28 text-sm shrink-0">Kreditor-Kto.:</Label>
                <Input
                  value={state.lieferant?.kreditorAccount || ''}
                  readOnly
                  className="flex-1 h-8"
                />
                <ShortcutHintButton shortcut="Strg+F1">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0"
                    onClick={() => setShowLieferantDialog(true)}
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </ShortcutHintButton>
              </div>
              {state.lieferant && (
                <div className="text-sm pl-28">
                  <div className="font-medium">{state.lieferant.name}</div>
                </div>
              )}
            </div>
          </div>
        </Card>

        {/* → Bestellung(en) importieren */}
        <div className="mb-2 flex items-center gap-2">
          <Button
            variant="link"
            className="text-sm text-blue-600 underline hover:text-blue-800 p-0 h-auto font-medium"
            onClick={() => setShowImportBestellungDialog(true)}
          >
            → Bestellung(en) importieren
          </Button>
          {state.lieferant && (
            <span className="text-muted-foreground text-xs">
              für {state.lieferant.name}
            </span>
          )}
        </div>

        {/* Positionen-Grid */}
        <Card className="mb-4 p-4">
          <h2 className="mb-2 font-semibold text-sm">Positionen</h2>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-14">Pos.-Nr.</TableHead>
                  <TableHead className="w-24">Artikel-Nr.</TableHead>
                  <TableHead className="w-24">Lief.Artikel-Nr.</TableHead>
                  <TableHead className="w-32">Bezeichn.</TableHead>
                  <TableHead className="w-32">Bezeichn2.</TableHead>
                  <TableHead className="w-20">Geb.-Me.</TableHead>
                  <TableHead className="w-16">Gebinde</TableHead>
                  <TableHead className="w-20">Menge</TableHead>
                  <TableHead className="w-16">Einheit</TableHead>
                  <TableHead className="w-24">Einh.-Preis</TableHead>
                  <TableHead className="w-24">Netto-Betr.</TableHead>
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
                  <TableHead className="w-20">Muster-Nr.</TableHead>
                  <TableHead className="w-24 text-right">Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {state.positionen.map((pos, idx) => (
                  <TableRow
                    key={idx}
                    className={
                      state.aktivePositionIndex === idx ? 'bg-green-100' : 'cursor-pointer hover:bg-muted/50'
                    }
                    onClick={() =>
                      setState((p) => ({ ...p, aktivePositionIndex: idx }))
                    }
                  >
                    <TableCell>{pos.posNr}</TableCell>
                    <TableCell>{pos.artikelNr}</TableCell>
                    <TableCell>{pos.lieferantArtikelNr}</TableCell>
                    <TableCell>{pos.bezeichnung}</TableCell>
                    <TableCell>{pos.bezeichnung2}</TableCell>
                    <TableCell>{pos.gebindeNr}</TableCell>
                    <TableCell>{pos.gebinde || ''}</TableCell>
                    <TableCell>{pos.menge}</TableCell>
                    <TableCell>{pos.einheit}</TableCell>
                    <TableCell>{pos.einzelpreis.toFixed(2)}</TableCell>
                    <TableCell>{pos.nettoBetrag.toFixed(2)}</TableCell>
                    <TableCell>{pos.bruttoBetrag.toFixed(2)}</TableCell>
                    <TableCell>{pos.niederlassung}</TableCell>
                    <TableCell>{pos.lagerhalle}</TableCell>
                    <TableCell>{pos.lagerfach}</TableCell>
                    <TableCell>{pos.charge}</TableCell>
                    <TableCell></TableCell>
                    <TableCell>{pos.serienNr}</TableCell>
                    <TableCell>{pos.kontraktNr}</TableCell>
                    <TableCell>{pos.streckeNr}</TableCell>
                    <TableCell>{pos.naBio}</TableCell>
                    <TableCell>{pos.musterNr}</TableCell>
                    <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
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
            <div className="space-y-1">
              <Label className="text-xs">Lief.Artikel-Nr.:</Label>
              <Input
                value={currentPos.lieferantArtikelNr}
                onChange={(e) =>
                  setCurrentPos((p) => ({ ...p, lieferantArtikelNr: e.target.value }))
                }
                className="h-8"
              />
            </div>
            <div className="space-y-1 col-span-2">
              <Label className="text-xs">Bezeichnung:</Label>
              <Input value={currentPos.artikelBezeichnung} readOnly className="h-8" />
              <Input value={currentPos.artikelBezeichnung2} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Gebinde-Me.:</Label>
              <Input
                value={currentPos.gebindeNr}
                onChange={(e) => setCurrentPos((p) => ({ ...p, gebindeNr: e.target.value }))}
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Gebinde:</Label>
              <Input
                type="number"
                value={currentPos.gebinde}
                onChange={(e) =>
                  setCurrentPos((p) => ({ ...p, gebinde: Number(e.target.value) }))
                }
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Menge:</Label>
              <Input
                type="number"
                value={currentPos.menge}
                onChange={(e) =>
                  setCurrentPos((p) => ({ ...p, menge: Number(e.target.value) }))
                }
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Einheit:</Label>
              <Input value={currentPos.einheit} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Einh.-Preis:</Label>
              <Input
                type="number"
                step="0.01"
                value={currentPos.einzelpreis}
                onChange={(e) =>
                  setCurrentPos((p) => ({ ...p, einzelpreis: Number(e.target.value) }))
                }
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Brutto-Preis:</Label>
              <Input value={currentPos.bruttoPreis.toFixed(2)} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Brutto-Betrag:</Label>
              <Input value={currentPos.bruttoBetrag.toFixed(2)} readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Rabatt %:</Label>
              <Input
                type="number"
                value={currentPos.prozent}
                onChange={(e) =>
                  setCurrentPos((p) => ({ ...p, prozent: Number(e.target.value) }))
                }
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">MWSt. %:</Label>
              <Input
                type="number"
                value={currentPos.mwstProzent}
                onChange={(e) =>
                  setCurrentPos((p) => ({ ...p, mwstProzent: Number(e.target.value) }))
                }
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Kostenstelle:</Label>
              <Input
                value={currentPos.kostenstelle}
                onChange={(e) =>
                  setCurrentPos((p) => ({ ...p, kostenstelle: e.target.value }))
                }
                className="h-8"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Kontrakt-Nr.:</Label>
              <Input
                value={currentPos.kontraktNr}
                onChange={(e) =>
                  setCurrentPos((p) => ({ ...p, kontraktNr: e.target.value }))
                }
                className="h-8"
              />
            </div>

            {/* Zeile-OK-Leiste */}
            <div className="col-span-6 flex items-center gap-2 pt-1 flex-wrap">
              <Button variant="outline" size="sm" className="h-8" onClick={() => setShowPopUpDialog(true)} title="Zusatzinfos">
                PopUp
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-8"
                onClick={() => push('Preis aktualisiert')}
              >
                Aktualisieren
              </Button>
              <div className="flex items-center gap-1">
                <Checkbox
                  checked={currentPos.skontierf}
                  onCheckedChange={(v) =>
                    setCurrentPos((p) => ({ ...p, skontierf: v === true }))
                  }
                />
                <Label className="text-xs">skontierfähig</Label>
              </div>
              <Button variant="outline" size="sm" className="h-8" onClick={() => setShowNiederlassungDialog(true)} title="Niederlassung">
                Niederlassung...
              </Button>
              <Button variant="outline" size="sm" className="h-8" onClick={() => setShowChargenSerienDialog(true)} title="Chargen/Serien">
                Chargen-/Serien-Nr.
              </Button>
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
          <div className="grid grid-cols-5 gap-4">
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
              <Label className="text-xs">Summe Gewicht:</Label>
              <Input value="0.00 kg" readOnly className="h-8" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Währung:</Label>
              <Input value="EUR" readOnly className="h-8" />
            </div>
          </div>
        </Card>
      </div>

      {/* Bottom-Toolbar */}
      <div className="border-t bg-white px-4 py-2 flex items-center justify-between">
        <div className="flex gap-2 flex-wrap">
          <Button
            onClick={() => setShowPrintDialog(true)}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <Printer className="h-4 w-4" />
            LS drucken
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="gap-2"
            onClick={() => setShowAttachmentDialog(true)}
          >
            <FileText className="h-4 w-4" />
            Unterlagen
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="gap-2"
            onClick={() => setShowAttachmentDialog(true)}
          >
            <Folder className="h-4 w-4" />
            Dateien
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="gap-2 text-red-600"
            onClick={() => setShowDeleteDialog(true)}
          >
            <Trash2 className="h-4 w-4" />
            LS löschen
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
            <Button variant="outline" onClick={() => navigate('/einkauf')} size="sm">
              Schließen
            </Button>
          </ShortcutHintButton>
        </div>
      </div>

      {/* Dialoge */}
      <LieferantSuchDialog
        open={showLieferantDialog}
        onClose={() => setShowLieferantDialog(false)}
        onSelect={handleLieferantSelect}
      />
      <ArtikelSuchDialog
        open={showArticleDialog}
        onClose={() => setShowArticleDialog(false)}
        onSelect={handleArticleSelect}
      />
      <LieferscheinDruckDialog
        open={showPrintDialog}
        onClose={() => setShowPrintDialog(false)}
        onConfirm={handlePrint}
      />
      <DmsAnhangDialog
        open={showAttachmentDialog}
        onClose={() => setShowAttachmentDialog(false)}
        businessObjectType="einkauf_lieferschein"
        businessObjectId={state.id}
        title="UNTERLAGEN / DATEIEN — EINKAUFS-LIEFERSCHEIN"
      />

      <Dialog open={showImportBestellungDialog} onOpenChange={setShowImportBestellungDialog}>
        <DialogContent className="sm:max-w-xl">
          <DialogHeader>
            <DialogTitle>Bestellung(en) importieren</DialogTitle>
          </DialogHeader>
          {!state.lieferant ? (
            <p className="text-sm text-muted-foreground py-4">
              Bitte wählen Sie zuerst einen Lieferanten aus. Anschließend können Sie offene Bestellungen dieses Lieferanten als Lieferschein-Positionen übernehmen.
            </p>
          ) : (
            <>
              <p className="text-sm text-muted-foreground mb-3">
                Bestellung auswählen — Positionen werden an die bestehende Positionsliste angehängt.
              </p>
              {loadingBestellungen ? (
                <p className="text-sm py-4">Bestellungen werden geladen…</p>
              ) : bestellungenList.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4">Keine Bestellungen für diesen Lieferanten gefunden.</p>
              ) : (
                <div className="max-h-64 overflow-y-auto border rounded">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-12"></TableHead>
                        <TableHead>Bestellnr.</TableHead>
                        <TableHead>Datum</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Positionen</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {bestellungenList.map((b) => (
                        <TableRow
                          key={b.id}
                          className={selectedBestellungId === b.id ? 'bg-muted' : ''}
                          onClick={() => setSelectedBestellungId(b.id)}
                        >
                          <TableCell>
                            <input
                              type="radio"
                              name="bestellung"
                              checked={selectedBestellungId === b.id}
                              onChange={() => setSelectedBestellungId(b.id)}
                            />
                          </TableCell>
                          <TableCell className="font-mono">{b.bestellnummer}</TableCell>
                          <TableCell>{b.bestelldatum ? new Date(b.bestelldatum).toLocaleDateString('de-DE') : '–'}</TableCell>
                          <TableCell>{b.status}</TableCell>
                          <TableCell className="text-right">{b.positionen_anz}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowImportBestellungDialog(false)}>Schließen</Button>
            {state.lieferant && bestellungenList.length > 0 && (
              <Button onClick={() => void handleImportBestellungPositionen()} disabled={!selectedBestellungId}>
                Positionen übernehmen
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showPopUpDialog} onOpenChange={setShowPopUpDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Zusatzinfos Position</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-2 text-sm py-2">
            <span className="text-muted-foreground">Pos.-Nr.:</span><span>{currentPos.posNr}</span>
            <span className="text-muted-foreground">Artikel:</span><span>{currentPos.artikelNr}</span>
            <span className="text-muted-foreground">Bezeichnung:</span><span className="col-span-2">{currentPos.artikelBezeichnung || '–'}</span>
            <span className="text-muted-foreground">Menge:</span><span>{currentPos.menge} {currentPos.einheit}</span>
            <span className="text-muted-foreground">Einzelpreis:</span><span>{currentPos.einzelpreis.toFixed(2)} €</span>
            <span className="text-muted-foreground">Kontrakt-Nr.:</span><span>{currentPos.kontraktNr || '–'}</span>
            <span className="text-muted-foreground">Skontierfähig:</span><span>{currentPos.skontierf ? 'Ja' : 'Nein'}</span>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPopUpDialog(false)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showNiederlassungDialog} onOpenChange={setShowNiederlassungDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Niederlassung wählen</DialogTitle>
          </DialogHeader>
          <div className="max-h-64 overflow-y-auto space-y-1 py-2">
            {branchesList.length === 0 && <p className="text-sm text-muted-foreground">Keine Niederlassungen geladen.</p>}
            {branchesList.map((b) => (
              <Button key={b.id} variant="outline" className="w-full justify-start" onClick={() => { setState((p) => ({ ...p, niederlassung: b.name || String(b.branch_number) })); setShowNiederlassungDialog(false); push('Niederlassung übernommen.'); }}>
                {b.name || `Nr. ${b.branch_number}`}
              </Button>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNiederlassungDialog(false)}>Abbrechen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showChargenSerienDialog} onOpenChange={setShowChargenSerienDialog}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Chargen- / Serien-Nr.</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label className="text-sm">Charge</Label>
              <Input value={state.positionCharge} onChange={(e) => setState((p) => ({ ...p, positionCharge: e.target.value }))} placeholder="z. B. CHARGE-001" className="mt-1" />
            </div>
            <div>
              <Label className="text-sm">Serien-Nr.</Label>
              <Input value={state.positionSerienNr} onChange={(e) => setState((p) => ({ ...p, positionSerienNr: e.target.value }))} placeholder="z. B. SN-12345" className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowChargenSerienDialog(false)}>Abbrechen</Button>
            <Button onClick={() => { setShowChargenSerienDialog(false); push('Charge/Serien-Nr. werden bei nächster Zeile OK übernommen.'); }}>Übernehmen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Lieferschein löschen?</DialogTitle>
          </DialogHeader>
          <div className="py-2 text-sm">
            {state.id ? (
              <>
                Lieferschein <strong>{state.lieferscheinNr}</strong> wird unwiderruflich gelöscht.
                Fortfahren?
              </>
            ) : (
              'Das Formular wird geleert. Nicht gespeicherte Daten gehen verloren.'
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Abbrechen
            </Button>
            <Button variant="destructive" onClick={() => void handleDelete()}>
              Löschen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
