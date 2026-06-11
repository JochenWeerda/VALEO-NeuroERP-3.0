import { useState } from 'react'
import { FileCheck2, Loader2, RefreshCw, Search, Upload, CheckCircle2, Archive } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from '@/hooks/use-toast'
import { useEvidenceDocuments } from '@/lib/api/docflow-evidence'
import { useArtifacts, useUploadArtifact, useSetFreigabe, type ArtifactItem } from '@/lib/api/docflow-artifact'

/**
 * Artefakt-Upload & Freigabe (DOM-DOC-004.2) — revisionssichere Artefakte je
 * Dokument hochladen (SHA-256, Versionierung) und freigeben/archivieren
 * (entwurf→freigegeben→archiviert).
 */

const STATUS_BADGE: Record<string, string> = {
  entwurf: 'bg-amber-100 text-amber-800', freigegeben: 'bg-emerald-100 text-emerald-800',
  archiviert: 'bg-muted text-muted-foreground',
}

function errDetail(err: unknown) {
  return (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Unbekannter Fehler'
}

function ArtifactActions({ doc, a }: { doc: string; a: ArtifactItem }) {
  const setFreigabe = useSetFreigabe(doc)
  const act = (zielStatus: 'freigegeben' | 'archiviert') => {
    if (setFreigabe.isPending) return
    setFreigabe.mutate({ artifactId: a.artifact_id, zielStatus }, {
      onSuccess: () => toast({ title: `Artefakt ${zielStatus}` }),
      onError: (err) => toast({ title: 'Freigabe fehlgeschlagen', description: errDetail(err), variant: 'destructive' }),
    })
  }
  if (a.freigabe_status === 'entwurf') {
    return <Button size="sm" variant="ghost" onClick={() => act('freigegeben')} disabled={setFreigabe.isPending}>
      {setFreigabe.isPending ? <Loader2 size={13} className="animate-spin mr-1" /> : <CheckCircle2 size={13} className="mr-1 text-emerald-600" />}Freigeben
    </Button>
  }
  if (a.freigabe_status === 'freigegeben') {
    return <Button size="sm" variant="ghost" onClick={() => act('archiviert')} disabled={setFreigabe.isPending}>
      {setFreigabe.isPending ? <Loader2 size={13} className="animate-spin mr-1" /> : <Archive size={13} className="mr-1" />}Archivieren
    </Button>
  }
  return <span className="text-[11px] text-muted-foreground">—</span>
}

function UploadForm({ doc }: { doc: string }) {
  const upload = useUploadArtifact(doc)
  const [fileName, setFileName] = useState('')
  const [content, setContent] = useState('')
  const valid = fileName.trim() !== '' && content !== ''
  const submit = () => {
    if (!valid || upload.isPending) return
    upload.mutate({ fileName, content }, {
      onSuccess: (d) => { toast({ title: `Artefakt hochgeladen (v${d.version})` }); setFileName(''); setContent('') },
      onError: (err) => toast({ title: 'Upload fehlgeschlagen', description: errDetail(err), variant: 'destructive' }),
    })
  }
  return (
    <Card>
      <CardHeader className="py-3"><CardTitle className="text-sm">Artefakt hochladen (neue Version)</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <label className="text-xs text-muted-foreground space-y-1">
            <span>Dateiname</span>
            <Input value={fileName} onChange={(e) => setFileName(e.target.value)} placeholder="rechnung.pdf" className="h-8" />
          </label>
          <label className="text-xs text-muted-foreground space-y-1">
            <span>Inhalt (→ SHA-256)</span>
            <Input value={content} onChange={(e) => setContent(e.target.value)} placeholder="Dokumentinhalt / Base64" className="h-8" />
          </label>
        </div>
        <div className="flex justify-end">
          <Button size="sm" onClick={submit} disabled={!valid || upload.isPending}>
            {upload.isPending ? <Loader2 size={14} className="animate-spin mr-1" /> : <Upload size={14} className="mr-1" />}
            Hochladen
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default function ArtefaktFreigabePage() {
  const [selected, setSelected] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const docs = useEvidenceDocuments(100)
  const artifacts = useArtifacts(selected)

  const list = (docs.data ?? []).filter((d) => !filter || d.doc_number.toLowerCase().includes(filter.toLowerCase()))
  const data = artifacts.data

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center gap-2">
        <FileCheck2 size={20} className="text-primary" />
        <h1 className="text-lg font-semibold">Artefakt-Upload & Freigabe</h1>
        <Button variant="outline" size="sm" className="ml-auto" onClick={() => void docs.refetch()} disabled={docs.isFetching}>
          {docs.isFetching ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
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
            {docs.isLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
            ) : list.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">Keine Dokumente.</div>
            ) : (
              <div className="divide-y">
                {list.map((d) => (
                  <button key={d.doc_number} onClick={() => setSelected(d.doc_number)}
                    className={`w-full text-left px-3 py-2 hover:bg-muted/50 ${selected === d.doc_number ? 'bg-muted' : ''}`}>
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-sm truncate">{d.doc_number}</span>
                      <Badge variant="outline" className="text-[10px]">{d.artefakte} Art.</Badge>
                    </div>
                    <div className="text-xs text-muted-foreground">{d.doc_type}{d.revisionssicher ? ' · revisionssicher' : ''}</div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-3">
          {!selected ? (
            <Card><CardContent className="py-16 text-center text-sm text-muted-foreground">Dokument wählen, um Artefakte zu verwalten.</CardContent></Card>
          ) : (
            <>
              <UploadForm doc={selected} />
              <Card>
                <CardHeader className="py-3"><CardTitle className="text-sm">Artefakte {data?.summary ? `(${data.summary.freigegeben} freigegeben / ${data.summary.anzahl})` : ''}</CardTitle></CardHeader>
                <CardContent className="p-0">
                  {artifacts.isLoading ? (
                    <div className="flex items-center justify-center py-8 text-muted-foreground"><Loader2 className="animate-spin mr-2" size={16} /> Lädt …</div>
                  ) : (data?.artifacts?.length ?? 0) === 0 ? (
                    <div className="py-8 text-center text-sm text-muted-foreground">Keine Artefakte.</div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="text-xs text-muted-foreground border-b">
                          <tr>
                            <th className="text-left font-medium px-3 py-1.5">Typ</th>
                            <th className="text-right font-medium px-3 py-1.5">Version</th>
                            <th className="text-left font-medium px-3 py-1.5">Datei</th>
                            <th className="text-left font-medium px-3 py-1.5">SHA-256</th>
                            <th className="text-left font-medium px-3 py-1.5">Freigabe</th>
                            <th className="text-right font-medium px-3 py-1.5">Aktion</th>
                          </tr>
                        </thead>
                        <tbody>
                          {(data?.artifacts ?? []).map((a) => (
                            <tr key={a.artifact_id} className="border-b last:border-0">
                              <td className="px-3 py-1.5">{a.artifact_type}</td>
                              <td className="px-3 py-1.5 text-right tabular-nums">v{a.version}{a.aktuell && <Badge variant="outline" className="ml-1 text-[10px]">aktuell</Badge>}</td>
                              <td className="px-3 py-1.5">{a.file_name ?? '—'}</td>
                              <td className="px-3 py-1.5 font-mono text-[11px] text-muted-foreground">{a.sha256 ? `${a.sha256.slice(0, 12)}…` : '—'}</td>
                              <td className="px-3 py-1.5"><Badge className={`text-[10px] ${STATUS_BADGE[a.freigabe_status] ?? ''}`}>{a.freigabe_status}</Badge></td>
                              <td className="px-3 py-1.5 text-right"><ArtifactActions doc={selected} a={a} /></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
