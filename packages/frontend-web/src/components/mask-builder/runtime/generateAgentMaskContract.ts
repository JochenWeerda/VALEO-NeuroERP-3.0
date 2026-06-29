/**
 * Phase 029 — AgentMaskContract generation
 *
 * Derives a machine-readable AgentMaskContract from a ScreenDefinition.
 * This ensures one canonical source of truth for both Human UI and AI Agents.
 */

import type { AgentMaskContract, ScreenDefinition, ScreenFieldDefinition } from '../schema'

function collectAllFields(screen: ScreenDefinition): ScreenFieldDefinition[] {
  const fields: ScreenFieldDefinition[] = [...(screen.fields ?? [])]
  for (const tab of screen.tabs ?? []) {
    fields.push(...(tab.fields ?? []))
  }
  return fields
}

/**
 * Generates an AgentMaskContract from a ScreenDefinition.
 *
 * The generated contract is deterministic — same input → same output.
 * Pages can override or extend it by merging with `screen.agentContract`.
 */
export function generateAgentMaskContract(screen: ScreenDefinition): AgentMaskContract {
  const allFields = collectAllFields(screen)

  const readableFields = allFields.map((f) => f.key)
  const editableFields = allFields.filter((f) => !f.readOnly).map((f) => f.key)

  // Fields marked sensitive by convention: password, token, secret, iban, bic, konto
  const SENSITIVE_PATTERNS = /passw|token|secret|iban|bic|konto_nr|credit_card/i
  const sensitiveFields = allFields
    .filter((f) => SENSITIVE_PATTERNS.test(f.key) || SENSITIVE_PATTERNS.test(f.label))
    .map((f) => f.key)

  const availableActions = (screen.actions ?? []).map((action) => ({
    key: action.key,
    label: action.label,
    dangerLevel: action.dangerLevel ?? 'safe',
    requiresHumanApproval: action.humanApprovalRequired ?? false,
    requiresConfirmation: action.requiresConfirmation ?? false,
    permission: action.permission,
  }))

  const validationRules = allFields
    .filter((f) => f.required)
    .map((f) => ({
      fieldKey: f.key,
      rule: 'required',
      severity: 'blocking' as const,
    }))

  // Merge with explicit agentContract if provided on the screen
  const explicit = screen.agentContract

  return {
    screenId: screen.id,
    domain: screen.domain,
    schemaVersion: screen.schemaVersion,
    contractVersion: 1,
    businessPurpose: explicit?.businessPurpose ?? `${screen.title} — ${screen.domain}`,
    primaryEntity: explicit?.primaryEntity ?? screen.id.split('/').pop() ?? screen.id,
    readableFields: explicit?.readableFields ?? readableFields,
    editableFields: explicit?.editableFields ?? editableFields,
    sensitiveFields: explicit?.sensitiveFields ?? sensitiveFields,
    availableActions: explicit?.availableActions ?? availableActions,
    validationRules: explicit?.validationRules ?? validationRules,
    workflowRules: explicit?.workflowRules ?? [],
    auditRequirements: explicit?.auditRequirements ?? (screen.actions ?? [])
      .filter((a) => a.auditReasonRequired)
      .map((a) => ({
        actionKey: a.key,
        requiresReason: true,
        requiresEvidence: false,
      })),
    recommendedAgentTasks: explicit?.recommendedAgentTasks ?? [],
    forbiddenAgentTasks: explicit?.forbiddenAgentTasks ?? [],
    testSelectors: explicit?.testSelectors ?? {
      screenRoot: `[data-testid="screen-${screen.id}"]`,
      submitButton: '[data-testid="form-submit-btn"]',
      workflowPanel: '[data-testid="workflow-panel"]',
    },
    examplePrompts: explicit?.examplePrompts ?? [],
  }
}
