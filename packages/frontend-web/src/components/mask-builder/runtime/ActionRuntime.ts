/**
 * ActionRuntime — Phase 026
 *
 * Dual-optimized action execution contract for Human UI and AI Agents.
 * Same ScreenActionDefinition drives both paths — no separate agent logic.
 */

import type { ActionDangerLevel } from '../schema'

export type ActionExecutionMode = 'execute' | 'dryRun' | 'validate' | 'propose'

export interface ActionRequest {
  actionKey: string
  entityId?: string
  payload?: Record<string, unknown>
  mode: ActionExecutionMode
  /** Agent-supplied idempotency key (ignored for human-triggered execute) */
  idempotencyKey?: string
  /** Required when auditReasonRequired: true */
  auditReason?: string
}

export interface ActionResult {
  actionKey: string
  mode: ActionExecutionMode
  success: boolean
  /** Proposed changes (dryRun / propose mode — no side effects executed) */
  proposedChanges?: Record<string, unknown>[]
  /** Validation errors (validate / dryRun mode) */
  validationErrors?: Array<{ field?: string; message: string; severity: 'blocking' | 'warning' }>
  /** Human-readable summary of what would happen or what happened */
  summary?: string
  /** Downstream entity IDs created/modified */
  affectedIds?: string[]
  error?: string
}

export interface ActionPolicy {
  actionKey: string
  dangerLevel: ActionDangerLevel
  requiresConfirmation: boolean
  requiresHumanApproval: boolean
  auditReasonRequired: boolean
  /** Set by AgentMaskContract — agent may not call this action directly */
  forbiddenForAgents: boolean
  idempotencyKey?: string
}

export interface ActionRuntimeOptions {
  screenId: string
  entityId?: string
  permissions: string[]
  isAgentCaller?: boolean
}

/**
 * Checks whether an action is permitted given current permissions and caller type.
 * Returns a blocking reason string if blocked, undefined if allowed.
 */
export function checkActionPolicy(
  policy: ActionPolicy,
  opts: ActionRuntimeOptions,
): string | undefined {
  if (opts.isAgentCaller && policy.forbiddenForAgents) {
    return `Action "${policy.actionKey}" ist für Agent-Aufrufe gesperrt.`
  }
  if (opts.isAgentCaller && policy.requiresHumanApproval) {
    return `Action "${policy.actionKey}" erfordert menschliche Genehmigung.`
  }
  return undefined
}

/**
 * Builds an ActionPolicy from ScreenActionDefinition extended fields.
 * Safe defaults: assume safe, no confirmation required.
 */
export function buildActionPolicy(actionDef: {
  key: string
  dangerLevel?: ActionDangerLevel
  requiresConfirmation?: boolean
  humanApprovalRequired?: boolean
  auditReasonRequired?: boolean
  idempotencyKey?: string
  forbiddenForAgents?: boolean
}): ActionPolicy {
  return {
    actionKey: actionDef.key,
    dangerLevel: actionDef.dangerLevel ?? 'safe',
    requiresConfirmation: actionDef.requiresConfirmation ?? false,
    requiresHumanApproval: actionDef.humanApprovalRequired ?? false,
    auditReasonRequired: actionDef.auditReasonRequired ?? false,
    forbiddenForAgents: actionDef.forbiddenForAgents ?? false,
    idempotencyKey: actionDef.idempotencyKey,
  }
}
