/**
 * ActionRuntime — Phase 026
 *
 * Dual-optimized action execution contract for Human UI and AI Agents.
 * Same ScreenActionDefinition drives both paths — no separate agent logic.
 */

import type { ActionDangerLevel } from '../schema'

export type ActionExecutionMode = 'execute' | 'dryRun' | 'validate' | 'propose'

/** Ausloeser einer Aktion — landet als trigger_source im Audit-Event (UIX-070). */
export type ActionTriggerSource = 'mask' | 'omnibox' | 'voice' | 'agent'

export interface ActionRequest {
  actionKey: string
  entityId?: string
  payload?: Record<string, unknown>
  mode: ActionExecutionMode
  /** Agent-supplied idempotency key (ignored for human-triggered execute) */
  idempotencyKey?: string
  /** Required when auditReasonRequired: true */
  auditReason?: string
  /** Herkunft des Ausloesers (Default 'mask') — fuers Audit (UIX-070). */
  triggerSource?: ActionTriggerSource
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

// ── Omnibox-NL-Sicherheitsmatrix (UIX-070) ───────────────────────────────────
// Einzige Quelle der Wahrheit fuer die Frage: was darf der Sprach-/Omnibox-Pfad
// mit einer Aktion tun? Die Matrix ist hart und spiegelt den Maskenpfad —
// tests/test_uix070_conversational_safety.py re-implementiert sie identisch als
// Gate ueber ALL_SCREEN_IDS. Zusammenhang:
//  - unavailable  : Aktion existiert im NL-Pfad nicht (forbiddenForAgents).
//  - navigateOnly : nur Navigation zur Maske, kein Draft (high/critical).
//  - ritual       : Command-Draft mit vollem Confirmation-Ritual (UIX-047).
//  - formPrefill  : Maske oeffnen + Felder vorfuellen, nichts armieren.
// Kein Pfad umgeht jemals eine Confirmation, die der Maskenpfad verlangt.

export type OmniboxActionDisposition = 'unavailable' | 'navigateOnly' | 'ritual' | 'formPrefill'

/** Konfidenz unter dieser Schwelle degradiert jeden Draft auf formPrefill. */
export const OMNIBOX_COMMAND_MIN_CONFIDENCE = 0.75

export function classifyOmniboxAction(
  policy: Pick<ActionPolicy, 'dangerLevel' | 'requiresConfirmation' | 'forbiddenForAgents'>,
  confidence: number,
): OmniboxActionDisposition {
  // 1. forbiddenForAgents → im NL-Pfad unsichtbar (wie fuer Agenten).
  if (policy.forbiddenForAgents) return 'unavailable'
  // 2. high/critical → niemals draftbar, nur Navigation zur Maske.
  if (policy.dangerLevel === 'high' || policy.dangerLevel === 'critical') return 'navigateOnly'
  // 3. Konfidenz zu niedrig → konservativ auf Vorfuellen degradieren (nichts armieren).
  if (confidence < OMNIBOX_COMMAND_MIN_CONFIDENCE) return 'formPrefill'
  // 4. moderate → immer Ritual.
  if (policy.dangerLevel === 'moderate') return 'ritual'
  // 5. safe → Ritual nur wenn die Maske Confirmation verlangt, sonst Vorfuellen.
  return policy.requiresConfirmation ? 'ritual' : 'formPrefill'
}
