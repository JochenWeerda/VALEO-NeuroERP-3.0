import { useState } from 'react'
import { Undo2, Loader2, RefreshCw, Search, Ban, ReceiptText } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription,
} from '@/components/ui/dialog'
import { toast } from '@/hooks/use-toast'
import { useSalesMatchOrders } from '@/lib/api/sales-match'
import { useStornoStatus, useStornoDelivery } from '@/lib/api/sales-storno'

/**
 * Lieferungs-Storno & Gutschrift (DOM-SALES-004.4) — Lieferschein stornieren
 * (fließt durchgängig in den Auftrag-Lieferschein-Match zurück); berechnete
 * Lieferungen sind storno-gesperrt (zuerst Gutschrift). Gutschrift-Übersicht.
 */

const STATUS_BADGE: Record<string, string> = {
  storniert: 'bg-red-100 text-red-800', geliefert: 'bg-emerald-100 text-emerald-800',
}

export default function LieferungStornoPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const [storno, setStorno] = useState<string | null>(null)
  const [grund, setGrund] = useState('')

  const orders = useSalesMatchOrders()
  const status = useStornoStatus(selected)
  const stornoMut = useStornoDelivery(selected)

  const list = (orders.data ?? []).filter((o) => !filter || o.order_number.toLowerCase().includes(filter.toLowerCase()))
  const d = status.data

  const confirmStorno = () => {
    if (!storno || !grund.trim() || stornoMut.isPending) return
    stornoMut.mutate(
      { lieferschein: storno, grund },
      {
        onSuccess: () => { toast({ title: `Lieferschein ${storno} storniert` }); setStorno(null); setGrund('') },
        onError: (err: unknown) => toast({
          title: 'Storno fehlgeschlagen',
          description: (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Unbekannter Fehler',
          variant: 'destructive',
        }),
      },
    )
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Undo2 size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Lieferung-Storno / Gutschrift</h1>
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
            ) : (
              <div className="divide-y">
                {list.map((o) => (
                  <button key={o.order_number} onClick={() => setSelected(o.order_number)}
                    className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${selected === o.order_number ? 'bg-muted' : ''}`}>
                    <div className="font-medium text-sm">{o.order_number}</div>
                    <div className="text-xs text-muted-foreground">{o.kunde ?? '—'}</div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-3">
          {!selected ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Auftrag wählen, um Lieferungen zu stornieren.</CardContent></Card>
          ) : status.isLoading ? (
            <Card><CardContent className="py-16 text-center text-muted-foreground"><Loader2 className="animate-spin mx-auto mb-2" size={18} /> Lädt …</CardContent></Card>
          ) : !d?.found ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">{d?.detail ?? 'Nicht gefunden.'}</CardContent></Card>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">{d.order_number}</span>
                <span className="text-sm text-muted-foreground">{d.kunde}</span>
                <Badge variant="outline">{d.summary?.storniert}/{d.summary?.lieferscheine} storniert</Badge>
                {(d.summary?.gutschriften ?? 0) > 0 && <Badge variant="secondary">{d.summary?.gutschriften} Gutschrift(en)</Badge>}
              </div>

              <Card>
                <CardHeader className="py-3"><CardTitle className="text-sm">Lieferscheine</CardTitle></CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="text-xs text-muted-foreground border-b">
                        <tr>
                          <th className="text-left font-medium px-3 py-1.5">Lieferschein</th>
                          <th className="text-left font-medium px-3 py-1.5">Status</th>
                          <th className="text-left font-medium px-3 py-1.5">Rechnung</th>
                          <th className="text-left font-medium px-3 py-1.5">Grund</th>
                          <th className="text-right font-medium px-3 py-1.5">Aktion</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(d.lieferscheine ?? []).map((ls) => (
                          <tr key={ls.lieferschein} className="border-b last:border-0">
                            <td className="px-3 py-1.5">{ls.lieferschein}</td>
                            <td className="px-3 py-1.5"><Badge className={`text-[10px] ${STATUS_BADGE[(ls.status ?? '').toLowerCase()] ?? ''}`}>{ls.status}</Badge></td>
                            <td className="px-3 py-1.5 text-muted-foreground">{ls.rechnung ?? '—'}</td>
                            <td className="px-3 py-1.5 text-muted-foreground">{ls.storno_grund ?? '—'}</td>
                            <td className="px-3 py-1.5 text-right">
                              {ls.storno_moeglich ? (
                                <Button size="sm" variant="ghost" onClick={() => { setStorno(ls.lieferschein); setGrund('') }}>
                                  <Ban size={13} className="text-status-error mr-1" />Storno
                                </Button>
                              ) : (
                                <span className="text-[11px] text-muted-foreground" title={ls.storno_sperrgrund ?? ''}>gesperrt</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {(d.gutschriften?.length ?? 0) > 0 && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm flex items-center gap-2"><ReceiptText size={14} /> Gutschriften (Kunde)</CardTitle></CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="text-xs text-muted-foreground border-b">
                          <tr>
                            <th className="text-left font-medium px-3 py-1.5">Gutschrift</th>
                            <th className="text-right font-medium px-3 py-1.5">Betrag</th>
                            <th className="text-left font-medium px-3 py-1.5">Status</th>
                            <th className="text-left font-medium px-3 py-1.5">Grund</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(d.gutschriften ?? []).map((g) => (
                            <tr key={g.gutschrift} className="border-b last:border-0">
                              <td className="px-3 py-1.5">{g.gutschrift}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums">{g.betrag != null ? g.betrag.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' }) : '—'}</td>
                              <td className="px-3 py-1.5">{g.status ?? '—'}</td>
                              <td className="px-3 py-1.5 text-muted-foreground">{g.grund ?? '—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </div>

      <Dialog open={!!storno} onOpenChange={(o) => { if (!o) { setStorno(null); setGrund('') } }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Lieferschein {storno} stornieren</DialogTitle>
            <DialogDescription>Der Storno fließt in den Auftrags-Abgleich zurück (Menge wird wieder offen). Grund erforderlich.</DialogDescription>
          </DialogHeader>
          <Textarea value={grund} onChange={(e) => setGrund(e.target.value)} placeholder="Grund des Stornos …" rows={3} />
          <DialogFooter>
            <Button variant="outline" onClick={() => { setStorno(null); setGrund('') }} disabled={stornoMut.isPending}>Abbrechen</Button>
            <Button variant="destructive" onClick={confirmStorno} disabled={!grund.trim() || stornoMut.isPending}>
              {stornoMut.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <Ban size={14} className="mr-1" />}
              Stornieren
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
