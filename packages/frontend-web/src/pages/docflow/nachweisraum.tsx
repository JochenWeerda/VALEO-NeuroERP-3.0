import { useState } from 'react'
import {
  ShieldCheck, Loader2, RefreshCw, Search, FileText, Link2, Euro, AlertTriangle, Info, CheckCircle2, Fingerprint,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useEvidenceDocuments, useEvidenceDetail, type EvidenceDoc } from '@/lib/api/docflow-evidence'

/**
 * Dokument-Nachweisraum (DOM-DOC-004) — GoBD-Sicht je Dokument: revisionssichere
 * Artefakte (SHA-256), Vorgangskette, Buchungsbezug, Lücken. Read-only.
 */

function DocDots({ d }: { d: EvidenceDoc }) {
  const dot = (ok: boolean, label: string) => (
    <span title={label} className={`inline-block h-2 w-2 rounded-full ${ok ? 'bg-emerald-500' : 'bg-muted-foreground/30'}`} />
  )
  return (
    <span className="inline-flex items-center gap-1">
      {dot(d.artefakte > 0, 'Artefakt')}{dot(d.revisionssicher, 'revisionssicher (Hash)')}{dot(d.gebucht, 'gebucht')}
    </span>
  )
}

export default function NachweisraumPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const docsQuery = useEvidenceDocuments(50)
  const detail = useEvidenceDetail(selected)

  const docs = (docsQuery.data ?? []).filter((d) => !filter || d.doc_number.toLowerCase().includes(filter.toLowerCase()))

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <ShieldCheck size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Nachweisraum</h1>
        <span className="text-sm text-muted-foreground">GoBD: Artefakte · Vorgangskette · Buchungen</span>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void docsQuery.refetch()} disabled={docsQuery.isFetching}>
          {docsQuery.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[22rem_1fr]">
        <Card className="h-fit">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Dokumente</CardTitle>
            <div className="relative">
              <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Nr. suchen…" className="h-8 pl-7" />
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[70vh] overflow-y-auto">
            {docsQuery.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
            ) : docs.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">Keine Dokumente.</div>
            ) : (
              <div className="divide-y">
                {docs.map((d) => (
                  <button key={d.doc_number} onClick={() => setSelected(d.doc_number)}
                    className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${selected === d.doc_number ? 'bg-muted' : ''}`}>
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-sm truncate">{d.doc_number}</span>
                      <DocDots d={d} />
                    </div>
                    <div className="text-xs text-muted-foreground">{d.doc_type} · {d.status}</div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-3">
          {!selected ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Dokument wählen, um die Nachweiskette zu sehen.</CardContent></Card>
          ) : detail.isLoading ? (
            <Card><CardContent className="py-16 text-center text-muted-foreground"><Loader2 className="animate-spin mx-auto mb-2" size={18} /> Lädt …</CardContent></Card>
          ) : !detail.data?.found ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">{detail.data?.detail ?? 'Nicht gefunden.'}</CardContent></Card>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">{detail.data.doc_number}</span>
                <Badge variant="outline">{detail.data.doc_type}</Badge>
                <Badge variant="outline">{detail.data.status}</Badge>
                {detail.data.summary?.revisionssicher
                  ? <Badge className="bg-emerald-600"><CheckCircle2 className="mr-1 h-3 w-3" />revisionssicher</Badge>
                  : <Badge variant="destructive"><AlertTriangle className="mr-1 h-3 w-3" />nicht revisionssicher</Badge>}
                {detail.data.summary?.gebucht && <Badge variant="secondary">gebucht</Badge>}
              </div>

              <Card>
                <CardHeader className="py-3"><CardTitle className="text-sm flex items-center gap-2"><FileText size={15} />Artefakte ({detail.data.artefakte?.length ?? 0})</CardTitle></CardHeader>
                <CardContent className="space-y-1.5">
                  {(detail.data.artefakte ?? []).length === 0 ? (
                    <div className="text-sm text-muted-foreground">Keine Artefakte.</div>
                  ) : (detail.data.artefakte ?? []).map((a) => (
                    <div key={a.id} className="flex items-center gap-2 text-sm border rounded p-2">
                      <Badge variant="outline">{a.typ}</Badge>
                      <span className="truncate">{a.datei || a.storage_key || '—'}</span>
                      {a.hash
                        ? <span className="ml-auto inline-flex items-center gap-1 text-xs text-emerald-700" title={a.hash}><Fingerprint size={12} />{a.hash.slice(0, 12)}…</span>
                        : <Badge variant="destructive" className="ml-auto">kein Hash</Badge>}
                    </div>
                  ))}
                </CardContent>
              </Card>

              {!!detail.data.vorgangskette?.length && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm flex items-center gap-2"><Link2 size={15} />Vorgangskette</CardTitle></CardHeader>
                  <CardContent className="space-y-1">
                    {detail.data.vorgangskette.map((k, i) => (
                      <div key={i} className="text-sm flex items-center gap-2">
                        <Badge variant="outline">{k.richtung}</Badge>
                        <span>{k.relation}</span>
                        <span className="text-muted-foreground">→ {k.partner_nr} ({k.partner_typ})</span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {!!detail.data.buchungen?.length && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm flex items-center gap-2"><Euro size={15} />Buchungen</CardTitle></CardHeader>
                  <CardContent className="space-y-1">
                    {detail.data.buchungen.map((b, i) => (
                      <div key={i} className="text-sm flex items-center gap-2">
                        <Badge variant="outline">{b.typ}</Badge>
                        <span className="tabular-nums">{b.betrag != null ? `${b.betrag} ${b.waehrung ?? ''}` : '—'}</span>
                        <span className="ml-auto text-xs text-muted-foreground">{b.posted_at ? new Date(b.posted_at).toLocaleString('de-DE') : ''}</span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {!!detail.data.luecken?.length && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Lücken & Hinweise</CardTitle></CardHeader>
                  <CardContent className="space-y-1.5">
                    {detail.data.luecken.map((l, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        {l.schwere === 'warnung' ? <AlertTriangle size={15} className="mt-0.5 text-amber-600 shrink-0" /> : <Info size={15} className="mt-0.5 text-sky-600 shrink-0" />}
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
