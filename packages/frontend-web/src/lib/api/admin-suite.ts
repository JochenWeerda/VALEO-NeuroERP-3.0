import { useQuery } from '@tanstack/react-query'
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

export function useAdminSuiteReadiness() {
  return useQuery({
    queryKey: ['admin-suite', 'readiness'],
    queryFn: async () => (await apiClient.get<AdminSuiteReadiness>('/api/v1/admin-suite/readiness')).data,
    staleTime: 30 * 1000,
  })
}
