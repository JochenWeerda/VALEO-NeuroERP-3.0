/**
 * Process Mining API Hooks — Gap 018
 * Ereignisbasierte Prozessbeobachtung: Bottlenecks, Top-Prozesse, Drilldown
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type ProcessSummary = {
  projection_key: string
  process_name: string
  total_executions: number
  avg_duration_sec: number
  p95_duration_sec: number
  error_rate_pct: number
  last_seen: string
}

export type ProcessBottleneck = {
  projection_key: string
  process_name: string
  bottleneck_type: 'duration' | 'error_rate' | 'queue_depth'
  severity: 'hoch' | 'mittel' | 'niedrig'
  current_value: number
  threshold_value: number
  affected_executions: number
  recommendation: string
}

export type ProcessMiningDrilldown = {
  projection_key: string
  process_name: string
  sla_target_sec: number
  sla_compliance_pct: number
  steps: Array<{
    step_name: string
    avg_duration_sec: number
    error_count: number
    is_bottleneck: boolean
  }>
  trend_7d: Array<{ date: string; executions: number; avg_duration_sec: number }>
}

export type ProcessMiningReport = {
  tenant_id: string
  generated_at: string
  total_processes: number
  processes: ProcessSummary[]
  bottlenecks: ProcessBottleneck[]
}

export function useProcessMiningTopProcesses(limit = 10) {
  return useQuery({
    queryKey: ['process-mining', 'top-processes', limit],
    queryFn: () => apiClient.get<ProcessSummary[]>(`/api/v1/process-mining/finance/top-processes?limit=${limit}`),
    staleTime: 60_000,
  })
}

export function useProcessMiningBottlenecks() {
  return useQuery({
    queryKey: ['process-mining', 'bottlenecks'],
    queryFn: () => apiClient.get<ProcessBottleneck[]>('/api/v1/process-mining/finance/bottlenecks'),
    staleTime: 60_000,
  })
}

export function useProcessMiningDrilldown(projectionKey: string) {
  return useQuery({
    queryKey: ['process-mining', 'drilldown', projectionKey],
    queryFn: () => apiClient.get<ProcessMiningDrilldown>(`/api/v1/process-mining/finance/drilldown/${projectionKey}`),
    enabled: !!projectionKey,
    staleTime: 30_000,
  })
}

export function useIdempotencyOverview() {
  return useQuery({
    queryKey: ['admin', 'idempotency-overview'],
    queryFn: () => apiClient.get<import('@/components/agent/IdempotencyMonitoringPanel').IdempotencyOverview>('/api/v1/process/actions/idempotency/overview'),
    staleTime: 30_000,
  })
}
