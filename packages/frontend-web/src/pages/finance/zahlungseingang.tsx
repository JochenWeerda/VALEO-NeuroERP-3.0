import { useMemo, useState } from 'react'
import { Banknote, Loader2, RefreshCw, Search } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from '@/hooks/use-toast'
import { useOffenePosten, type OpItem } from '@/lib/api/finance-op'
import { useClearings, useRecordPayment } from '@/lib/api/finance-clearing'

/**
 * Zahlungseingang / OP-Auszifferung (DOM-FIN-004.3) — offenen Debitoren-Posten
 * (teil-)ausziffern: Zahlung + optional Skonto reduziert den offenen Betrag.
 */

function eur(v: number | null | undefined) {
  return v == null ? '—' : v.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })
}

function PaymentForm({ op }: { op: OpItem }) {
  const record = useRecordPayment()
  const [betrag, setBetrag] = useState('')
  const [skonto, setSkonto] = useState('')
  const offen = op.offen ?? 0
  const betragNum = Number(betrag)
  const skontoNum = skonto === '' ? 0 : Number(skonto)
  const valid = betragNum > 0 && betragNum + skontoNum <= offen + 0.01

  const submit = () => {
    if (!valid || record.isPending || !op.rechnungsnr) return
    record.mutate(
      { rechnungsnr: op.rechnungsnr, betrag: betragNum, skontoBetrag: skontoNum || undefined },
      {
        onSuccess: (d) => {
          toast({ title: d.voll_ausgeziffert ? 'OP vollständig ausgeziffert' : 'Teilzahlung verbucht', description: `Offen: ${eur(d.neu_offen)}` })
          setBetrag(''); setSkonto('')
        },
        onError: (err: unknown) => toast({
          title: 'Auszifferung fehlgeschlagen',
          description: (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Unbekannter Fehler',
          variant: 'destructive',
        }),
      },
    )
  }

  return (
    <Card>
      <CardHeader className="py-3"><CardTitle className="text-sm">Zahlungseingang · {op.rechnungsnr} (offen {eur(offen)})</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
          <label className="text-xs text-muted-foreground space-y-1">
            <span>Zahlungsbetrag</span>
            <Input type="number" value={betrag} onChange={(e) => setBetrag(e.target.value)} placeholder="0,00" className="h-8" />
          </label>
          <label className="text-xs text-muted-foreground space-y-1">
            <span>Skonto {op.skonto_aktiv ? `(aktiv ${op.skonto_prozent}%)` : ''}</span>
            <Input type="number" value={skonto} onChange={(e) => setSkonto(e.target.value)} placeholder="0,00" className="h-8" />
          </label>
          <div className="flex items-end">
            <Button size="sm" className="w-full" onClick={submit} disabled={!valid || record.isPending}>
              {record.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <Banknote size={14} className="mr-1" />}
              Ausziffern
            </Button>
          </div>
        </div>
        {betragNum + skontoNum > offen + 0.01 && <div className="text-xs text-red-600">Ausgleich übersteigt offenen Betrag.</div>}
      </CardContent>
    </Card>
  )
}

function ClearingHistory({ rechnungsnr }: { rechnungsnr: string }) {
  const clearings = useClearings(rechnungsnr)
  if ((clearings.data?.length ?? 0) === 0) return null
  return (
    <Card>
      <CardHeader className="py-3"><CardTitle className="text-sm">Auszifferungen</CardTitle></CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-xs text-muted-foreground border-b">
              <tr>
                <th className="text-left font-medium px-3 py-1.5">Datum</th>
                <th className="text-right font-medium px-3 py-1.5">Betrag</th>
                <th className="text-right font-medium px-3 py-1.5">Skonto</th>
                <th className="text-right font-medium px-3 py-1.5">Ausgleich</th>
                <th className="text-left font-medium px-3 py-1.5">Status</th>
              </tr>
            </thead>
            <tbody>
              {(clearings.data ?? []).map((c, i) => (
                <tr key={i} className="border-b last:border-0">
                  <td className="px-3 py-1.5">{c.datum ? new Date(c.datum).toLocaleDateString('de-DE') : '—'}</td>
                  <td className="px-3 py-1.5 text-right tabular-nums">{eur(c.betrag)}</td>
                  <td className="px-3 py-1.5 text-right tabular-nums">{eur(c.skonto)}</td>
                  <td className="px-3 py-1.5 text-right tabular-nums font-medium">{eur(c.ausgleich)}</td>
                  <td className="px-3 py-1.5"><Badge variant="secondary" className="text-[10px]">{c.status}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}

export default function ZahlungseingangPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const op = useOffenePosten('debitor')

  const items = useMemo(
    () => (op.data?.items ?? []).filter((i) => (i.offen ?? 0) > 0 && (!filter || (i.rechnungsnr ?? '').toLowerCase().includes(filter.toLowerCase()))),
    [op.data, filter],
  )
  const current = items.find((i) => i.rechnungsnr === selected) ?? null

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Banknote size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Zahlungseingang / Auszifferung</h1>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void op.refetch()} disabled={op.isFetching}>
          {op.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[22rem_1fr]">
        <Card className="h-fit">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Offene Debitoren-Posten</CardTitle>
            <div className="relative">
              <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Nr. suchen…" className="h-8 pl-7" />
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[70vh] overflow-y-auto">
            {op.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
            ) : items.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">Keine offenen Posten.</div>
            ) : (
              <div className="divide-y">
                {items.map((i) => (
                  <button key={i.rechnungsnr} onClick={() => setSelected(i.rechnungsnr)}
                    className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${selected === i.rechnungsnr ? 'bg-muted' : ''}`}>
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-sm truncate">{i.rechnungsnr}</span>
                      <span className="text-xs tabular-nums">{eur(i.offen)}</span>
                    </div>
                    <div className="text-xs text-muted-foreground">{i.partner ?? '—'}{i.ueberfaellig ? ` · ${i.tage_ueberfaellig} Tage überfällig` : ''}</div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-3">
          {!current ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Offenen Posten wählen, um einen Zahlungseingang zu erfassen.</CardContent></Card>
          ) : (
            <>
              <PaymentForm op={current} />
              {current.rechnungsnr && <ClearingHistory rechnungsnr={current.rechnungsnr} />}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
