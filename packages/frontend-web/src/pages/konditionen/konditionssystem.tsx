import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useToast } from '@/hooks/use-toast'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  calculatePrice,
  createIndividualpreis,
  createPreisliste,
  createRabattgruppe,
  createRabattklasse,
  createRabattsatz,
  deleteIndividualpreis,
  deletePreisliste,
  deleteRabattgruppe,
  deleteRabattklasse,
  deleteRabattsatz,
  listIndividualpreise,
  listPreislisten,
  listRabattgruppen,
  listRabattklassen,
  listRabattsaetze,
  type Individualpreis,
  type Preisliste,
  type Rabattgruppe,
  type Rabattklasse,
  type Rabattsatz,
} from '@/lib/api/konditionen'
import { Calculator, List, Percent, Tag, Trash2, Plus } from 'lucide-react'

const TABS = ['Preislisten', 'Rabattgruppen', 'Rabattklassen', 'Rabattsätze', 'Individualpreise', 'Preisfindung'] as const
type Tab = (typeof TABS)[number]

function fmt(v: number) {
  return v.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 4 })
}

function fmtEur(v: number) {
  return v.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
}

// ── Shared helpers ────────────────────────────────────────────────────────────

function TabBar({ active, onChange }: { active: Tab; onChange: (t: Tab) => void }) {
  return (
    <div className="flex gap-1 border-b flex-wrap">
      {TABS.map(t => (
        <button
          key={t}
          onClick={() => onChange(t)}
          className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
            active === t ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          {t}
        </button>
      ))}
    </div>
  )
}

function EmptyRow({ cols, msg = 'Keine Einträge' }: { cols: number; msg?: string }) {
  return (
    <tr>
      <td colSpan={cols} className="py-6 text-center text-sm text-muted-foreground">
        {msg}
      </td>
    </tr>
  )
}

// ── Preislisten ───────────────────────────────────────────────────────────────

function PreislistenTab() {
  const qc = useQueryClient()
  const { toast } = useToast()
  const [name, setName] = useState('')
  const [typ, setTyp] = useState('standard')
  const [vonBis, setVonBis] = useState({ from: '', to: '' })
  const [creating, setCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const q = useQuery({ queryKey: ['konditionen', 'preislisten'], queryFn: () => listPreislisten() })
  const inv = () => qc.invalidateQueries({ queryKey: ['konditionen', 'preislisten'] })

  const handleCreate = async () => {
    if (!name || creating) return
    setCreating(true)
    try {
      await createPreisliste({
        name,
        price_list_type: typ,
        currency: 'EUR',
        is_active: true,
        valid_from: vonBis.from || null,
        valid_until: vonBis.to || null,
        items: [],
      })
      toast({ title: 'Preisliste angelegt', description: name })
      setName('')
      setVonBis({ from: '', to: '' })
      inv()
    } catch {
      toast({ title: 'Fehler', description: 'Preisliste konnte nicht angelegt werden.', variant: 'destructive' })
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (pl: Preisliste) => {
    if (deletingId) return
    setDeletingId(pl.id)
    try {
      await deletePreisliste(pl.id)
      toast({ title: 'Preisliste gelöscht', description: pl.name })
      inv()
    } catch {
      toast({ title: 'Fehler', description: 'Löschen fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><List className="h-4 w-4" /> Neue Preisliste</CardTitle>
          <CardDescription>Preislisten enthalten Artikel-Einzel- und Staffelpreise mit Gültigkeitszeitraum.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3 items-end">
          <div className="space-y-1">
            <label className="text-xs font-medium">Name *</label>
            <Input className="w-56" value={name} onChange={e => setName(e.target.value)} placeholder="z. B. VK-Standardliste 2026" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Typ</label>
            <select className="border rounded px-2 py-1.5 text-sm" value={typ} onChange={e => setTyp(e.target.value)}>
              <option value="standard">Standard</option>
              <option value="customer">Kundenliste</option>
              <option value="promotion">Aktionsliste</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Gültig von</label>
            <Input type="date" className="w-36" value={vonBis.from} onChange={e => setVonBis(p => ({ ...p, from: e.target.value }))} />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Gültig bis</label>
            <Input type="date" className="w-36" value={vonBis.to} onChange={e => setVonBis(p => ({ ...p, to: e.target.value }))} />
          </div>
          <Button disabled={!name || creating} onClick={() => void handleCreate()}>
            <Plus className="h-3 w-3 mr-1" />{creating ? 'Speichere…' : 'Anlegen'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Preislisten</CardTitle></CardHeader>
        <CardContent>
          {q.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
          {q.isError && <p className="text-sm text-destructive">Fehler beim Laden.</p>}
          {q.data && (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="py-2 pr-3">Name</th>
                  <th className="py-2 pr-3">Typ</th>
                  <th className="py-2 pr-3">Gültig von</th>
                  <th className="py-2 pr-3">Gültig bis</th>
                  <th className="py-2 pr-3">Pos.</th>
                  <th className="py-2 pr-3">Aktiv</th>
                  <th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {q.data.length === 0 && <EmptyRow cols={7} />}
                {(q.data as Preisliste[]).map(pl => (
                  <tr key={pl.id} className="border-b border-border/50">
                    <td className="py-2 pr-3 font-medium">{pl.name}</td>
                    <td className="py-2 pr-3 text-muted-foreground">{pl.price_list_type}</td>
                    <td className="py-2 pr-3 text-xs">{pl.valid_from ? new Date(pl.valid_from).toLocaleDateString('de-DE') : '—'}</td>
                    <td className="py-2 pr-3 text-xs">{pl.valid_until ? new Date(pl.valid_until).toLocaleDateString('de-DE') : 'unbegrenzt'}</td>
                    <td className="py-2 pr-3 tabular-nums">{pl.item_count}</td>
                    <td className="py-2 pr-3">
                      <Badge variant={pl.is_active ? 'outline' : 'secondary'}>{pl.is_active ? 'Aktiv' : 'Inaktiv'}</Badge>
                    </td>
                    <td className="py-2">
                      <Button size="sm" variant="ghost" disabled={deletingId === pl.id} onClick={() => void handleDelete(pl)}>
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

// ── Rabattgruppen ─────────────────────────────────────────────────────────────

function RabattgruppenTab() {
  const qc = useQueryClient()
  const { toast } = useToast()
  const [richtung, setRichtung] = useState<'EK' | 'VK'>('VK')
  const [gruppeNr, setGruppeNr] = useState('')
  const [bezeichnung, setBezeichnung] = useState('')
  const [creating, setCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const q = useQuery({ queryKey: ['konditionen', 'rabattgruppen', richtung], queryFn: () => listRabattgruppen(richtung) })
  const inv = () => qc.invalidateQueries({ queryKey: ['konditionen', 'rabattgruppen'] })

  const handleCreate = async () => {
    if (!gruppeNr || !bezeichnung || creating) return
    setCreating(true)
    try {
      await createRabattgruppe({ gruppe_nr: gruppeNr, bezeichnung, richtung })
      toast({ title: 'Rabattgruppe angelegt', description: `[${gruppeNr}] ${bezeichnung}` })
      setGruppeNr('')
      setBezeichnung('')
      inv()
    } catch {
      toast({ title: 'Fehler', description: 'Anlegen fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (g: Rabattgruppe) => {
    if (deletingId) return
    setDeletingId(g.id)
    try {
      await deleteRabattgruppe(g.id)
      toast({ title: 'Gelöscht', description: g.gruppe_nr })
      inv()
    } catch {
      toast({ title: 'Fehler', description: 'Löschen fehlgeschlagen (ggf. noch in Verwendung).', variant: 'destructive' })
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Tag className="h-4 w-4" /> Rabattgruppe anlegen [RAG]</CardTitle>
          <CardDescription>Rabattgruppen werden Artikeln zugeordnet (getrennt für EK und VK).</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3 items-end">
          <div className="space-y-1">
            <label className="text-xs font-medium">Richtung</label>
            <select className="border rounded px-2 py-1.5 text-sm" value={richtung} onChange={e => setRichtung(e.target.value as 'EK' | 'VK')}>
              <option value="VK">VK (Verkauf)</option>
              <option value="EK">EK (Einkauf)</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Gruppen-Nr *</label>
            <Input className="w-28" value={gruppeNr} onChange={e => setGruppeNr(e.target.value.toUpperCase())} placeholder="z. B. A1" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Bezeichnung *</label>
            <Input className="w-56" value={bezeichnung} onChange={e => setBezeichnung(e.target.value)} placeholder="z. B. Düngemittel VK" />
          </div>
          <Button disabled={!gruppeNr || !bezeichnung || creating} onClick={() => void handleCreate()}>
            <Plus className="h-3 w-3 mr-1" />{creating ? 'Speichere…' : 'Anlegen'}
          </Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Rabattgruppen ({richtung})</CardTitle>
        </CardHeader>
        <CardContent>
          {q.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
          {q.data && (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="py-2 pr-3">Nr</th><th className="py-2 pr-3">Bezeichnung</th><th className="py-2 pr-3">Richtung</th><th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {q.data.length === 0 && <EmptyRow cols={4} />}
                {(q.data as Rabattgruppe[]).map(g => (
                  <tr key={g.id} className="border-b border-border/50">
                    <td className="py-2 pr-3 font-mono font-medium">{g.gruppe_nr}</td>
                    <td className="py-2 pr-3">{g.bezeichnung}</td>
                    <td className="py-2 pr-3"><Badge variant="secondary">{g.richtung}</Badge></td>
                    <td className="py-2">
                      <Button size="sm" variant="ghost" disabled={deletingId === g.id} onClick={() => void handleDelete(g)}>
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

// ── Rabattklassen ─────────────────────────────────────────────────────────────

function RabattklassenTab() {
  const qc = useQueryClient()
  const { toast } = useToast()
  const [richtung, setRichtung] = useState<'EK' | 'VK'>('VK')
  const [klasseNr, setKlasseNr] = useState('')
  const [bezeichnung, setBezeichnung] = useState('')
  const [creating, setCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const q = useQuery({ queryKey: ['konditionen', 'rabattklassen', richtung], queryFn: () => listRabattklassen(richtung) })
  const inv = () => qc.invalidateQueries({ queryKey: ['konditionen', 'rabattklassen'] })

  const handleCreate = async () => {
    if (!klasseNr || !bezeichnung || creating) return
    setCreating(true)
    try {
      await createRabattklasse({ klasse_nr: klasseNr, bezeichnung, richtung })
      toast({ title: 'Rabattklasse angelegt', description: `[${klasseNr}] ${bezeichnung}` })
      setKlasseNr('')
      setBezeichnung('')
      inv()
    } catch {
      toast({ title: 'Fehler', description: 'Anlegen fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (k: Rabattklasse) => {
    if (deletingId) return
    setDeletingId(k.id)
    try {
      await deleteRabattklasse(k.id)
      toast({ title: 'Gelöscht', description: k.klasse_nr })
      inv()
    } catch {
      toast({ title: 'Fehler', description: 'Löschen fehlgeschlagen (ggf. noch in Verwendung).', variant: 'destructive' })
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Tag className="h-4 w-4" /> Rabattklasse anlegen [RAK]</CardTitle>
          <CardDescription>Rabattklassen werden Kunden/Lieferanten zugeordnet (getrennt für EK und VK).</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3 items-end">
          <div className="space-y-1">
            <label className="text-xs font-medium">Richtung</label>
            <select className="border rounded px-2 py-1.5 text-sm" value={richtung} onChange={e => setRichtung(e.target.value as 'EK' | 'VK')}>
              <option value="VK">VK (Verkauf)</option>
              <option value="EK">EK (Einkauf)</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Klassen-Nr *</label>
            <Input className="w-28" value={klasseNr} onChange={e => setKlasseNr(e.target.value.toUpperCase())} placeholder="z. B. K1" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Bezeichnung *</label>
            <Input className="w-56" value={bezeichnung} onChange={e => setBezeichnung(e.target.value)} placeholder="z. B. Genossenschaftsmitglied" />
          </div>
          <Button disabled={!klasseNr || !bezeichnung || creating} onClick={() => void handleCreate()}>
            <Plus className="h-3 w-3 mr-1" />{creating ? 'Speichere…' : 'Anlegen'}
          </Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className="text-base">Rabattklassen ({richtung})</CardTitle></CardHeader>
        <CardContent>
          {q.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
          {q.data && (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="py-2 pr-3">Nr</th><th className="py-2 pr-3">Bezeichnung</th><th className="py-2 pr-3">Richtung</th><th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {q.data.length === 0 && <EmptyRow cols={4} />}
                {(q.data as Rabattklasse[]).map(k => (
                  <tr key={k.id} className="border-b border-border/50">
                    <td className="py-2 pr-3 font-mono font-medium">{k.klasse_nr}</td>
                    <td className="py-2 pr-3">{k.bezeichnung}</td>
                    <td className="py-2 pr-3"><Badge variant="secondary">{k.richtung}</Badge></td>
                    <td className="py-2">
                      <Button size="sm" variant="ghost" disabled={deletingId === k.id} onClick={() => void handleDelete(k)}>
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

// ── Rabattsätze ───────────────────────────────────────────────────────────────

function RabattsaetzeTab() {
  const qc = useQueryClient()
  const { toast } = useToast()
  const [richtung, setRichtung] = useState<'EK' | 'VK'>('VK')
  const [gruppeNr, setGruppeNr] = useState('')
  const [klasseNr, setKlasseNr] = useState('')
  const [rabatt, setRabatt] = useState('')
  const [abMenge, setAbMenge] = useState('')
  const [gueltigAb, setGueltigAb] = useState('')
  const [creating, setCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const q = useQuery({ queryKey: ['konditionen', 'rabattsaetze', richtung], queryFn: () => listRabattsaetze({ richtung }) })
  const inv = () => qc.invalidateQueries({ queryKey: ['konditionen', 'rabattsaetze'] })

  const handleCreate = async () => {
    if (!gruppeNr || !klasseNr || !rabatt || creating) return
    setCreating(true)
    try {
      await createRabattsatz({
        rabattgruppe_nr: gruppeNr,
        rabattklasse_nr: klasseNr,
        richtung,
        rabatt_prozent: Number(rabatt),
        ab_menge: abMenge ? Number(abMenge) : undefined,
        gueltig_ab: gueltigAb || new Date().toISOString().split('T')[0],
      })
      toast({ title: 'Rabattsatz angelegt', description: `${gruppeNr} × ${klasseNr} = ${rabatt}%` })
      setGruppeNr('')
      setKlasseNr('')
      setRabatt('')
      setAbMenge('')
      setGueltigAb('')
      inv()
    } catch {
      toast({ title: 'Fehler', description: 'Anlegen fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (s: Rabattsatz) => {
    if (deletingId) return
    setDeletingId(s.id)
    try {
      await deleteRabattsatz(s.id)
      toast({ title: 'Gelöscht' })
      inv()
    } catch {
      toast({ title: 'Fehler', description: 'Löschen fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Percent className="h-4 w-4" /> Rabattsatz anlegen</CardTitle>
          <CardDescription>
            Kombination Rabattgruppe (Artikel) × Rabattklasse (Kunde/Lieferant) → Rabatt %.
            Gestaffelt über ab_menge möglich.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3 items-end">
          <div className="space-y-1">
            <label className="text-xs font-medium">Richtung</label>
            <select className="border rounded px-2 py-1.5 text-sm" value={richtung} onChange={e => setRichtung(e.target.value as 'EK' | 'VK')}>
              <option value="VK">VK</option><option value="EK">EK</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Rabattgruppe-Nr *</label>
            <Input className="w-28" value={gruppeNr} onChange={e => setGruppeNr(e.target.value.toUpperCase())} placeholder="z. B. A1" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Rabattklasse-Nr *</label>
            <Input className="w-28" value={klasseNr} onChange={e => setKlasseNr(e.target.value.toUpperCase())} placeholder="z. B. K1" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Rabatt % *</label>
            <Input className="w-24" inputMode="decimal" value={rabatt} onChange={e => setRabatt(e.target.value)} placeholder="z. B. 5.00" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Ab Menge (Staffel)</label>
            <Input className="w-24" inputMode="decimal" value={abMenge} onChange={e => setAbMenge(e.target.value)} placeholder="0 = immer" />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Gültig ab</label>
            <Input type="date" className="w-36" value={gueltigAb} onChange={e => setGueltigAb(e.target.value)} />
          </div>
          <Button disabled={!gruppeNr || !klasseNr || !rabatt || creating} onClick={() => void handleCreate()}>
            <Plus className="h-3 w-3 mr-1" />{creating ? 'Speichere…' : 'Anlegen'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Rabattsätze ({richtung})</CardTitle></CardHeader>
        <CardContent>
          {q.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
          {q.data && (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="py-2 pr-3">Gruppe</th><th className="py-2 pr-3">Klasse</th><th className="py-2 pr-3">Rabatt %</th>
                  <th className="py-2 pr-3">Ab Menge</th><th className="py-2 pr-3">Gültig ab</th><th className="py-2 pr-3">Gültig bis</th><th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {q.data.length === 0 && <EmptyRow cols={7} />}
                {(q.data as Rabattsatz[]).map(s => (
                  <tr key={s.id} className="border-b border-border/50">
                    <td className="py-2 pr-3 font-mono">{s.rabattgruppe_nr}</td>
                    <td className="py-2 pr-3 font-mono">{s.rabattklasse_nr}</td>
                    <td className="py-2 pr-3 tabular-nums font-medium text-green-700">{fmt(Number(s.rabatt_prozent))}%</td>
                    <td className="py-2 pr-3 tabular-nums">{s.ab_menge != null ? fmt(Number(s.ab_menge)) : '—'}</td>
                    <td className="py-2 pr-3 text-xs">{s.gueltig_ab ? new Date(s.gueltig_ab).toLocaleDateString('de-DE') : '—'}</td>
                    <td className="py-2 pr-3 text-xs">{s.gueltig_bis ? new Date(s.gueltig_bis).toLocaleDateString('de-DE') : 'unbegrenzt'}</td>
                    <td className="py-2">
                      <Button size="sm" variant="ghost" disabled={deletingId === s.id} onClick={() => void handleDelete(s)}>
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

// ── Individualpreise ──────────────────────────────────────────────────────────

function IndividualpreiseTab() {
  const qc = useQueryClient()
  const { toast } = useToast()
  const [typ, setTyp] = useState<'VK' | 'EK'>('VK')
  const [artikelNr, setArtikelNr] = useState('')
  const [partnerNr, setPartnerNr] = useState('')
  const [preis, setPreis] = useState('')
  const [staffel, setStaffel] = useState('')
  const [vonBis, setVonBis] = useState({ from: '', to: '' })
  const [creating, setCreating] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const q = useQuery({ queryKey: ['konditionen', 'individualpreise', typ], queryFn: () => listIndividualpreise({ preis_typ: typ }) })
  const inv = () => qc.invalidateQueries({ queryKey: ['konditionen', 'individualpreise'] })

  const handleCreate = async () => {
    if (!artikelNr || !preis || !vonBis.from || creating) return
    setCreating(true)
    try {
      await createIndividualpreis({
        preis_typ: typ,
        artikel_nr: artikelNr,
        partner_nr: partnerNr || null,
        gueltig_von: vonBis.from,
        gueltig_bis: vonBis.to || null,
        preis_eur: Number(preis),
        staffel_menge: staffel ? Number(staffel) : 0,
        waehrung: 'EUR',
        mengeneinheit: null,
        notiz: null,
      })
      toast({ title: 'Individualpreis angelegt', description: `${artikelNr} → ${fmtEur(Number(preis))}` })
      setArtikelNr('')
      setPartnerNr('')
      setPreis('')
      setStaffel('')
      setVonBis({ from: '', to: '' })
      inv()
    } catch {
      toast({ title: 'Fehler', description: 'Anlegen fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (ip: Individualpreis) => {
    if (deletingId) return
    setDeletingId(ip.id)
    try {
      await deleteIndividualpreis(ip.id)
      toast({ title: 'Gelöscht' })
      inv()
    } catch {
      toast({ title: 'Fehler', description: 'Löschen fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Tag className="h-4 w-4" /> Individualpreis anlegen [PRI/PRIE]</CardTitle>
          <CardDescription>
            Artikel- und ggf. partnerspezifische Preise mit Gültigkeitszeitraum und Mengenstaffel.
            Partner-Nr leer = gilt für alle Kunden/Lieferanten.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-3 items-end">
            <div className="space-y-1">
              <label className="text-xs font-medium">Typ</label>
              <select className="border rounded px-2 py-1.5 text-sm" value={typ} onChange={e => setTyp(e.target.value as 'VK' | 'EK')}>
                <option value="VK">VK (Verkauf)</option><option value="EK">EK (Einkauf)</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Artikel-Nr *</label>
              <Input className="w-36" value={artikelNr} onChange={e => setArtikelNr(e.target.value)} placeholder="z. B. ART-0042" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Partner-Nr (opt.)</label>
              <Input className="w-36" value={partnerNr} onChange={e => setPartnerNr(e.target.value)} placeholder="Kunden-/Lief.-Nr" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Preis (€) *</label>
              <Input className="w-28" inputMode="decimal" value={preis} onChange={e => setPreis(e.target.value)} placeholder="z. B. 42.50" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Ab Menge</label>
              <Input className="w-24" inputMode="decimal" value={staffel} onChange={e => setStaffel(e.target.value)} placeholder="0" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Gültig von *</label>
              <Input type="date" className="w-36" value={vonBis.from} onChange={e => setVonBis(p => ({ ...p, from: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Gültig bis</label>
              <Input type="date" className="w-36" value={vonBis.to} onChange={e => setVonBis(p => ({ ...p, to: e.target.value }))} />
            </div>
            <Button disabled={!artikelNr || !preis || !vonBis.from || creating} onClick={() => void handleCreate()}>
              <Plus className="h-3 w-3 mr-1" />{creating ? 'Speichere…' : 'Anlegen'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Individualpreise ({typ})</CardTitle></CardHeader>
        <CardContent>
          {q.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
          {q.data && (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="py-2 pr-3">Artikel-Nr</th><th className="py-2 pr-3">Partner-Nr</th><th className="py-2 pr-3">Preis</th>
                  <th className="py-2 pr-3">Ab Menge</th><th className="py-2 pr-3">Gültig von</th><th className="py-2 pr-3">Gültig bis</th><th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {q.data.length === 0 && <EmptyRow cols={7} />}
                {(q.data as Individualpreis[]).map(ip => (
                  <tr key={ip.id} className="border-b border-border/50">
                    <td className="py-2 pr-3 font-mono">{ip.artikel_nr}</td>
                    <td className="py-2 pr-3 text-muted-foreground">{ip.partner_nr ?? '(alle)'}</td>
                    <td className="py-2 pr-3 tabular-nums font-medium">{fmtEur(Number(ip.preis_eur))}</td>
                    <td className="py-2 pr-3 tabular-nums">{Number(ip.staffel_menge) > 0 ? fmt(Number(ip.staffel_menge)) : '—'}</td>
                    <td className="py-2 pr-3 text-xs">{new Date(ip.gueltig_von).toLocaleDateString('de-DE')}</td>
                    <td className="py-2 pr-3 text-xs">{ip.gueltig_bis ? new Date(ip.gueltig_bis).toLocaleDateString('de-DE') : 'unbegrenzt'}</td>
                    <td className="py-2">
                      <Button size="sm" variant="ghost" disabled={deletingId === ip.id} onClick={() => void handleDelete(ip)}>
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

// ── Preisfindung (Live-Kalkulator) ────────────────────────────────────────────

const SOURCE_LABELS: Record<string, string> = {
  base: 'Artikelstamm',
  price_list: 'Preisliste',
  contract: 'Kontrakt',
  customer_discount: 'Kundenrabatt',
  employee_discount: 'Mitarbeiterrabatt',
}

function PreisfindungTab() {
  const { toast } = useToast()
  const [artikelId, setArtikelId] = useState('')
  const [kundenId, setKundenId] = useState('')
  const [menge, setMenge] = useState('1')
  const [kontraktId, setKontraktId] = useState('')
  const [calculating, setCalculating] = useState(false)
  const [result, setResult] = useState<Awaited<ReturnType<typeof calculatePrice>> | null>(null)

  const handleCalculate = async () => {
    if (!artikelId || calculating) return
    setCalculating(true)
    setResult(null)
    try {
      const r = await calculatePrice({
        article_id: artikelId,
        customer_id: kundenId || undefined,
        quantity: menge ? Number(menge) : 1,
        contract_id: kontraktId || undefined,
      })
      setResult(r)
    } catch {
      toast({ title: 'Fehler', description: 'Preisfindung fehlgeschlagen (Artikel nicht gefunden?).', variant: 'destructive' })
    } finally {
      setCalculating(false)
    }
  }

  return (
    <div className="space-y-4 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Calculator className="h-4 w-4" /> Preisfindung (Live-Kalkulator)</CardTitle>
          <CardDescription>
            Hierarchische Preisfindung: Preisliste → Kontrakt → Kundenrabatt → Basispreis.
            Nur eine Rabattstufe wird angewendet (nicht additiv).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium">Artikel-ID *</label>
              <Input value={artikelId} onChange={e => setArtikelId(e.target.value)} placeholder="Artikel-UUID oder Nummer" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Menge</label>
              <Input inputMode="decimal" value={menge} onChange={e => setMenge(e.target.value)} placeholder="1" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Kunden-ID (optional)</label>
              <Input value={kundenId} onChange={e => setKundenId(e.target.value)} placeholder="UUID des Kunden" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Kontrakt-ID (optional)</label>
              <Input value={kontraktId} onChange={e => setKontraktId(e.target.value)} placeholder="UUID des Kontrakts" />
            </div>
          </div>
          <Button disabled={!artikelId || calculating} onClick={() => void handleCalculate()}>
            <Calculator className="h-3 w-3 mr-1" />{calculating ? 'Berechne…' : 'Preis berechnen'}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <Card className="border-green-200 bg-green-50/40 dark:bg-green-950/20">
          <CardHeader>
            <CardTitle className="text-base text-green-800">Ergebnis Preisfindung</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Listenpreis</p>
                <p className="text-xl font-bold tabular-nums">{fmtEur(Number(result.list_price))}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Rabatt</p>
                <p className="text-xl font-bold tabular-nums text-amber-700">{fmt(Number(result.discount))}%</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Nettopreis</p>
                <p className="text-2xl font-bold tabular-nums text-green-700">{fmtEur(Number(result.net_price))}</p>
              </div>
            </div>
            <div className="mt-4 pt-3 border-t flex gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Preisquelle: </span>
                <Badge variant="outline">{SOURCE_LABELS[result.source] ?? result.source}</Badge>
              </div>
              {result.price_list_id && (
                <div><span className="text-muted-foreground">Preisliste: </span><span className="font-mono text-xs">{result.price_list_id}</span></div>
              )}
              {result.contract_id && (
                <div><span className="text-muted-foreground">Kontrakt: </span><span className="font-mono text-xs">{result.contract_id}</span></div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// ── Hauptseite ────────────────────────────────────────────────────────────────

export default function KonditionssystemPage(): JSX.Element {
  const [activeTab, setActiveTab] = useState<Tab>('Preislisten')

  return (
    <div className="p-6 space-y-4 max-w-6xl">
      <div>
        <h1 className="text-2xl font-bold">Konditionssystem / Preisfindung</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Preislisten · Rabattgruppen/-klassen · Individualpreise · Hierarchische Preisfindung
        </p>
      </div>

      <TabBar active={activeTab} onChange={setActiveTab} />

      {activeTab === 'Preislisten' && <PreislistenTab />}
      {activeTab === 'Rabattgruppen' && <RabattgruppenTab />}
      {activeTab === 'Rabattklassen' && <RabattklassenTab />}
      {activeTab === 'Rabattsätze' && <RabattsaetzeTab />}
      {activeTab === 'Individualpreise' && <IndividualpreiseTab />}
      {activeTab === 'Preisfindung' && <PreisfindungTab />}
    </div>
  )
}
