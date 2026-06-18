import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useToast } from '@/hooks/use-toast'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  createBuchung,
  createKostenart,
  createKostenstelle,
  deleteBuchung,
  deleteKostenart,
  deleteKostenstelle,
  getKostenstellenReport,
  listBuchungen,
  listKostenarten,
  listKostenstellen,
  updateKostenstelle,
  type KostenstelleArt,
  type Kostenstelle,
  type Kostenart,
  type Kostenbuchung,
  type KostenstelleAuswertung,
} from '@/lib/api/kostenrechnung'
import {
  BarChart3,
  BookOpen,
  Building2,
  Euro,
  Plus,
  Tag,
  Trash2,
  TrendingDown,
  TrendingUp,
} from 'lucide-react'

const TABS = ['Auswertung', 'Kostenstellen', 'Kostenarten', 'Buchungen'] as const
type Tab = (typeof TABS)[number]

const KST_ARTEN: KostenstelleArt[] = ['KOSTENSTELLE', 'KOSTENTRAEGER', 'PROJEKT', 'ABTEILUNG']
const KST_ART_LABELS: Record<string, string> = {
  KOSTENSTELLE: 'Kostenstelle', KOSTENTRAEGER: 'Kostenträger', PROJEKT: 'Projekt', ABTEILUNG: 'Abteilung',
}
const KOA_GRUPPEN = ['PERSONAL', 'MATERIAL', 'ABSCHREIBUNG', 'FREMDLEISTUNG', 'ENERGIE', 'SONSTIGE'] as const
const KOA_GRUPPE_LABELS: Record<string, string> = {
  PERSONAL: 'Personal', MATERIAL: 'Material', ABSCHREIBUNG: 'Abschreibung',
  FREMDLEISTUNG: 'Fremdleistung', ENERGIE: 'Energie', SONSTIGE: 'Sonstige',
}

const fmtEur = (v: number) =>
  v.toLocaleString('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 })
const fmtEurFull = (v: number) =>
  v.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })

function TabBar({ active, onChange }: { active: Tab; onChange: (t: Tab) => void }) {
  return (
    <div className="flex gap-1 border-b flex-wrap">
      {TABS.map(t => (
        <button
          key={t}
          onClick={() => onChange(t)}
          className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
            active === t ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          {t}
        </button>
      ))}
    </div>
  )
}

// ── Auswertung ────────────────────────────────────────────────────────────────

function AuswertungTab() {
  const today = new Date()
  const [von, setVon] = useState(`${today.getFullYear()}-01-01`)
  const [bis, setBis] = useState(today.toISOString().split('T')[0])
  const [queried, setQueried] = useState({ von, bis })
  const [loading, setLoading] = useState(false)

  const q = useQuery({
    queryKey: ['kostenrechnung', 'report', queried.von, queried.bis],
    queryFn: () => getKostenstellenReport(queried.von, queried.bis),
  })

  const handleAbfragen = async () => {
    if (loading) return
    setLoading(true)
    setQueried({ von, bis })
    setLoading(false)
  }

  const r = q.data

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="pt-4 flex flex-wrap gap-3 items-end">
          <div className="space-y-1">
            <label className="text-xs font-medium">Von</label>
            <Input type="date" className="w-36" value={von} onChange={e => setVon(e.target.value)} />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Bis</label>
            <Input type="date" className="w-36" value={bis} onChange={e => setBis(e.target.value)} />
          </div>
          <Button disabled={loading} onClick={() => void handleAbfragen()}>
            <BarChart3 className="h-3 w-3 mr-1" /> Auswerten
          </Button>
        </CardContent>
      </Card>

      {q.isLoading && <p className="text-sm text-muted-foreground p-2">Lade Auswertung…</p>}
      {q.isError && <p className="text-sm text-destructive p-2">Fehler beim Laden der Auswertung.</p>}

      {r && (
        <>
          <div className="grid gap-4 sm:grid-cols-4">
            {[
              { label: 'Budget gesamt', value: fmtEur(Number(r.gesamt_budget)), icon: Euro, color: 'text-blue-700' },
              { label: 'Verbraucht (Ist)', value: fmtEur(Number(r.gesamt_verbraucht)), icon: TrendingDown, color: 'text-amber-700' },
              { label: 'Verfügbar', value: fmtEur(Number(r.gesamt_offen)), icon: TrendingUp, color: Number(r.gesamt_offen) >= 0 ? 'text-green-700' : 'text-red-700' },
              {
                label: 'Auslastung',
                value: Number(r.gesamt_budget) > 0 ? `${((Number(r.gesamt_verbraucht) / Number(r.gesamt_budget)) * 100).toFixed(1)}%` : '—',
                icon: BarChart3,
                color: 'text-foreground',
              },
            ].map(({ label, value, icon: Icon, color }) => (
              <Card key={label}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <Icon className={`h-4 w-4 ${color}`} />
                    <span className={`text-xl font-bold tabular-nums ${color}`}>{value}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <BarChart3 className="h-4 w-4" /> Kostenstellen-Übersicht
              </CardTitle>
              <CardDescription>
                {queried.von} — {queried.bis} · {r.auswertungen.length} Kostenstellen
              </CardDescription>
            </CardHeader>
            <CardContent>
              {r.auswertungen.length === 0 ? (
                <p className="text-sm text-muted-foreground">Keine aktiven Kostenstellen vorhanden.</p>
              ) : (
                <div className="space-y-4">
                  {(r.auswertungen as KostenstelleAuswertung[]).map(kst => (
                    <div key={kst.kostenstelle_id} className="space-y-2">
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="font-mono text-xs text-muted-foreground mr-2">{kst.nummer}</span>
                          <span className="font-semibold">{kst.bezeichnung}</span>
                          <Badge variant="outline" className="ml-2 text-xs">{KST_ART_LABELS[kst.kostenstelle_art] ?? kst.kostenstelle_art}</Badge>
                        </div>
                        <div className="text-right shrink-0 ml-4">
                          <div className="font-bold tabular-nums">{fmtEur(Number(kst.verbraucht))}</div>
                          <div className="text-xs text-muted-foreground">Budget: {fmtEur(Number(kst.budget))}</div>
                          {kst.buchungen_anzahl > 0 && (
                            <div className="text-xs text-muted-foreground">{kst.buchungen_anzahl} Buchungen</div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all ${
                              kst.auslastung_prozent > 100 ? 'bg-red-600'
                              : kst.auslastung_prozent > 90 ? 'bg-orange-500'
                              : kst.auslastung_prozent > 75 ? 'bg-amber-400'
                              : 'bg-green-500'
                            }`}
                            style={{ width: `${Math.min(kst.auslastung_prozent, 100)}%` }}
                          />
                        </div>
                        <Badge
                          variant={kst.auslastung_prozent > 100 ? 'destructive' : kst.auslastung_prozent > 90 ? 'secondary' : 'outline'}
                          className="tabular-nums w-16 justify-center"
                        >
                          {kst.auslastung_prozent.toFixed(1)}%
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

// ── Kostenstellen-Stammdaten ──────────────────────────────────────────────────

function KostenstellenTab() {
  const qc = useQueryClient()
  const { toast } = useToast()
  const [nummer, setNummer] = useState('')
  const [bezeichnung, setBezeichnung] = useState('')
  const [art, setArt] = useState<KostenstelleArt>('KOSTENSTELLE')
  const [verantwortlicher, setVerantwortlicher] = useState('')
  const [budget, setBudget] = useState('')
  const [budgetPeriode, setBudgetPeriode] = useState('MONAT')
  const [creating, setCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)

  const q = useQuery({ queryKey: ['kostenrechnung', 'kostenstellen'], queryFn: () => listKostenstellen() })
  const inv = () => qc.invalidateQueries({ queryKey: ['kostenrechnung', 'kostenstellen'] })

  const handleCreate = async () => {
    if (!nummer || !bezeichnung || creating) return
    setCreating(true)
    try {
      await createKostenstelle({
        nummer,
        bezeichnung,
        kostenstelle_art: art,
        verantwortlicher: verantwortlicher || null,
        budget: budget ? Number(budget) : null,
        budget_periode: budget ? budgetPeriode as 'MONAT' | 'QUARTAL' | 'JAHR' : null,
        aktiv: true,
        uebergeordnet: null,
      })
      toast({ title: 'Kostenstelle angelegt', description: `[${nummer}] ${bezeichnung}` })
      setNummer('')
      setBezeichnung('')
      setVerantwortlicher('')
      setBudget('')
      inv()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Fehler'
      toast({ title: 'Fehler', description: msg, variant: 'destructive' })
    } finally {
      setCreating(false)
    }
  }

  const handleToggleAktiv = async (kst: Kostenstelle) => {
    if (editingId) return
    setEditingId(kst.id)
    try {
      await updateKostenstelle(kst.id, { ...kst, aktiv: !kst.aktiv })
      toast({ title: kst.aktiv ? 'Deaktiviert' : 'Aktiviert', description: kst.bezeichnung })
      inv()
    } catch {
      toast({ title: 'Fehler', variant: 'destructive' })
    } finally {
      setEditingId(null)
    }
  }

  const handleDelete = async (kst: Kostenstelle) => {
    if (deletingId) return
    setDeletingId(kst.id)
    try {
      await deleteKostenstelle(kst.id)
      toast({ title: 'Kostenstelle gelöscht', description: kst.nummer })
      inv()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Löschen fehlgeschlagen (ggf. noch Buchungen vorhanden)'
      toast({ title: 'Fehler', description: msg, variant: 'destructive' })
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Building2 className="h-4 w-4" /> Kostenstelle anlegen [KST]</CardTitle>
          <CardDescription>Kostenstellen, Kostenträger, Projekte und Abteilungen mit Budget.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-3 items-end">
            <div className="space-y-1">
              <label className="text-xs font-medium">Nummer *</label>
              <Input className="w-28" value={nummer} onChange={e => setNummer(e.target.value)} placeholder="z. B. 4100" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Bezeichnung *</label>
              <Input className="w-56" value={bezeichnung} onChange={e => setBezeichnung(e.target.value)} placeholder="z. B. Getreidelager" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Art</label>
              <select className="border rounded px-2 py-1.5 text-sm" value={art} onChange={e => setArt(e.target.value as KostenstelleArt)}>
                {KST_ARTEN.map(a => <option key={a} value={a}>{KST_ART_LABELS[a]}</option>)}
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Verantwortlicher</label>
              <Input className="w-36" value={verantwortlicher} onChange={e => setVerantwortlicher(e.target.value)} placeholder="Name" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Budget (€)</label>
              <Input className="w-32" inputMode="decimal" value={budget} onChange={e => setBudget(e.target.value)} placeholder="z. B. 50000" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Budget-Periode</label>
              <select className="border rounded px-2 py-1.5 text-sm" value={budgetPeriode} onChange={e => setBudgetPeriode(e.target.value)} disabled={!budget}>
                <option value="MONAT">Monat</option>
                <option value="QUARTAL">Quartal</option>
                <option value="JAHR">Jahr</option>
              </select>
            </div>
            <Button disabled={!nummer || !bezeichnung || creating} onClick={() => void handleCreate()}>
              <Plus className="h-3 w-3 mr-1" />{creating ? 'Speichere…' : 'Anlegen'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Kostenstellen-Stammdaten</CardTitle></CardHeader>
        <CardContent>
          {q.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
          {q.isError && <p className="text-sm text-destructive">Fehler beim Laden.</p>}
          {q.data && (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="py-2 pr-3">Nr</th>
                  <th className="py-2 pr-3">Bezeichnung</th>
                  <th className="py-2 pr-3">Art</th>
                  <th className="py-2 pr-3">Verantwortlicher</th>
                  <th className="py-2 pr-3">Budget</th>
                  <th className="py-2 pr-3">Status</th>
                  <th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {q.data.length === 0 && (
                  <tr><td colSpan={7} className="py-6 text-center text-muted-foreground text-sm">Keine Kostenstellen vorhanden — oben anlegen.</td></tr>
                )}
                {(q.data as Kostenstelle[]).map(kst => (
                  <tr key={kst.id} className="border-b border-border/50">
                    <td className="py-2 pr-3 font-mono font-medium">{kst.nummer}</td>
                    <td className="py-2 pr-3">{kst.bezeichnung}</td>
                    <td className="py-2 pr-3"><Badge variant="outline" className="text-xs">{KST_ART_LABELS[kst.kostenstelle_art] ?? kst.kostenstelle_art}</Badge></td>
                    <td className="py-2 pr-3 text-muted-foreground">{kst.verantwortlicher ?? '—'}</td>
                    <td className="py-2 pr-3 tabular-nums">
                      {kst.budget != null ? (
                        <span>{fmtEur(Number(kst.budget))}<span className="text-xs text-muted-foreground ml-1">/{kst.budget_periode?.toLowerCase()}</span></span>
                      ) : '—'}
                    </td>
                    <td className="py-2 pr-3">
                      <button
                        disabled={editingId === kst.id}
                        onClick={() => void handleToggleAktiv(kst)}
                        className="cursor-pointer"
                      >
                        <Badge variant={kst.aktiv ? 'outline' : 'secondary'}>{kst.aktiv ? 'Aktiv' : 'Inaktiv'}</Badge>
                      </button>
                    </td>
                    <td className="py-2">
                      <Button size="sm" variant="ghost" disabled={deletingId === kst.id} onClick={() => void handleDelete(kst)}>
                        <Trash2 className="h-3 w-3 text-destructive" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// ── Kostenarten ───────────────────────────────────────────────────────────────

function KostenartenTab() {
  const qc = useQueryClient()
  const { toast } = useToast()
  const [nummer, setNummer] = useState('')
  const [bezeichnung, setBezeichnung] = useState('')
  const [gruppe, setGruppe] = useState('SONSTIGE')
  const [kontoNr, setKontoNr] = useState('')
  const [creating, setCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const q = useQuery({ queryKey: ['kostenrechnung', 'kostenarten'], queryFn: () => listKostenarten() })
  const inv = () => qc.invalidateQueries({ queryKey: ['kostenrechnung', 'kostenarten'] })

  const handleCreate = async () => {
    if (!nummer || !bezeichnung || creating) return
    setCreating(true)
    try {
      await createKostenart({
        nummer, bezeichnung,
        kostenart_gruppe: gruppe as Kostenart['kostenart_gruppe'],
        konto_nr: kontoNr || null,
        aktiv: true,
      })
      toast({ title: 'Kostenart angelegt', description: `[${nummer}] ${bezeichnung}` })
      setNummer('')
      setBezeichnung('')
      setKontoNr('')
      inv()
    } catch {
      toast({ title: 'Fehler', variant: 'destructive' })
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (koa: Kostenart) => {
    if (deletingId) return
    setDeletingId(koa.id)
    try {
      await deleteKostenart(koa.id)
      toast({ title: 'Gelöscht', description: koa.nummer })
      inv()
    } catch {
      toast({ title: 'Fehler', description: 'Löschen fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setDeletingId(null)
    }
  }

  const GRUPPE_COLORS: Record<string, string> = {
    PERSONAL: 'bg-blue-100 text-blue-800', MATERIAL: 'bg-amber-100 text-amber-800',
    ABSCHREIBUNG: 'bg-purple-100 text-purple-800', FREMDLEISTUNG: 'bg-orange-100 text-orange-800',
    ENERGIE: 'bg-yellow-100 text-yellow-800', SONSTIGE: 'bg-gray-100 text-gray-700',
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Tag className="h-4 w-4" /> Kostenart anlegen [KOA]</CardTitle>
          <CardDescription>Kostenarten strukturieren Kosten nach Aufwandscharakter (Personal, Material, Energie…).</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3 items-end">
          <div className="space-y-1">
            <label className="text-xs font-medium">Nummer *</label>
            <Input className="w-24" value={nummer} onChange={e => setNummer(e.target.value)} placeholder="z. B. 410" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Bezeichnung *</label>
            <Input className="w-56" value={bezeichnung} onChange={e => setBezeichnung(e.target.value)} placeholder="z. B. Löhne und Gehälter" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Gruppe</label>
            <select className="border rounded px-2 py-1.5 text-sm" value={gruppe} onChange={e => setGruppe(e.target.value)}>
              {KOA_GRUPPEN.map(g => <option key={g} value={g}>{KOA_GRUPPE_LABELS[g]}</option>)}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">FiBu-Konto (opt.)</label>
            <Input className="w-24" value={kontoNr} onChange={e => setKontoNr(e.target.value)} placeholder="z. B. 4100" />
          </div>
          <Button disabled={!nummer || !bezeichnung || creating} onClick={() => void handleCreate()}>
            <Plus className="h-3 w-3 mr-1" />{creating ? 'Speichere…' : 'Anlegen'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Kostenarten</CardTitle></CardHeader>
        <CardContent>
          {q.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
          {q.data && (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="py-2 pr-3">Nr</th><th className="py-2 pr-3">Bezeichnung</th>
                  <th className="py-2 pr-3">Gruppe</th><th className="py-2 pr-3">FiBu-Konto</th><th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {q.data.length === 0 && <tr><td colSpan={5} className="py-6 text-center text-sm text-muted-foreground">Keine Kostenarten vorhanden.</td></tr>}
                {(q.data as Kostenart[]).map(koa => (
                  <tr key={koa.id} className="border-b border-border/50">
                    <td className="py-2 pr-3 font-mono font-medium">{koa.nummer}</td>
                    <td className="py-2 pr-3">{koa.bezeichnung}</td>
                    <td className="py-2 pr-3">
                      <span className={`text-xs px-2 py-0.5 rounded font-medium ${GRUPPE_COLORS[koa.kostenart_gruppe] ?? ''}`}>
                        {KOA_GRUPPE_LABELS[koa.kostenart_gruppe] ?? koa.kostenart_gruppe}
                      </span>
                    </td>
                    <td className="py-2 pr-3 font-mono text-xs text-muted-foreground">{koa.konto_nr ?? '—'}</td>
                    <td className="py-2">
                      <Button size="sm" variant="ghost" disabled={deletingId === koa.id} onClick={() => void handleDelete(koa)}>
                        <Trash2 className="h-3 w-3 text-destructive" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// ── Buchungen ─────────────────────────────────────────────────────────────────

function BuchungenTab() {
  const qc = useQueryClient()
  const { toast } = useToast()
  const { data: kostenstellen = [] } = useQuery({
    queryKey: ['kostenrechnung', 'kostenstellen'],
    queryFn: () => listKostenstellen(),
  })
  const { data: kostenarten = [] } = useQuery({
    queryKey: ['kostenrechnung', 'kostenarten'],
    queryFn: () => listKostenarten(),
  })

  const [filterKstId, setFilterKstId] = useState('')
  const [filterPeriode, setFilterPeriode] = useState('')
  const [kstId, setKstId] = useState('')
  const [koaId, setKoaId] = useState('')
  const [datum, setDatum] = useState(new Date().toISOString().split('T')[0])
  const [betrag, setBetrag] = useState('')
  const [buchungstext, setBuchungstext] = useState('')
  const [beleg, setBeleg] = useState('')
  const [creating, setCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const q = useQuery({
    queryKey: ['kostenrechnung', 'buchungen', filterKstId, filterPeriode],
    queryFn: () => listBuchungen({
      kostenstelle_id: filterKstId || undefined,
      periode: filterPeriode || undefined,
    }),
  })
  const inv = () => qc.invalidateQueries({ queryKey: ['kostenrechnung', 'buchungen'] })

  const handleCreate = async () => {
    if (!kstId || !betrag || !datum || creating) return
    setCreating(true)
    try {
      await createBuchung({
        kostenstelle_id: kstId,
        kostenart_id: koaId || undefined,
        buchungsdatum: datum,
        betrag_eur: Number(betrag),
        buchungstext: buchungstext || undefined,
        belegnummer: beleg || undefined,
      })
      toast({ title: 'Buchung erfasst', description: `${fmtEurFull(Number(betrag))} auf ${kostenstellen.find(k => k.id === kstId)?.bezeichnung ?? kstId}` })
      setBetrag('')
      setBuchungstext('')
      setBeleg('')
      inv()
      qc.invalidateQueries({ queryKey: ['kostenrechnung', 'report'] })
    } catch {
      toast({ title: 'Fehler', description: 'Buchung fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (b: Kostenbuchung) => {
    if (deletingId) return
    setDeletingId(b.id)
    try {
      await deleteBuchung(b.id)
      toast({ title: 'Buchung gelöscht' })
      inv()
      qc.invalidateQueries({ queryKey: ['kostenrechnung', 'report'] })
    } catch {
      toast({ title: 'Fehler', variant: 'destructive' })
    } finally {
      setDeletingId(null)
    }
  }

  const kstMap = Object.fromEntries(kostenstellen.map(k => [k.id, k]))
  const koaMap = Object.fromEntries(kostenarten.map(k => [k.id, k]))

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><BookOpen className="h-4 w-4" /> Kostenbuchung erfassen</CardTitle>
          <CardDescription>Kosten manuell einer Kostenstelle zuordnen. Positiv = Kosten, negativ = Korrekturbuchung.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3 items-end">
          <div className="space-y-1">
            <label className="text-xs font-medium">Kostenstelle *</label>
            <select className="border rounded px-2 py-1.5 text-sm w-48" value={kstId} onChange={e => setKstId(e.target.value)}>
              <option value="">— wählen —</option>
              {kostenstellen.map(k => <option key={k.id} value={k.id}>{k.nummer} — {k.bezeichnung}</option>)}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Kostenart</label>
            <select className="border rounded px-2 py-1.5 text-sm w-40" value={koaId} onChange={e => setKoaId(e.target.value)}>
              <option value="">— optional —</option>
              {kostenarten.map(k => <option key={k.id} value={k.id}>{k.nummer} — {k.bezeichnung}</option>)}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Datum *</label>
            <Input type="date" className="w-36" value={datum} onChange={e => setDatum(e.target.value)} />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Betrag (€) *</label>
            <Input className="w-28" inputMode="decimal" value={betrag} onChange={e => setBetrag(e.target.value)} placeholder="z. B. 2500.00" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Buchungstext</label>
            <Input className="w-48" value={buchungstext} onChange={e => setBuchungstext(e.target.value)} placeholder="z. B. Miete Juni" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Beleg-Nr</label>
            <Input className="w-28" value={beleg} onChange={e => setBeleg(e.target.value)} placeholder="z. B. RE-2026-042" />
          </div>
          <Button disabled={!kstId || !betrag || !datum || creating} onClick={() => void handleCreate()}>
            <Plus className="h-3 w-3 mr-1" />{creating ? 'Buche…' : 'Buchen'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Buchungsliste</CardTitle>
          <div className="flex gap-2 flex-wrap">
            <select className="border rounded px-2 py-1 text-sm w-48" value={filterKstId} onChange={e => setFilterKstId(e.target.value)}>
              <option value="">Alle Kostenstellen</option>
              {kostenstellen.map(k => <option key={k.id} value={k.id}>{k.nummer} — {k.bezeichnung}</option>)}
            </select>
            <Input
              className="w-28" placeholder="YYYY-MM" value={filterPeriode}
              onChange={e => setFilterPeriode(e.target.value)}
            />
          </div>
        </CardHeader>
        <CardContent>
          {q.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
          {q.data && (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="py-2 pr-3">Datum</th><th className="py-2 pr-3">Kostenstelle</th>
                  <th className="py-2 pr-3">Kostenart</th><th className="py-2 pr-3">Buchungstext</th>
                  <th className="py-2 pr-3">Beleg</th><th className="py-2 pr-3 text-right">Betrag</th><th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {q.data.length === 0 && <tr><td colSpan={7} className="py-6 text-center text-sm text-muted-foreground">Keine Buchungen vorhanden.</td></tr>}
                {(q.data as Kostenbuchung[]).map(b => (
                  <tr key={b.id} className="border-b border-border/50">
                    <td className="py-2 pr-3 text-xs">{new Date(b.buchungsdatum).toLocaleDateString('de-DE')}</td>
                    <td className="py-2 pr-3 font-mono text-xs">{kstMap[b.kostenstelle_id]?.nummer ?? b.kostenstelle_id.slice(0, 8)}</td>
                    <td className="py-2 pr-3 text-muted-foreground text-xs">{b.kostenart_id ? (koaMap[b.kostenart_id]?.nummer ?? '?') : '—'}</td>
                    <td className="py-2 pr-3 max-w-[200px] truncate">{b.buchungstext ?? '—'}</td>
                    <td className="py-2 pr-3 font-mono text-xs text-muted-foreground">{b.belegnummer ?? '—'}</td>
                    <td className={`py-2 pr-3 text-right tabular-nums font-medium ${Number(b.betrag_eur) < 0 ? 'text-green-700' : ''}`}>
                      {fmtEurFull(Number(b.betrag_eur))}
                    </td>
                    <td className="py-2">
                      <Button size="sm" variant="ghost" disabled={deletingId === b.id} onClick={() => void handleDelete(b)}>
                        <Trash2 className="h-3 w-3 text-destructive" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// ── Hauptseite ────────────────────────────────────────────────────────────────

export default function KostenstellenrechnungPage(): JSX.Element {
  const [activeTab, setActiveTab] = useState<Tab>('Auswertung')

  return (
    <div className="p-6 space-y-4 max-w-6xl">
      <div>
        <h1 className="text-2xl font-bold">Kostenstellenrechnung</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Kostenstellen [KST] · Kostenarten [KOA] · Buchungen · Budget-Auswertung
        </p>
      </div>

      <TabBar active={activeTab} onChange={setActiveTab} />

      {activeTab === 'Auswertung' && <AuswertungTab />}
      {activeTab === 'Kostenstellen' && <KostenstellenTab />}
      {activeTab === 'Kostenarten' && <KostenartenTab />}
      {activeTab === 'Buchungen' && <BuchungenTab />}
    </div>
  )
}
