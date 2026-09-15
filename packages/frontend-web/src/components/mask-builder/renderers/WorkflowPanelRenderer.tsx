import { useMutation, useQueryClient } from '@tanstack/react-query'
import { AtSign, MessageSquareText, Send } from 'lucide-react'
import { type FormEvent, useMemo, useState } from 'react'
import { Callout, type CalloutVariant } from '@/components/ui/callout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { collabKeys, createEntityNote, useEntityNotes, type CollabMention, type CollabNote } from '@/lib/api/collab'
import type { ScreenContextRailSection, ScreenWorkflowDefinition } from '../schema'
import type { WorkflowState } from '../runtime/WorkflowRuntime'

const TONE_VARIANTS: Record<string, CalloutVariant> = {
  neutral: 'default',
  success: 'success',
  warning: 'warning',
  danger: 'error',
  info: 'info',
}

export function WorkflowPanelRenderer({
  workflow,
  workflowState,
  contextRailSections,
  entityType,
  entityId,
  currentUserId = 'dev-user',
}: {
  workflow?: ScreenWorkflowDefinition
  workflowState?: WorkflowState
  contextRailSections?: ScreenContextRailSection[]
  entityType?: string
  entityId?: string
  currentUserId?: string
}): JSX.Element | null {
  const workflowPanel = renderWorkflowPanel(workflow, workflowState)
  const showCollab = contextRailSections?.includes('collab') === true
  if (!showCollab) return workflowPanel

  return (
    <aside
      className="space-y-3"
      data-testid="context-rail"
      data-context-rail-sections={contextRailSections?.join(',')}
    >
      {workflowPanel}
      {entityType && entityId ? (
        <CollabRailSection entityType={entityType} entityId={entityId} currentUserId={currentUserId} />
      ) : null}
    </aside>
  )
}

function renderWorkflowPanel(
  workflow?: ScreenWorkflowDefinition,
  workflowState?: WorkflowState,
): JSX.Element | null {
  if (workflowState && workflowState.status.currentStatus !== 'unknown') {
    const { status, nextAllowedActions, blockingReasons, policyHints } = workflowState
    const toneVariant = TONE_VARIANTS[status.tone] ?? TONE_VARIANTS['neutral']
    return (
      <Callout
        variant={toneVariant}
        className="rounded-md p-4"
        data-testid="workflow-panel"
        data-status={status.currentStatus}
        data-blocked={workflowState.isBlocked}
      >
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">{status.statusLabel}</span>
          {workflowState.isTerminal && (
            <span className="text-xs opacity-70">Abgeschlossen</span>
          )}
        </div>

        {blockingReasons.filter((r) => r.blocking).length > 0 && (
          <ul className="mt-2 space-y-1" aria-label="Blockierende Gründe">
            {blockingReasons.filter((r) => r.blocking).map((r) => (
              <li key={r.code} className="text-xs text-destructive" data-block-code={r.code}>
                ⚠ {r.message}
              </li>
            ))}
          </ul>
        )}

        {nextAllowedActions.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1" aria-label="Nächste Aktionen">
            {nextAllowedActions.map((a) => (
              <span
                key={a.actionKey}
                className="rounded bg-background/60 px-2 py-0.5 text-xs"
                data-next-action={a.actionKey}
              >
                {a.label}
              </span>
            ))}
          </div>
        )}

        {policyHints.filter((h) => h.severity !== 'info').length > 0 && (
          <ul className="mt-2 space-y-1" aria-label="Hinweise">
            {policyHints.filter((h) => h.severity !== 'info').map((h) => (
              <li key={h.ruleId} className="text-xs opacity-80">
                {h.message}
              </li>
            ))}
          </ul>
        )}
      </Callout>
    )
  }

  // FSX-030/FSX-021: Der fruehere Platzhalter zeigte den internen Prozess-
  // schluessel ("Workflow: order-to-cash") in der Fachmaske. Das ist Technik im
  // Arbeitsbereich und sagt dem Sachbearbeiter nichts. Solange kein
  // WorkflowState vorliegt, gibt es hier nichts Ehrliches zu zeigen — der
  // Prozessstand gehoert dann ins Prozessband, das seine Phasen aus der
  // ScreenDefinition und seinen Stand aus dem WorkflowState bezieht.
  return null
}

function parseMentions(body: string, mentionDraft: string): CollabMention[] {
  const ids = new Set<string>()
  for (const match of body.matchAll(/@([A-Za-z0-9_.:-]+)/g)) {
    if (match[1]) ids.add(match[1])
  }
  const manual = mentionDraft.trim().replace(/^@/, '')
  if (manual) ids.add(manual)
  return [...ids].map((userId) => ({ user_id: userId }))
}

function CollabRailSection({
  entityType,
  entityId,
  currentUserId,
}: {
  entityType: string
  entityId: string
  currentUserId: string
}): JSX.Element {
  const [body, setBody] = useState('')
  const [mentionDraft, setMentionDraft] = useState('')
  const queryClient = useQueryClient()
  const queryKey = collabKeys.notes(entityType, entityId)
  const notesQuery = useEntityNotes(entityType, entityId)
  const notes = notesQuery.data ?? []
  const mentionCount = notes.filter((note) =>
    note.mentions.some((mention) => mention.user_id === currentUserId),
  ).length

  const previewMentions = useMemo(() => parseMentions(body, mentionDraft), [body, mentionDraft])
  const createMutation = useMutation({
    mutationFn: createEntityNote,
    onMutate: async (input) => {
      await queryClient.cancelQueries({ queryKey })
      const previous = queryClient.getQueryData<CollabNote[]>(queryKey) ?? []
      const optimistic: CollabNote = {
        id: `optimistic-${Date.now()}`,
        tenant_id: '',
        entity_type: input.entity_type,
        entity_id: input.entity_id,
        body: input.body,
        mentions: input.mentions,
        created_by: currentUserId,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        deleted_at: null,
      }
      queryClient.setQueryData<CollabNote[]>(queryKey, [...previous, optimistic])
      return { previous }
    },
    onError: (_error, _input, context) => {
      queryClient.setQueryData(queryKey, context?.previous ?? [])
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey })
    },
  })

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault()
    const trimmed = body.trim()
    if (!trimmed || createMutation.isPending) return
    try {
      await createMutation.mutateAsync({
        entity_type: entityType,
        entity_id: entityId,
        body: trimmed,
        mentions: previewMentions,
      })
      setBody('')
      setMentionDraft('')
    } finally {
      // React Query owns the mutation lifecycle; this block preserves submit reset invariants.
    }
  }

  return (
    <section
      className="rounded-md border border-border bg-background p-4 text-sm"
      data-testid="collab-rail"
      aria-label="Notizen"
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 font-medium">
          <MessageSquareText className="h-4 w-4" aria-hidden="true" />
          <span>Notizen</span>
        </div>
        <Badge variant={mentionCount > 0 ? 'default' : 'outline'} data-testid="collab-mention-badge">
          {mentionCount}
        </Badge>
      </div>

      <div className="mt-3 space-y-2" aria-live="polite">
        {notesQuery.isLoading && <p className="text-xs text-muted-foreground">Laedt...</p>}
        {notes.length === 0 && !notesQuery.isLoading && (
          <p className="text-xs text-muted-foreground">Keine Notizen</p>
        )}
        {notes.map((note) => (
          <article key={note.id} className="rounded border bg-muted/20 p-2" data-testid="collab-note">
            <p className="whitespace-pre-wrap text-sm">{note.body}</p>
            {note.mentions.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {note.mentions.map((mention) => (
                  <Badge key={mention.user_id} variant="secondary" className="text-[11px]">
                    @{mention.display ?? mention.user_id}
                  </Badge>
                ))}
              </div>
            )}
          </article>
        ))}
      </div>

      <form className="mt-3 space-y-2" onSubmit={(event) => { void handleSubmit(event) }}>
        <Textarea
          aria-label="Notiz"
          data-testid="collab-note-body"
          value={body}
          onChange={(event) => setBody(event.target.value)}
          placeholder="Notiz schreiben"
          rows={3}
        />
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <AtSign className="pointer-events-none absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" aria-hidden="true" />
            <Input
              aria-label="Mention"
              data-testid="collab-mention-input"
              className="pl-8"
              value={mentionDraft}
              onChange={(event) => setMentionDraft(event.target.value)}
              placeholder="user-id"
            />
          </div>
          <Button
            type="submit"
            size="icon"
            disabled={!body.trim() || createMutation.isPending}
            aria-label="Notiz senden"
            data-testid="collab-note-submit"
          >
            <Send className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      </form>
    </section>
  )
}
