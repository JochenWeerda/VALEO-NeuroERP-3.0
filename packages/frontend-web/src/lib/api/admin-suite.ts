import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type ReadinessStatus = 'ready' | 'warning' | 'blocked' | 'unchecked'

export type ReadinessEvidence = {
  key: string
  label: string
  status: ReadinessStatus
  source: string
  evidence: string
  details: string[]
  checked_at: string
}

export type AdminSuiteReadiness = {
  status: ReadinessStatus
  score: number
  ready_count: number
  warning_count: number
  blocked_count: number
  unchecked_count: number
  evaluated_count: number
  checked_at: string
  evidence: ReadinessEvidence[]
}

export type SetupStepStatus = 'unchecked' | 'in_progress' | 'warning' | 'blocked' | 'completed'

export type SetupStep = {
  key: string
  label: string
  status: SetupStepStatus
  target_path?: string | null
  evidence?: string | null
  responsible?: string | null
  updated_at?: string | null
}

export type SetupSession = {
  tenant_id: string
  status: SetupStepStatus
  completed_count: number
  total_count: number
  updated_at?: string | null
  steps: SetupStep[]
}

export function useAdminSuiteReadiness() {
  return useQuery({
    queryKey: ['admin-suite', 'readiness'],
    queryFn: async () => (await apiClient.get<AdminSuiteReadiness>('/api/v1/admin-suite/readiness')).data,
    staleTime: 30 * 1000,
  })
}

export function useAdminSuiteSetup() {
  return useQuery({
    queryKey: ['admin-suite', 'setup'],
    queryFn: async () => (await apiClient.get<SetupSession>('/api/v1/admin-suite/setup')).data,
  })
}

export function useUpdateAdminSuiteSetupStep() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ key, status }: { key: string; status: SetupStepStatus }) =>
      (await apiClient.patch<SetupSession>(`/api/v1/admin-suite/setup/steps/${key}`, { status })).data,
    onSuccess: (data) => queryClient.setQueryData(['admin-suite', 'setup'], data),
  })
}
