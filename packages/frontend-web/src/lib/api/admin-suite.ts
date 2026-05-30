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

export type MigrationProfile = {
  key: string
  label: string
  status: 'available' | 'blocked' | 'planned'
  adapter?: string | null
  notes: string
}

export type MigrationBatch = {
  id: string
  tenant_id: string
  source_profile: string
  source_ref: string
  source_hash: string
  mapping_version: string
  dry_run: boolean
  status: 'dry_run' | 'staged' | 'reconciliation_pending' | 'approved' | 'blocked'
  reconciliation: Record<string, boolean>
  created_at: string
  updated_at: string
}

export type MigrationCockpit = {
  profiles: MigrationProfile[]
  batches: MigrationBatch[]
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

export function useAdminSuiteMigration() {
  return useQuery({
    queryKey: ['admin-suite', 'migration'],
    queryFn: async () => (await apiClient.get<MigrationCockpit>('/api/v1/admin-suite/migration')).data,
  })
}
