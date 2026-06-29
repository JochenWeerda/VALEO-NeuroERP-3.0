/**
 * WorkflowRuntime — Phase 027
 *
 * Machine-readable workflow state for Human UI and AI Agents.
 * Derived from ScreenWorkflowDefinition + live API data.
 */

import type { ActionDangerLevel } from '../schema'

export interface WorkflowStatusInfo {
  /** Current status key (e.g. 'draft', 'approved', 'released') */
  currentStatus: string
  /** Human-readable status label */
  statusLabel: string
  /** Tone for visual indicator */
  tone: 'neutral' | 'success' | 'warning' | 'danger' | 'info'
}

export interface NextAllowedAction {
  actionKey: string
  label: string
  dangerLevel: ActionDangerLevel
  requiresConfirmation: boolean
  /** Why this action is available at this point in the workflow */
  rationale?: string
}

export interface BlockingReason {
  code: string
  message: string
  /** Which field or condition is blocking */
  context?: string
  /** True if this is a hard block (cannot proceed); false = soft warning */
  blocking: boolean
}

export interface AuditTrailEntry {
  timestamp: string
  actor: string
  actionKey: string
  fromStatus: string
  toStatus: string
  reason?: string
}

export interface PolicyHint {
  /** Policy rule identifier */
  ruleId: string
  message: string
  severity: 'info' | 'warning' | 'blocking'
  /** Suggested resolution for the user or agent */
  suggestion?: string
}

export interface WorkflowState {
  status: WorkflowStatusInfo
  nextAllowedActions: NextAllowedAction[]
  blockingReasons: BlockingReason[]
  auditTrail: AuditTrailEntry[]
  policyHints: PolicyHint[]
  /** True if any hard-blocking reason exists */
  isBlocked: boolean
  /** True if the entity is in a terminal status (no further transitions) */
  isTerminal: boolean
}

export function buildWorkflowState(raw: Partial<WorkflowState> | null | undefined): WorkflowState {
  if (!raw) {
    return {
      status: { currentStatus: 'unknown', statusLabel: 'Unbekannt', tone: 'neutral' },
      nextAllowedActions: [],
      blockingReasons: [],
      auditTrail: [],
      policyHints: [],
      isBlocked: false,
      isTerminal: false,
    }
  }
  const blockingReasons = raw.blockingReasons ?? []
  return {
    status: raw.status ?? { currentStatus: 'unknown', statusLabel: 'Unbekannt', tone: 'neutral' },
    nextAllowedActions: raw.nextAllowedActions ?? [],
    blockingReasons,
    auditTrail: raw.auditTrail ?? [],
    policyHints: raw.policyHints ?? [],
    isBlocked: blockingReasons.some((r) => r.blocking),
    isTerminal: raw.isTerminal ?? false,
  }
}
