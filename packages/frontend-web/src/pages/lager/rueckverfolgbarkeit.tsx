import { useEffect, useState } from 'react'
import {
  GitBranch, Scale, ClipboardCheck, Warehouse, Receipt, Loader2, RefreshCw,
  CheckCircle2, AlertTriangle, Info, ArrowDown, Search, History, Plus, Bot,
  Lock, Unlock, Droplets, Ban,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { useToast } from '@/hooks/use-toast'
import {
  useTraceTickets, useTrace, useSyncChain, useAddChainEvent, useLotAction, useCancelChain,
  type TraceNode, type TraceTicket, type ChainEvent,
} from '@/lib/api/supply-chain'

function errDetail(e: unknown, fallback: string): string {
  const d = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
  return typeof d === 'string' ? d : fallback
}

const STATUS_LABEL: Record<string, string> = {
  offen: 'offen', erfasst: 'erfasst', freigegeben: 'freigegeben',
  eingelagert: 'eingelagert', abgerechnet: 'abgerechnet', storniert: 'storniert',
}

/**
 * Rückverfolgbarkeit (DOM-SUPPLY-004) — durchgängige, prüfbare Kette je Lieferung:
 * Wiegung → Annahme → Lager → Abrechnung (Rückgrat: Wiegeschein). Zeigt Status je
 * Stufe, Mengen-Konsistenz (Schwund/Differenz) und Lücken (fehlende Folgeobjekte).
 */

const STAGE_ICON: Record<string, JSX.Element> = {
  wiegung: <Scale size={16} />,
  annahme: <ClipboardCheck size={16} />,
  lager: <Warehouse size={16} />,
  abrechnung: <Receipt size={16} />,
}

const fmtKg = (kg: number | null | undefined) =>
  kg == null ? '—' : `${kg.toLocaleString('de-DE', { maximumFractionDigits: 0 })} kg`

function StageNode({ node }: { node: TraceNode }) {
  return (
    <div className="rounded-lg border p-3">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 font-medium text-sm">
          <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-muted">
            {STAGE_ICON[node.stage] ?? <GitBranch size={16} />}
          </span>
          {node.label}
          {node.ref && <span className="text-muted-foreground font-normal">· {node.ref}</span>}
        </div>
        <div className="flex items-center gap-2">
          {node.menge_kg != null && <span className="text-sm tabular-nums">{fmtKg(node.menge_kg)}</span>}
          {node.status && <Badge variant="outline">{node.status}</Badge>}
        </div>
      </div>
      <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-0.5 text-xs text-muted-foreground md:grid-cols-3">
        {Object.entries(node.facts)
          .filter(([, v]) => v != null && typeof v !== 'object')
          .map(([k, v]) => (
            <div key={k} className="truncate"><span className="opacity-70">{k}:</span> {String(v)}</div>
          ))}
      </div>
    </div>
  )
}

function LotActions({ node }: { node: TraceNode }) {
  const { toast } = useToast()
  const action = useLotAction()
  const [grund, setGrund] = useState('')
  const [menge, setMenge] = useState('')
  const gesperrt = node.status === 'gesperrt'

  const run = async (kind: 'block' | 'release' | 'shrinkage') => {
    if (!grund.trim()) {
      toast({ title: 'Grund fehlt', description: 'Bitte einen Grund angeben.', variant: 'destructive' })
      return
    }
    if (kind === 'shrinkage' && !menge) {
      toast({ title: 'Menge fehlt', description: 'Bitte Schwundmenge (kg) angeben.', variant: 'destructive' })
      return
    }
    try {
      await action.mutateAsync(
        kind === 'shrinkage'
          ? { kind, lotId: node.ref_id, grund: grund.trim(), mengeKg: Number(menge) }
          : { kind, lotId: node.ref_id, grund: grund.trim() },
      )
      setGrund(''); setMenge('')
      toast({ title: 'Erledigt', description: 'Lager-Aktion protokolliert.' })
    } catch (e) {
      toast({ title: 'Fehler', description: errDetail(e, 'Aktion fehlgeschlagen.'), variant: 'destructive' })
    }
  }

  return (
    <div className="ml-9 mt-1 flex flex-col gap-2 rounded-md border bg-muted/20 p-2 sm:flex-row sm:items-center">
      <Input value={grund} onChange={(e) => setGrund(e.target.value)} placeholder="Grund…" className="h-8 flex-1" disabled={action.isPending} />
      {!gesperrt && (
        <div className="flex items-center gap-1">
          <Input value={menge} onChange={(e) => setMenge(e.target.value)} type="number" placeholder="Schwund kg" className="h-8 w-28" disabled={action.isPending} />
          <Button size="sm" variant="outline" onClick={() => run('shrinkage')} disabled={action.isPending}>
            <Droplets size={14} className="mr-1" />Schwund
          </Button>
        </div>
      )}
      {gesperrt ? (
        <Button size="sm" variant="outline" onClick={() => run('release')} disabled={action.isPending}>
          {action.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <Unlock size={14} className="mr-1" />}QS-Freigabe
        </Button>
      ) : (
        <Button size="sm" variant="outline" onClick={() => run('block')} disabled={action.isPending}>
          {action.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <Lock size={14} className="mr-1" />}Sperren
        </Button>
      )}
    </div>
  )
}

function CompletenessDots({ t }: { t: TraceTicket }) {
  const dot = (ok: boolean, label: string) => (
    <span
      title={label}
      className={`inline-block h-2 w-2 rounded-full ${ok ? 'bg-emerald-500' : 'bg-muted-foreground/30'}`}
    />
  )
  return (
    <span className="inline-flex items-center gap-1">
      {dot(true, 'Wiegung')}{dot(t.hat_annahme, 'Annahme')}{dot(t.hat_lager, 'Lager')}{dot(t.hat_abrechnung, 'Abrechnung')}
    </span>
  )
}

export default function RueckverfolgbarkeitPage() {
  const { toast } = useToast()
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const ticketsQuery = useTraceTickets(50)
  const trace = useTrace(selected)
  const syncChain = useSyncChain()
  const addEvent = useAddChainEvent()
  const cancelChain = useCancelChain()

  // Ereignis-Erfassung (Korrektur/Abweichung/Notiz)
  const [evType, setEvType] = useState('korrektur')
  const [evGrund, setEvGrund] = useState('')
  const [evMenge, setEvMenge] = useState('')

  // Ketten-Storno
  const [stornoOpen, setStornoOpen] = useState(false)
  const [stornoGrund, setStornoGrund] = useState('')

  // Bei Auswahl: Ereignis-Log idempotent aus Ist-Zustand befüllen (Backfill).
  useEffect(() => {
    if (selected) syncChain.mutate(selected)
  }, [selected])

  const tickets = (ticketsQuery.data ?? []).filter(
    (t) => !filter || (t.ticket_nr || '').toLowerCase().includes(filter.toLowerCase()),
  )

  const submitEvent = async () => {
    if (!selected) return
    if (!evGrund.trim()) {
      toast({ title: 'Grund/Notiz fehlt', description: 'Bitte einen Text zum Ereignis angeben.', variant: 'destructive' })
      return
    }
    try {
      const res = await addEvent.mutateAsync({
        ticketId: selected,
        eventType: evType,
        abweichungGrund: evGrund.trim(),
        ...(evMenge ? { mengeKg: Number(evMenge) } : {}),
      })
      if (res.ok) {
        setEvGrund(''); setEvMenge('')
        toast({ title: 'Ereignis erfasst', description: 'Der Vorgang wurde revisionsfest protokolliert.' })
      } else {
        toast({ title: 'Hinweis', description: res.detail ?? 'Nicht erfasst', variant: 'destructive' })
      }
    } catch {
      toast({ title: 'Fehler', description: 'Ereignis konnte nicht erfasst werden.', variant: 'destructive' })
    }
  }

  const submitStorno = async () => {
    if (!selected) return
    if (!stornoGrund.trim()) {
      toast({ title: 'Grund fehlt', description: 'Bitte einen Storno-Grund angeben.', variant: 'destructive' })
      return
    }
    try {
      const res = await cancelChain.mutateAsync({ ticket: selected, grund: stornoGrund.trim() })
      if (res.ok) {
        setStornoOpen(false); setStornoGrund('')
        toast({ title: 'Kette storniert', description: `Lots zurückgesetzt: ${(res.stornierte_lots ?? []).join(', ') || '—'}` })
      }
    } catch (e) {
      toast({ title: 'Storno nicht möglich', description: errDetail(e, 'Storno fehlgeschlagen.'), variant: 'destructive' })
    }
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <GitBranch size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Rückverfolgbarkeit</h1>
        <span className="text-sm text-muted-foreground">Wiegung → Annahme → Lager → Abrechnung</span>
        <Button
          variant="outline" size="sm" className="ml-auto"
          onClick={() => void ticketsQuery.refetch()} disabled={ticketsQuery.isFetching}
        >
          {ticketsQuery.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[20rem_1fr]">
        {/* Picker */}
        <Card className="h-fit">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Wiegescheine</CardTitle>
            <div className="relative">
              <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={filter} onChange={(e) => setFilter(e.target.value)}
                placeholder="Nr. suchen…" className="h-8 pl-7"
              />
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[70vh] overflow-y-auto">
            {ticketsQuery.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                <Loader2 className="animate-spin mr-2" size={16} /> Lädt …
              </div>
            ) : tickets.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">Keine Wiegescheine.</div>
            ) : (
              <div className="divide-y">
                {tickets.map((t) => (
                  <button
                    key={t.ticket_id}
                    onClick={() => setSelected(t.ticket_nr)}
                    className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${
                      selected === t.ticket_nr ? 'bg-muted' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-sm">{t.ticket_nr}</span>
                      <CompletenessDots t={t} />
                    </div>
                    <div className="text-xs text-muted-foreground flex justify-between">
                      <span>{t.datum ? new Date(t.datum).toLocaleDateString('de-DE') : '—'}</span>
                      <span className="tabular-nums">{fmtKg(t.menge_kg)}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Kette */}
        <div className="space-y-3">
          {!selected ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">
              Wiegeschein links wählen, um die durchgängige Kette anzuzeigen.
            </CardContent></Card>
          ) : trace.isLoading ? (
            <Card><CardContent className="py-16 text-center text-muted-foreground">
              <Loader2 className="animate-spin mx-auto mb-2" size={18} /> Kette wird geladen …
            </CardContent></Card>
          ) : !trace.data?.found ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">
              {trace.data?.detail ?? 'Keine Kette gefunden.'}
            </CardContent></Card>
          ) : (
            <>
              {/* Summary */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">{trace.data.ticket_nr}</span>
                <Badge variant="outline" className="capitalize">
                  Status: {STATUS_LABEL[trace.data.kanon_status?.status ?? 'offen'] ?? trace.data.kanon_status?.status}
                </Badge>
                {trace.data.summary?.vollstaendig
                  ? <Badge className="bg-emerald-600"><CheckCircle2 className="mr-1 h-3 w-3" />Kette vollständig</Badge>
                  : <Badge variant="secondary">Kette unvollständig</Badge>}
                {trace.data.summary?.hat_mengen_abweichung && (
                  <Badge variant="destructive"><AlertTriangle className="mr-1 h-3 w-3" />Mengen-Abweichung</Badge>
                )}
                {!!trace.data.summary?.offene_luecken && (
                  <Badge variant="outline">{trace.data.summary.offene_luecken} Lücke(n)</Badge>
                )}
                {trace.data.kanon_status?.status !== 'storniert' && (
                  <Button size="sm" variant="outline" className="ml-auto text-red-700 hover:text-red-800"
                    onClick={() => setStornoOpen((v) => !v)}>
                    <Ban size={14} className="mr-1" />Kette stornieren
                  </Button>
                )}
              </div>

              {stornoOpen && trace.data.kanon_status?.status !== 'storniert' && (
                <div className="flex flex-col gap-2 rounded-md border border-red-200 bg-red-50 p-2 sm:flex-row sm:items-center">
                  <Input value={stornoGrund} onChange={(e) => setStornoGrund(e.target.value)}
                    placeholder="Storno-Grund (Pflicht)…" className="h-9 flex-1" disabled={cancelChain.isPending} />
                  <Button size="sm" variant="destructive" onClick={submitStorno} disabled={cancelChain.isPending}>
                    {cancelChain.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <Ban size={14} className="mr-1" />}
                    Storno bestätigen
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setStornoOpen(false)} disabled={cancelChain.isPending}>
                    Abbrechen
                  </Button>
                </div>
              )}

              {/* Genealogie-Timeline */}
              <div className="space-y-1">
                {((kette) => kette.map((node, i) => (
                  <div key={node.ref_id}>
                    <StageNode node={node} />
                    {node.stage === 'lager' && <LotActions node={node} />}
                    {i < kette.length - 1 && (
                      <div className="flex justify-center py-0.5 text-muted-foreground"><ArrowDown size={14} /></div>
                    )}
                  </div>
                )))(trace.data.kette ?? [])}
              </div>

              {/* Mengen-Konsistenz */}
              {!!trace.data.mengen_konsistenz?.length && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Mengen-Konsistenz</CardTitle></CardHeader>
                  <CardContent className="space-y-1.5">
                    {trace.data.mengen_konsistenz.map((c, i) => (
                      <div key={i} className={`flex items-center justify-between rounded border p-2 text-sm ${
                        c.abweichung ? 'border-red-200 bg-red-50 text-red-900' : 'border-emerald-200 bg-emerald-50/50'
                      }`}>
                        <span>{c.von} → {c.nach}</span>
                        <span className="tabular-nums">
                          {fmtKg(c.menge_von_kg)} → {fmtKg(c.menge_nach_kg)}{' '}
                          ({c.differenz_pct != null ? `${c.differenz_pct > 0 ? '+' : ''}${c.differenz_pct}%` : '—'})
                        </span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Lücken */}
              {!!trace.data.luecken?.length && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Lücken & Hinweise</CardTitle></CardHeader>
                  <CardContent className="space-y-1.5">
                    {trace.data.luecken.map((l, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        {l.schwere === 'warnung'
                          ? <AlertTriangle size={15} className="mt-0.5 text-amber-600 shrink-0" />
                          : <Info size={15} className="mt-0.5 text-sky-600 shrink-0" />}
                        <span><span className="opacity-60">[{l.stufe}]</span> {l.text}</span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Ereignis-Log (revisionsfest, append-only) */}
              <Card>
                <CardHeader className="py-3">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <History size={15} /> Ereignis-Log
                    {syncChain.isPending && <Loader2 size={13} className="animate-spin text-muted-foreground" />}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {(trace.data.ereignisse ?? []).length === 0 ? (
                    <div className="text-sm text-muted-foreground">Noch keine Ereignisse.</div>
                  ) : (
                    <ol className="relative border-l pl-4 space-y-2">
                      {(trace.data.ereignisse ?? []).map((e: ChainEvent) => (
                        <li key={e.id} className="text-sm">
                          <span className="absolute left-[-5px] mt-1.5 h-2 w-2 rounded-full bg-primary" />
                          <div className="flex flex-wrap items-center gap-2">
                            <Badge variant="outline" className="capitalize">{e.event_type}</Badge>
                            <span className="opacity-60">[{e.stage}]</span>
                            {e.ref_label && <span className="font-medium">{e.ref_label}</span>}
                            {e.source === 'manual' && <Badge variant="secondary" className="text-[10px]">manuell</Badge>}
                            {e.source === 'backfill' && (
                              <Badge variant="secondary" className="text-[10px]"><Bot size={10} className="mr-0.5" />abgeleitet</Badge>
                            )}
                            {e.menge_kg != null && <span className="tabular-nums text-xs">{fmtKg(e.menge_kg)}</span>}
                            <span className="ml-auto text-xs text-muted-foreground">
                              {e.occurred_at ? new Date(e.occurred_at).toLocaleString('de-DE') : ''}
                            </span>
                          </div>
                          {e.abweichung_grund && <div className="text-xs text-muted-foreground">{e.abweichung_grund}</div>}
                        </li>
                      ))}
                    </ol>
                  )}

                  {/* Ereignis erfassen */}
                  <div className="mt-3 flex flex-col gap-2 rounded-md border bg-muted/30 p-2 sm:flex-row sm:items-center">
                    <NativeSelect value={evType} onChange={(e) => setEvType(e.target.value)} className="h-9 sm:w-40">
                      <option value="korrektur">Korrektur</option>
                      <option value="abweichung">Abweichung</option>
                      <option value="storniert">Storno</option>
                      <option value="notiz">Notiz</option>
                    </NativeSelect>
                    <Input value={evGrund} onChange={(e) => setEvGrund(e.target.value)}
                      placeholder="Grund / Notiz…" className="h-9 flex-1" />
                    <Input value={evMenge} onChange={(e) => setEvMenge(e.target.value)}
                      type="number" placeholder="Menge kg (optional)" className="h-9 sm:w-44" />
                    <Button size="sm" onClick={submitEvent} disabled={addEvent.isPending}>
                      {addEvent.isPending ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
                      <span className="ml-1">Erfassen</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
