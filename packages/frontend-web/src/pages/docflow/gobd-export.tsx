import { useState } from 'react'
import { PackageOpen, Loader2, RefreshCw, Search, FileArchive, CheckCircle2, XCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from '@/hooks/use-toast'
import { useEvidenceDocuments } from '@/lib/api/docflow-evidence'
import { useGobdExport, usePaperlessProbe, type GobdManifest } from '@/lib/api/docflow-gobd'

/**
 * GoBD-Exportpaket & Paperless-Liveprobe (DOM-DOC-004.4) — je Vorgang ein
 * revisionssicheres Manifest (Artefakt-Hashes + Prüfsumme) erzeugen + DMS-Probe.
 */

export default function GobdExportPage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const [manifest, setManifest] = useState<GobdManifest | null>(null)
  const docs = useEvidenceDocuments(100)
  const probe = usePaperlessProbe()
  const exp = useGobdExport()

  const list = (docs.data ?? []).filter((d) => !filter || d.doc_number.toLowerCase().includes(filter.toLowerCase()))

  const runExport = () => {
    if (!selected || exp.isPending) return
    exp.mutate(selected, {
      onSuccess: (d) => {
        if (d.found && d.manifest) { setManifest(d.manifest); toast({ title: 'GoBD-Paket erzeugt', description: `${d.manifest.anzahl_artefakte} Artefakte${d.manifest.revisionssicher ? ' · revisionssicher' : ''}` }) }
        else toast({ title: 'Export nicht möglich', description: d.detail, variant: 'destructive' })
      },
      onError: () => toast({ title: 'Export fehlgeschlagen', variant: 'destructive' }),
    })
  }

  const downloadManifest = () => {
    if (!manifest) return
    const blob = new Blob([JSON.stringify(manifest, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `GoBD_${manifest.vorgang}.json`; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <PackageOpen size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">GoBD-Export</h1>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => { void docs.refetch(); void probe.refetch() }} disabled={docs.isFetching}>
          {docs.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
          <span className="ml-1">Aktualisieren</span>
        </Button>
      </div>

      <Card>
        <CardContent className="p-3 flex items-center gap-2 text-sm">
          <span className="text-muted-foreground">DMS / Paperless:</span>
          {probe.isLoading ? <Loader2 size={14} className="animate-spin" /> : !probe.data?.konfiguriert ? (
            <Badge variant="outline" className="text-amber-700">nicht konfiguriert</Badge>
          ) : probe.data?.erreichbar ? (
            <Badge className="bg-emerald-100 text-emerald-800"><CheckCircle2 size={12} className="mr-1" />erreichbar</Badge>
          ) : (
            <Badge className="bg-red-100 text-red-800"><XCircle size={12} className="mr-1" />nicht erreichbar</Badge>
          )}
          <span className="text-xs text-muted-foreground">{probe.data?.detail}</span>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[22rem_1fr]">
        <Card className="h-fit">
          <CardHeader className="py-3">
            <CardTitle className="text-sm">Vorgänge</CardTitle>
            <div className="relative">
              <Search size={14} className="absolute left-2 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Nr. suchen…" className="h-8 pl-7" />
            </div>
          </CardHeader>
          <CardContent className="p-0 max-h-[70vh] overflow-y-auto">
            {docs.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
            ) : (
              <div className="divide-y">
                {list.map((d) => (
                  <button key={d.doc_number} onClick={() => { setSelected(d.doc_number); setManifest(null) }}
                    className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${selected === d.doc_number ? 'bg-muted' : ''}`}>
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-sm truncate">{d.doc_number}</span>
                      {d.revisionssicher && <Badge variant="outline" className="text-[10px]">rev.-sicher</Badge>}
                    </div>
                    <div className="text-xs text-muted-foreground">{d.doc_type} · {d.artefakte} Artefakte</div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-3">
          {!selected ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Vorgang wählen, um ein GoBD-Exportpaket zu erzeugen.</CardContent></Card>
          ) : (
            <>
              <div className="flex items-center gap-2">
                <span className="font-medium">{selected}</span>
                <Button size="sm" className="ml-auto" onClick={runExport} disabled={exp.isPending}>
                  {exp.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <FileArchive size={14} className="mr-1" />}
                  GoBD-Paket erzeugen
                </Button>
                {manifest && <Button size="sm" variant="outline" onClick={downloadManifest}>Manifest (JSON)</Button>}
              </div>

              {manifest && (
                <Card>
                  <CardHeader className="py-3"><CardTitle className="text-sm">Manifest</CardTitle></CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
                      <div><div className="text-xs text-muted-foreground">Artefakte</div><div className="font-semibold tabular-nums">{manifest.anzahl_artefakte}</div></div>
                      <div><div className="text-xs text-muted-foreground">Buchungen</div><div className="font-semibold tabular-nums">{manifest.buchungen}</div></div>
                      <div><div className="text-xs text-muted-foreground">Offene Lücken</div><div className="font-semibold tabular-nums">{manifest.offene_luecken}</div></div>
                      <div><div className="text-xs text-muted-foreground">Revisionssicher</div><div>{manifest.revisionssicher ? <Badge className="bg-emerald-100 text-emerald-800">ja</Badge> : <Badge className="bg-red-100 text-red-800">nein</Badge>}</div></div>
                    </div>
                    <div className="text-xs"><span className="text-muted-foreground">Prüfsumme (SHA-256): </span><span className="font-mono">{manifest.pruefsumme_sha256}</span></div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="text-xs text-muted-foreground border-b">
                          <tr><th className="text-left font-medium px-3 py-1.5">Datei</th><th className="text-left font-medium px-3 py-1.5">Typ</th><th className="text-left font-medium px-3 py-1.5">SHA-256</th></tr>
                        </thead>
                        <tbody>
                          {manifest.artefakte.map((a, i) => (
                            <tr key={i} className="border-b last:border-0">
                              <td className="px-3 py-1.5">{a.datei ?? '—'}</td>
                              <td className="px-3 py-1.5">{a.typ}</td>
                              <td className="px-3 py-1.5 font-mono text-[11px] text-muted-foreground">{a.sha256 ? `${a.sha256.slice(0, 16)}…` : '—'}</td>
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
