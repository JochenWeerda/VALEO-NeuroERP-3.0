/**
 * Workflows API Hooks
 * TanStack Query hooks for Agent Workflow management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// Types
export type WorkflowProposal = {
  created_at: string
  items: Array<{
    article_id: string
    article_name: string
    order_quantity: number
    reason: string
    estimated_cost: number
  }>
  total_estimated_cost: number
}

export type WorkflowStatus = {
  workflow_id: string
  status: 'pending_approval' | 'completed' | 'rejected'
  proposal?: WorkflowProposal
  order_id?: string
  created_at?: string
}

export type ApprovalRequest = {
  approved: boolean
  rejection_reason?: string
}

// Query Keys
export const workflowKeys = {
  all: ['workflows'] as const,
  status: (id: string) => [...workflowKeys.all, 'status', id] as const,
}

// Hooks
// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function useWorkflowStatus(workflowId: string) {
  return useQuery({
    queryKey: workflowKeys.status(workflowId),
    queryFn: async () => {
      const response = await apiClient.get<WorkflowStatus>(
        `/api/v1/agents/bestellvorschlag/status/${workflowId}`
      )
      return response.data
    },
    enabled: !!workflowId,
    refetchInterval: (data) => {
      // Stop polling if workflow is completed or rejected
      if (data?.status === 'completed' || data?.status === 'rejected') {
        return false
      }
      return 5000 // Poll every 5 seconds while pending
    },
  })
}

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function useTriggerWorkflow() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (tenant_id = 'system') => {
      const response = await apiClient.post('/api/v1/agents/bestellvorschlag/trigger', {
        tenant_id,
        parameters: {}
      })
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: workflowKeys.status(data.workflow_id) })
    },
  })
}

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function useApproveWorkflow() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ 
      workflowId, 
      approved, 
      rejection_reason 
    }: { 
      workflowId: string
      approved: boolean
      rejection_reason?: string
    }) => {
      const response = await apiClient.post(
        `/api/v1/agents/bestellvorschlag/approve/${workflowId}`,
        { approved, rejection_reason }
      )
      return response.data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: workflowKeys.status(variables.workflowId) })
    },
  })
}

