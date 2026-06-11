import { Boxes, Loader2, RefreshCw, AlertTriangle, BellRing } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { toast } from '@/hooks/use-toast'
import {
  useEngagement,
  useDunningCandidates,
  useCreateReminder,
  type DunningCandidate,
} from '@/lib/api/contract-engagement'

/**
 * Kontrakt-Engagement & Kontraktmahnung (DOM-CON-004.3) — offene Kontraktmenge je
 * Artikel (Netto-Position Einkauf−Verkauf) und je Partei + überfällige Kontrakte mahnen.
 */

function Num({ v, unit }: { v: number | null | undefined; unit?: string }) {
  return <span className="tabular-nums">{v ?? 0}{unit ? ` ${unit}` : ''}</span>
}

function DunningRow({ c, onMahnen, pending }: { c: DunningCandidate; onMahnen: () => void; pending: boolean }) {
  return (
    <tr className="border-b last:border-0">
      <td className="px-3 py-1.5 font-medium">{c.contract_no}</td>
      <td className="px-3 py-1.5"><Badge variant="outline" className="text-[10px]">{c.typ}</Badge></td>
      <td className="px-3 py-1.5">{c.party_id ?? '—'}</td>
      <td className="px-3 py-1.5 text-right"><Num v={c.offen} unit={c.einheit ?? ''} /></td>
      <td className="px-3 py-1.5 text-right text-red-600">{c.tage_ueberfaellig} Tage</td>
      <td className="px-3 py-1.5 text-center">{c.letzte_mahnstufe ?? '—'}</td>
      <td className="px-3 py-1.5 text-right">
        <Button size="sm" variant="outline" onClick={onMahnen} disabled={pending}>
          {pending ? <Loader2 size={13} className="animate-spin mr-1" /> : <BellRing size={13} className="mr-1" />}
          Mahnen (St. {c.naechste_mahnstufe})
        </Button>
      </td>
    </tr>
  )
}

export default function KontraktEngagementPage() {
  const engagement = useEngagement()
  const candidates = useDunningCandidates()
  const createReminder = useCreateReminder()

  const mahnen = (c: DunningCandidate) => {
    if (createReminder.isPending) return
    createReminder.mutate(
      { kontrakt: c.contract_no },
      {
        onSuccess: (d) => toast({ title: `Mahnung Stufe ${d.mahnstufe} erfasst`, description: `${c.contract_no} · offen ${d.offen} ${c.einheit ?? ''}` }),
        onError: (err: unknown) => {
          const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
          toast({ title: 'Mahnung fehlgeschlagen', description: detail ?? 'Unbekannter Fehler', variant: 'destructive' })
        },
      },
    )
  }

  const s = engagement.data?.summary

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Boxes size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Kontrakt-Engagement</h1>
        <Button variant="outline" size="sm" className="ml-auto"
          onClick={() => { void engagement.refetch(); void candidates.refetch() }}
          disabled={engagement.isFetching || candidates.isFetching}>
          {engagement.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <Card>
        <CardContent className="p-3 grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
          <div><div className="text-xs text-muted-foreground">Einkauf offen</div><div className="font-semibold tabular-nums text-emerald-700"><Num v={s?.einkauf_offen} /></div></div>
          <div><div className="text-xs text-muted-foreground">Verkauf offen</div><div className="font-semibold tabular-nums text-sky-700"><Num v={s?.verkauf_offen} /></div></div>
          <div><div className="text-xs text-muted-foreground">Netto-Engagement</div><div className={`font-semibold tabular-nums ${(s?.netto ?? 0) >= 0 ? 'text-emerald-700' : 'text-red-700'}`}><Num v={s?.netto} /></div></div>
          <div><div className="text-xs text-muted-foreground">Artikel / Parteien</div><div className="font-semibold tabular-nums">{s?.artikel_anzahl ?? 0} / {s?.parteien_anzahl ?? 0}</div></div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader className="py-3"><CardTitle className="text-sm">Engagement je Artikel</CardTitle></CardHeader>
          <CardContent className="p-0">
            {engagement.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-xs text-muted-foreground border-b">
                    <tr>
                      <th className="text-left font-medium px-3 py-1.5">Artikel</th>
                      <th className="text-right font-medium px-3 py-1.5">EK offen</th>
                      <th className="text-right font-medium px-3 py-1.5">VK offen</th>
                      <th className="text-right font-medium px-3 py-1.5">Netto</th>
                      <th className="text-right font-medium px-3 py-1.5">Kontrakte</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(engagement.data?.by_article ?? []).map((a) => (
                      <tr key={a.artikel} className="border-b last:border-0">
                        <td className="px-3 py-1.5">{a.artikel}</td>
                        <td className="px-3 py-1.5 text-right tabular-nums">{a.einkauf_offen}</td>
                        <td className="px-3 py-1.5 text-right tabular-nums">{a.verkauf_offen}</td>
                        <td className={`px-3 py-1.5 text-right tabular-nums font-medium ${a.netto >= 0 ? 'text-emerald-700' : 'text-red-700'}`}>{a.netto}</td>
                        <td className="px-3 py-1.5 text-right tabular-nums">{a.kontrakte}</td>
                      </tr>
                    ))}
                    {!engagement.isLoading && (engagement.data?.by_article?.length ?? 0) === 0 && (
                      <tr><td colSpan={5} className="px-3 py-6 text-center text-muted-foreground">Kein offenes Engagement.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="py-3"><CardTitle className="text-sm">Engagement je Partei</CardTitle></CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Partei</th>
                    <th className="text-right font-medium px-3 py-1.5">Offen gesamt</th>
                    <th className="text-right font-medium px-3 py-1.5">Kontrakte</th>
                  </tr>
                </thead>
                <tbody>
                  {(engagement.data?.by_party ?? []).map((p) => (
                    <tr key={p.party_id} className="border-b last:border-0">
                      <td className="px-3 py-1.5">{p.party_id}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{p.offen}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{p.kontrakte}</td>
                    </tr>
                  ))}
                  {!engagement.isLoading && (engagement.data?.by_party?.length ?? 0) === 0 && (
                    <tr><td colSpan={3} className="px-3 py-6 text-center text-muted-foreground">Keine offenen Parteien.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="py-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <AlertTriangle size={15} className="text-amber-600" /> Kontraktmahnung — überfällig & untererfüllt
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {candidates.isLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
          ) : (candidates.data?.length ?? 0) === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">Keine überfälligen Kontrakte.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Kontrakt</th>
                    <th className="text-left font-medium px-3 py-1.5">Typ</th>
                    <th className="text-left font-medium px-3 py-1.5">Partei</th>
                    <th className="text-right font-medium px-3 py-1.5">Offen</th>
                    <th className="text-right font-medium px-3 py-1.5">Überfällig</th>
                    <th className="text-center font-medium px-3 py-1.5">Letzte St.</th>
                    <th className="text-right font-medium px-3 py-1.5">Aktion</th>
                  </tr>
                </thead>
                <tbody>
                  {(candidates.data ?? []).map((c) => (
                    <DunningRow
                      key={c.contract_no}
                      c={c}
                      onMahnen={() => mahnen(c)}
                      pending={createReminder.isPending && createReminder.variables?.kontrakt === c.contract_no}
                    />
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
