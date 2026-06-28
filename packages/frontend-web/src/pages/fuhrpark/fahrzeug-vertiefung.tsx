import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useToast } from '@/hooks/use-toast'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  changeFahrzeugStatus,
  createFahrzeugBussgeld,
  createFahrzeugSchaden,
  getFahrzeugStatusHistorie,
  getFahrzeugWartungVorhersage,
  leasingRueckgabe,
  listFahrzeugBussgeld,
  listFahrzeugSchaeden,
  updateFahrzeugBussgeld,
  updateFahrzeugSchaden,
  type FahrzeugBussgeld,
  type FahrzeugSchaden,
  type FahrzeugStatusHistorieEintrag,
} from '@/lib/api/fuhrpark'
import { AlertTriangle, Car, CheckCircle, Clock, FileText, Shield, Wrench } from 'lucide-react'

const TABS = ['Statushistorie', 'Schadensfälle', 'Bußgelder', 'Wartungsvorhersage', 'Leasing-Rückgabe'] as const
type Tab = (typeof TABS)[number]

const STATUS_LABELS: Record<string, string> = {
  verfuegbar: 'Verfügbar',
  unterwegs: 'Unterwegs',
  wartung: 'Wartung',
  ausgeschieden: 'Ausgeschieden',
}

const SCHADEN_STATUS_LABELS: Record<string, string> = {
  offen: 'Offen',
  bearbeitung: 'In Bearbeitung',
  abgeschlossen: 'Abgeschlossen',
}

const BUSSGELD_STATUS_LABELS: Record<string, string> = {
  offen: 'Offen',
  bezahlt: 'Bezahlt',
  einspruch: 'Einspruch',
  'verjährt': 'Verjährt',
}

function statusBadgeVariant(s: string): 'default' | 'outline' | 'destructive' | 'secondary' {
  if (s === 'verfuegbar' || s === 'abgeschlossen' || s === 'bezahlt') return 'outline'
  if (s === 'ausgeschieden' || s === 'offen') return 'destructive'
  return 'secondary'
}

export default function FahrzeugVertiefungPage(): JSX.Element {
  const [fahrzeugId, setFahrzeugId] = useState('')
  const [activeTab, setActiveTab] = useState<Tab>('Statushistorie')
  const { toast } = useToast()
  const qc = useQueryClient()

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ['fuhrpark-vertiefung', fahrzeugId] })
  }

  // ── Status-Historie ─────────────────────────────────────────────────────────
  const historieQ = useQuery({
    queryKey: ['fuhrpark-vertiefung', fahrzeugId, 'historie'],
    queryFn: () => getFahrzeugStatusHistorie(fahrzeugId),
    enabled: Boolean(fahrzeugId) && activeTab === 'Statushistorie',
  })

  const [neuerStatus, setNeuerStatus] = useState('verfuegbar')
  const [statusGrund, setStatusGrund] = useState('')
  const [statusKm, setStatusKm] = useState('')
  const [statusPending, setStatusPending] = useState(false)

  const handleStatusWechsel = async () => {
    if (!fahrzeugId || statusPending) return
    setStatusPending(true)
    try {
      await changeFahrzeugStatus(fahrzeugId, {
        zu_status: neuerStatus,
        grund: statusGrund || undefined,
        km_stand: statusKm ? Number(statusKm) : undefined,
      })
      toast({ title: 'Status geändert', description: `→ ${STATUS_LABELS[neuerStatus] ?? neuerStatus}` })
      setStatusGrund('')
      setStatusKm('')
      invalidate()
    } catch {
      toast({ title: 'Fehler', description: 'Statuswechsel fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setStatusPending(false)
    }
  }

  // ── Schadensfälle ───────────────────────────────────────────────────────────
  const schadenQ = useQuery({
    queryKey: ['fuhrpark-vertiefung', fahrzeugId, 'schaeden'],
    queryFn: () => listFahrzeugSchaeden(fahrzeugId),
    enabled: Boolean(fahrzeugId) && activeTab === 'Schadensfälle',
  })

  const [schadenOrt, setSchadenOrt] = useState('')
  const [schadenBeschr, setSchadenBeschr] = useState('')
  const [schadenHoehe, setSchadenHoehe] = useState('')
  const [schadenVersGem, setSchadenVersGem] = useState(false)
  const [schadenPending, setSchadenPending] = useState(false)

  const handleSchadenAnlegen = async () => {
    if (!fahrzeugId || !schadenOrt || !schadenBeschr || schadenPending) return
    setSchadenPending(true)
    try {
      await createFahrzeugSchaden(fahrzeugId, {
        datum: new Date().toISOString(),
        ort: schadenOrt,
        beschreibung: schadenBeschr,
        schadenhoehe_eur: schadenHoehe ? Number(schadenHoehe) : null,
        versicherung_gemeldet: schadenVersGem,
        versicherungs_nr: null,
        gegner_kennzeichen: null,
        polizei_aktenzeichen: null,
        erstellt_von: null,
        status: 'offen',
      })
      toast({ title: 'Schadensfall angelegt' })
      setSchadenOrt('')
      setSchadenBeschr('')
      setSchadenHoehe('')
      setSchadenVersGem(false)
      invalidate()
    } catch {
      toast({ title: 'Fehler', description: 'Schadensfall konnte nicht angelegt werden.', variant: 'destructive' })
    } finally {
      setSchadenPending(false)
    }
  }

  const [abschliessendePending, setAbschliessendePending] = useState<Set<string>>(new Set())

  const handleSchadenAbschliessen = async (schaden: FahrzeugSchaden) => {
    if (abschliessendePending.has(schaden.id)) return
    setAbschliessendePending(prev => new Set(prev).add(schaden.id))
    try {
      await updateFahrzeugSchaden(fahrzeugId, schaden.id, {
        status: 'abgeschlossen',
      })
      toast({ title: 'Schadensfall abgeschlossen' })
      invalidate()
    } catch {
      toast({ title: 'Fehler', description: 'Abschluss fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setAbschliessendePending(prev => { const s = new Set(prev); s.delete(schaden.id); return s })
    }
  }

  // ── Bußgelder ───────────────────────────────────────────────────────────────
  const bussQ = useQuery({
    queryKey: ['fuhrpark-vertiefung', fahrzeugId, 'bussgeld'],
    queryFn: () => listFahrzeugBussgeld(fahrzeugId),
    enabled: Boolean(fahrzeugId) && activeTab === 'Bußgelder',
  })

  const [bgTatbestand, setBgTatbestand] = useState('')
  const [bgBetrag, setBgBetrag] = useState('')
  const [bgOrt, setBgOrt] = useState('')
  const [bgPending, setBgPending] = useState(false)
  const [bezahlenPending, setBezahlenPending] = useState<Set<string>>(new Set())

  const handleBussAnlegen = async () => {
    if (!fahrzeugId || !bgTatbestand || !bgBetrag || bgPending) return
    setBgPending(true)
    try {
      await createFahrzeugBussgeld(fahrzeugId, {
        datum: new Date().toISOString(),
        tatbestand: bgTatbestand,
        betrag_eur: Number(bgBetrag),
        ort: bgOrt || undefined,
      })
      toast({ title: 'Bußgeld angelegt' })
      setBgTatbestand('')
      setBgBetrag('')
      setBgOrt('')
      invalidate()
    } catch {
      toast({ title: 'Fehler', description: 'Bußgeld konnte nicht angelegt werden.', variant: 'destructive' })
    } finally {
      setBgPending(false)
    }
  }

  const handleBgBezahlen = async (bg: FahrzeugBussgeld) => {
    if (bezahlenPending.has(bg.id)) return
    setBezahlenPending(prev => new Set(prev).add(bg.id))
    try {
      await updateFahrzeugBussgeld(fahrzeugId, bg.id, { bezahlt_am: new Date().toISOString(), status: 'bezahlt' })
      toast({ title: 'Als bezahlt markiert' })
      invalidate()
    } catch {
      toast({ title: 'Fehler', description: 'Aktualisierung fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setBezahlenPending(prev => { const s = new Set(prev); s.delete(bg.id); return s })
    }
  }

  // ── Wartungsvorhersage ──────────────────────────────────────────────────────
  const wartungQ = useQuery({
    queryKey: ['fuhrpark-vertiefung', fahrzeugId, 'wartung'],
    queryFn: () => getFahrzeugWartungVorhersage(fahrzeugId),
    enabled: Boolean(fahrzeugId) && activeTab === 'Wartungsvorhersage',
  })

  // ── Leasing-Rückgabe ────────────────────────────────────────────────────────
  const [lrKm, setLrKm] = useState('')
  const [lrBemerkung, setLrBemerkung] = useState('')
  const [lrPending, setLrPending] = useState(false)
  const [lrErgebnis, setLrErgebnis] = useState<Record<string, unknown> | null>(null)

  const handleLeasingRueckgabe = async () => {
    if (!fahrzeugId || !lrKm || lrPending) return
    setLrPending(true)
    try {
      const result = await leasingRueckgabe(fahrzeugId, {
        rueckgabedatum: new Date().toISOString(),
        km_stand_bei_rueckgabe: Number(lrKm),
        zustand_bemerkung: lrBemerkung || undefined,
      })
      setLrErgebnis(result.rueckgabe_protokoll)
      toast({ title: 'Leasing-Rückgabe eingeleitet', description: 'Fahrzeug auf "ausgeschieden" gesetzt.' })
      invalidate()
    } catch (_rawErr: unknown) {
      const err = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      const msg = err instanceof Error ? err.message : 'Unbekannter Fehler'
      toast({ title: 'Fehler', description: msg, variant: 'destructive' })
    } finally {
      setLrPending(false)
    }
  }

  return (
    <div className="p-6 space-y-4 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold">Fuhrpark Vertiefung</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Statushistorie · Schadensfälle · Bußgelder · Wartungsvorhersage · Leasing-Rückgabe
        </p>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-sm font-medium whitespace-nowrap">Fahrzeug-ID</label>
        <Input
          className="w-64"
          placeholder="z. B. F-ABC12345"
          value={fahrzeugId}
          onChange={e => setFahrzeugId(e.target.value.trim())}
        />
        {!fahrzeugId && (
          <span className="text-xs text-muted-foreground">Fahrzeug-ID eingeben, um Daten zu laden</span>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {TABS.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* ── Statushistorie ─────────────────────────────────────────────────── */}
      {activeTab === 'Statushistorie' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Car className="h-4 w-4" /> Statuswechsel
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-3 items-end">
              <div className="space-y-1">
                <label className="text-xs font-medium">Neuer Status</label>
                <select
                  className="border rounded px-2 py-1.5 text-sm"
                  value={neuerStatus}
                  onChange={e => setNeuerStatus(e.target.value)}
                >
                  {Object.entries(STATUS_LABELS).map(([v, l]) => (
                    <option key={v} value={v}>{l}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium">Grund (optional)</label>
                <Input className="w-52" value={statusGrund} onChange={e => setStatusGrund(e.target.value)} placeholder="z. B. TÜV fällig" />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium">KM-Stand (optional)</label>
                <Input className="w-28" inputMode="decimal" value={statusKm} onChange={e => setStatusKm(e.target.value)} placeholder="z. B. 125000" />
              </div>
              <Button disabled={!fahrzeugId || statusPending} onClick={() => void handleStatusWechsel()}>
                {statusPending ? 'Speichere…' : 'Status wechseln'}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Statushistorie</CardTitle>
            </CardHeader>
            <CardContent>
              {!fahrzeugId && <p className="text-sm text-muted-foreground">Fahrzeug-ID eingeben.</p>}
              {historieQ.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
              {historieQ.isError && <p className="text-sm text-destructive">Fehler beim Laden.</p>}
              {historieQ.data && (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-muted-foreground">
                      <th className="py-2 pr-3">Zeitpunkt</th>
                      <th className="py-2 pr-3">Von</th>
                      <th className="py-2 pr-3">Nach</th>
                      <th className="py-2 pr-3">KM-Stand</th>
                      <th className="py-2">Grund</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historieQ.data.length === 0 && (
                      <tr><td colSpan={5} className="py-4 text-center text-muted-foreground">Keine Einträge</td></tr>
                    )}
                    {(historieQ.data as FahrzeugStatusHistorieEintrag[]).map(e => (
                      <tr key={e.id} className="border-b border-border/50">
                        <td className="py-2 pr-3 text-xs text-muted-foreground">{new Date(e.timestamp).toLocaleString('de-DE')}</td>
                        <td className="py-2 pr-3"><Badge variant="secondary">{STATUS_LABELS[e.von_status ?? ''] ?? e.von_status ?? '—'}</Badge></td>
                        <td className="py-2 pr-3"><Badge variant={statusBadgeVariant(e.zu_status)}>{STATUS_LABELS[e.zu_status] ?? e.zu_status}</Badge></td>
                        <td className="py-2 pr-3 tabular-nums">{e.km_stand != null ? `${e.km_stand.toLocaleString('de-DE')} km` : '—'}</td>
                        <td className="py-2 text-muted-foreground">{e.grund ?? '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── Schadensfälle ──────────────────────────────────────────────────── */}
      {activeTab === 'Schadensfälle' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-500" /> Neuen Schadensfall anlegen
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-medium">Ort *</label>
                  <Input value={schadenOrt} onChange={e => setSchadenOrt(e.target.value)} placeholder="z. B. Autobahn A7, km 123" />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium">Schadenshöhe (€)</label>
                  <Input inputMode="decimal" value={schadenHoehe} onChange={e => setSchadenHoehe(e.target.value)} placeholder="z. B. 2500.00" />
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium">Beschreibung *</label>
                <Input value={schadenBeschr} onChange={e => setSchadenBeschr(e.target.value)} placeholder="Kurzbeschreibung des Schadensereignisses" />
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="vers-gem" checked={schadenVersGem} onChange={e => setSchadenVersGem(e.target.checked)} className="h-4 w-4" />
                <label htmlFor="vers-gem" className="text-sm">Versicherung gemeldet</label>
              </div>
              <Button
                disabled={!fahrzeugId || !schadenOrt || !schadenBeschr || schadenPending}
                onClick={() => void handleSchadenAnlegen()}
              >
                {schadenPending ? 'Speichere…' : 'Schadensfall anlegen'}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="text-base">Schadensfälle</CardTitle></CardHeader>
            <CardContent>
              {!fahrzeugId && <p className="text-sm text-muted-foreground">Fahrzeug-ID eingeben.</p>}
              {schadenQ.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
              {schadenQ.isError && <p className="text-sm text-destructive">Fehler beim Laden.</p>}
              {schadenQ.data && (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-muted-foreground">
                      <th className="py-2 pr-3">Datum</th>
                      <th className="py-2 pr-3">Ort</th>
                      <th className="py-2 pr-3">Schaden</th>
                      <th className="py-2 pr-3">Versicherung</th>
                      <th className="py-2 pr-3">Status</th>
                      <th className="py-2" />
                    </tr>
                  </thead>
                  <tbody>
                    {schadenQ.data.length === 0 && (
                      <tr><td colSpan={6} className="py-4 text-center text-muted-foreground">Keine Schadensfälle</td></tr>
                    )}
                    {(schadenQ.data as FahrzeugSchaden[]).map(s => (
                      <tr key={s.id} className="border-b border-border/50">
                        <td className="py-2 pr-3 text-xs">{new Date(s.datum).toLocaleDateString('de-DE')}</td>
                        <td className="py-2 pr-3">{s.ort}</td>
                        <td className="py-2 pr-3 tabular-nums">
                          {s.schadenhoehe_eur != null
                            ? s.schadenhoehe_eur.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
                            : '—'}
                        </td>
                        <td className="py-2 pr-3">
                          {s.versicherung_gemeldet
                            ? <Shield className="h-4 w-4 text-green-600" />
                            : <span className="text-muted-foreground text-xs">nein</span>}
                        </td>
                        <td className="py-2 pr-3">
                          <Badge variant={statusBadgeVariant(s.status)}>
                            {SCHADEN_STATUS_LABELS[s.status] ?? s.status}
                          </Badge>
                        </td>
                        <td className="py-2">
                          {s.status !== 'abgeschlossen' && (
                            <Button
                              size="sm"
                              variant="outline"
                              disabled={abschliessendePending.has(s.id)}
                              onClick={() => void handleSchadenAbschliessen(s)}
                            >
                              <CheckCircle className="h-3 w-3 mr-1" />
                              {abschliessendePending.has(s.id) ? '…' : 'Abschließen'}
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── Bußgelder ──────────────────────────────────────────────────────── */}
      {activeTab === 'Bußgelder' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <FileText className="h-4 w-4" /> Bußgeld / Verwarnung anlegen
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1 col-span-2">
                  <label className="text-xs font-medium">Tatbestand *</label>
                  <Input value={bgTatbestand} onChange={e => setBgTatbestand(e.target.value)} placeholder="z. B. Überladung 5 t, §34 StVZO" />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium">Betrag (€) *</label>
                  <Input inputMode="decimal" value={bgBetrag} onChange={e => setBgBetrag(e.target.value)} placeholder="395.00" />
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium">Ort (optional)</label>
                <Input value={bgOrt} onChange={e => setBgOrt(e.target.value)} placeholder="z. B. BAB 7, Weende-Nord" />
              </div>
              <Button
                disabled={!fahrzeugId || !bgTatbestand || !bgBetrag || bgPending}
                onClick={() => void handleBussAnlegen()}
              >
                {bgPending ? 'Speichere…' : 'Bußgeld anlegen'}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="text-base">Bußgelder & Verwarnungen</CardTitle></CardHeader>
            <CardContent>
              {!fahrzeugId && <p className="text-sm text-muted-foreground">Fahrzeug-ID eingeben.</p>}
              {bussQ.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
              {bussQ.isError && <p className="text-sm text-destructive">Fehler beim Laden.</p>}
              {bussQ.data && (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-muted-foreground">
                      <th className="py-2 pr-3">Datum</th>
                      <th className="py-2 pr-3">Tatbestand</th>
                      <th className="py-2 pr-3">Betrag</th>
                      <th className="py-2 pr-3">Fällig</th>
                      <th className="py-2 pr-3">Status</th>
                      <th className="py-2" />
                    </tr>
                  </thead>
                  <tbody>
                    {bussQ.data.length === 0 && (
                      <tr><td colSpan={6} className="py-4 text-center text-muted-foreground">Keine Einträge</td></tr>
                    )}
                    {(bussQ.data as FahrzeugBussgeld[]).map(bg => (
                      <tr key={bg.id} className="border-b border-border/50">
                        <td className="py-2 pr-3 text-xs">{new Date(bg.datum).toLocaleDateString('de-DE')}</td>
                        <td className="py-2 pr-3 max-w-[200px] truncate">{bg.tatbestand}</td>
                        <td className="py-2 pr-3 tabular-nums font-medium">
                          {bg.betrag_eur.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
                        </td>
                        <td className="py-2 pr-3 text-xs">
                          {bg.faellig_am ? new Date(bg.faellig_am).toLocaleDateString('de-DE') : '—'}
                        </td>
                        <td className="py-2 pr-3">
                          <Badge variant={statusBadgeVariant(bg.status)}>
                            {BUSSGELD_STATUS_LABELS[bg.status] ?? bg.status}
                          </Badge>
                        </td>
                        <td className="py-2">
                          {bg.status === 'offen' && (
                            <Button
                              size="sm"
                              variant="outline"
                              disabled={bezahlenPending.has(bg.id)}
                              onClick={() => void handleBgBezahlen(bg)}
                            >
                              <CheckCircle className="h-3 w-3 mr-1" />
                              {bezahlenPending.has(bg.id) ? '…' : 'Bezahlt'}
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── Wartungsvorhersage ─────────────────────────────────────────────── */}
      {activeTab === 'Wartungsvorhersage' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Wrench className="h-4 w-4" /> Wartungsvorhersage (KM-basiert)
              </CardTitle>
              <CardDescription>Berechnet nächste Fälligkeiten aus KM-Stand und konfigurierten Terminarten.</CardDescription>
            </CardHeader>
            <CardContent>
              {!fahrzeugId && <p className="text-sm text-muted-foreground">Fahrzeug-ID eingeben.</p>}
              {wartungQ.isLoading && <p className="text-sm text-muted-foreground">Lade…</p>}
              {wartungQ.isError && <p className="text-sm text-destructive">Fehler beim Laden.</p>}
              {wartungQ.data && (
                <div className="space-y-4">
                  <div className="grid grid-cols-4 gap-3">
                    <div className="rounded border p-3 text-center">
                      <p className="text-xs text-muted-foreground">Aktuell KM</p>
                      <p className="text-lg font-bold tabular-nums">
                        {wartungQ.data.aktueller_km_stand.toLocaleString('de-DE')}
                      </p>
                    </div>
                    {[
                      { label: 'TÜV in Tagen', val: wartungQ.data.tuev_faellig_in_tagen },
                      { label: 'ASU in Tagen', val: wartungQ.data.asu_faellig_in_tagen },
                      { label: 'Inspektion in Tagen', val: wartungQ.data.inspektion_faellig_in_tagen },
                    ].map(({ label, val }) => (
                      <div key={label} className={`rounded border p-3 text-center ${val != null && val <= 30 ? 'border-amber-300 bg-amber-50' : ''}`}>
                        <p className="text-xs text-muted-foreground">{label}</p>
                        <p className={`text-lg font-bold tabular-nums ${val != null && val <= 30 ? 'text-amber-700' : ''}`}>
                          {val != null ? val : '—'}
                        </p>
                      </div>
                    ))}
                  </div>

                  {wartungQ.data.vorhersagen_nach_km.length > 0 && (
                    <div className="overflow-auto rounded border">
                      <table className="w-full text-sm">
                        <thead className="bg-muted/30">
                          <tr className="text-left text-muted-foreground">
                            <th className="px-3 py-2">Terminart</th>
                            <th className="px-3 py-2 text-right">Intervall (km)</th>
                            <th className="px-3 py-2 text-right">Fällig in (km)</th>
                            <th className="px-3 py-2 text-right">Fällig bei (km)</th>
                            <th className="px-3 py-2 text-center">Dringend</th>
                          </tr>
                        </thead>
                        <tbody>
                          {wartungQ.data.vorhersagen_nach_km.map(v => (
                            <tr key={v.terminart} className={`border-t ${v.dringend ? 'bg-amber-50 dark:bg-amber-950/20' : ''}`}>
                              <td className="px-3 py-2 font-medium">{v.terminart}</td>
                              <td className="px-3 py-2 text-right tabular-nums">{v.intervall_km > 0 ? v.intervall_km.toLocaleString('de-DE') : '—'}</td>
                              <td className="px-3 py-2 text-right tabular-nums">{v.faellig_in_km != null ? v.faellig_in_km.toLocaleString('de-DE') : '—'}</td>
                              <td className="px-3 py-2 text-right tabular-nums">{v.faellig_bei_km != null ? v.faellig_bei_km.toLocaleString('de-DE') : '—'}</td>
                              <td className="px-3 py-2 text-center">
                                {v.dringend ? <AlertTriangle className="h-4 w-4 text-amber-500 mx-auto" /> : <span className="text-muted-foreground text-xs">—</span>}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ── Leasing-Rückgabe ───────────────────────────────────────────────── */}
      {activeTab === 'Leasing-Rückgabe' && (
        <div className="space-y-4">
          <Card className="border-amber-200/80 bg-amber-50/40 dark:bg-amber-950/20">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="h-4 w-4 text-amber-600" /> Leasing-Rückgabe einleiten
              </CardTitle>
              <CardDescription>
                Setzt das Fahrzeug auf Status <strong>ausgeschieden</strong> und protokolliert den KM-Stand.
                Nur für Fahrzeuge mit hinterlegter Leasinggesellschaft.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-medium">KM-Stand bei Rückgabe *</label>
                  <Input
                    inputMode="decimal"
                    value={lrKm}
                    onChange={e => setLrKm(e.target.value)}
                    placeholder="z. B. 145000"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium">Zustandsbemerkung (optional)</label>
                  <Input
                    value={lrBemerkung}
                    onChange={e => setLrBemerkung(e.target.value)}
                    placeholder="z. B. leichte Kratzer Beifahrertür"
                  />
                </div>
              </div>
              <Button
                variant="destructive"
                disabled={!fahrzeugId || !lrKm || lrPending}
                onClick={() => void handleLeasingRueckgabe()}
              >
                {lrPending ? 'Wird verarbeitet…' : 'Leasing-Rückgabe einleiten'}
              </Button>

              {lrErgebnis && (
                <div className="rounded border border-green-200 bg-green-50 p-4 space-y-1 dark:bg-green-950/20">
                  <p className="text-sm font-semibold text-green-700">Rückgabe protokolliert</p>
                  <pre className="text-xs text-green-600 whitespace-pre-wrap">
                    {JSON.stringify(lrErgebnis, null, 2)}
                  </pre>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
