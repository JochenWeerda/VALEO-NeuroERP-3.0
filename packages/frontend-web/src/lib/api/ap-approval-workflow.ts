import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type APApprovalStatus = 'not_requested' | 'pending' | 'partially_approved' | 'approved' | 'rejected'

type ExplainabilityDetail = {
  label: string
  value: string
}

export type APApprovalStatusResponse = {
  invoice_id: string
  status: APApprovalStatus
  required_approvals: number
  current_approvals: number
  approvals: Array<Record<string, unknown>>
  rejections: Array<Record<string, unknown>>
  applicable_rule: Record<string, unknown> | null
  can_post: boolean
  can_pay: boolean
  override_resolution: Record<string, unknown>
  explainability: {
    status: 'allowed' | 'blocked' | 'approval-required' | 'exception'
    summary: string
    rule_id?: string
    reason?: string
    source_scope?: string
    details?: ExplainabilityDetail[]
  }
}

type APApprovalRequestPayload = {
  invoice_id: string
  requested_by: string
  comment?: string
}

type APApprovalActionPayload = {
  invoice_id: string
  approved_by: string
  action: 'approve' | 'reject'
  comment?: string
}

export const apApprovalKeys = {
  all: ['ap-approval-workflow'] as const,
  status: (invoiceId: string) => [...apApprovalKeys.all, 'status', invoiceId] as const,
}

export function useAPApprovalStatus(invoiceId: string) {
  return useQuery({
    queryKey: apApprovalKeys.status(invoiceId),
    queryFn: async () =>
      (
        await apiClient.get<APApprovalStatusResponse>(
          `/api/v1/ap/approval-workflow/status/${encodeURIComponent(invoiceId)}`
        )
      ).data,
    enabled: invoiceId.length > 0,
  })
}

export function useRequestAPApproval() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (payload: APApprovalRequestPayload) =>
      (
        await apiClient.post<APApprovalStatusResponse>(
          '/api/v1/ap/approval-workflow/request',
          payload
        )
      ).data,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: apApprovalKeys.status(data.invoice_id) })
    },
  })
}

export function useActOnAPApproval() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (payload: APApprovalActionPayload) =>
      (
        await apiClient.post<APApprovalStatusResponse>(
          '/api/v1/ap/approval-workflow/approve',
          payload
        )
      ).data,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: apApprovalKeys.status(data.invoice_id) })
    },
  })
}
