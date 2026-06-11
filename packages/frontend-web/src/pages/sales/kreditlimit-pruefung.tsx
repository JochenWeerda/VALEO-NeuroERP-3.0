import { useState } from 'react'
import { ShieldCheck, Loader2, RefreshCw, Search } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useSalesMatchOrders } from '@/lib/api/sales-match'
import { useCreditCustomers, useOrderCredit, type CreditAmpel } from '@/lib/api/sales-credit'

/**
 * Kreditlimit-Prüfung (DOM-SALES-004.3) — Kunden-Kreditampel (Limit vs. offene
 * Exposure) und Auftrags-Kreditprüfung (Wirkung des Auftrags auf den Rahmen) +
 * Billing-Status je Lieferschein.
 */

const AMPEL: Record<string, { cls: string; label: string }> = {
  ok: { cls: 'bg-emerald-100 text-emerald-800', label: 'OK' },
  warnung: { cls: 'bg-amber-100 text-amber-800', label: 'Warnung' },
  blockiert: { cls: 'bg-red-100 text-red-800', label: 'Blockiert' },
  kein_limit: { cls: 'bg-muted text-muted-foreground', label: 'kein Limit' },
}

function AmpelBadge({ ampel }: { ampel: CreditAmpel }) {
  const a = AMPEL[ampel] ?? AMPEL.kein_limit
  return <Badge className={`text-[10px] ${a.cls}`}>{a.label}</Badge>
}

function eur(v: number | null | undefined) {
  return v == null ? '—' : v.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
}

export default function KreditlimitPruefungPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const customers = useCreditCustomers()
  const orders = useSalesMatchOrders()
  const credit = useOrderCredit(selected)

  const list = (orders.data ?? []).filter((o) => !filter || o.order_number.toLowerCase().includes(filter.toLowerCase()))
  const d = credit.data

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <ShieldCheck size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Kreditlimit-Prüfung</h1>
        <Button variant="outline" size="sm" className="ml-auto"
          onClick={() => { void customers.refetch(); void orders.refetch() }}
          disabled={customers.isFetching || orders.isFetching}>
          {customers.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <Card>
        <CardHeader className="py-3"><CardTitle className="text-sm">Kunden-Kreditampel</CardTitle></CardHeader>
        <CardContent className="p-0">
          {customers.isLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Kunde</th>
                    <th className="text-right font-medium px-3 py-1.5">Limit</th>
                    <th className="text-right font-medium px-3 py-1.5">Exposure</th>
                    <th className="text-right font-medium px-3 py-1.5">Verfügbar</th>
                    <th className="text-right font-medium px-3 py-1.5">Auslastung</th>
                    <th className="text-left font-medium px-3 py-1.5">Ampel</th>
                  </tr>
                </thead>
                <tbody>
                  {(customers.data ?? []).map((c) => (
                    <tr key={c.customer_id} className="border-b last:border-0">
                      <td className="px-3 py-1.5">{c.kunde ?? c.customer_id}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(c.limit)}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(c.exposure)}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(c.verfuegbar)}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{c.limit > 0 ? `${c.auslastung_pct}%` : '—'}</td>
                      <td className="px-3 py-1.5"><AmpelBadge ampel={c.ampel} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[22rem_1fr]">
        <Card className="h-fit">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Aufträge prüfen</CardTitle>
            <div className="relative">
              <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Nr. suchen…" className="h-8 pl-7" />
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[60vh] overflow-y-auto">
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
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Auftrag wählen, um die Kreditlimit-Prüfung zu sehen.</CardContent></Card>
          ) : credit.isLoading ? (
            <Card><CardContent className="py-16 text-center text-muted-foreground"><Loader2 className="animate-spin mx-auto mb-2" size={18} /> Lädt …</CardContent></Card>
          ) : !d?.found ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">{d?.detail ?? 'Nicht gefunden.'}</CardContent></Card>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">{d.order_number}</span>
                <span className="text-sm text-muted-foreground">{d.kunde}</span>
                {d.kredit && <AmpelBadge ampel={d.kredit.ampel} />}
              </div>
              <Card>
                <CardContent className="p-3 grid grid-cols-2 gap-3 text-sm md:grid-cols-3">
                  <div><div className="text-xs text-muted-foreground">Kreditlimit</div><div className="font-semibold tabular-nums">{eur(d.kredit?.limit)}</div></div>
                  <div><div className="text-xs text-muted-foreground">Exposure (andere)</div><div className="font-semibold tabular-nums">{eur(d.kredit?.exposure)}</div></div>
                  <div><div className="text-xs text-muted-foreground">Verfügbar</div><div className="font-semibold tabular-nums">{eur(d.kredit?.verfuegbar)}</div></div>
                  <div><div className="text-xs text-muted-foreground">Auftragswert</div><div className="font-semibold tabular-nums">{eur(d.auftrag_betrag)}</div></div>
                  <div><div className="text-xs text-muted-foreground">Auslastung mit Auftrag</div><div className={`font-semibold tabular-nums ${(d.kredit?.auslastung_neu_pct ?? 0) >= 100 ? 'text-red-700' : (d.kredit?.auslastung_neu_pct ?? 0) >= 80 ? 'text-amber-700' : 'text-emerald-700'}`}>{d.kredit?.limit ? `${d.kredit?.auslastung_neu_pct}%` : '—'}</div></div>
                  <div><div className="text-xs text-muted-foreground">Offen unberechnet</div><div className="font-semibold tabular-nums">{d.summary?.offen_unberechnet} / {d.summary?.lieferscheine} LS</div></div>
                </CardContent>
              </Card>

              {(d.billing?.length ?? 0) > 0 && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Billing-Status</CardTitle></CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="text-xs text-muted-foreground border-b">
                          <tr>
                            <th className="text-left font-medium px-3 py-1.5">Lieferschein</th>
                            <th className="text-left font-medium px-3 py-1.5">Rechnung</th>
                            <th className="text-left font-medium px-3 py-1.5">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(d.billing ?? []).map((b) => (
                            <tr key={b.lieferschein} className="border-b last:border-0">
                              <td className="px-3 py-1.5">{b.lieferschein}</td>
                              <td className="px-3 py-1.5 text-muted-foreground">{b.rechnung ?? '—'}</td>
                              <td className="px-3 py-1.5">
                                <Badge className={`text-[10px] ${b.billing_status === 'berechnet' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>{b.billing_status}</Badge>
                              </td>
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
    </div>
  )
}
