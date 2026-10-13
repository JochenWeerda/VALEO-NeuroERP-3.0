import { useCallback, useRef, useState } from 'react'
import { apiClient } from '@/lib/api-client'
import type { ScreenActionDefinition } from '../schema'
import { prepareDocflowCommand, docflowCommandResult, docflowErrorResult } from './docflow-command-adapter'
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
  const intentRef = useRef<{ signature: string; key: string } | null>(null)

  const executeAction = useCallback(
    async (req: ActionRequest): Promise<ActionResult> => {
      if (pendingRef.current) {
        return { actionKey: req.actionKey, mode: req.mode, success: false, error: 'Aktion bereits aktiv.' }
      }

      const actionDef = actions.find((a) => a.key === req.actionKey)
      if (!actionDef) {
        return { actionKey: req.actionKey, mode: req.mode, success: false, error: `Unbekannte Aktion: ${req.actionKey}` }
      }

      const policy = buildActionPolicy(actionDef)

      const blocked = checkActionPolicy(policy, opts)
      if (blocked) {
        return { actionKey: req.actionKey, mode: req.mode, success: false, error: blocked }
      }

      if (actionDef.inputFlow) {
        return { actionKey: req.actionKey, mode: req.mode, success: false,
          error: 'Diese Aktion erfordert die Eingabe und Bestaetigung in der Maske.' }
      }

      // DocFlow exposes domain-command bodies, not the generic _mode envelope.
      // Until a versioned adapter is registered, a preview must never mutate a document.
      if (req.mode !== 'execute' && !actionDef.commandBinding && /^\/api\/v1\/docflow(?:\/|$)/.test(actionDef.commandEndpoint ?? '')) {
        return { actionKey: req.actionKey, mode: req.mode, success: false,
          error: 'DocFlow-Vorschau ist ohne passenden Command-Adapter gesperrt.' }
      }

      if (req.mode === 'execute' && !actionDef.commandBinding && /^\/api\/v1\/docflow(?:\/|$)/.test(actionDef.commandEndpoint ?? '')) {
        return { actionKey: req.actionKey, mode: req.mode, success: false, error: 'DocFlow-Command-Adapter fehlt.' }
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
        if (actionDef.commandBinding) {
          const signature = JSON.stringify([opts.screenId, opts.entityId, req.actionKey,
            req.expectedVersion ?? opts.entityData?.version, req.payload ?? {}, req.auditReason ?? '', actionDef.commandBinding])
          if (intentRef.current?.signature !== signature) {
            intentRef.current = { signature, key: crypto.randomUUID() }
          }
          const prepared = prepareDocflowCommand(actionDef, req, opts, req.idempotencyKey ?? intentRef.current.key)
          const response = await apiClient.request<unknown>({ method: 'POST', url: prepared.url, data: prepared.body })
          const result = docflowCommandResult(actionDef, req, opts, response.data)
          setLastResult(result)
          return result
        }
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
        if (actionDef.commandBinding) {
          const result = docflowErrorResult(req, err)
          setLastResult(result)
          return result
        }
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
