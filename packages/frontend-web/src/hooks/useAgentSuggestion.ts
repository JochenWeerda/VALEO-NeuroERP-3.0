/**
 * useAgentSuggestion — Trigger a NeuroASSIST capability and poll for a suggestion.
 * Designed to live inside Wizard steps: fires on demand, shows inline Accept/Dismiss.
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type AgentSuggestionStatus =
  | 'idle'
  | 'loading'
  | 'ready'
  | 'accepted'
  | 'dismissed'
  | 'error'

export type AgentSuggestionState<T = Record<string, unknown>> = {
  suggestion: T | null
  isLoading: boolean
  status: AgentSuggestionStatus
  runId: string | null
  trigger: () => void
  accept: (overrideSuggestion?: T) => void
  dismiss: () => void
  reset: () => void
}

type RunResponse = {
  run_id: string
  status: string
  result: Record<string, unknown>
  started_at: string
  capability_key: string
  correlation_id: string
  runtime: Record<string, unknown>
}

export function useAgentSuggestion<T = Record<string, unknown>>(
  capabilityKey: string,
  parameters: Record<string, unknown>,
  options?: {
    extractSuggestion?: (run: RunResponse) => T | null
  },
): AgentSuggestionState<T> {
  const [runId, setRunId] = useState<string | null>(null)
  const [suggestionStatus, setSuggestionStatus] = useState<AgentSuggestionStatus>('idle')
  const [suggestion, setSuggestion] = useState<T | null>(null)

  // Keep parameters fresh without causing useCallback re-creation
  const parametersRef = useRef(parameters)
  parametersRef.current = parameters
  const extractRef = useRef(options?.extractSuggestion)
  extractRef.current = options?.extractSuggestion

  // Trigger: POST to start the run
  const triggerMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post<RunResponse>('/api/v1/agents/neuroassist/runs', {
        capability_key: capabilityKey,
        tenant_id: 'system',
        parameters: parametersRef.current,
      })
      return response.data
    },
  })

  // Poll: GET run status until completed/rejected
  const pollQuery = useQuery({
    queryKey: ['agent-suggestion', capabilityKey, runId],
    queryFn: async () => {
      if (!runId) throw new Error('runId required')
      const response = await apiClient.get<RunResponse>(`/api/v1/agents/neuroassist/runs/${runId}`)
      return response.data
    },
    enabled: !!runId && suggestionStatus === 'loading',
    refetchInterval: (query) => {
      const status = (query.state.data as RunResponse | undefined)?.status
      if (status === 'completed' || status === 'rejected' || status === 'failed') return false
      return 2000
    },
  })

  // React to poll result
  useEffect(() => {
    if (!pollQuery.data || suggestionStatus !== 'loading') return
    const { status, result } = pollQuery.data
    if (status === 'completed') {
      const extracted = extractRef.current
        ? extractRef.current(pollQuery.data)
        : (result as unknown as T)
      setSuggestion(extracted)
      setSuggestionStatus('ready')
    } else if (status === 'rejected' || status === 'failed') {
      setSuggestionStatus('error')
    }
  }, [pollQuery.data, suggestionStatus])

  const trigger = useCallback(() => {
    setSuggestionStatus('loading')
    setSuggestion(null)
    setRunId(null)
    triggerMutation.mutate(undefined, {
      onSuccess: (data) => setRunId(data.run_id),
      onError: () => setSuggestionStatus('error'),
    })
  }, [capabilityKey, triggerMutation])

  const accept = useCallback((override?: T) => {
    if (override !== undefined) setSuggestion(override)
    setSuggestionStatus('accepted')
  }, [])

  const dismiss = useCallback(() => {
    setSuggestion(null)
    setSuggestionStatus('dismissed')
  }, [])

  const reset = useCallback(() => {
    setSuggestion(null)
    setSuggestionStatus('idle')
    setRunId(null)
  }, [])

  return {
    suggestion,
    isLoading: suggestionStatus === 'loading' || triggerMutation.isPending,
    status: suggestionStatus,
    runId,
    trigger,
    accept,
    dismiss,
    reset,
  }
}
