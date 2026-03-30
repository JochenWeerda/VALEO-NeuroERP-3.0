/**
 * Workflows API Hooks
 * TanStack Query hooks for Agent Workflow management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'
import { useTenant } from '@/hooks/useTenant'

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
  capability_key?: string
  runtime?: Record<string, unknown>
  result?: Record<string, unknown>
}

export type ApprovalRequest = {
  approved: boolean
  rejection_reason?: string
}

type NeuroAssistRunResponse = {
  run_id: string
  correlation_id: string
  capability_key: string
  status: 'pending_approval' | 'completed' | 'rejected'
  started_at: string
  runtime: Record<string, unknown>
  result: Record<string, unknown>
}

type NeuroAssistGateResponse = {
  run_id: string
  correlation_id: string
  capability_key: string
  started_at: string
  status: 'pending_approval' | 'completed' | 'rejected'
  runtime: Record<string, unknown>
  result: Record<string, unknown>
}

export type RunListItem = {
  run_id: string
  capability_key: string
  status: 'pending_approval' | 'completed' | 'rejected' | 'running' | 'failed'
  started_at: string
  result: Record<string, unknown>
  runtime?: Record<string, unknown>
}

// Query Keys
export const workflowKeys = {
  all: ['workflows'] as const,
  status: (id: string) => [...workflowKeys.all, 'status', id] as const,
  list: (status?: string) => [...workflowKeys.all, 'list', status ?? 'all'] as const,
}

// Hooks
export function useWorkflowStatus(workflowId: string) {
  return useQuery({
    queryKey: workflowKeys.status(workflowId),
    queryFn: async () => {
      const response = await apiClient.get<NeuroAssistRunResponse>(
        `/api/v1/agents/neuroassist/runs/${workflowId}`
      )
      const payload = response.data
      const result = payload.result ?? {}
      return {
        workflow_id: payload.run_id,
        status: payload.status,
        proposal: result.proposal as WorkflowProposal | undefined,
        order_id: result.order_id as string | undefined,
        created_at: (result.created_at as string | undefined) ?? payload.started_at,
        capability_key: payload.capability_key,
        runtime: payload.runtime,
        result,
      } satisfies WorkflowStatus
    },
    enabled: !!workflowId,
    initialData: null,
    refetchInterval: (query) => {
      // Stop polling if workflow is completed or rejected
      const data = query.state.data as any
      if (data?.status === 'completed' || data?.status === 'rejected') {
        return false
      }
      return 5000 // Poll every 5 seconds while pending
    },
  })
}

export function useTriggerWorkflow() {
  const queryClient = useQueryClient()
  const { tenantId } = useTenant()

  return useMutation({
    mutationFn: async (overrideTenantId?: string) => {
      const tid = overrideTenantId ?? tenantId
      const response = await apiClient.post<NeuroAssistRunResponse>('/api/v1/agents/neuroassist/runs', {
        capability_key: 'bestellvorschlag_assistant',
        tenant_id: tid,
        parameters: {},
      })
      return {
        workflow_id: response.data.run_id,
        correlation_id: response.data.correlation_id,
        status: response.data.status,
        started_at: response.data.started_at,
        capability_key: response.data.capability_key,
        runtime: response.data.runtime,
      }
    },
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: workflowKeys.status(data.workflow_id) })
    },
  })
}

export function useListRuns(statusFilter?: string) {
  return useQuery({
    queryKey: workflowKeys.list(statusFilter),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (statusFilter) params.set('status', statusFilter)
      params.set('limit', '50')
      const response = await apiClient.get<RunListItem[]>(
        `/api/v1/agents/neuroassist/runs?${params.toString()}`,
      )
      return response.data
    },
    refetchInterval: 10000,
  })
}

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
      const response = await apiClient.post<NeuroAssistGateResponse>(
        `/api/v1/agents/neuroassist/runs/${workflowId}/gates`,
        {
          gate_type: 'approval_gate',
          decision: approved ? 'approve' : 'reject',
          rejection_reason,
        }
      )
      return {
        workflow_id: response.data.run_id,
        approved,
        order_id: response.data.result.order_id as string | undefined,
        status: response.data.status,
        capability_key: response.data.capability_key,
        runtime: response.data.runtime,
      }
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: workflowKeys.status(variables.workflowId) })
    },
  })
}

