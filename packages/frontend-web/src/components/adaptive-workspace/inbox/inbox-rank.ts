import type { TypedFachaktion, WorkspaceSignal } from '@/workspace/types'
import { inboxOpenDecision } from './inbox-contract'
import type { InboxQueueItem, InboxQueueSnapshot } from './types'

/**
 * Dieselben geladenen Queue-Zeilen als situative Signale fuer rankWorkspaceItems.
 * Route nur ueber inboxOpenDecision. Leere Queue, 401 (hidden), Fehler und
 * pending liefern nichts. Approve und Buchung entstehen hier nicht.
 * Ein Live-Signal, das dieselbe Zeile schon zaehlt, wird nicht erneut angehaengt.
 * Der Sammelzaehler `queue-inbox` auf `workspace.document-inbox` ist keine Zeile.
 * Vorhandene Pruefcodes aus Unsicherheiten und Dubletten haengen am Signal.
 * Keine neue Pruefung, keine Positionszeilen, kein Approve.
 */
export function situationalItemsFromInboxQueue(
  state: InboxQueueSnapshot,
  live: readonly WorkspaceSignal[] = [],
): { actions: TypedFachaktion[]; signals: WorkspaceSignal[] } {
  if (state.status !== 'ready') {
    return { actions: [], signals: [] }
  }

  const actions: TypedFachaktion[] = []
  const signals: WorkspaceSignal[] = []
  const seen = new Set<string>()
  for (const item of state.items) {
    const decision = inboxOpenDecision(item)
    if (!decision.href || inboxItemBooks(item)) {
      continue
    }
    const actionId = `inbox.queue.${item.id}`
    if (seen.has(actionId)) {
      continue
    }
    seen.add(actionId)
    const signalId = `inbox:${item.id}`
    const liveForItem = live.filter((signal) =>
      signal.id !== 'queue-inbox'
      && signal.source !== 'queue:inbox'
      && (
        signal.id === signalId
        || signal.id === actionId
        || signal.relatedActionIds.includes(actionId)
        || signal.relatedActionIds.includes(item.id)
      ),
    )
    const action: TypedFachaktion = {
      id: actionId,
      label: decision.mode === 'overview'
        ? decision.actionLabel
        : (item.proposal.label.trim() || item.id),
      kind: 'navigate',
      layer: 'situational',
      keywords: [item.id, item.proposal.document_kind ?? '', item.proposal.label].filter((part) => part !== ''),
      requiredScopes: [],
      businessDomain: 'documents',
      target: { route: decision.href },
      mcpIntent: 'navigate',
      reasonTemplate: item.proposal.reason || item.proposal.label,
    }
    if (liveForItem.length > 0) {
      if (liveForItem.some((signal) => signal.relatedActionIds.includes(actionId))) {
        actions.push(action)
      }
      continue
    }
    actions.push(action)
    const reasonCodes = existingInboxReasonCodes(item)
    signals.push({
      id: signalId,
      kind: 'open-task',
      layer: 'situational',
      relatedActionIds: [actionId],
      severity: 3,
      source: 'inbox-queue',
      ...(reasonCodes.length > 0 ? { reasonCodes } : {}),
    })
  }
  return { actions, signals }
}

/** Codes, die Queue, Widget oder Vertrag schon tragen. Nichts neu berechnen. */
function existingInboxReasonCodes(item: InboxQueueItem): string[] {
  const codes: string[] = []
  const seen = new Set<string>()
  const push = (code: string | undefined): void => {
    const value = code?.trim()
    if (!value || seen.has(value)) return
    seen.add(value)
    codes.push(value)
  }
  for (const hint of item.uncertainties ?? []) push(hint.code)
  for (const hint of item.command.uncertainties ?? []) push(hint.code)
  for (const hint of item.command.prefill?.uncertainties ?? []) push(hint.code)
  const hasDuplicate = item.duplicates.length > 0
    || (item.command.duplicates?.length ?? 0) > 0
    || (item.command.prefill?.duplicates?.length ?? 0) > 0
  if (hasDuplicate) push('dublette')
  return codes
}

function inboxItemBooks(item: InboxQueueItem): boolean {
  // The trusted contract fixes these flags to false; decoded server payloads
  // can still violate it. Check their runtime values before ranking.
  const payload = item as unknown as {
    booking_allowed?: unknown
    command?: { executable?: unknown; booking?: unknown; prefill?: { booking?: unknown } }
  }
  return payload.booking_allowed === true
    || payload.command?.executable === true
    || payload.command?.booking === true
    || payload.command?.prefill?.booking === true
}
