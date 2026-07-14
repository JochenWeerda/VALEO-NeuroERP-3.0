import { useState } from 'react'
import { FileSignature, Loader2, RefreshCw, Search, AlertTriangle, Info, CheckCircle2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { useContracts, useContractDetail, type ContractRow } from '@/lib/api/contract-fulfillment'

/**
 * Kontrakt-Erfüllungsstand (DOM-CON-004) — kontrahiert vs. abgerufen je Kontrakt:
 * Erfüllungsgrad, offene Menge, Status, überfällige Kontrakte, Preis-/Fixierungsinfo.
 */

const STATUS_STYLE: Record<string, string> = {
  erfuellt: 'text-emerald-700', teilerfuellt: 'text-amber-700', uebererfuellt: 'text-red-700', offen: 'text-muted-foreground',
}

function Bar({ pct, over }: { pct: number; over: boolean }) {
  const w = Math.min(100, Math.max(0, pct))
  return (
    <div className="h-2 w-full rounded bg-muted overflow-hidden">
      <div className={`h-full ${over ? 'bg-red-500' : pct >= 99.5 ? 'bg-emerald-500' : 'bg-amber-500'}`} style={{ width: `${w}%` }} />
    </div>
  )
}

function Row({ c, active, onClick }: { c: ContractRow; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${active ? 'bg-muted' : ''}`}>
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium text-sm truncate">{c.contract_no}</span>
        <Badge variant="outline" className="text-[10px]">{c.typ}</Badge>
      </div>
      <div className="mt-1"><Bar pct={c.erfuellung_pct} over={c.erfuellung_status === 'uebererfuellt'} /></div>
      <div className="text-xs text-muted-foreground flex justify-between mt-0.5">
        <span>{c.erfuellung_pct}% · {c.erfuellung_status}</span>
        {c.ueberfaellig && <span className="text-status-error">überfällig</span>}
      </div>
    </button>
  )
}

export default function KontraktErfuellungPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [typ, setTyp] = useState('alle')
  const [filter, setFilter] = useState('')
  const listQuery = useContracts(typ)
  const detail = useContractDetail(selected)

  const contracts = (listQuery.data ?? []).filter((c) => !filter || c.contract_no.toLowerCase().includes(filter.toLowerCase()))

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <FileSignature size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Kontrakt-Erfüllung</h1>
        <NativeSelect value={typ} onChange={(e) => setTyp(e.target.value)} className="h-8 w-32">
          <option value="alle">Alle</option>
          <option value="EINKAUF">Einkauf</option>
          <option value="VERKAUF">Verkauf</option>
        </NativeSelect>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void listQuery.refetch()} disabled={listQuery.isFetching}>
          {listQuery.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[22rem_1fr]">
        <Card className="h-fit">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Kontrakte</CardTitle>
            <div className="relative">
              <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Nr. suchen…" className="h-8 pl-7" />
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[70vh] overflow-y-auto">
            {listQuery.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
            ) : contracts.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">Keine Kontrakte.</div>
            ) : (
              <div className="divide-y">
                {contracts.map((c) => <Row key={c.contract_no} c={c} active={selected === c.contract_no} onClick={() => setSelected(c.contract_no)} />)}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-3">
          {!selected ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Kontrakt wählen, um den Erfüllungsstand zu sehen.</CardContent></Card>
          ) : detail.isLoading ? (
            <Card><CardContent className="py-16 text-center text-muted-foreground"><Loader2 className="animate-spin mx-auto mb-2" size={18} /> Lädt …</CardContent></Card>
          ) : !detail.data?.found ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">{detail.data?.detail ?? 'Nicht gefunden.'}</CardContent></Card>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">{detail.data.contract_no}</span>
                <Badge variant="outline">{detail.data.contract_type}</Badge>
                <Badge variant="outline" className="capitalize">{detail.data.summary?.status}</Badge>
                {detail.data.summary?.status === 'erfuellt'
                  ? <Badge className="bg-emerald-600"><CheckCircle2 className="mr-1 h-3 w-3" />erfüllt</Badge>
                  : <Badge variant="secondary">{detail.data.summary?.erfuellung_pct}% erfüllt</Badge>}
                {detail.data.ueberfaellig && <Badge variant="destructive"><AlertTriangle className="mr-1 h-3 w-3" />überfällig</Badge>}
              </div>

              <Card>
                <CardContent className="p-3 grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
                  <div><div className="text-xs text-muted-foreground">Kontrahiert</div><div className="font-semibold tabular-nums">{detail.data.summary?.menge_kontrakt} {detail.data.einheit}</div></div>
                  <div><div className="text-xs text-muted-foreground">Abgerufen</div><div className="font-semibold tabular-nums">{detail.data.summary?.abgerufen} {detail.data.einheit}</div></div>
                  <div><div className="text-xs text-muted-foreground">Offen</div><div className="font-semibold tabular-nums">{detail.data.summary?.offen} {detail.data.einheit}</div></div>
                  <div><div className="text-xs text-muted-foreground">Preismodell</div><div className="font-semibold">{detail.data.pricing?.modell || '—'}</div></div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="py-3"><CardTitle className="text-sm">Positionen</CardTitle></CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="text-xs text-muted-foreground border-b">
                        <tr>
                          <th className="text-left font-medium px-3 py-1.5">Pos</th>
                          <th className="text-left font-medium px-3 py-1.5">Artikel</th>
                          <th className="text-right font-medium px-3 py-1.5">Kontrahiert</th>
                          <th className="text-right font-medium px-3 py-1.5">Abgerufen</th>
                          <th className="text-right font-medium px-3 py-1.5">Offen</th>
                          <th className="text-left font-medium px-3 py-1.5">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(detail.data.positionen ?? []).map((p) => (
                          <tr key={p.position_no} className="border-b last:border-0">
                            <td className="px-3 py-1.5">{p.position_no}</td>
                            <td className="px-3 py-1.5">{p.artikel}{p.is_matif && <Badge variant="outline" className="ml-1 text-[10px]">MATIF</Badge>}</td>
                            <td className="px-3 py-1.5 text-right tabular-nums">{p.menge_kontrakt}</td>
                            <td className="px-3 py-1.5 text-right tabular-nums">{p.abgerufen}</td>
                            <td className="px-3 py-1.5 text-right tabular-nums">{p.offen}</td>
                            <td className={`px-3 py-1.5 font-medium ${STATUS_STYLE[p.status] ?? ''}`}>{p.status} ({p.erfuellung_pct}%)</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {!!detail.data.luecken?.length && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Hinweise & Lücken</CardTitle></CardHeader>
                  <CardContent className="space-y-1.5">
                    {detail.data.luecken.map((l, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        {l.schwere === 'warnung' ? <AlertTriangle size={15} className="mt-0.5 text-status-warning shrink-0" /> : <Info size={15} className="mt-0.5 text-sky-600 shrink-0" />}
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
