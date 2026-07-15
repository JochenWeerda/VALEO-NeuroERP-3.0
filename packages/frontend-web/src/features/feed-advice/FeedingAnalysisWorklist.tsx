import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AlertCircle } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useScreenDefinition } from '@/lib/api/masks'
import { createFeedingAnalysis, previewFeedingAnalysisImport, type FeedingAnalysisValueInput } from '@/lib/api/feeding-feed-analyses'
import { listFeedingFeeds } from '@/lib/api/feeding-feed-catalog'
import { getAxiosErrorMessage } from '@/lib/api-client'

function value(nutrient_code: string, original_value: string, original_unit_code: string,
  canonical_unit_code: string, basis: 'fresh_matter' | 'dry_matter', estimated = false): FeedingAnalysisValueInput {
  return { nutrient_code, original_value, original_unit_code, canonical_unit_code, basis,
    value_status: estimated ? 'estimated' : 'measured' }
}

export function FeedingAnalysisWorklist(): JSX.Element {
  const schemaQuery = useScreenDefinition('futtermittel/analysen')
  const runtime = useUniversalMaskRuntime({ screenId: 'futtermittel/analysen', schema: schemaQuery.data,
    permissions: ['futtermittel.analyse.create'], enabled: Boolean(schemaQuery.data) })
  const feeds = useQuery({ queryKey: ['feeding-feed-catalog', 'options'], queryFn: listFeedingFeeds })
  const [open, setOpen] = useState(false)
  const [feedId, setFeedId] = useState('')
  const [name, setName] = useState('')
  const [sample, setSample] = useState('')
  const [laboratory, setLaboratory] = useState('')
  const [dryMatter, setDryMatter] = useState('')
  const [protein, setProtein] = useState('')
  const [energy, setEnergy] = useState('')
  const [documentId, setDocumentId] = useState('')
  const [importValues, setImportValues] = useState<FeedingAnalysisValueInput[] | null>(null)
  const [originalSha, setOriginalSha] = useState('')
  const [sourceFile, setSourceFile] = useState('')
  const [warnings, setWarnings] = useState<string[]>([])
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)

  async function save(): Promise<void> {
    if (!feedId || !name.trim() || !dryMatter) return
    setSaving(true); setFeedback(null)
    try {
      const values = importValues ?? [value('dry_matter', dryMatter, 'percent', 'g_per_kg', 'fresh_matter')]
      if (!importValues && protein) values.push(value('crude_protein', protein, 'percent', 'g_per_kg', 'dry_matter'))
      if (!importValues && energy) values.push(value('metabolizable_energy', energy, 'MJ_per_kg', 'MJ_per_kg', 'dry_matter', true))
      const created = await createFeedingAnalysis({ feed_id: feedId, bezeichnung: name.trim(),
        probe_nr: sample.trim() || undefined, labor: laboratory.trim() || undefined,
        method: importValues ? 'Laborimport mit Vorschau' : 'Manuelle Erfassung', values,
        quelle_datei: sourceFile || undefined, original_sha256: originalSha || undefined,
        original_document_id: documentId.trim() || undefined })
      setOpen(false)
      window.history.pushState(null, '', `/futtermittel/grundfutteranalysen/${encodeURIComponent(created.id)}`)
      window.dispatchEvent(new PopStateEvent('popstate'))
    } catch (error) { setFeedback(getAxiosErrorMessage(error)) } finally { setSaving(false) }
  }

  async function preview(file: File): Promise<void> {
    setSaving(true); setFeedback(null)
    try {
      const result = await previewFeedingAnalysisImport(file)
      setName(result.analysis.bezeichnung ?? file.name)
      setSample(result.analysis.probe_nr ?? '')
      setLaboratory(result.analysis.labor ?? '')
      setImportValues(result.values); setOriginalSha(result.sha256); setSourceFile(result.filename)
      setWarnings(result.warnings)
      const dm = result.values.find((item) => item.nutrient_code === 'dry_matter')
      if (dm) setDryMatter(dm.original_value)
    } catch (error) { setFeedback(getAxiosErrorMessage(error)) } finally { setSaving(false) }
  }

  if (schemaQuery.isLoading || !runtime.plan) return <p className="px-4 py-6 text-sm text-muted-foreground">Analyse-Worklist wird geladen…</p>
  if (schemaQuery.error || runtime.entityError) return <p className="flex gap-2 px-4 py-6 text-sm text-destructive" role="alert"><AlertCircle className="h-4 w-4" />Analysen konnten nicht geladen werden.</p>
  return <div data-testid="feeding-analysis-worklist">
    {feedback ? <p role="alert" className="mb-3 rounded-md border border-destructive/30 px-3 py-2 text-sm text-destructive">{feedback}</p> : null}
    <UniversalMaskRenderer plan={runtime.plan} data={runtime.entityData} tables={runtime.tableRows}
      tableQueryStates={runtime.tableQueryStates} tableTotals={runtime.tableTotals}
      onTableQueryChange={runtime.setTableQuery} onOverlayChange={runtime.updateUserOverlay}
      onOverlayReset={runtime.resetUserOverlay} lookupBindings={runtime.lookupBindings}
      onAction={(key) => { if (key === 'import_analysis') setOpen(true) }} />
    <Dialog open={open} onOpenChange={setOpen}><DialogContent><DialogHeader><DialogTitle>Futteranalyse erfassen</DialogTitle>
      <DialogDescription>Originalwerte und Rechenwerte bleiben getrennt nachvollziehbar. Geschätzte Energie wird sichtbar gekennzeichnet.</DialogDescription></DialogHeader>
      <div className="grid gap-3 py-2 sm:grid-cols-2">
        <div className="grid gap-1 sm:col-span-2"><Label htmlFor="analysis-file">Laborbericht als PDF oder CSV</Label><Input id="analysis-file" type="file" accept=".pdf,.csv" onChange={(event) => { const file = event.target.files?.[0]; if (file) void preview(file) }} /><p className="text-xs text-muted-foreground">Die Vorschau speichert noch nichts. Importierte Belege benötigen vor der Freigabe eine revisionssichere DMS-Referenz.</p></div>
        <div className="grid gap-1 sm:col-span-2"><Label htmlFor="analysis-feed">Futtermittel</Label><select id="analysis-feed" className="h-10 rounded-md border bg-background px-3 text-sm" value={feedId} onChange={(event) => setFeedId(event.target.value)}><option value="">Bitte wählen</option>{feeds.data?.map((feed) => <option key={feed.id} value={feed.id}>{feed.name} · {feed.artikel_nummer}</option>)}</select></div>
        <div className="grid gap-1"><Label htmlFor="analysis-name">Probenbezeichnung</Label><Input id="analysis-name" value={name} onChange={(event) => setName(event.target.value)} /></div>
        <div className="grid gap-1"><Label htmlFor="analysis-sample">Probennummer</Label><Input id="analysis-sample" value={sample} onChange={(event) => setSample(event.target.value)} /></div>
        <div className="grid gap-1"><Label htmlFor="analysis-lab">Labor</Label><Input id="analysis-lab" value={laboratory} onChange={(event) => setLaboratory(event.target.value)} /></div>
        <div className="grid gap-1"><Label htmlFor="analysis-dm">Trockensubstanz % OS</Label><Input id="analysis-dm" type="number" min="0.01" max="100" step="0.01" value={dryMatter} onChange={(event) => setDryMatter(event.target.value)} /></div>
        <div className="grid gap-1"><Label htmlFor="analysis-protein">Rohprotein % TM</Label><Input id="analysis-protein" type="number" min="0" max="100" step="0.01" value={protein} onChange={(event) => setProtein(event.target.value)} /></div>
        <div className="grid gap-1"><Label htmlFor="analysis-energy">ME MJ/kg TM (Schätzwert)</Label><Input id="analysis-energy" type="number" min="0" step="0.001" value={energy} onChange={(event) => setEnergy(event.target.value)} /></div>
        {sourceFile ? <div className="grid gap-1 sm:col-span-2"><Label htmlFor="analysis-document">DMS-Beleg-ID für {sourceFile}</Label><Input id="analysis-document" value={documentId} onChange={(event) => setDocumentId(event.target.value)} placeholder="Nach revisionssicherem DMS-Upload eintragen" />{warnings.map((warning) => <p key={warning} className="text-xs text-amber-700">{warning}</p>)}</div> : null}
      </div><DialogFooter><Button variant="outline" onClick={() => setOpen(false)}>Abbrechen</Button><Button disabled={saving || !feedId || !name.trim() || !dryMatter} onClick={() => void save()}>{saving ? 'Speichert…' : 'Analyse anlegen'}</Button></DialogFooter>
    </DialogContent></Dialog>
  </div>
}
