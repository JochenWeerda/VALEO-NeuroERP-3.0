import { useMemo, useState } from 'react'
import { AlertCircle, ArrowLeft } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useScreenDefinition } from '@/lib/api/masks'
import { transitionRationVersion, type RationDetail, type RationStatus } from '@/lib/api/rations-lifecycle'
import { getAxiosErrorMessage } from '@/lib/api-client'

const ACTIONS: Record<string, { from: RationStatus[]; to: RationStatus; reason: boolean; schedule?: boolean }> = {
  submit_review: { from: ['draft'], to: 'in_review', reason: false },
  approve: { from: ['in_review'], to: 'approved', reason: false },
  schedule: { from: ['approved'], to: 'scheduled', reason: false, schedule: true },
  activate: { from: ['approved', 'scheduled'], to: 'active', reason: false },
  retire: { from: ['active'], to: 'retired', reason: true },
  archive: { from: ['draft', 'approved', 'retired'], to: 'archived', reason: true },
}

export function RationLifecycleDetail({ rationId }: { rationId: string }): JSX.Element {
  const schemaQuery = useScreenDefinition('agrar/ration')
  const runtime = useUniversalMaskRuntime({
    screenId: 'agrar/ration',
    entityId: rationId,
    schema: schemaQuery.data,
    permissions: ['futtermittel.rations.update'],
    enabled: Boolean(schemaQuery.data && rationId),
  })
  const detail = runtime.entityData as unknown as Partial<RationDetail>
  const currentStatus = detail.latest_status
  const plan = useMemo(() => {
    if (!runtime.plan || !currentStatus) return runtime.plan
    return {
      ...runtime.plan,
      actions: runtime.plan.actions.filter((action) => ACTIONS[action.key]?.from.includes(currentStatus)),
    }
  }, [runtime.plan, currentStatus])
  const [pendingAction, setPendingAction] = useState<string | null>(null)
  const [reason, setReason] = useState('')
  const [feedingStart, setFeedingStart] = useState('')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)

  const action = pendingAction ? ACTIONS[pendingAction] : undefined

  async function execute(): Promise<void> {
    if (!action || !detail.latest_version_id || !currentStatus) return
    setSaving(true)
    setFeedback(null)
    try {
      await transitionRationVersion({
        versionId: detail.latest_version_id,
        expectedStatus: currentStatus,
        targetStatus: action.to,
        reason: reason.trim() || undefined,
        feedingStart: feedingStart ? new Date(feedingStart).toISOString() : undefined,
      })
      setPendingAction(null)
      setReason('')
      setFeedingStart('')
      setFeedback(`Status wurde auf „${action.to}“ gesetzt.`)
      await runtime.refetch()
      if (action.to === 'active') {
        const snapshot = detail.versions?.find((version) => version.id === detail.latest_version_id)?.snapshot
        const mobile = snapshot?.mobile
        if (mobile && typeof mobile === 'object') {
          localStorage.setItem('valeo.rations.active-mobile.v1', JSON.stringify(mobile))
        }
      }
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  if (schemaQuery.isLoading || !plan) {
    return <p className="px-4 py-6 text-sm text-muted-foreground">Rationsfreigabe wird geladen…</p>
  }
  if (schemaQuery.error || runtime.entityError) {
    return <p className="flex gap-2 px-4 py-6 text-sm text-destructive" role="alert"><AlertCircle className="h-4 w-4" />Ration konnte nicht geladen werden.</p>
  }

  return (
    <div data-testid="ration-lifecycle-detail">
      <a href="/portal/rationsoptimierung?view=rations" className="mb-3 inline-flex min-h-touch items-center gap-2 rounded-md px-3 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Zur Rationsliste
      </a>
      {feedback ? <p className="mb-3 rounded-md border bg-muted px-3 py-2 text-sm" role="status">{feedback}</p> : null}
      <UniversalMaskRenderer
        plan={plan}
        data={runtime.entityData}
        tables={runtime.tableRows}
        tableQueryStates={runtime.tableQueryStates}
        tableTotals={runtime.tableTotals}
        onTableQueryChange={runtime.setTableQuery}
        onOverlayChange={runtime.updateUserOverlay}
        onOverlayReset={runtime.resetUserOverlay}
        lookupBindings={runtime.lookupBindings}
        entityId={rationId}
        onAction={(actionKey) => setPendingAction(actionKey)}
      />

      <Dialog open={Boolean(pendingAction)} onOpenChange={(open) => { if (!open) setPendingAction(null) }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Lifecycle-Schritt bestaetigen</DialogTitle>
            <DialogDescription>
              Status {currentStatus ?? '–'} wird auf {action?.to ?? '–'} gesetzt. Der Vorgang wird auditiert.
            </DialogDescription>
          </DialogHeader>
          {action?.schedule ? (
            <div className="grid gap-2">
              <Label htmlFor="ration-feeding-start">Fuetterungsbeginn</Label>
              <Input id="ration-feeding-start" type="datetime-local" value={feedingStart} onChange={(event) => setFeedingStart(event.target.value)} />
            </div>
          ) : null}
          <div className="grid gap-2">
            <Label htmlFor="ration-transition-reason">Grund {action?.reason ? '(Pflicht)' : '(optional)'}</Label>
            <Textarea id="ration-transition-reason" value={reason} onChange={(event) => setReason(event.target.value)} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPendingAction(null)}>Abbrechen</Button>
            <Button disabled={saving || Boolean(action?.reason && !reason.trim()) || Boolean(action?.schedule && !feedingStart)} onClick={() => { void execute() }}>
              {saving ? 'Verarbeitet…' : 'Status wechseln'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
