import { useState } from 'react'
import {
  GitBranch, Scale, ClipboardCheck, Warehouse, Receipt, Loader2, RefreshCw,
  CheckCircle2, AlertTriangle, Info, ArrowDown, Search,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  useTraceTickets, useTrace, type TraceNode, type TraceTicket,
} from '@/lib/api/supply-chain'

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
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const ticketsQuery = useTraceTickets(50)
  const trace = useTrace(selected)

  const tickets = (ticketsQuery.data ?? []).filter(
    (t) => !filter || (t.ticket_nr || '').toLowerCase().includes(filter.toLowerCase()),
  )

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
                {trace.data.summary?.vollstaendig
                  ? <Badge className="bg-emerald-600"><CheckCircle2 className="mr-1 h-3 w-3" />Kette vollständig</Badge>
                  : <Badge variant="secondary">Kette unvollständig</Badge>}
                {trace.data.summary?.hat_mengen_abweichung && (
                  <Badge variant="destructive"><AlertTriangle className="mr-1 h-3 w-3" />Mengen-Abweichung</Badge>
                )}
                {!!trace.data.summary?.offene_luecken && (
                  <Badge variant="outline">{trace.data.summary.offene_luecken} Lücke(n)</Badge>
                )}
              </div>

              {/* Genealogie-Timeline */}
              <div className="space-y-1">
                {((kette) => kette.map((node, i) => (
                  <div key={node.ref_id}>
                    <StageNode node={node} />
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
            </>
          )}
        </div>
      </div>
    </div>
  )
}
