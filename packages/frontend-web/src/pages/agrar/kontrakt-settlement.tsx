import { useState } from 'react'
import { Receipt, Loader2, RefreshCw, Search, Ban, FileCheck2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription,
} from '@/components/ui/dialog'
import { toast } from '@/hooks/use-toast'
import { useContracts, type ContractRow } from '@/lib/api/contract-fulfillment'
import {
  useSettlementStatus, useHandover, useStornoMovement, useStornoFixing,
} from '@/lib/api/contract-settlement'

/**
 * Kontrakt-Settlement & Storno (DOM-CON-004.4) — Abruf-Bewegungen an die Abrechnung
 * übergeben; Bewegungen/Fixierungen stornieren (frei werdende Mengen). Fail-closed:
 * abgerechnete Bewegungen sind storno-gesperrt.
 */

const STATUS_BADGE: Record<string, string> = {
  offen: 'bg-amber-100 text-amber-800', abgerechnet: 'bg-emerald-100 text-emerald-800',
  storniert: 'bg-red-100 text-red-800', aktiv: 'bg-sky-100 text-sky-800',
}

type StornoTarget = { kind: 'movement' | 'fixing'; id: string; label: string } | null

function Row({ c, active, onClick }: { c: ContractRow; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick} className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${active ? 'bg-muted' : ''}`}>
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium text-sm truncate">{c.contract_no}</span>
        <Badge variant="outline" className="text-[10px]">{c.typ}</Badge>
      </div>
      <div className="text-xs text-muted-foreground mt-0.5">{c.party_id ?? '—'} · {c.menge_kontrakt} {c.einheit}</div>
    </button>
  )
}

export default function KontraktSettlementPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const [storno, setStorno] = useState<StornoTarget>(null)
  const [grund, setGrund] = useState('')

  const listQuery = useContracts('alle')
  const status = useSettlementStatus(selected)
  const handover = useHandover()
  const stornoMovement = useStornoMovement(selected)
  const stornoFixing = useStornoFixing(selected)

  const contracts = (listQuery.data ?? []).filter((c) => !filter || c.contract_no.toLowerCase().includes(filter.toLowerCase()))
  const data = status.data
  const einheit = data?.einheit ?? ''

  const doHandover = (movementId?: string) => {
    if (!selected || handover.isPending) return
    handover.mutate(
      { kontrakt: selected, movementId },
      {
        onSuccess: (d) => toast({ title: `${d.uebergeben} Bewegung(en) abgerechnet` }),
        onError: (err: unknown) => toast({ title: 'Übergabe fehlgeschlagen', description: errDetail(err), variant: 'destructive' }),
      },
    )
  }

  const confirmStorno = () => {
    if (!storno || !grund.trim()) return
    const onErr = (err: unknown) => toast({ title: 'Storno fehlgeschlagen', description: errDetail(err), variant: 'destructive' })
    const onOk = (d: { frei_menge: number }) => { toast({ title: 'Storniert', description: `Frei: ${d.frei_menge} ${einheit}` }); setStorno(null); setGrund('') }
    if (storno.kind === 'movement') stornoMovement.mutate({ movementId: storno.id, grund }, { onSuccess: onOk, onError: onErr })
    else stornoFixing.mutate({ fixingId: storno.id, grund }, { onSuccess: onOk, onError: onErr })
  }

  const stornoPending = stornoMovement.isPending || stornoFixing.isPending

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Receipt size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Kontrakt-Settlement</h1>
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
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Kontrakt wählen, um Bewegungen abzurechnen oder zu stornieren.</CardContent></Card>
          ) : status.isLoading ? (
            <Card><CardContent className="py-16 text-center text-muted-foreground"><Loader2 className="animate-spin mx-auto mb-2" size={18} /> Lädt …</CardContent></Card>
          ) : !data?.found ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">{data?.detail ?? 'Nicht gefunden.'}</CardContent></Card>
          ) : (
            <>
              <Card>
                <CardContent className="p-3 grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
                  <div><div className="text-xs text-muted-foreground">Abgerufen</div><div className="font-semibold tabular-nums">{data.summary?.abgerufen} {einheit}</div></div>
                  <div><div className="text-xs text-muted-foreground">Abgerechnet</div><div className="font-semibold tabular-nums text-emerald-700">{data.summary?.abgerechnet} {einheit}</div></div>
                  <div><div className="text-xs text-muted-foreground">Offen (Abruf)</div><div className="font-semibold tabular-nums text-amber-700">{data.summary?.offen_abruf} {einheit}</div></div>
                  <div><div className="text-xs text-muted-foreground">Fixiert aktiv</div><div className="font-semibold tabular-nums">{data.summary?.fixiert_aktiv} {einheit}</div></div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="py-3 flex-row items-center justify-between">
                  <CardTitle className="text-sm">Abruf-Bewegungen</CardTitle>
                  {(data.summary?.offen_abruf ?? 0) > 0 && (
                    <Button size="sm" variant="outline" onClick={() => doHandover()} disabled={handover.isPending}>
                      {handover.isPending ? <Loader2 size={13} className="animate-spin mr-1" /> : <FileCheck2 size={13} className="mr-1" />}
                      Alle offenen abrechnen
                    </Button>
                  )}
                </CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="text-xs text-muted-foreground border-b">
                        <tr>
                          <th className="text-right font-medium px-3 py-1.5">Menge</th>
                          <th className="text-left font-medium px-3 py-1.5">Datum</th>
                          <th className="text-left font-medium px-3 py-1.5">Status</th>
                          <th className="text-left font-medium px-3 py-1.5">Beleg/Grund</th>
                          <th className="text-right font-medium px-3 py-1.5">Aktion</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(data.bewegungen ?? []).map((m) => (
                          <tr key={m.movement_id} className="border-b last:border-0">
                            <td className="px-3 py-1.5 text-right tabular-nums">{m.menge}</td>
                            <td className="px-3 py-1.5">{m.datum ? new Date(m.datum).toLocaleDateString('de-DE') : '—'}</td>
                            <td className="px-3 py-1.5"><Badge className={`text-[10px] ${STATUS_BADGE[m.status] ?? ''}`}>{m.status}</Badge></td>
                            <td className="px-3 py-1.5 text-muted-foreground">{m.invoice_no ?? m.storno_grund ?? '—'}</td>
                            <td className="px-3 py-1.5 text-right">
                              {m.status === 'offen' && (
                                <span className="inline-flex gap-1">
                                  <Button size="sm" variant="ghost" onClick={() => doHandover(m.movement_id)} disabled={handover.isPending}><FileCheck2 size={13} /></Button>
                                  <Button size="sm" variant="ghost" onClick={() => { setStorno({ kind: 'movement', id: m.movement_id, label: `Bewegung ${m.menge} ${einheit}` }); setGrund('') }}><Ban size={13} className="text-status-error" /></Button>
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                        {(data.bewegungen?.length ?? 0) === 0 && (
                          <tr><td colSpan={5} className="px-3 py-6 text-center text-muted-foreground">Keine Bewegungen.</td></tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {(data.fixierungen?.length ?? 0) > 0 && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Fixierungen</CardTitle></CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="text-xs text-muted-foreground border-b">
                          <tr>
                            <th className="text-left font-medium px-3 py-1.5">#</th>
                            <th className="text-right font-medium px-3 py-1.5">Menge</th>
                            <th className="text-right font-medium px-3 py-1.5">Effektiv</th>
                            <th className="text-left font-medium px-3 py-1.5">Status</th>
                            <th className="text-right font-medium px-3 py-1.5">Aktion</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(data.fixierungen ?? []).map((f) => (
                            <tr key={f.fixing_id} className="border-b last:border-0">
                              <td className="px-3 py-1.5">{f.fixing_no}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums">{f.menge}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums">{f.effektiv_preis}</td>
                              <td className="px-3 py-1.5"><Badge className={`text-[10px] ${STATUS_BADGE[f.status] ?? ''}`}>{f.status}</Badge></td>
                              <td className="px-3 py-1.5 text-right">
                                {f.status === 'aktiv' && (
                                  <Button size="sm" variant="ghost" onClick={() => { setStorno({ kind: 'fixing', id: f.fixing_id, label: `Fixierung #${f.fixing_no} (${f.menge} ${einheit})` }); setGrund('') }}><Ban size={13} className="text-status-error" /></Button>
                                )}
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

      <Dialog open={!!storno} onOpenChange={(o) => { if (!o) { setStorno(null); setGrund('') } }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Storno — {storno?.label}</DialogTitle>
            <DialogDescription>Storno-Grund ist erforderlich und wird revisionssicher protokolliert.</DialogDescription>
          </DialogHeader>
          <Textarea value={grund} onChange={(e) => setGrund(e.target.value)} placeholder="Grund des Stornos …" rows={3} />
          <DialogFooter>
            <Button variant="outline" onClick={() => { setStorno(null); setGrund('') }} disabled={stornoPending}>Abbrechen</Button>
            <Button variant="destructive" onClick={confirmStorno} disabled={!grund.trim() || stornoPending}>
              {stornoPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <Ban size={14} className="mr-1" />}
              Stornieren
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function errDetail(err: unknown): string {
  return (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Unbekannter Fehler'
}
