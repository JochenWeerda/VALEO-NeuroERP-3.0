import { useState } from 'react'
import {
  Workflow, FileText, ClipboardCheck, Truck, Receipt, Loader2, RefreshCw, Search,
  ArrowDown, CheckCircle2, AlertTriangle, Info,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useO2COrders, useO2C, type O2CNode, type O2COrder } from '@/lib/api/o2c-chain'

/**
 * Auftragskette / Order-to-Cash (DOM-SALES-004) — Angebot→Auftrag→Lieferschein→
 * Rechnung je Auftrag, mit kanonischem Status und Lücken (kein LS / keine Rechnung).
 */

const STAGE_ICON: Record<string, JSX.Element> = {
  angebot: <FileText size={16} />,
  auftrag: <ClipboardCheck size={16} />,
  lieferschein: <Truck size={16} />,
  rechnung: <Receipt size={16} />,
}
const STATUS_LABEL: Record<string, string> = {
  angebot: 'Angebot', auftrag: 'Auftrag', geliefert: 'geliefert', berechnet: 'berechnet',
}

function OrderDots({ o }: { o: O2COrder }) {
  const dot = (ok: boolean, l: string) => <span title={l} className={`inline-block h-2 w-2 rounded-full ${ok ? 'bg-emerald-500' : 'bg-muted-foreground/30'}`} />
  return <span className="inline-flex items-center gap-1">{dot(true, 'Auftrag')}{dot(o.hat_lieferschein, 'Lieferschein')}{dot(o.hat_rechnung, 'Rechnung')}</span>
}

export default function AuftragskettePage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const ordersQuery = useO2COrders(50)
  const chain = useO2C(selected)

  const orders = (ordersQuery.data ?? []).filter((o) => !filter || o.order_number.toLowerCase().includes(filter.toLowerCase()))

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Workflow size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Auftragskette</h1>
        <span className="text-sm text-muted-foreground">Angebot → Auftrag → Lieferschein → Rechnung</span>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void ordersQuery.refetch()} disabled={ordersQuery.isFetching}>
          {ordersQuery.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[20rem_1fr]">
        <Card className="h-fit">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Aufträge</CardTitle>
            <div className="relative">
              <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Nr. suchen…" className="h-8 pl-7" />
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[70vh] overflow-y-auto">
            {ordersQuery.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
            ) : orders.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">Keine Aufträge.</div>
            ) : (
              <div className="divide-y">
                {orders.map((o) => (
                  <button key={o.order_number} onClick={() => setSelected(o.order_number)}
                    className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${selected === o.order_number ? 'bg-muted' : ''}`}>
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-sm truncate">{o.order_number}</span>
                      <OrderDots o={o} />
                    </div>
                    <div className="text-xs text-muted-foreground truncate">{o.kunde || '—'}</div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-3">
          {!selected ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Auftrag wählen, um die Kette zu sehen.</CardContent></Card>
          ) : chain.isLoading ? (
            <Card><CardContent className="py-16 text-center text-muted-foreground"><Loader2 className="animate-spin mx-auto mb-2" size={18} /> Lädt …</CardContent></Card>
          ) : !chain.data?.found ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">{chain.data?.detail ?? 'Nicht gefunden.'}</CardContent></Card>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">{chain.data.order_number}</span>
                {chain.data.kunde && <span className="text-sm text-muted-foreground">· {chain.data.kunde}</span>}
                <Badge variant="outline" className="capitalize">Status: {STATUS_LABEL[chain.data.summary?.status ?? ''] ?? chain.data.summary?.status}</Badge>
                {chain.data.summary?.vollstaendig
                  ? <Badge className="bg-emerald-600"><CheckCircle2 className="mr-1 h-3 w-3" />vollständig</Badge>
                  : <Badge variant="secondary">offen</Badge>}
              </div>

              <div className="space-y-1">
                {((kette) => kette.map((node: O2CNode, i: number) => (
                  <div key={`${node.stage}-${node.ref}-${i}`}>
                    <div className="rounded-lg border p-3 flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2 font-medium text-sm">
                        <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-muted">{STAGE_ICON[node.stage] ?? <FileText size={16} />}</span>
                        {node.label}{node.ref && <span className="text-muted-foreground font-normal">· {node.ref}</span>}
                      </div>
                      <div className="flex items-center gap-2">
                        {node.betrag != null && <span className="text-sm tabular-nums">{node.betrag.toLocaleString('de-DE')} €</span>}
                        {node.status && <Badge variant="outline">{node.status}</Badge>}
                      </div>
                    </div>
                    {i < kette.length - 1 && <div className="flex justify-center py-0.5 text-muted-foreground"><ArrowDown size={14} /></div>}
                  </div>
                )))(chain.data.kette ?? [])}
              </div>

              {!!chain.data.luecken?.length && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Lücken & Hinweise</CardTitle></CardHeader>
                  <CardContent className="space-y-1.5">
                    {chain.data.luecken.map((l, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        {l.schwere === 'warnung' ? <AlertTriangle size={15} className="mt-0.5 text-status-warning shrink-0" /> : <Info size={15} className="mt-0.5 text-sky-600 shrink-0" />}
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
