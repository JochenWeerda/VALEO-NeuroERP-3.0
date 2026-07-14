import { useState } from 'react'
import { CalendarCheck, Loader2, RefreshCw, Lock, LockOpen, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription,
} from '@/components/ui/dialog'
import { toast } from '@/hooks/use-toast'
import { usePeriods, useClosePeriod, useReopenPeriod, type AccountingPeriod } from '@/lib/api/finance-period'

/**
 * Periodenabschluss (DOM-FIN-004.4) — Buchungsperioden abschließen/sperren:
 * Abschluss nur bei abschlussreifer Periode (keine offenen / Storno-inkonsistenten
 * Posten); Erzwingen mit Hinweis; Wiedereröffnung mit Pflicht-Grund.
 */

export default function PeriodenabschlussPage() {
  const periods = usePeriods()
  const close = useClosePeriod()
  const reopen = useReopenPeriod()
  const [reopenTarget, setReopenTarget] = useState<string | null>(null)
  const [grund, setGrund] = useState('')

  const errDetail = (err: unknown) => (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Unbekannter Fehler'

  const doClose = (p: AccountingPeriod, force: boolean) => {
    if (close.isPending) return
    close.mutate(
      { period: p.period, force },
      {
        onSuccess: (d) => toast({ title: `Periode ${p.period} abgeschlossen`, description: d.erzwungen ? 'Erzwungen trotz offener Posten' : undefined }),
        onError: (err) => toast({ title: 'Abschluss fehlgeschlagen', description: errDetail(err), variant: 'destructive' }),
      },
    )
  }

  const confirmReopen = () => {
    if (!reopenTarget || !grund.trim() || reopen.isPending) return
    reopen.mutate(
      { period: reopenTarget, grund },
      {
        onSuccess: () => { toast({ title: `Periode ${reopenTarget} wieder geöffnet` }); setReopenTarget(null); setGrund('') },
        onError: (err) => toast({ title: 'Wiedereröffnung fehlgeschlagen', description: errDetail(err), variant: 'destructive' }),
      },
    )
  }

  const closingPeriod = close.isPending ? close.variables?.period : null

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <CalendarCheck size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Periodenabschluss</h1>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void periods.refetch()} disabled={periods.isFetching}>
          {periods.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <Card>
        <CardHeader className="py-3"><CardTitle className="text-sm">Buchungsperioden</CardTitle></CardHeader>
        <CardContent className="p-0">
          {periods.isLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
          ) : (periods.data?.length ?? 0) === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">Keine Perioden.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Periode</th>
                    <th className="text-left font-medium px-3 py-1.5">Zeitraum</th>
                    <th className="text-left font-medium px-3 py-1.5">Status</th>
                    <th className="text-right font-medium px-3 py-1.5">Offen</th>
                    <th className="text-right font-medium px-3 py-1.5">Storno-inkons.</th>
                    <th className="text-left font-medium px-3 py-1.5">Reife</th>
                    <th className="text-right font-medium px-3 py-1.5">Aktion</th>
                  </tr>
                </thead>
                <tbody>
                  {(periods.data ?? []).map((p) => {
                    const pending = closingPeriod === p.period
                    return (
                      <tr key={p.period} className="border-b last:border-0">
                        <td className="px-3 py-1.5 font-medium">{p.period}</td>
                        <td className="px-3 py-1.5 text-muted-foreground">{p.start} – {p.end}</td>
                        <td className="px-3 py-1.5">
                          <Badge className={`text-[10px] ${p.status === 'closed' ? 'bg-red-100 text-red-800' : 'bg-emerald-100 text-emerald-800'}`}>
                            {p.status === 'closed' ? 'abgeschlossen' : 'offen'}
                          </Badge>
                        </td>
                        <td className="px-3 py-1.5 text-right tabular-nums">{p.offen_count}</td>
                        <td className="px-3 py-1.5 text-right tabular-nums">{p.storno_inkonsistent > 0 ? <span className="text-status-error">{p.storno_inkonsistent}</span> : 0}</td>
                        <td className="px-3 py-1.5">
                          {p.abschlussreif ? <span className="text-emerald-700">reif</span> : <span className="text-amber-700 inline-flex items-center gap-1"><AlertTriangle size={12} />offen</span>}
                        </td>
                        <td className="px-3 py-1.5 text-right">
                          {p.status === 'closed' ? (
                            <Button size="sm" variant="ghost" onClick={() => { setReopenTarget(p.period); setGrund('') }}>
                              <LockOpen size={13} className="mr-1" />Öffnen
                            </Button>
                          ) : p.abschlussreif ? (
                            <Button size="sm" variant="ghost" onClick={() => doClose(p, false)} disabled={pending}>
                              {pending ? <Loader2 size={13} className="animate-spin mr-1" /> : <Lock size={13} className="mr-1" />}Abschließen
                            </Button>
                          ) : (
                            <Button size="sm" variant="ghost" className="text-amber-700" onClick={() => doClose(p, true)} disabled={pending}>
                              {pending ? <Loader2 size={13} className="animate-spin mr-1" /> : <Lock size={13} className="mr-1" />}Erzwingen
                            </Button>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={!!reopenTarget} onOpenChange={(o) => { if (!o) { setReopenTarget(null); setGrund('') } }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Periode {reopenTarget} wieder öffnen</DialogTitle>
            <DialogDescription>Die Wiedereröffnung einer abgeschlossenen Periode wird mit Grund protokolliert.</DialogDescription>
          </DialogHeader>
          <Textarea value={grund} onChange={(e) => setGrund(e.target.value)} placeholder="Grund der Wiedereröffnung …" rows={3} />
          <DialogFooter>
            <Button variant="outline" onClick={() => { setReopenTarget(null); setGrund('') }} disabled={reopen.isPending}>Abbrechen</Button>
            <Button onClick={confirmReopen} disabled={!grund.trim() || reopen.isPending}>
              {reopen.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <LockOpen size={14} className="mr-1" />}
              Wieder öffnen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
