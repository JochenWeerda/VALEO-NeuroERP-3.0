import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { buildWorkflowState, type WorkflowState } from './WorkflowRuntime'

export interface UseWorkflowStateOptions {
  screenId: string
  entityId?: string
  workflowEndpoint?: string
  enabled?: boolean
  staleTimeMs?: number
}

export interface UseWorkflowStateResult {
  workflowState: WorkflowState
  isLoading: boolean
  error: unknown
  refetch: () => void
}

/**
 * Fetches and normalizes workflow state for a screen entity.
 *
 * The backend endpoint should return a WorkflowState-shaped payload.
 * If no endpoint is configured, returns a safe empty state.
 */
export function useWorkflowState({
  screenId,
  entityId,
  workflowEndpoint,
  enabled = true,
  staleTimeMs = 30_000,
}: UseWorkflowStateOptions): UseWorkflowStateResult {
  const resolvedEndpoint = useMemo(() => {
    if (!workflowEndpoint || !entityId) return undefined
    return workflowEndpoint
      .replace('{entity_id}', entityId)
      .replace('{screen_id}', screenId)
  }, [workflowEndpoint, entityId, screenId])

  const query = useQuery({
    queryKey: ['workflow-state', screenId, entityId],
    queryFn: async () => {
      if (!resolvedEndpoint) return null
      const res = await apiClient.get<Partial<WorkflowState>>(resolvedEndpoint)
      return res.data
    },
    enabled: enabled && Boolean(resolvedEndpoint),
    staleTime: staleTimeMs,
  })

  const workflowState = useMemo(
    () => buildWorkflowState(query.data),
    [query.data],
  )

  return {
    workflowState,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  }
}
