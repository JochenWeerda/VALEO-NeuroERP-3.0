import { useState } from 'react'
import { AlertCircle } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useScreenDefinition } from '@/lib/api/masks'
import { updateFeedingFeed, type FeedApprovalStatus, type FeedKind, type FeedingFeedDetail as FeedDetail } from '@/lib/api/feeding-feed-catalog'
import { getAxiosErrorMessage } from '@/lib/api-client'

const KINDS: FeedKind[] = ['forage', 'concentrate', 'mineral', 'additive', 'byproduct', 'liquid', 'other']
const STATUSES: FeedApprovalStatus[] = ['draft', 'approved', 'blocked', 'retired']

export function FeedingFeedDetail({ feedId }: { feedId?: string }): JSX.Element {
  const schemaQuery = useScreenDefinition('futtermittel/einzelfuttermittel')
  const runtime = useUniversalMaskRuntime({
    screenId: 'futtermittel/einzelfuttermittel', entityId: feedId, schema: schemaQuery.data,
    permissions: ['futtermittel.einzelfm.update'], enabled: Boolean(schemaQuery.data && feedId),
  })
  const detail = runtime.entityData as unknown as Partial<FeedDetail>
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [kind, setKind] = useState<FeedKind>('other')
  const [status, setStatus] = useState<FeedApprovalStatus>('draft')
  const [dryMatter, setDryMatter] = useState('')
  const [reason, setReason] = useState('')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)

  function beginEdit(): void {
    setName(detail.name ?? '')
    setCategory(detail.art ?? '')
    setKind(detail.feed_kind ?? 'other')
    setStatus(detail.approval_status ?? 'draft')
    setDryMatter(detail.trockensubstanz ?? '')
    setReason('')
    setOpen(true)
  }

  async function save(): Promise<void> {
    if (!feedId || !detail.revision || !name.trim() || !category.trim() || reason.trim().length < 3) return
    setSaving(true)
    setFeedback(null)
    try {
      await updateFeedingFeed(feedId, {
        expected_revision: detail.revision, reason: reason.trim(), name: name.trim(), art: category.trim(),
        feed_kind: kind, approval_status: status, trockensubstanz: dryMatter || null,
      })
      setOpen(false)
      setFeedback('Futtermittel wurde als neue Revision gespeichert.')
      await runtime.refetch()
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  if (schemaQuery.isLoading || !runtime.plan) return <p className="px-4 py-6 text-sm text-muted-foreground">Futtermittel wird geladen…</p>
  if (schemaQuery.error || runtime.entityError) return <p className="flex gap-2 px-4 py-6 text-sm text-destructive" role="alert"><AlertCircle className="h-4 w-4" />Futtermittel konnte nicht geladen werden.</p>

  return <div data-testid="feeding-feed-detail">
    {feedback ? <p className="mb-3 rounded-md border bg-muted px-3 py-2 text-sm" role="status">{feedback}</p> : null}
    <UniversalMaskRenderer plan={runtime.plan} data={runtime.entityData} tables={runtime.tableRows} tableQueryStates={runtime.tableQueryStates} tableTotals={runtime.tableTotals} onTableQueryChange={runtime.setTableQuery} onOverlayChange={runtime.updateUserOverlay} onOverlayReset={runtime.resetUserOverlay} lookupBindings={runtime.lookupBindings} entityId={feedId} onAction={(key) => { if (key === 'edit') beginEdit() }} />
    <Dialog open={open} onOpenChange={setOpen}><DialogContent><DialogHeader><DialogTitle>Futtermittel bearbeiten</DialogTitle><DialogDescription>Die Aenderung bleibt als neue Stammrevision nachvollziehbar.</DialogDescription></DialogHeader>
      <div className="grid gap-3 py-2 sm:grid-cols-2">
        <div className="grid gap-1"><Label htmlFor="feed-name">Bezeichnung</Label><Input id="feed-name" value={name} onChange={(event) => setName(event.target.value)} /></div>
        <div className="grid gap-1"><Label htmlFor="feed-category">Kategorie</Label><Input id="feed-category" value={category} onChange={(event) => setCategory(event.target.value)} /></div>
        <div className="grid gap-1"><Label htmlFor="feed-kind">Futterart</Label><select id="feed-kind" className="h-10 rounded-md border bg-background px-3 text-sm" value={kind} onChange={(event) => setKind(event.target.value as FeedKind)}>{KINDS.map((value) => <option key={value}>{value}</option>)}</select></div>
        <div className="grid gap-1"><Label htmlFor="feed-status">Freigabestatus</Label><select id="feed-status" className="h-10 rounded-md border bg-background px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value as FeedApprovalStatus)}>{STATUSES.map((value) => <option key={value}>{value}</option>)}</select></div>
        <div className="grid gap-1"><Label htmlFor="feed-dm">Trockenmasse %</Label><Input id="feed-dm" type="number" min="0.001" max="100" step="0.001" value={dryMatter} onChange={(event) => setDryMatter(event.target.value)} /></div>
        <div className="grid gap-1 sm:col-span-2"><Label htmlFor="feed-reason">Aenderungsgrund</Label><Textarea id="feed-reason" value={reason} onChange={(event) => setReason(event.target.value)} /></div>
      </div>
      <DialogFooter><Button variant="outline" onClick={() => setOpen(false)}>Abbrechen</Button><Button disabled={saving || !name.trim() || !category.trim() || reason.trim().length < 3} onClick={() => { void save() }}>{saving ? 'Speichert…' : 'Neue Revision speichern'}</Button></DialogFooter>
    </DialogContent></Dialog>
  </div>
}
