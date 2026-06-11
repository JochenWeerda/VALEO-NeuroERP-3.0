import { useEffect, useMemo, useState } from 'react'
import { LineChart, Loader2, RefreshCw, Search, AlertTriangle, TrendingUp, TrendingDown, Lock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { toast } from '@/hooks/use-toast'
import { useContracts, type ContractRow } from '@/lib/api/contract-fulfillment'
import {
  useFixingWorkspace,
  useCreateFixing,
  type FixingPosition,
} from '@/lib/api/contract-fixing'

/**
 * Kontrakt-Fixierungs-Arbeitsraum (DOM-CON-004.2) — Teilfixierung MATIF-bepreister
 * Kontrakte (Menge zu MATIF-Preis + Prämie) und Mark-to-Market gegen die jüngste
 * Marktnotierung: fixierter Anteil, offener Anteil, Bewertungsergebnis.
 */

function fmtEur(v: number | null | undefined): string {
  if (v == null) return '—'
  return v.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
}

function Bar({ pct }: { pct: number }) {
  const w = Math.min(100, Math.max(0, pct))
  return (
    <div className="h-2 w-full rounded bg-muted overflow-hidden">
      <div className="h-full bg-sky-500" style={{ width: `${w}%` }} />
    </div>
  )
}

function Row({ c, active, onClick }: { c: ContractRow; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${active ? 'bg-muted' : ''}`}>
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium text-sm truncate">{c.contract_no}</span>
        <Badge variant="outline" className="text-[10px]">{c.typ}</Badge>
      </div>
      <div className="text-xs text-muted-foreground mt-0.5">{c.party_id ?? '—'} · {c.menge_kontrakt} {c.einheit}</div>
    </button>
  )
}

function FixingForm({ kontrakt, position, einheit, defaultPraemie }: {
  kontrakt: string; position: FixingPosition; einheit: string; defaultPraemie: number | null
}) {
  const create = useCreateFixing()
  const [menge, setMenge] = useState('')
  const [preis, setPreis] = useState('')
  const [praemie, setPraemie] = useState(defaultPraemie != null ? String(defaultPraemie) : '')
  const [notiz, setNotiz] = useState('')

  useEffect(() => {
    setPraemie(defaultPraemie != null ? String(defaultPraemie) : '')
  }, [defaultPraemie, position.line_id])

  const offen = position.offen_zu_fixieren ?? 0
  const mengeNum = Number(menge)
  const preisNum = Number(preis)
  const valid = mengeNum > 0 && mengeNum <= offen && preisNum > 0

  const submit = () => {
    if (!valid || create.isPending) return
    create.mutate(
      {
        kontrakt,
        position: String(position.position_no),
        menge: mengeNum,
        matifPreis: preisNum,
        praemie: praemie === '' ? undefined : Number(praemie),
        notiz: notiz || undefined,
      },
      {
        onSuccess: (d) => {
          toast({ title: `Fixierung #${d.fixing_no} angelegt`, description: `Offen verbleibend: ${d.offen_nach} ${einheit}` })
          setMenge(''); setPreis(''); setNotiz('')
        },
        onError: (err: unknown) => {
          const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
          toast({ title: 'Fixierung fehlgeschlagen', description: detail ?? 'Unbekannter Fehler', variant: 'destructive' })
        },
      },
    )
  }

  return (
    <Card>
      <CardHeader className="py-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Lock size={14} /> Teilfixierung · Position {position.position_no} ({position.artikel})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <label className="text-xs text-muted-foreground space-y-1">
            <span>Menge ({einheit}) · offen {offen}</span>
            <Input type="number" value={menge} onChange={(e) => setMenge(e.target.value)} placeholder="0" className="h-8" />
          </label>
          <label className="text-xs text-muted-foreground space-y-1">
            <span>MATIF-Preis</span>
            <Input type="number" value={preis} onChange={(e) => setPreis(e.target.value)} placeholder="0,00" className="h-8" />
          </label>
          <label className="text-xs text-muted-foreground space-y-1">
            <span>Prämie/Basis</span>
            <Input type="number" value={praemie} onChange={(e) => setPraemie(e.target.value)} placeholder="0,00" className="h-8" />
          </label>
          <label className="text-xs text-muted-foreground space-y-1">
            <span>Notiz</span>
            <Input value={notiz} onChange={(e) => setNotiz(e.target.value)} placeholder="optional" className="h-8" />
          </label>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            {menge && preis ? `Effektiv ≈ ${(preisNum + (praemie === '' ? 0 : Number(praemie))).toFixed(2)} / ${einheit}` : 'Menge + MATIF-Preis eingeben'}
            {mengeNum > offen && <span className="text-red-600 ml-2">Menge übersteigt offene {offen} {einheit}</span>}
          </span>
          <Button size="sm" onClick={submit} disabled={!valid || create.isPending}>
            {create.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <Lock size={14} className="mr-1" />}
            Fixieren
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default function KontraktFixierungPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [typ, setTyp] = useState('alle')
  const [filter, setFilter] = useState('')
  const [activePos, setActivePos] = useState<number | null>(null)
  const listQuery = useContracts(typ)
  const ws = useFixingWorkspace(selected)

  const contracts = (listQuery.data ?? []).filter((c) => !filter || c.contract_no.toLowerCase().includes(filter.toLowerCase()))
  const matifPositions = useMemo(() => (ws.data?.positionen ?? []).filter((p) => p.is_matif), [ws.data])
  const currentPos = matifPositions.find((p) => p.position_no === activePos) ?? matifPositions[0] ?? null

  useEffect(() => { setActivePos(null) }, [selected])

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <LineChart size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Kontrakt-Fixierung</h1>
        <NativeSelect value={typ} onChange={(e) => setTyp(e.target.value)} className="h-8 w-32">
          <option value="alle">Alle</option>
          <option value="EINKAUF">Einkauf</option>
          <option value="VERKAUF">Verkauf</option>
        </NativeSelect>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void listQuery.refetch()} disabled={listQuery.isFetching}>
          {listQuery.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[22rem_1fr]">
        <Card className="h-fit">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Kontrakte</CardTitle>
            <div className="relative">
              <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Nr. suchen…" className="h-8 pl-7" />
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[70vh] overflow-y-auto">
            {listQuery.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
            ) : contracts.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">Keine Kontrakte.</div>
            ) : (
              <div className="divide-y">
                {contracts.map((c) => <Row key={c.contract_no} c={c} active={selected === c.contract_no} onClick={() => setSelected(c.contract_no)} />)}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-3">
          {!selected ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Kontrakt wählen, um den Fixierungs-Arbeitsraum zu öffnen.</CardContent></Card>
          ) : ws.isLoading ? (
            <Card><CardContent className="py-16 text-center text-muted-foreground"><Loader2 className="animate-spin mx-auto mb-2" size={18} /> Lädt …</CardContent></Card>
          ) : !ws.data?.found ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">{ws.data?.detail ?? 'Nicht gefunden.'}</CardContent></Card>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">{ws.data.contract_no}</span>
                <Badge variant="outline">{ws.data.contract_type}</Badge>
                {ws.data.pricing?.modell && <Badge variant="secondary">{ws.data.pricing.modell}</Badge>}
                <Badge variant="outline">{ws.data.summary?.fixierungsgrad_pct}% fixiert</Badge>
              </div>

              <Card>
                <CardContent className="p-3 grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
                  <div><div className="text-xs text-muted-foreground">Kontrahiert</div><div className="font-semibold tabular-nums">{ws.data.summary?.menge_kontrakt} {ws.data.einheit}</div></div>
                  <div><div className="text-xs text-muted-foreground">Fixiert</div><div className="font-semibold tabular-nums">{ws.data.summary?.fixiert} {ws.data.einheit}</div></div>
                  <div><div className="text-xs text-muted-foreground">Offen zu fixieren</div><div className="font-semibold tabular-nums">{ws.data.summary?.offen_zu_fixieren} {ws.data.einheit}</div></div>
                  <div>
                    <div className="text-xs text-muted-foreground">Bewertung fixiert</div>
                    {ws.data.summary?.bewertbar ? (
                      <div className={`font-semibold tabular-nums flex items-center gap-1 ${(ws.data.summary.bewertung_fixiert_eur ?? 0) >= 0 ? 'text-emerald-700' : 'text-red-700'}`}>
                        {(ws.data.summary.bewertung_fixiert_eur ?? 0) >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                        {fmtEur(ws.data.summary.bewertung_fixiert_eur)}
                      </div>
                    ) : <div className="text-sm text-muted-foreground">keine Notierung</div>}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="py-3"><CardTitle className="text-sm">Positionen (MATIF zum Fixieren wählbar)</CardTitle></CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="text-xs text-muted-foreground border-b">
                        <tr>
                          <th className="text-left font-medium px-3 py-1.5">Pos</th>
                          <th className="text-left font-medium px-3 py-1.5">Artikel</th>
                          <th className="text-right font-medium px-3 py-1.5">Kontrahiert</th>
                          <th className="text-right font-medium px-3 py-1.5">Fixiert</th>
                          <th className="text-right font-medium px-3 py-1.5">Offen</th>
                          <th className="text-left font-medium px-3 py-1.5 w-32">Fixierungsgrad</th>
                          <th className="text-right font-medium px-3 py-1.5">Ø-Fix eff.</th>
                          <th className="text-right font-medium px-3 py-1.5">Markt eff.</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(ws.data.positionen ?? []).map((p) => {
                          const selectable = p.is_matif
                          const isActive = currentPos?.position_no === p.position_no
                          return (
                            <tr
                              key={p.position_no}
                              onClick={selectable ? () => setActivePos(p.position_no) : undefined}
                              className={`border-b last:border-0 ${selectable ? 'cursor-pointer hover:bg-muted/40' : 'opacity-60'} ${isActive ? 'bg-sky-50' : ''}`}
                            >
                              <td className="px-3 py-1.5">{p.position_no}</td>
                              <td className="px-3 py-1.5">{p.artikel}{p.is_matif && <Badge variant="outline" className="ml-1 text-[10px]">MATIF</Badge>}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums">{p.menge_kontrakt}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums">{p.fixiert}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums">{p.offen_zu_fixieren}</td>
                              <td className="px-3 py-1.5"><Bar pct={p.fixierungsgrad_pct} /><span className="text-[10px] text-muted-foreground">{p.fixierungsgrad_pct}%</span></td>
                              <td className="px-3 py-1.5 text-right tabular-nums">{p.avg_fixpreis_effektiv ?? '—'}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums">{p.notierung?.markt_effektiv ?? '—'}</td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {currentPos ? (
                <FixingForm
                  kontrakt={ws.data.contract_no ?? ''}
                  position={currentPos}
                  einheit={ws.data.einheit ?? ''}
                  defaultPraemie={ws.data.pricing?.praemie_wert ?? null}
                />
              ) : (
                <Card><CardContent className="py-6 text-center text-sm text-muted-foreground">Keine MATIF-Position — Fixierung nur für MATIF-bepreiste Kontrakte.</CardContent></Card>
              )}

              {currentPos && currentPos.fixings.length > 0 && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Fixierungen · Position {currentPos.position_no}</CardTitle></CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="text-xs text-muted-foreground border-b">
                          <tr>
                            <th className="text-left font-medium px-3 py-1.5">#</th>
                            <th className="text-right font-medium px-3 py-1.5">Menge</th>
                            <th className="text-right font-medium px-3 py-1.5">MATIF</th>
                            <th className="text-right font-medium px-3 py-1.5">Prämie</th>
                            <th className="text-right font-medium px-3 py-1.5">Effektiv</th>
                            <th className="text-left font-medium px-3 py-1.5">Datum</th>
                            <th className="text-left font-medium px-3 py-1.5">Notiz</th>
                          </tr>
                        </thead>
                        <tbody>
                          {currentPos.fixings.map((f) => (
                            <tr key={f.fixing_no} className="border-b last:border-0">
                              <td className="px-3 py-1.5">{f.fixing_no}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums">{f.menge}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums">{f.matif_price}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums">{f.praemie}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums font-medium">{f.effektiv_preis}</td>
                              <td className="px-3 py-1.5">{f.datum ? new Date(f.datum).toLocaleDateString('de-DE') : '—'}</td>
                              <td className="px-3 py-1.5 text-muted-foreground">{f.notiz ?? '—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}

              {!ws.data.summary?.bewertbar && matifPositions.length > 0 && (
                <div className="flex items-start gap-2 text-sm text-amber-700">
                  <AlertTriangle size={15} className="mt-0.5 shrink-0" />
                  <span>Keine Marktnotierung für das Kontrakt-Symbol hinterlegt — Mark-to-Market-Bewertung nicht möglich.</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
