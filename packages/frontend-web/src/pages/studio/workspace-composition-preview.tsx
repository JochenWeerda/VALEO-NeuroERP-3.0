/**
 * Studio-Preview: Arbeitsraum aus Metadaten zusammensetzen (lokal).
 * Speichert in localStorage valeo.workspace.composition — kein Server-Write.
 * Authoring: Formular + optionaler Studio-Dialog (nach ScreenDefinition-Freigabe).
 */

import { useCallback, useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'
import { auth } from '@/lib/auth'
import { tenantFromToken } from '@/lib/tenant-from-token'
import { WorkspaceCompositionAuthoringDialog } from '@/studio/WorkspaceCompositionAuthoringDialog'
import { WorkspaceCompositionAuthoringForm } from '@/studio/WorkspaceCompositionAuthoringForm'
import { WorkspaceCompositionHost } from '@/studio/WorkspaceCompositionHost'
import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  WORKSPACE_COMPOSITION_PREVIEW_ROUTE,
} from '@/studio/workspace-composition-runtime'
import {
  clearWorkspaceCompositionSession,
  initialWorkspaceCompositionDraft,
  resolveComposableWorkspace,
  saveWorkspaceCompositionSession,
  workspaceCompositionStorageKey,
} from '@/studio/workspace-composition-session'
import {
  type WorkspaceComposition,
  type WorkspaceCompositionIssue,
} from '@/studio/workspace-composition'

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

function loadCompose(sub?: string | null, tenantId?: string | null): ComposeState {
  const initial = initialWorkspaceCompositionDraft(localStorage, WORKSPACE_COMPOSITION_FIXTURE, sub, tenantId)
  return {
    draft: initial.draft,
    mounted: initial.mounted,
    issues: initial.issues,
  }
}

export default function WorkspaceCompositionPreviewPage(): JSX.Element {
  const { user } = useAuth()
  const sub = user?.sub ?? null
  const tenantId = tenantFromToken(auth.getAccessToken())
  const storageKey = workspaceCompositionStorageKey(sub, tenantId)
  const [state, setState] = useState<ComposeState>(() => loadCompose(sub, tenantId))
  const [saveMessage, setSaveMessage] = useState<string | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  useEffect(() => {
    setState(loadCompose(sub, tenantId))
  }, [sub, tenantId])

  const commitDraft = useCallback((nextDraft: WorkspaceComposition) => {
    setSaveMessage(null)
    setState(applyDraft(nextDraft))
  }, [])

  const handleSave = useCallback(() => {
    const result = saveWorkspaceCompositionSession(state.draft, localStorage, sub, tenantId)
    if (!result.ok) {
      setState({ draft: state.draft, mounted: null, issues: result.issues })
      setSaveMessage(null)
      return
    }
    setState({ draft: result.composition, mounted: result.composition, issues: [] })
    setSaveMessage(`Gespeichert in localStorage (${storageKey})`)
  }, [state.draft, storageKey, sub, tenantId])

  const handleReset = useCallback(() => {
    clearWorkspaceCompositionSession(localStorage, sub, tenantId)
    const reset = applyDraft(WORKSPACE_COMPOSITION_FIXTURE)
    setState(reset)
    setSaveMessage('Zurückgesetzt auf Fixture')
  }, [sub, tenantId])

  return (
    <main
      className="mx-auto flex w-full max-w-6xl flex-col gap-4 p-4"
      data-testid="workspace-composition-preview"
      data-preview-route={WORKSPACE_COMPOSITION_PREVIEW_ROUTE}
      data-storage-key={storageKey}
    >
      <header className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex flex-col gap-1">
          <h1 className="text-lg font-semibold tracking-tight">WorkspaceComposition Studio</h1>
          <p className="text-xs text-muted-foreground">
            Arbeitsraum aus Metadaten — Slots und View-Reihenfolge lokal, Host nur bei gültiger Composition
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          onClick={() => setDialogOpen(true)}
          data-testid="workspace-composition-open-authoring-dialog"
        >
          Authoring-Dialog
        </Button>
      </header>

      <div className="rounded-(--radius) border border-border bg-card p-4">
        <WorkspaceCompositionAuthoringForm
          draft={state.draft}
          issues={state.issues}
          catalog={WORKSPACE_COMPOSITION_FIXTURE}
          saveMessage={saveMessage}
          onDraftChange={commitDraft}
          onSave={handleSave}
          onReset={handleReset}
        />
      </div>

      <WorkspaceCompositionAuthoringDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        sub={sub}
        tenantId={tenantId}
        catalog={WORKSPACE_COMPOSITION_FIXTURE}
        onSaved={(composition) => {
          setState({ draft: composition, mounted: composition, issues: [] })
          setSaveMessage(`Gespeichert in localStorage (${storageKey})`)
        }}
        onDraftChange={(draft, mounted, issues) => {
          setState({ draft, mounted, issues })
        }}
      />

      {state.mounted ? (
        <WorkspaceCompositionHost
          key={`${state.mounted.id}:${state.mounted.studioVersion}:${state.mounted.views.map((v) => v.id).join(',')}:${state.mounted.specializedComponents.map((s) => s.id).join(',')}`}
          composition={state.mounted}
        />
      ) : (
        <p
          className="text-sm text-muted-foreground"
          data-testid="workspace-composition-host-skipped"
        >
          Kein Host-Mount — Composition zuerst korrigieren.
        </p>
      )}
    </main>
  )
}
