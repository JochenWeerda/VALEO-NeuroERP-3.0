import { useState } from 'react'
import { PackageCheck, Loader2, RefreshCw, Search, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useSalesMatchOrders, useSalesMatch, type SalesMatchOrderRow } from '@/lib/api/sales-match'

/**
 * Auftrag-↔-Lieferschein-Abgleich (DOM-SALES-004.2) — Positions-Match je Auftrag:
 * bestellt vs. geliefert, offene Menge/Wert, Teil-/Überlieferung, Lücken.
 */

const STATUS_STYLE: Record<string, string> = {
  vollstaendig: 'text-emerald-700', teilgeliefert: 'text-amber-700',
  ueberliefert: 'text-red-700', offen: 'text-muted-foreground',
}

function Row({ o, active, onClick }: { o: SalesMatchOrderRow; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${active ? 'bg-muted' : ''}`}>
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium text-sm truncate">{o.order_number}</span>
        {o.hat_lieferschein ? <Badge variant="outline" className="text-[10px]">LS</Badge> : <Badge variant="secondary" className="text-[10px]">kein LS</Badge>}
      </div>
      <div className="text-xs text-muted-foreground mt-0.5">{o.kunde ?? '—'} · {o.positionen} Pos.</div>
    </button>
  )
}

export default function AuftragLieferscheinAbgleichPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const orders = useSalesMatchOrders()
  const match = useSalesMatch(selected)

  const list = (orders.data ?? []).filter((o) => !filter || o.order_number.toLowerCase().includes(filter.toLowerCase()))
  const d = match.data

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <PackageCheck size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Auftrag-Lieferschein-Abgleich</h1>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void orders.refetch()} disabled={orders.isFetching}>
          {orders.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[22rem_1fr]">
        <Card className="h-fit">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Aufträge</CardTitle>
            <div className="relative">
              <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Nr. suchen…" className="h-8 pl-7" />
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[70vh] overflow-y-auto">
            {orders.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
            ) : list.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">Keine Aufträge.</div>
            ) : (
              <div className="divide-y">
                {list.map((o) => <Row key={o.order_number} o={o} active={selected === o.order_number} onClick={() => setSelected(o.order_number)} />)}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-3">
          {!selected ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Auftrag wählen, um den Positions-Abgleich zu sehen.</CardContent></Card>
          ) : match.isLoading ? (
            <Card><CardContent className="py-16 text-center text-muted-foreground"><Loader2 className="animate-spin mx-auto mb-2" size={18} /> Lädt …</CardContent></Card>
          ) : !d?.found ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">{d?.detail ?? 'Nicht gefunden.'}</CardContent></Card>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">{d.order_number}</span>
                <span className="text-sm text-muted-foreground">{d.kunde}</span>
                {d.summary?.vollstaendig_geliefert
                  ? <Badge className="bg-emerald-600">vollständig geliefert</Badge>
                  : <Badge variant="secondary">{d.summary?.offen_positionen} Position(en) offen</Badge>}
                {d.summary?.hat_abweichung && <Badge variant="destructive"><AlertTriangle className="mr-1 h-3 w-3" />Abweichung</Badge>}
              </div>

              <Card>
                <CardHeader className="py-3"><CardTitle className="text-sm">Positions-Match</CardTitle></CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="text-xs text-muted-foreground border-b">
                        <tr>
                          <th className="text-left font-medium px-3 py-1.5">Pos</th>
                          <th className="text-left font-medium px-3 py-1.5">Artikel</th>
                          <th className="text-right font-medium px-3 py-1.5">Bestellt</th>
                          <th className="text-right font-medium px-3 py-1.5">Geliefert</th>
                          <th className="text-right font-medium px-3 py-1.5">Offen</th>
                          <th className="text-left font-medium px-3 py-1.5">Status</th>
                          <th className="text-right font-medium px-3 py-1.5">Wert offen</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(d.positionen ?? []).map((p) => (
                          <tr key={p.pos_nr} className="border-b last:border-0">
                            <td className="px-3 py-1.5">{p.pos_nr}</td>
                            <td className="px-3 py-1.5">{p.artikel_nr}<div className="text-[11px] text-muted-foreground">{p.bezeichnung}</div></td>
                            <td className="px-3 py-1.5 text-right tabular-nums">{p.bestellt} {p.einheit}</td>
                            <td className="px-3 py-1.5 text-right tabular-nums">{p.geliefert} {p.einheit}</td>
                            <td className="px-3 py-1.5 text-right tabular-nums">{p.offen}</td>
                            <td className={`px-3 py-1.5 font-medium ${STATUS_STYLE[p.status] ?? ''}`}>{p.status}</td>
                            <td className="px-3 py-1.5 text-right tabular-nums">{p.wert_offen != null ? p.wert_offen.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' }) : '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {(d.lieferscheine?.length ?? 0) > 0 && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Lieferscheine</CardTitle></CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="text-xs text-muted-foreground border-b">
                          <tr>
                            <th className="text-left font-medium px-3 py-1.5">Lieferschein</th>
                            <th className="text-left font-medium px-3 py-1.5">Datum</th>
                            <th className="text-left font-medium px-3 py-1.5">Status</th>
                            <th className="text-left font-medium px-3 py-1.5">Rechnung</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(d.lieferscheine ?? []).map((ls) => (
                            <tr key={ls.lieferschein} className="border-b last:border-0">
                              <td className="px-3 py-1.5">{ls.lieferschein}</td>
                              <td className="px-3 py-1.5">{ls.datum ? new Date(ls.datum).toLocaleDateString('de-DE') : '—'}</td>
                              <td className="px-3 py-1.5">{ls.status ?? '—'}</td>
                              <td className="px-3 py-1.5 text-muted-foreground">{ls.rechnung ?? '—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}

              {!!d.luecken?.length && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Lücken</CardTitle></CardHeader>
                  <CardContent className="space-y-1.5">
                    {d.luecken.map((l, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        <AlertTriangle size={15} className="mt-0.5 text-status-warning shrink-0" />
                        <span>{l.text}</span>
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
