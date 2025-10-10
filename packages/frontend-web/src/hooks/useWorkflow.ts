import { useEffect, useState } from 'react'
import { useSSE } from '@/lib/sse'
import { useLive } from '@/state/live'

export type WorkflowState = 'draft' | 'pending' | 'approved' | 'posted' | 'rejected'
export type WorkflowAction = 'submit' | 'approve' | 'reject' | 'post'

export function useWorkflow(domain: 'sales' | 'purchase', number: string) {
  const [state, setState] = useState<WorkflowState>('draft')
  const [loading, setLoading] = useState(false)
  const setWorkflowEvent = useLive((s) => s.setWorkflowEvent)

  // SSE-Listener für Workflow-Events
  useSSE('workflow', (event: any) => {
    if (event.domain === domain && event.number === number) {
      setState(event.to as WorkflowState)
      setWorkflowEvent(event)
    }
  })

  async function fetchState() {
    try {
      const r = await fetch(`/api/workflow/${domain}/${number}`)
      const j = await r.json()
      if (j.ok) setState(j.state)
    } catch (e) {
      // Silent fail
    }
  }

  async function transition(action: WorkflowAction, payload: any) {
    setLoading(true)
    try {
      const r = await fetch(`/api/workflow/${domain}/${number}/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, ...payload })
      })
      const j = await r.json()
      if (j.ok) setState(j.state)
      return j
    } catch (e) {
      console.error('Failed to transition workflow:', e)
      return { ok: false, error: e instanceof Error ? e.message : 'Unknown error' }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (number) fetchState()
  }, [domain, number])

  return { state, transition, loading, refresh: fetchState }
}