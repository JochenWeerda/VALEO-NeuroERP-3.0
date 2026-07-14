import { useState } from 'react'
import { ClipboardCheck, Loader2, RefreshCw, Search, AlertTriangle, Info, CheckCircle2, PackageCheck, MessageSquarePlus, FileMinus2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { toast } from '@/hooks/use-toast'
import { useMatchOrders, useMatch, useCreateFollowUp, useCreateErsCredit, type MatchOrder, type FollowUpCreate } from '@/lib/api/procurement-match'

/**
 * Wareneingangs-Abgleich / 3-Wege-Match (DOM-PROC-004) — Bestellung ↔ Wareneingang ↔ Rechnung:
 * je Position bestellt vs. geliefert, offene Menge/Wert, Über-/Unterlieferung, Lücken.
 */

const STATUS_STYLE: Record<string, string> = {
  vollstaendig: 'text-emerald-700',
  teilgeliefert: 'text-amber-700',
  ueberliefert: 'text-red-700',
  offen: 'text-muted-foreground',
}

const fmt = (n: number | null | undefined, suffix = '') =>
  n == null ? '—' : `${n.toLocaleString('de-DE', { maximumFractionDigits: 2 })}${suffix}`

const FOLLOW_UP_LABELS: Record<FollowUpCreate['action_type'], string> = {
  nachforderung: 'Nachforderung',
  reklamation: 'Reklamation',
  eskalation: 'Eskalation',
  freigabe: 'Manuelle Freigabe',
}

function OrderDots({ o }: { o: MatchOrder }) {
  return (
    <span title={o.hat_wareneingang ? 'Wareneingang vorhanden' : 'kein Wareneingang'}
      className={`inline-block h-2 w-2 rounded-full ${o.hat_wareneingang ? 'bg-emerald-500' : 'bg-muted-foreground/30'}`} />
  )
}

export default function WareneingangsabgleichPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const [pendingAction, setPendingAction] = useState<FollowUpCreate['action_type'] | null>(null)
  const [grund, setGrund] = useState('')
  const ordersQuery = useMatchOrders(50)
  const match = useMatch(selected)
  const followUpMutation = useCreateFollowUp(selected)
  const ersMutation = useCreateErsCredit(selected)

  const hatAusnahmen = !!(match.data?.ausnahmen?.length || match.data?.luecken?.length || match.data?.summary?.hat_ausnahme)

  const submitErs = async () => {
    if (!selected || !match.data?.ers_preview?.berechtigt) return
    try {
      await ersMutation.mutateAsync({ bestellnummer: selected })
      toast({ title: 'ERS-Gutschrift erzeugt', description: fmt(match.data.ers_preview.betrag_netto, ' € netto') })
      void match.refetch()
    } catch (err) {
      toast({
        variant: 'destructive',
        title: 'ERS fehlgeschlagen',
        description: err instanceof Error ? err.message : 'Unbekannter Fehler',
      })
    }
  }

  const submitFollowUp = async () => {
    if (!selected || !pendingAction) return
    const text = grund.trim()
    if (text.length < 3) {
      toast({ variant: 'destructive', title: 'Grund erforderlich', description: 'Bitte mindestens 3 Zeichen eingeben.' })
      return
    }
    const firstCode = match.data?.ausnahmen?.[0]?.code ?? match.data?.luecken?.[0]?.code ?? null
    try {
      await followUpMutation.mutateAsync({
        bestellnummer: selected,
        action_type: pendingAction,
        grund: text,
        ausnahme_code: firstCode,
      })
      toast({ title: 'Folgeaktion erfasst', description: FOLLOW_UP_LABELS[pendingAction] })
      setPendingAction(null)
      setGrund('')
      void match.refetch()
    } catch (err) {
      toast({
        variant: 'destructive',
        title: 'Speichern fehlgeschlagen',
        description: err instanceof Error ? err.message : 'Unbekannter Fehler',
      })
    }
  }

  const orders = (ordersQuery.data ?? []).filter((o) => !filter || o.bestellnummer.toLowerCase().includes(filter.toLowerCase()))

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <ClipboardCheck size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Wareneingangs-Abgleich</h1>
        <span className="text-sm text-muted-foreground">3-Wege-Match: Bestellung ↔ Wareneingang ↔ Rechnung</span>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void ordersQuery.refetch()} disabled={ordersQuery.isFetching}>
          {ordersQuery.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[20rem_1fr]">
        <Card className="h-fit">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Bestellungen</CardTitle>
            <div className="relative">
              <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Nr. suchen…" className="h-8 pl-7" />
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[70vh] overflow-y-auto">
            {ordersQuery.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
            ) : orders.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">Keine Bestellungen.</div>
            ) : (
              <div className="divide-y">
                {orders.map((o) => (
                  <button key={o.bestellnummer} onClick={() => setSelected(o.bestellnummer)}
                    className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${selected === o.bestellnummer ? 'bg-muted' : ''}`}>
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-sm truncate">{o.bestellnummer}</span>
                      <OrderDots o={o} />
                    </div>
                    <div className="text-xs text-muted-foreground flex justify-between">
                      <span>{o.positionen} Pos. · {o.status}</span>
                      <span className="tabular-nums">{fmt(o.netto_summe, ' €')}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-3">
          {!selected ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Bestellung wählen, um den Abgleich zu sehen.</CardContent></Card>
          ) : match.isLoading ? (
            <Card><CardContent className="py-16 text-center text-muted-foreground"><Loader2 className="animate-spin mx-auto mb-2" size={18} /> Lädt …</CardContent></Card>
          ) : !match.data?.found ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">{match.data?.detail ?? 'Nicht gefunden.'}</CardContent></Card>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">{match.data.bestellnummer}</span>
                {match.data.summary?.vollstaendig_geliefert
                  ? <Badge className="bg-emerald-600"><CheckCircle2 className="mr-1 h-3 w-3" />vollständig geliefert</Badge>
                  : <Badge variant="secondary">offen/teilweise</Badge>}
                {match.data.summary?.hat_abweichung && <Badge variant="destructive"><AlertTriangle className="mr-1 h-3 w-3" />Mengenabweichung</Badge>}
                {!!match.data.summary?.offene_luecken && <Badge variant="outline">{match.data.summary.offene_luecken} Hinweis(e)</Badge>}
                {match.data.summary?.drei_wege_abgeglichen
                  ? <Badge className="bg-emerald-700">3-Wege abgeglichen</Badge>
                  : match.data.three_way && <Badge variant="destructive">Rechnungsstufe offen</Badge>}
              </div>

              {match.data.three_way && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Rechnungsstufe</CardTitle></CardHeader>
                  <CardContent className="grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
                    <div><div className="text-xs text-muted-foreground">Bestellt</div><div className="tabular-nums font-medium">{fmt(match.data.three_way.bestellt_wert, ' €')}</div></div>
                    <div><div className="text-xs text-muted-foreground">Geliefert (Wert)</div><div className="tabular-nums font-medium">{fmt(match.data.three_way.geliefert_wert, ' €')}</div></div>
                    <div><div className="text-xs text-muted-foreground">Fakturiert</div><div className="tabular-nums font-medium">{fmt(match.data.three_way.fakturiert_netto, ' €')}</div></div>
                    <div><div className="text-xs text-muted-foreground">Status</div><div className="font-medium">{match.data.three_way.status}</div></div>
                  </CardContent>
                </Card>
              )}

              {!!match.data.rechnungen?.length && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Eingangsrechnungen</CardTitle></CardHeader>
                  <CardContent className="space-y-1">
                    {match.data.rechnungen.map((r) => (
                      <div key={r.id} className="text-sm flex items-center gap-2">
                        <Badge variant="outline">{r.rechnungsnummer}</Badge>
                        <span className="text-muted-foreground">{r.status}</span>
                        <span className="ml-auto tabular-nums">{fmt(r.gesamt_netto, ' €')}</span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              <Card>
                <CardHeader className="py-3"><CardTitle className="text-sm">Positionen</CardTitle></CardHeader>
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
                          <th className="text-right font-medium px-3 py-1.5">Offener Wert</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(match.data.positionen ?? []).map((p) => (
                          <tr key={p.pos_nr} className="border-b last:border-0">
                            <td className="px-3 py-1.5">{p.pos_nr}</td>
                            <td className="px-3 py-1.5">{p.bezeichnung || p.artikel_nr}</td>
                            <td className="px-3 py-1.5 text-right tabular-nums">{fmt(p.bestellt, ` ${p.einheit ?? ''}`)}</td>
                            <td className="px-3 py-1.5 text-right tabular-nums">{fmt(p.geliefert)}</td>
                            <td className="px-3 py-1.5 text-right tabular-nums">{fmt(p.offen)}</td>
                            <td className={`px-3 py-1.5 font-medium ${STATUS_STYLE[p.status] ?? ''}`}>
                              {p.status}{p.abweichung_pct ? ` (${p.abweichung_pct > 0 ? '+' : ''}${p.abweichung_pct}%)` : ''}
                            </td>
                            <td className="px-3 py-1.5 text-right tabular-nums">{fmt(p.wert_offen, ' €')}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {!!match.data.wareneingaenge?.length && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm flex items-center gap-2"><PackageCheck size={15} />Wareneingänge</CardTitle></CardHeader>
                  <CardContent className="space-y-1">
                    {match.data.wareneingaenge.map((g, i) => (
                      <div key={i} className="text-sm flex items-center gap-2">
                        <Badge variant="outline">{g.gr_number}</Badge>
                        <span className="text-muted-foreground">{g.status}</span>
                        <span className="ml-auto text-xs text-muted-foreground">{g.datum ? new Date(g.datum).toLocaleDateString('de-DE') : ''}</span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {!!(match.data.ausnahmen?.length || match.data.luecken?.length) && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Ausnahmen & Lücken</CardTitle></CardHeader>
                  <CardContent className="space-y-1.5">
                    {(match.data.ausnahmen ?? match.data.luecken ?? []).map((l, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        {l.schwere === 'warnung' ? <AlertTriangle size={15} className="mt-0.5 text-status-warning shrink-0" /> : <Info size={15} className="mt-0.5 text-sky-600 shrink-0" />}
                        <span>{l.text}</span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {match.data.ers_preview?.berechtigt && (
                <Card>
                  <CardHeader className="py-3">
                    <CardTitle className="text-sm flex items-center gap-2"><FileMinus2 size={15} />ERS-Gutschrift</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="text-sm">
                      Vorschau: <span className="font-medium tabular-nums">{fmt(match.data.ers_preview.betrag_netto, ' € netto')}</span>
                      <span className="text-muted-foreground"> · {match.data.ers_preview.anzahl_zeilen} Position(en)</span>
                    </div>
                    <Button size="sm" onClick={() => void submitErs()} disabled={ersMutation.isPending}>
                      {ersMutation.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : null}
                      Gutschrift erzeugen
                    </Button>
                    {!!match.data.ers_credits?.length && (
                      <div className="border-t pt-3 space-y-2">
                        <div className="text-xs font-medium text-muted-foreground">Erfasste Gutschriften</div>
                        {match.data.ers_credits.map((g) => (
                          <div key={g.id} className="text-sm flex items-center gap-2">
                            <Badge variant="outline">{g.gutschrift_nummer}</Badge>
                            <span className="text-muted-foreground">{g.status}</span>
                            <span className="ml-auto tabular-nums">{fmt(g.betrag_netto, ' €')}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {hatAusnahmen && (
                <Card>
                  <CardHeader className="py-3">
                    <CardTitle className="text-sm flex items-center gap-2"><MessageSquarePlus size={15} />Folgeaktionen</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex flex-wrap gap-2">
                      {(Object.keys(FOLLOW_UP_LABELS) as FollowUpCreate['action_type'][]).map((action) => (
                        <Button
                          key={action}
                          size="sm"
                          variant={pendingAction === action ? 'default' : 'outline'}
                          disabled={followUpMutation.isPending}
                          onClick={() => setPendingAction(action)}
                        >
                          {FOLLOW_UP_LABELS[action]}
                        </Button>
                      ))}
                    </div>
                    {pendingAction && (
                      <div className="space-y-2">
                        <Textarea
                          value={grund}
                          onChange={(e) => setGrund(e.target.value)}
                          placeholder={`Grund für ${FOLLOW_UP_LABELS[pendingAction]} …`}
                          rows={3}
                        />
                        <div className="flex gap-2">
                          <Button size="sm" onClick={() => void submitFollowUp()} disabled={followUpMutation.isPending}>
                            {followUpMutation.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : null}
                            Erfassen
                          </Button>
                          <Button size="sm" variant="ghost" disabled={followUpMutation.isPending} onClick={() => { setPendingAction(null); setGrund('') }}>
                            Abbrechen
                          </Button>
                        </div>
                      </div>
                    )}
                    {!!match.data.follow_ups?.length && (
                      <div className="border-t pt-3 space-y-2">
                        <div className="text-xs font-medium text-muted-foreground">Protokoll (append-only)</div>
                        {match.data.follow_ups.map((f) => (
                          <div key={f.id} className="text-sm rounded-md border px-3 py-2">
                            <div className="flex flex-wrap items-center gap-2">
                              <Badge variant="outline">{FOLLOW_UP_LABELS[f.action_type as FollowUpCreate['action_type']] ?? f.action_type}</Badge>
                              {f.eskalationsstufe > 1 && <span className="text-xs text-muted-foreground">Stufe {f.eskalationsstufe}</span>}
                              {f.created_at && <span className="text-xs text-muted-foreground ml-auto">{new Date(f.created_at).toLocaleString('de-DE')}</span>}
                            </div>
                            <p className="mt-1">{f.grund}</p>
                          </div>
                        ))}
                      </div>
                    )}
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
