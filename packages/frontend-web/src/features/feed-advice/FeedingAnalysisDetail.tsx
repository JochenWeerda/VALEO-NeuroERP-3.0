import { useState } from 'react'
import { AlertCircle } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useScreenDefinition } from '@/lib/api/masks'
import { transitionFeedingAnalysis, validateFeedingAnalysis, type FeedingAnalysisDetail as Detail } from '@/lib/api/feeding-feed-analyses'
import { getAxiosErrorMessage } from '@/lib/api-client'

export function FeedingAnalysisDetail({ analysisId }: { analysisId?: string }): JSX.Element {
  const schemaQuery = useScreenDefinition('futtermittel/analyse')
  const runtime = useUniversalMaskRuntime({ screenId: 'futtermittel/analyse', entityId: analysisId,
    schema: schemaQuery.data, permissions: ['futtermittel.analyse.validate', 'futtermittel.analyse.release', 'futtermittel.analyse.reject'],
    enabled: Boolean(schemaQuery.data && analysisId) })
  const detail = runtime.entityData as unknown as Partial<Detail>
  const [target, setTarget] = useState<'released' | 'rejected' | null>(null)
  const [reason, setReason] = useState('')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)

  async function validate(): Promise<void> {
    if (!analysisId || !detail.revision) return
    setSaving(true); setFeedback(null)
    try { await validateFeedingAnalysis(analysisId, detail.revision); setFeedback('Plausibilitätsprüfung abgeschlossen.'); await runtime.refetch() }
    catch (error) { setFeedback(getAxiosErrorMessage(error)) } finally { setSaving(false) }
  }
  async function transition(): Promise<void> {
    if (!analysisId || !detail.revision || !target || reason.trim().length < 3) return
    setSaving(true); setFeedback(null)
    try { await transitionFeedingAnalysis(analysisId, target, detail.revision, reason.trim()); setTarget(null); setReason('');
      setFeedback(target === 'released' ? 'Analyse wurde als aktive Version freigegeben.' : 'Analyse wurde nachvollziehbar zurückgewiesen.'); await runtime.refetch() }
    catch (error) { setFeedback(getAxiosErrorMessage(error)) } finally { setSaving(false) }
  }
  if (schemaQuery.isLoading || !runtime.plan) return <p className="px-4 py-6 text-sm text-muted-foreground">Analyse wird geladen…</p>
  if (schemaQuery.error || runtime.entityError) return <p className="flex gap-2 px-4 py-6 text-sm text-destructive" role="alert"><AlertCircle className="h-4 w-4" />Analyse konnte nicht geladen werden.</p>
  return <div data-testid="feeding-analysis-detail">
    {feedback ? <p className="mb-3 rounded-md border bg-muted px-3 py-2 text-sm" role="status">{feedback}</p> : null}
    <UniversalMaskRenderer plan={runtime.plan} data={runtime.entityData} tables={runtime.tableRows}
      tableQueryStates={runtime.tableQueryStates} tableTotals={runtime.tableTotals}
      onTableQueryChange={runtime.setTableQuery} onOverlayChange={runtime.updateUserOverlay}
      onOverlayReset={runtime.resetUserOverlay} lookupBindings={runtime.lookupBindings} entityId={analysisId}
      onAction={(key) => { if (key === 'validate') void validate(); if (key === 'release') setTarget('released'); if (key === 'reject') setTarget('rejected') }} />
    <Dialog open={target !== null} onOpenChange={(open) => { if (!open) setTarget(null) }}><DialogContent><DialogHeader>
      <DialogTitle>{target === 'released' ? 'Analyse freigeben' : 'Analyse zurückweisen'}</DialogTitle>
      <DialogDescription>{target === 'released' ? 'Die Analyse wird zur aktiven Berechnungsgrundlage; eine bisher aktive Version wird ersetzt.' : 'Die Zurückweisung beendet diese Version unveränderlich.'}</DialogDescription>
      </DialogHeader><div className="grid gap-1 py-2"><Label htmlFor="analysis-reason">Auditgrund</Label><Textarea id="analysis-reason" value={reason} onChange={(event) => setReason(event.target.value)} /></div>
      <DialogFooter><Button variant="outline" onClick={() => setTarget(null)}>Abbrechen</Button><Button disabled={saving || reason.trim().length < 3} variant={target === 'rejected' ? 'destructive' : 'default'} onClick={() => void transition()}>{saving ? 'Speichert…' : target === 'released' ? 'Verbindlich freigeben' : 'Zurückweisen'}</Button></DialogFooter>
    </DialogContent></Dialog>
  </div>
}
