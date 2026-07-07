/**
 * Generic page wrapper for native ScreenDefinitions (temporary=False).
 * Replaces legacy handcrafted detail pages when a non-temporary SD is available.
 *
 * Dialog flow:
 *  1. Action triggered → check requiresConfirmation → ConfirmationDialog
 *  2. After confirm → if dangerLevel >= moderate and commandEndpoint exists → dryRun call → PreviewDialog
 *  3. After preview → if auditReasonRequired → AuditReasonDialog
 *  4. Execute with collected auditReason
 */

import { useNavigate } from '@tanstack/react-router'
import { ArrowLeft, AlertCircle, AlertTriangle, ShieldAlert } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { UniversalMaskRenderer, useHumanActionDispatch, useUniversalMaskRuntime } from '@/components/mask-builder'
import { useMaskPilotState } from '@/features/mask-pilot/use-mask-pilot-state'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useScreenDefinition } from '@/lib/api/masks'
import { useToast } from '@/hooks/use-toast'
import type { ActionResult } from '@/components/mask-builder/runtime/useActionRuntime'

interface UniversalNativeDetailPageProps {
  screenId: string
  entityId: string | undefined
  testId?: string
}

interface PendingAction {
  actionKey: string
  payload: Record<string, unknown>
  label: string
  dangerLevel: string
  requiresConfirmation: boolean
  auditReasonRequired: boolean
  hasDryRun: boolean
}

interface ProposedChange {
  field?: string
  from?: unknown
  to?: unknown
  description?: string
  [key: string]: unknown
}

function renderProposedChange(change: unknown, index: number): string {
  if (typeof change === 'string') return change
  if (typeof change !== 'object' || change === null) return String(change)
  const c = change as ProposedChange
  if (typeof c.description === 'string') return c.description
  if (c.field !== undefined && c.from !== undefined && c.to !== undefined) {
    const label = String(c.field).replace(/_/g, ' ')
    const capitalized = label.charAt(0).toUpperCase() + label.slice(1)
    return `${capitalized} wird von „${String(c.from)}" auf „${String(c.to)}" geändert.`
  }
  if (c.field !== undefined && c.to !== undefined) {
    const label = String(c.field).replace(/_/g, ' ')
    const capitalized = label.charAt(0).toUpperCase() + label.slice(1)
    return `${capitalized} wird auf „${String(c.to)}" gesetzt.`
  }
  const entries = Object.entries(c).slice(0, 3).map(([k, v]) => `${k}: ${String(v)}`)
  return entries.join(', ') || `Änderung ${index + 1}`
}

const MODERATE_OR_ABOVE = new Set(['moderate', 'high', 'critical'])

export function UniversalNativeDetailPage({
  screenId,
  entityId,
  testId,
}: UniversalNativeDetailPageProps): JSX.Element {
  const { onTabChange } = useMaskPilotState()
  const navigate = useNavigate()
  const { toast } = useToast()
  const schemaQuery = useScreenDefinition(screenId, { enabled: Boolean(entityId) })
  const [actionError, setActionError] = useState<string | null>(null)
  const [validationErrors, setValidationErrors] = useState<{ field?: string; message: string }[]>([])

  // Multi-step dialog state
  const [pendingAction, setPendingAction] = useState<PendingAction | null>(null)
  const [stage, setStage] = useState<'confirm' | 'preview' | 'audit' | null>(null)
  const [dryRunResult, setDryRunResult] = useState<ActionResult | null>(null)
  const [auditReason, setAuditReason] = useState('')

  const runtime = useUniversalMaskRuntime({
    screenId,
    entityId,
    schema: schemaQuery.data,
    enabled: Boolean(entityId) && schemaQuery.data?.adapter?.temporary === false,
  })
  const actionRuntime = useHumanActionDispatch(schemaQuery.data?.actions ?? [], {
    screenId,
    entityId,
    permissions: schemaQuery.data?.permissions ?? [],
  })

  // --- Worker: final execute (no UI state ownership) ---
  async function doExecute(actionKey: string, payload: Record<string, unknown>, reason?: string): Promise<void> {
    const result = await actionRuntime.executeAction({
      actionKey,
      entityId,
      payload,
      mode: 'execute',
      auditReason: reason,
    })
    if (!result.success) {
      const errs = result.validationErrors ?? []
      if (errs.length > 0) {
        setValidationErrors(errs)
        setActionError(null)
      } else {
        setActionError(result.error ?? `Aktion "${actionKey}" fehlgeschlagen.`)
        setValidationErrors([])
      }
      return
    }
    setActionError(null)
    setValidationErrors([])
    const label = schemaQuery.data?.actions?.find((a: { key: string }) => a.key === actionKey)?.label ?? actionKey
    toast({ title: `${label} erfolgreich`, description: result.summary })
    await runtime.refetch()
  }

  // --- Handler: called by UniversalMaskRenderer ---
  async function handleAction(actionKey: string, payload: Record<string, unknown>): Promise<void> {
    setActionError(null)
    setValidationErrors([])
    const actionDef = schemaQuery.data?.actions?.find((a: { key: string }) => a.key === actionKey)
    const hasDryRun = Boolean(
      actionDef?.commandEndpoint &&
      !actionDef?.stubReason &&
      MODERATE_OR_ABOVE.has(actionDef?.dangerLevel ?? 'safe'),
    )
    const pending: PendingAction = {
      actionKey,
      payload,
      label: actionDef?.label ?? actionKey,
      dangerLevel: actionDef?.dangerLevel ?? 'safe',
      requiresConfirmation: actionDef?.requiresConfirmation ?? false,
      auditReasonRequired: actionDef?.auditReasonRequired ?? false,
      hasDryRun,
    }

    if (pending.requiresConfirmation) {
      setPendingAction(pending)
      setStage('confirm')
      return
    }
    await advanceFromConfirm(pending)
  }

  // --- Step 1: after ConfirmationDialog ---
  async function advanceFromConfirm(pending: PendingAction): Promise<void> {
    if (pending.hasDryRun) {
      const result = await actionRuntime.executeAction({
        actionKey: pending.actionKey,
        entityId,
        payload: pending.payload,
        mode: 'dryRun',
      })
      if (result.proposedChanges && result.proposedChanges.length > 0) {
        setDryRunResult(result)
        setPendingAction(pending)
        setStage('preview')
        return
      }
    }
    await advanceFromPreview(pending)
  }

  // --- Step 2: after PreviewDialog ---
  async function advanceFromPreview(pending: PendingAction): Promise<void> {
    if (pending.auditReasonRequired) {
      setAuditReason('')
      setPendingAction(pending)
      setStage('audit')
      return
    }
    await doExecute(pending.actionKey, pending.payload)
    resetDialogs()
  }

  // --- Step 3: after AuditReasonDialog ---
  async function advanceFromAudit(): Promise<void> {
    if (!pendingAction) return
    await doExecute(pendingAction.actionKey, pendingAction.payload, auditReason)
    resetDialogs()
  }

  function resetDialogs(): void {
    setPendingAction(null)
    setStage(null)
    setDryRunResult(null)
    setAuditReason('')
    setActionError(null)
    setValidationErrors([])
  }

  // --- Empty entity guard ---
  if (!entityId) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 p-12 text-center">
        <AlertCircle className="h-10 w-10 text-muted-foreground" />
        <div>
          <p className="text-lg font-medium">Kein Datensatz ausgewählt</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Bitte wählen Sie einen Eintrag aus der Liste aus, um die Details anzuzeigen.
          </p>
        </div>
        <Button variant="outline" onClick={() => void navigate({ to: -1 as never })}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Zurück zur Liste
        </Button>
      </div>
    )
  }

  // --- Error state ---
  if (schemaQuery.error || runtime.entityError) {
    const errMsg = getAxiosErrorMessage(schemaQuery.error ?? runtime.entityError)
    const isNotFound =
      errMsg?.includes('404') ||
      errMsg?.toLowerCase().includes('not found') ||
      errMsg?.toLowerCase().includes('valid uuid') ||
      errMsg?.toLowerCase().includes('uuid_parsing')
    return (
      <div className="flex flex-col items-center justify-center gap-4 p-12 text-center">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <div>
          <p className="text-lg font-medium">
            {isNotFound ? 'Datensatz nicht gefunden' : 'Fehler beim Laden'}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            {isNotFound ? 'Der angeforderte Datensatz existiert nicht oder wurde gelöscht.' : errMsg}
          </p>
        </div>
        <Button variant="outline" onClick={() => void navigate({ to: -1 as never })}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Zurück
        </Button>
      </div>
    )
  }

  if (!runtime.plan) {
    return (
      <div className="border-b bg-muted/30 px-4 py-2 text-sm text-muted-foreground md:px-8">
        Wird geladen…
      </div>
    )
  }

  return (
    <>
      <div data-testid={testId ?? `native-detail-${screenId.replace('/', '-')}`} data-runtime="native">
        {runtime.isEntityLoading && (
          <div className="border-b bg-muted/30 px-4 py-2 text-sm text-muted-foreground md:px-8">
            Daten werden geladen…
          </div>
        )}
        {actionRuntime.loadingActionKey && (
          <div className="border-b bg-muted/30 px-4 py-2 text-sm text-muted-foreground md:px-8">
            Aktion wird ausgefuehrt...
          </div>
        )}
        {actionError && (
          <div className="flex items-start gap-2 border-b border-destructive/30 bg-destructive/10 px-4 py-2 text-sm text-destructive md:px-8" role="alert">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{actionError}</span>
          </div>
        )}
        {validationErrors.length > 0 && (
          <div className="border-b border-destructive/30 bg-destructive/10 px-4 py-2 text-sm text-destructive md:px-8" role="alert">
            <div className="flex items-center gap-2 font-medium">
              <AlertCircle className="h-4 w-4" />
              Validierungsfehler:
            </div>
            <ul className="mt-1 list-inside list-disc space-y-0.5">
              {validationErrors.map((e, i) => (
                <li key={i}>{e.field ? <strong>{e.field}:</strong> : null} {e.message}</li>
              ))}
            </ul>
          </div>
        )}
        <UniversalMaskRenderer
          plan={runtime.plan}
          data={runtime.entityData}
          entityId={entityId}
          tables={runtime.tableRows}
          tableQueryStates={runtime.tableQueryStates}
          tableTotals={runtime.tableTotals}
          lookupBindings={runtime.lookupBindings}
          onTabChange={onTabChange}
          onTableQueryChange={runtime.setTableQuery}
          overlay={runtime.userOverlay}
          onOverlayChange={runtime.updateUserOverlay}
          onOverlayReset={runtime.resetUserOverlay}
          onAction={handleAction}
        />
      </div>

      {/* UIX-047: Confirmation Dialog — danger-aware styling */}
      <AlertDialog
        open={stage === 'confirm'}
        onOpenChange={(open) => { if (!open) resetDialogs() }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              {pendingAction?.dangerLevel === 'critical' || pendingAction?.dangerLevel === 'high' ? (
                <ShieldAlert className="h-5 w-5 text-destructive" />
              ) : pendingAction?.dangerLevel === 'moderate' ? (
                <AlertTriangle className="h-5 w-5 text-amber-500" />
              ) : null}
              Aktion bestätigen
            </AlertDialogTitle>
            <AlertDialogDescription asChild>
              <div>
                <p>
                  Möchten Sie <strong>{pendingAction?.label}</strong> wirklich ausführen?
                </p>
                {(pendingAction?.dangerLevel === 'critical' || pendingAction?.dangerLevel === 'high') && (
                  <p className="mt-2 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm font-medium text-destructive">
                    Diese Aktion ist unwiderruflich und kann weitreichende Folgen haben.
                  </p>
                )}
                {pendingAction?.dangerLevel === 'moderate' && (
                  <p className="mt-2 text-sm text-amber-700">
                    Diese Aktion kann nicht ohne weiteres rückgängig gemacht werden.
                  </p>
                )}
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={resetDialogs}>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              className={
                pendingAction?.dangerLevel === 'critical' || pendingAction?.dangerLevel === 'high'
                  ? 'bg-destructive text-destructive-foreground hover:bg-destructive/90'
                  : ''
              }
              onClick={() => {
                if (pendingAction) void advanceFromConfirm(pendingAction)
              }}
            >
              Bestätigen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* UIX-047: dryRun Preview Dialog — human-readable proposedChanges */}
      <Dialog open={stage === 'preview'} onOpenChange={(open) => { if (!open) resetDialogs() }}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Vorschau: {pendingAction?.label}</DialogTitle>
            <DialogDescription>
              Die folgenden Änderungen werden nach Bestätigung durchgeführt.
            </DialogDescription>
          </DialogHeader>
          <div className="rounded-md border bg-muted/40 p-3 text-sm">
            {dryRunResult?.proposedChanges && dryRunResult.proposedChanges.length > 0 ? (
              <ul className="space-y-1.5">
                {dryRunResult.proposedChanges.map((change, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-foreground/40" />
                    <span>{renderProposedChange(change, i)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-muted-foreground">Keine Vorab-Änderungen verfügbar.</p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={resetDialogs}>Abbrechen</Button>
            <Button
              onClick={() => {
                if (pendingAction) void advanceFromPreview(pendingAction)
              }}
            >
              Ausführen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* UIX-047: Audit Reason Dialog — min 10 chars, better hint */}
      <Dialog open={stage === 'audit'} onOpenChange={(open) => { if (!open) resetDialogs() }}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Begründung erforderlich</DialogTitle>
            <DialogDescription asChild>
              <div>
                <p>
                  Bitte geben Sie eine Begründung für <strong>{pendingAction?.label}</strong> an.
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Die Begründung wird im Audit-Log festgehalten und ist für Revisionen nachvollziehbar.
                </p>
              </div>
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="audit-reason">
              Begründung <span className="text-muted-foreground">(mindestens 10 Zeichen)</span>
            </Label>
            <Input
              id="audit-reason"
              value={auditReason}
              onChange={(e) => setAuditReason(e.target.value)}
              placeholder="z. B. Kundenwunsch, Fehlerkorrektur…"
              autoFocus
            />
            {auditReason.length > 0 && auditReason.trim().length < 10 && (
              <p className="text-xs text-destructive">
                Bitte mindestens 10 Zeichen eingeben ({10 - auditReason.trim().length} fehlen).
              </p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={resetDialogs}>Abbrechen</Button>
            <Button
              disabled={auditReason.trim().length < 10}
              onClick={() => void advanceFromAudit()}
            >
              Bestätigen & Ausführen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
