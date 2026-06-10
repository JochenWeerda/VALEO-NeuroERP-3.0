import { useState } from 'react'
import { Euro, Loader2, RefreshCw, AlertTriangle, Percent } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { NativeSelect } from '@/components/ui/native-select'
import { useOffenePosten } from '@/lib/api/finance-op'

/**
 * Offene-Posten-Cockpit (DOM-FIN-004) — OP-Aging mit Buckets (nicht fällig /
 * 1–30 / 31–60 / 60+), Mahnstufe und aktivem Skonto. Read-only.
 */

const BUCKET_LABEL: Record<string, string> = {
  nicht_faellig: 'Nicht fällig', '1-30': '1–30 Tage', '31-60': '31–60 Tage', '60+': '60+ Tage',
}

const eur = (n: number | null | undefined) =>
  n == null ? '—' : `${n.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`

export default function OffenePostenCockpitPage() {
  const [typ, setTyp] = useState('alle')
  const { data, isLoading, isFetching, refetch } = useOffenePosten(typ)
  const s = data?.summary

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Euro size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Offene Posten</h1>
        <NativeSelect value={typ} onChange={(e) => setTyp(e.target.value)} className="h-8 w-40">
          <option value="alle">Alle</option>
          <option value="debitor">Debitoren</option>
          <option value="kreditor">Kreditoren</option>
        </NativeSelect>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void refetch()} disabled={isFetching}>
          {isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      {/* Aging-Summen */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-5">
        <Card><CardContent className="p-3">
          <div className="text-xs text-muted-foreground">Summe offen</div>
          <div className="text-lg font-semibold tabular-nums">{eur(s?.summe_offen)}</div>
        </CardContent></Card>
        {(s?.buckets ?? []).map((b) => (
          <Card key={b.bucket} className={b.bucket === '60+' && b.summe > 0 ? 'border-red-300' : ''}>
            <CardContent className="p-3">
              <div className="text-xs text-muted-foreground">{BUCKET_LABEL[b.bucket] ?? b.bucket}</div>
              <div className="text-lg font-semibold tabular-nums">{eur(b.summe)}</div>
              <div className="text-xs text-muted-foreground">{b.anzahl} OP</div>
            </CardContent>
          </Card>
        ))}
      </div>
      {!!s?.summe_ueberfaellig && (
        <div className="text-sm text-red-700 inline-flex items-center gap-1">
          <AlertTriangle size={14} /> Überfällig gesamt: {eur(s.summe_ueberfaellig)}
        </div>
      )}

      <Card>
        <CardHeader className="py-3"><CardTitle className="text-sm">Offene Posten ({s?.anzahl ?? 0})</CardTitle></CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center py-12 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={18} /> Lädt …</div>
          ) : (data?.items.length ?? 0) === 0 ? (
            <div className="py-12 text-center text-sm text-muted-foreground">Keine offenen Posten.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-muted-foreground border-b">
                  <tr>
                    <th className="text-left font-medium px-3 py-1.5">Rechnung</th>
                    <th className="text-left font-medium px-3 py-1.5">Konto</th>
                    <th className="text-left font-medium px-3 py-1.5">Partner</th>
                    <th className="text-left font-medium px-3 py-1.5">Fällig</th>
                    <th className="text-right font-medium px-3 py-1.5">Offen</th>
                    <th className="text-left font-medium px-3 py-1.5">Aging</th>
                    <th className="text-left font-medium px-3 py-1.5">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {(data?.items ?? []).map((i) => (
                    <tr key={i.rechnungsnr} className={`border-b last:border-0 ${i.bucket === '60+' ? 'bg-red-50/60' : ''}`}>
                      <td className="px-3 py-1.5 font-mono text-xs">{i.rechnungsnr}</td>
                      <td className="px-3 py-1.5">{i.konto_typ}</td>
                      <td className="px-3 py-1.5">{i.partner || '—'}</td>
                      <td className="px-3 py-1.5">{i.faelligkeit ? new Date(i.faelligkeit).toLocaleDateString('de-DE') : '—'}</td>
                      <td className="px-3 py-1.5 text-right tabular-nums">{eur(i.offen)}</td>
                      <td className="px-3 py-1.5">
                        {i.ueberfaellig
                          ? <span className="text-red-700">{i.tage_ueberfaellig} T überfällig</span>
                          : <span className="text-muted-foreground">nicht fällig</span>}
                      </td>
                      <td className="px-3 py-1.5">
                        <span className="inline-flex items-center gap-1">
                          {i.mahnstufe > 0 && <Badge variant="destructive">Mahnstufe {i.mahnstufe}</Badge>}
                          {i.skonto_aktiv && <Badge variant="secondary" className="gap-1"><Percent size={10} />Skonto</Badge>}
                        </span>
                      </td>
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
