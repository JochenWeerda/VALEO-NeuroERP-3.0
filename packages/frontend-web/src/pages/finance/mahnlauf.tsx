import { MailWarning, Loader2, RefreshCw, Send } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { toast } from '@/hooks/use-toast'
import { useDunningCandidates, useDunningNotices, useRunDunning } from '@/lib/api/finance-dunning'

/**
 * Mahnlauf (DOM-FIN-004.2) — überfällige Debitoren-OP mahnen: nächste Mahnstufe,
 * Gebühr/Zinsen/Gesamt + Zahlungsfrist; Mahnlauf erzeugt Mahnungen und eskaliert.
 */

function eur(v: number | null | undefined) {
  return v == null ? '—' : v.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
}

export default function MahnlaufPage() {
  const candidates = useDunningCandidates()
  const notices = useDunningNotices()
  const run = useRunDunning()

  const doRun = () => {
    if (run.isPending) return
    run.mutate(
      {},
      {
        onSuccess: (d) => toast({ title: `Mahnlauf abgeschlossen`, description: `${d.erzeugt} Mahnung(en) erzeugt` }),
        onError: (err: unknown) => toast({
          title: 'Mahnlauf fehlgeschlagen',
          description: (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Unbekannter Fehler',
          variant: 'destructive',
        }),
      },
    )
  }

  const cand = candidates.data ?? []

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <MailWarning size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Mahnlauf</h1>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => { void candidates.refetch(); void notices.refetch() }} disabled={candidates.isFetching}>
          {candidates.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
        <Button size="sm" onClick={doRun} disabled={run.isPending || cand.length === 0}>
          {run.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <Send size={14} className="mr-1" />}
          Mahnlauf ausführen ({cand.length})
        </Button>
      </div>

      <Card>
        <CardHeader className="py-3"><CardTitle className="text-sm">Mahnkandidaten (überfällige Debitoren-OP)</CardTitle></CardHeader>
        <CardContent className="p-0">
          {candidates.isLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
          ) : cand.length === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">Keine überfälligen Debitoren-OP.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Rechnung</th>
                    <th className="text-left font-medium px-3 py-1.5">Partner</th>
                    <th className="text-right font-medium px-3 py-1.5">Überfällig</th>
                    <th className="text-right font-medium px-3 py-1.5">Offen</th>
                    <th className="text-center font-medium px-3 py-1.5">Stufe</th>
                    <th className="text-right font-medium px-3 py-1.5">Gebühr</th>
                    <th className="text-right font-medium px-3 py-1.5">Zinsen</th>
                    <th className="text-right font-medium px-3 py-1.5">Gesamt</th>
                  </tr>
                </thead>
                <tbody>
                  {cand.map((c) => (
                    <tr key={c.op_id} className="border-b last:border-0">
                      <td className="px-3 py-1.5 font-medium">{c.rechnungsnr}</td>
                      <td className="px-3 py-1.5">{c.partner ?? '—'}</td>
                      <td className="px-3 py-1.5 text-right text-red-600">{c.tage_ueberfaellig} Tage</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(c.offen)}</td>
                      <td className="px-3 py-1.5 text-center"><Badge variant="outline" className="text-[10px]">{c.aktuelle_stufe} → {c.naechste_stufe}</Badge></td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(c.dunning_fee)}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(c.interest)}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums font-medium">{eur(c.total_amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="py-3"><CardTitle className="text-sm">Erzeugte Mahnungen</CardTitle></CardHeader>
        <CardContent className="p-0">
          {notices.isLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
          ) : (notices.data?.length ?? 0) === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">Noch keine Mahnungen erzeugt.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Rechnung</th>
                    <th className="text-left font-medium px-3 py-1.5">Partner</th>
                    <th className="text-center font-medium px-3 py-1.5">Stufe</th>
                    <th className="text-right font-medium px-3 py-1.5">Gesamt</th>
                    <th className="text-left font-medium px-3 py-1.5">Frist</th>
                    <th className="text-left font-medium px-3 py-1.5">Datum</th>
                    <th className="text-left font-medium px-3 py-1.5">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(notices.data ?? []).map((n, i) => (
                    <tr key={i} className="border-b last:border-0">
                      <td className="px-3 py-1.5">{n.rechnungsnr ?? '—'}</td>
                      <td className="px-3 py-1.5">{n.partner ?? '—'}</td>
                      <td className="px-3 py-1.5 text-center"><Badge variant="secondary" className="text-[10px]">{n.stufe}</Badge></td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(n.gesamt)}</td>
                      <td className="px-3 py-1.5">{n.frist ? new Date(n.frist).toLocaleDateString('de-DE') : '—'}</td>
                      <td className="px-3 py-1.5">{n.datum ? new Date(n.datum).toLocaleDateString('de-DE') : '—'}</td>
                      <td className="px-3 py-1.5">{n.status ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
