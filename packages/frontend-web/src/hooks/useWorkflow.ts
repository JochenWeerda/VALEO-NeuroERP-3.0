import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSSE } from '@/lib/sse'
import { useLive } from '@/state/live'

export type WorkflowState = 'draft' | 'pending' | 'approved' | 'posted' | 'rejected'
export type WorkflowAction = 'submit' | 'approve' | 'reject' | 'post'

type WorkflowEventMessage = {
  domain: string
  number: string
  from: WorkflowState
  to: WorkflowState
  action: WorkflowAction
  performedBy: string
  performedAt: string
}

type WorkflowTransitionResponse = {
  ok: boolean
  state?: WorkflowState
  error?: string
}

type WorkflowStateResponse = {
  ok: boolean
  state: WorkflowState
}

interface WorkflowHook {
  state: WorkflowState
  loading: boolean
  transition: (action: WorkflowAction, payload?: Record<string, unknown>) => Promise<WorkflowTransitionResponse>
  refresh: () => Promise<void>
}

const isWorkflowEvent = (payload: unknown): payload is WorkflowEventMessage => {
  if (payload == null || typeof payload !== 'object') {
    return false
  }
  const candidate = payload as Partial<WorkflowEventMessage>
  return (
    typeof candidate.domain === 'string' &&
    typeof candidate.number === 'string' &&
    typeof candidate.to === 'string'
  )
}

export function useWorkflow(domain: 'sales' | 'purchase', number: string): WorkflowHook {
  const [state, setState] = useState<WorkflowState>('draft')
  const [loading, setLoading] = useState<boolean>(false)
  const setWorkflowEvent = useLive((store) => store.setWorkflowEvent)

  const handleWorkflowEvent = useCallback((event: unknown): void => {
    if (!isWorkflowEvent(event)) {
      return
    }
    if (event.domain === domain && event.number === number) {
      setState(event.to)
      const parsedTs = Date.parse(event.performedAt)
      setWorkflowEvent({
        domain: event.domain,
        number: event.number,
        from: event.from,
        to: event.to,
        action: event.action,
        ts: Number.isNaN(parsedTs) ? Date.now() : parsedTs,
      })
    }
  }, [domain, number, setWorkflowEvent])

  useSSE('workflow', handleWorkflowEvent)

  const fetchState = useCallback(async (): Promise<void> => {
    if (number.length === 0) {
      return
    }
    try {
      const response = await fetch(`/api/workflow/${domain}/${number}`)
      const payload = (await response.json()) as WorkflowStateResponse
      if (payload.ok) {
        setState(payload.state)
      }
    } catch {
      // ignore fetch errors, state remains unchanged
    }
  }, [domain, number])

  const transition = useCallback(async (
    action: WorkflowAction,
    payload: Record<string, unknown> = {},
  ): Promise<WorkflowTransitionResponse> => {
    setLoading(true)
    try {
      const response = await fetch(`/api/workflow/${domain}/${number}/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, ...payload }),
      })
      const json = (await response.json()) as WorkflowTransitionResponse
      if (json.ok && json.state) {
        setState(json.state)
      }
      return json
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      console.error('Failed to transition workflow:', message)
      return { ok: false, error: message }
    } finally {
      setLoading(false)
    }
  }, [domain, number])

  useEffect(() => {
    void fetchState()
  }, [fetchState])

  return useMemo(() => ({ state, loading, transition, refresh: fetchState }), [fetchState, loading, state, transition])
}
