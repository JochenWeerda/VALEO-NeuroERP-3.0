/**
 * Studio-Dialog: WorkspaceComposition authoren (Slots/Inbox/Dispo, Views, Metadaten).
 * Persistenz: bestehendes localStorage/Fixture-Muster — kein Server-Write.
 * Host bleibt getrennt (WorkspaceCompositionHost).
 */

import { useCallback, useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { WorkspaceCompositionAuthoringForm } from './WorkspaceCompositionAuthoringForm'
import {
  type ReleasedScreenRef,
} from './workspace-composition-authoring'
import { WORKSPACE_COMPOSITION_FIXTURE } from './workspace-composition.fixture'
import {
  type WorkspaceComposition,
  type WorkspaceCompositionIssue,
} from './workspace-composition'
import {
  clearWorkspaceCompositionSession,
  initialWorkspaceCompositionDraft,
  resolveComposableWorkspace,
  saveWorkspaceCompositionSession,
  workspaceCompositionStorageKey,
} from './workspace-composition-session'

export type WorkspaceCompositionAuthoringDialogProps = {
  open: boolean
  onOpenChange: (_open: boolean) => void
  /** Auth-Sub fuer Mandanten-Key; optional. */
  sub?: string | null
  tenantId?: string | null
  storage?: Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>
  catalog?: WorkspaceComposition
  /** Nach ScreenDefinition-Freigabe: View-Aufnahme anbieten. */
  releasedScreen?: ReleasedScreenRef | null
  /** Nach erfolgreichem Speichern — z. B. Preview/Host remounten. */
  onSaved?: (_composition: WorkspaceComposition) => void
  /** Draft-Aenderung live (optional, fuer Preview neben dem Dialog). */
  onDraftChange?: (_draft: WorkspaceComposition, _mounted: WorkspaceComposition | null, _issues: WorkspaceCompositionIssue[]) => void
}

type ComposeState = {
  draft: WorkspaceComposition
  mounted: WorkspaceComposition | null
  issues: WorkspaceCompositionIssue[]
}

function applyDraft(draft: WorkspaceComposition): ComposeState {
  const resolved = resolveComposableWorkspace(draft)
  if (!resolved.ok) {
    return { draft, mounted: null, issues: resolved.issues }
  }
  return { draft: resolved.composition, mounted: resolved.composition, issues: [] }
}

function loadCompose(
  storage: Pick<Storage, 'getItem'>,
  catalog: WorkspaceComposition,
  sub?: string | null,
  tenantId?: string | null,
): ComposeState {
  const initial = initialWorkspaceCompositionDraft(storage, catalog, sub, tenantId)
  return {
    draft: initial.draft,
    mounted: initial.mounted,
    issues: initial.issues,
  }
}

const noopStorage: Pick<Storage, 'getItem' | 'setItem' | 'removeItem'> = {
  getItem: () => null,
  setItem: () => undefined,
  removeItem: () => undefined,
}

export function WorkspaceCompositionAuthoringDialog({
  open,
  onOpenChange,
  sub = null,
  tenantId = null,
  storage,
  catalog = WORKSPACE_COMPOSITION_FIXTURE,
  releasedScreen = null,
  onSaved,
  onDraftChange,
}: WorkspaceCompositionAuthoringDialogProps): JSX.Element {
  const resolvedStorage =
    storage
    ?? (typeof localStorage !== 'undefined' ? localStorage : noopStorage)
  const storageKey = workspaceCompositionStorageKey(sub, tenantId)
  const [state, setState] = useState<ComposeState>(() =>
    loadCompose(resolvedStorage, catalog, sub, tenantId),
  )
  const [saveMessage, setSaveMessage] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!open) return
    const next = loadCompose(resolvedStorage, catalog, sub, tenantId)
    setState(next)
    setSaveMessage(null)
    onDraftChange?.(next.draft, next.mounted, next.issues)
    // Nur beim Oeffnen / Scope-Wechsel neu laden — nicht bei jedem onDraftChange.
  }, [open, sub, tenantId, catalog, resolvedStorage])

  const commitDraft = useCallback(
    (nextDraft: WorkspaceComposition) => {
      setSaveMessage(null)
      const next = applyDraft(nextDraft)
      setState(next)
      onDraftChange?.(next.draft, next.mounted, next.issues)
    },
    [onDraftChange],
  )

  const handleSave = useCallback(() => {
    if (saving) return
    setSaving(true)
    try {
      const result = saveWorkspaceCompositionSession(
        state.draft,
        resolvedStorage,
        sub,
        tenantId,
      )
      if (!result.ok) {
        const next = { draft: state.draft, mounted: null, issues: result.issues }
        setState(next)
        setSaveMessage(null)
        onDraftChange?.(next.draft, next.mounted, next.issues)
        return
      }
      const next = {
        draft: result.composition,
        mounted: result.composition,
        issues: [] as WorkspaceCompositionIssue[],
      }
      setState(next)
      setSaveMessage(`Gespeichert (${storageKey})`)
      onDraftChange?.(next.draft, next.mounted, next.issues)
      onSaved?.(result.composition)
    } finally {
      setSaving(false)
    }
  }, [
    saving,
    state.draft,
    resolvedStorage,
    sub,
    tenantId,
    storageKey,
    onDraftChange,
    onSaved,
  ])

  const handleReset = useCallback(() => {
    clearWorkspaceCompositionSession(resolvedStorage, sub, tenantId)
    const reset = applyDraft(catalog)
    setState(reset)
    setSaveMessage('Zurückgesetzt auf Fixture')
    onDraftChange?.(reset.draft, reset.mounted, reset.issues)
  }, [resolvedStorage, sub, tenantId, catalog, onDraftChange])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="max-h-[90vh] max-w-2xl overflow-y-auto"
        data-testid="workspace-composition-authoring-dialog"
        data-storage-key={storageKey}
      >
        <DialogHeader>
          <DialogTitle>Arbeitsraum zusammensetzen</DialogTitle>
          <DialogDescription>
            Slots (Inbox, Dispo-Tafel), Views und Metadaten lokal bearbeiten — Host nur bei
            gültiger Composition. Kein Server-Write.
          </DialogDescription>
        </DialogHeader>

        <WorkspaceCompositionAuthoringForm
          draft={state.draft}
          issues={state.issues}
          catalog={catalog}
          releasedScreen={releasedScreen}
          saveMessage={saveMessage}
          onDraftChange={commitDraft}
          onSave={handleSave}
          onReset={handleReset}
          hideActions
        />

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            type="button"
            variant="outline"
            onClick={handleReset}
            disabled={saving}
            data-testid="workspace-composition-dialog-reset"
          >
            Fixture laden
          </Button>
          <Button
            type="button"
            onClick={handleSave}
            disabled={saving || state.issues.length > 0}
            data-testid="workspace-composition-save"
          >
            {saving ? 'Speichern…' : 'Speichern'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
