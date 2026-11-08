/**
 * Authoring-Formular fuer WorkspaceComposition (Slots, Views, Metadaten).
 * Host mountet getrennt — Form schreibt nur Draft/Metadaten.
 */

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import {
  patchWorkspaceCompositionMeta,
  setSpecializedHostView,
  upsertReleasedScreenView,
  type ReleasedScreenRef,
} from './workspace-composition-authoring'
import {
  SPECIALIZED_COMPONENT_KINDS,
  normalizeWorkspaceComposition,
  type SpecializedComponentKind,
  type WorkspaceComposition,
  type WorkspaceCompositionIssue,
} from './workspace-composition'
import {
  isSpecializedKindEnabled,
  moveWorkspaceView,
  setSpecializedKindEnabled,
} from './workspace-composition-session'
import { WORKSPACE_COMPOSITION_FIXTURE } from './workspace-composition.fixture'

const SLOT_LABELS: Record<SpecializedComponentKind, string> = {
  inbox: 'Document-Inbox',
  disposition_board: 'Dispo-Tafel',
}

export type WorkspaceCompositionAuthoringFormProps = {
  draft: WorkspaceComposition
  issues: WorkspaceCompositionIssue[]
  catalog?: WorkspaceComposition
  /** Optional: freigegebene ScreenDefinition nach Studio-Freigabe. */
  releasedScreen?: ReleasedScreenRef | null
  saveMessage?: string | null
  onDraftChange: (_next: WorkspaceComposition) => void
  onSave: () => void
  onReset: () => void
  /** Speichern/Reset-Buttons ausblenden (Dialog-Footer uebernimmt). */
  hideActions?: boolean
  className?: string
}

export function WorkspaceCompositionAuthoringForm({
  draft,
  issues,
  catalog = WORKSPACE_COMPOSITION_FIXTURE,
  releasedScreen = null,
  saveMessage = null,
  onDraftChange,
  onSave,
  onReset,
  hideActions = false,
  className,
}: WorkspaceCompositionAuthoringFormProps): JSX.Element {
  const orderedViews = normalizeWorkspaceComposition(draft).views
  const enabledKinds = SPECIALIZED_COMPONENT_KINDS.filter((kind) =>
    isSpecializedKindEnabled(draft, kind),
  )

  return (
    <section
      className={className ?? 'flex flex-col gap-4'}
      data-testid="workspace-composition-composer"
      aria-label="Composition zusammensetzen"
    >
      <fieldset className="flex flex-col gap-2">
        <legend className="text-2xs tracking-wide uppercase text-muted-foreground">
          Metadaten
        </legend>
        <div className="flex flex-col gap-1">
          <Label htmlFor="workspace-composition-title">Titel</Label>
          <Input
            id="workspace-composition-title"
            value={draft.title}
            onChange={(event) =>
              onDraftChange(patchWorkspaceCompositionMeta(draft, { title: event.target.value }))
            }
            data-testid="workspace-composition-meta-title"
          />
        </div>
        <div className="flex flex-col gap-1">
          <Label htmlFor="workspace-composition-description">Beschreibung</Label>
          <Input
            id="workspace-composition-description"
            value={draft.description ?? ''}
            onChange={(event) =>
              onDraftChange(
                patchWorkspaceCompositionMeta(draft, {
                  description: event.target.value,
                }),
              )
            }
            data-testid="workspace-composition-meta-description"
          />
        </div>
        <div className="flex flex-col gap-1">
          <Label htmlFor="workspace-composition-default-view">Standard-View</Label>
          <NativeSelect
            id="workspace-composition-default-view"
            value={draft.defaultViewId ?? ''}
            onChange={(event) =>
              onDraftChange(
                patchWorkspaceCompositionMeta(draft, {
                  defaultViewId: event.target.value || null,
                }),
              )
            }
            data-testid="workspace-composition-meta-default-view"
          >
            <option value="">— keine —</option>
            {orderedViews.map((view) => (
              <option key={view.id} value={view.id}>
                {view.label} ({view.screenId})
              </option>
            ))}
          </NativeSelect>
        </div>
      </fieldset>

      <fieldset className="flex flex-col gap-2">
        <legend className="text-2xs tracking-wide uppercase text-muted-foreground">
          Spezial-Slots
        </legend>
        {SPECIALIZED_COMPONENT_KINDS.map((kind) => {
          const enabled = isSpecializedKindEnabled(draft, kind)
          const hostViewId =
            draft.specializedComponents.find((slot) => slot.kind === kind)?.hostViewId ?? ''
          return (
            <div
              key={kind}
              className="flex flex-col gap-2 rounded-(--radius) border border-border px-3 py-2"
            >
              <label
                className="flex min-h-11 items-center gap-2 text-sm"
                data-testid={`workspace-composition-toggle-${kind}`}
              >
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={(event) =>
                    onDraftChange(
                      setSpecializedKindEnabled(draft, kind, event.target.checked, catalog),
                    )
                  }
                />
                <span>{SLOT_LABELS[kind]}</span>
                <span className="text-xs text-muted-foreground">({kind})</span>
              </label>
              {enabled ? (
                <div className="flex flex-col gap-1 pl-6">
                  <Label htmlFor={`workspace-composition-host-${kind}`}>Host-View</Label>
                  <NativeSelect
                    id={`workspace-composition-host-${kind}`}
                    value={hostViewId}
                    onChange={(event) =>
                      onDraftChange(setSpecializedHostView(draft, kind, event.target.value))
                    }
                    data-testid={`workspace-composition-host-${kind}`}
                  >
                    {orderedViews.map((view) => (
                      <option key={view.id} value={view.id}>
                        {view.label}
                      </option>
                    ))}
                  </NativeSelect>
                </div>
              ) : null}
            </div>
          )
        })}
      </fieldset>

      <div className="flex flex-col gap-2">
        <p className="text-2xs tracking-wide uppercase text-muted-foreground">Views</p>
        <ol className="flex flex-col gap-2" data-testid="workspace-composition-view-editor">
          {orderedViews.map((view, index) => (
            <li
              key={view.id}
              className="flex flex-wrap items-center gap-2 rounded-(--radius) border border-border px-3 py-2"
              data-testid={`workspace-composition-view-row-${view.id}`}
            >
              <span className="min-w-0 flex-1 text-sm">
                {view.label}
                <span className="ml-2 text-xs text-muted-foreground">{view.screenId}</span>
              </span>
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={index === 0}
                onClick={() => onDraftChange(moveWorkspaceView(draft, view.id, 'up'))}
                data-testid={`workspace-composition-view-up-${view.id}`}
              >
                Nach oben
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={index === orderedViews.length - 1}
                onClick={() => onDraftChange(moveWorkspaceView(draft, view.id, 'down'))}
                data-testid={`workspace-composition-view-down-${view.id}`}
              >
                Nach unten
              </Button>
            </li>
          ))}
        </ol>
      </div>

      {releasedScreen ? (
        <div
          className="flex flex-col gap-2 rounded-(--radius) border border-border bg-muted/30 p-3"
          data-testid="workspace-composition-released-screen"
        >
          <p className="text-2xs tracking-wide uppercase text-muted-foreground">
            Freigegebene ScreenDefinition
          </p>
          <p className="text-sm">
            {releasedScreen.label}
            <span className="ml-2 text-xs text-muted-foreground">{releasedScreen.screenId}</span>
          </p>
          <Button
            type="button"
            variant="outline"
            onClick={() =>
              onDraftChange(
                upsertReleasedScreenView(draft, { ...releasedScreen, asDefault: true }),
              )
            }
            data-testid="workspace-composition-add-released"
          >
            Als View in Arbeitsraum aufnehmen
          </Button>
        </div>
      ) : null}

      {!hideActions ? (
        <div className="flex flex-wrap gap-2">
          <Button type="button" onClick={onSave} data-testid="workspace-composition-save">
            Speichern
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={onReset}
            data-testid="workspace-composition-reset"
          >
            Fixture laden
          </Button>
        </div>
      ) : null}

      {saveMessage ? (
        <p className="text-sm text-status-success" data-testid="workspace-composition-save-ok">
          {saveMessage}
        </p>
      ) : null}

      {enabledKinds.length === 0 ? (
        <p className="text-xs text-muted-foreground" data-testid="workspace-composition-no-slots">
          Keine Spezial-Slots aktiv — Host zeigt nur Views-Band (Studio) bzw. leere Slots (embedded).
        </p>
      ) : null}

      {issues.length > 0 ? (
        <div
          role="alert"
          className="rounded-(--radius) border border-status-error/40 bg-status-error/5 p-3"
          data-testid="workspace-composition-issues"
        >
          <p className="text-sm font-medium text-status-error">
            Composition ungültig — Host wird nicht gemountet
          </p>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-foreground">
            {issues.map((issue) => (
              <li key={`${issue.path}:${issue.code}`}>
                <code className="text-xs">{issue.path || '(root)'}</code>
                {' · '}
                {issue.message}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  )
}
