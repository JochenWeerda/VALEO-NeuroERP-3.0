import { useCallback, useRef, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import type { ScreenActionDefinition } from '../schema'
import {
  buildActionPolicy,
  checkActionPolicy,
  type ActionExecutionMode,
  type ActionRequest,
  type ActionResult,
  type ActionRuntimeOptions,
} from './ActionRuntime'

export interface UseActionRuntimeResult {
  executeAction: (_req: ActionRequest) => Promise<ActionResult>
  loadingActionKey: string | null
  lastResult: ActionResult | null
}

/**
 * Executes mask actions with policy enforcement, duplicate-submit guard,
 * and support for dryRun/validate/propose/execute modes.
 *
 * Both Human UI (execute) and AI Agent (dryRun/validate/propose) use this.
 */
export function useActionRuntime(
  actions: ScreenActionDefinition[],
  opts: ActionRuntimeOptions,
): UseActionRuntimeResult {
  const [loadingActionKey, setLoadingActionKey] = useState<string | null>(null)
  const [lastResult, setLastResult] = useState<ActionResult | null>(null)
  const pendingRef = useRef(false)

  const executeAction = useCallback(
    async (req: ActionRequest): Promise<ActionResult> => {
      if (pendingRef.current) {
        return { actionKey: req.actionKey, mode: req.mode, success: false, error: 'Aktion bereits aktiv.' }
      }

      const actionDef = actions.find((a) => a.key === req.actionKey)
      if (!actionDef) {
        return { actionKey: req.actionKey, mode: req.mode, success: false, error: `Unbekannte Aktion: ${req.actionKey}` }
      }

      const policy = buildActionPolicy({
        ...actionDef,
        forbiddenForAgents: false, // AgentMaskContract override applied at page level
      })

      const blocked = checkActionPolicy(policy, opts)
      if (blocked) {
        return { actionKey: req.actionKey, mode: req.mode, success: false, error: blocked }
      }

      if (!actionDef.commandEndpoint) {
        // No endpoint — stub result for actions not yet fully wired
        const result: ActionResult = {
          actionKey: req.actionKey,
          mode: req.mode,
          success: req.mode !== 'execute',
          summary: req.mode === 'execute'
            ? undefined
            : `[${req.mode}] Keine Endpunkt-Konfiguration für "${req.actionKey}".`,
          proposedChanges: req.mode !== 'execute' ? [] : undefined,
        }
        setLastResult(result)
        return result
      }

      pendingRef.current = true
      setLoadingActionKey(req.actionKey)

      try {
        const method = actionDef.method ?? 'POST'
        const endpoint = actionDef.commandEndpoint
          .replace('{entity_id}', opts.entityId ?? '')
          .replace('{screen_id}', opts.screenId)

        const body: Record<string, unknown> = {
          ...(req.payload ?? {}),
          ...(req.mode !== 'execute' ? { _mode: req.mode } : {}),
          ...(req.auditReason ? { _auditReason: req.auditReason } : {}),
          ...(req.idempotencyKey ? { _idempotencyKey: req.idempotencyKey } : {}),
        }

        const response = await apiClient.request<ActionResult>({
          method,
          url: endpoint,
          data: body,
        })

        const result: ActionResult = response.data
        setLastResult(result)
        return result
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unbekannter Fehler'
        const result: ActionResult = { actionKey: req.actionKey, mode: req.mode, success: false, error: errorMessage }
        setLastResult(result)
        return result
      } finally {
        pendingRef.current = false
        setLoadingActionKey(null)
      }
    },
    [actions, opts],
  )

  return { executeAction, loadingActionKey, lastResult }
}

/** Convenience wrapper for human-triggered execute */
export function useHumanActionDispatch(
  actions: ScreenActionDefinition[],
  opts: Omit<ActionRuntimeOptions, 'isAgentCaller'>,
): UseActionRuntimeResult {
  return useActionRuntime(actions, { ...opts, isAgentCaller: false })
}

/** Wrapper for AI agent callers — enforces humanApprovalRequired checks */
export function useAgentActionDispatch(
  actions: ScreenActionDefinition[],
  opts: Omit<ActionRuntimeOptions, 'isAgentCaller'>,
): UseActionRuntimeResult {
  return useActionRuntime(actions, { ...opts, isAgentCaller: true })
}

export type { ActionExecutionMode, ActionRequest, ActionResult }
