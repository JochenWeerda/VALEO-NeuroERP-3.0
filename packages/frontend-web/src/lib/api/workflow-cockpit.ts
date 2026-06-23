import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type WfProcessStatus =
  | 'pending'
  | 'running'
  | 'blocked_external_gate'
  | 'failed'
  | 'completed'
  | 'compensated'

export type WfEvent = {
  event_id: string
  kind: string
  message: string
  occurred_at: string
  source: string
  payload: Record<string, unknown>
}

export type WfBlocker = {
  blocker_id: string
  blocker_type: string
  message: string
  external_system: string | null
  since: string
  retryable: boolean
  resolved: boolean
}

export type WfProcess = {
  process_instance_id: string
  tenant_id: string
  process_key: string
  status: WfProcessStatus
  correlation_id: string
  idempotency_key: string | null
  business_object_ref: string | null
  current_step: string | null
  created_at: string
  updated_at: string
  audit_ref: string | null
  active_blocker_count: number
  replayable: boolean
  blockers: WfBlocker[]
  events: WfEvent[]
}

export type WfSummary = {
  tenant_id: string
  total_processes: number
  by_status: Record<string, number>
  blocked_external_gate: number
  replayable: number
}

export const wfCockpitKeys = {
  summary: ['wf-cockpit-summary'] as const,
  processes: (status?: string, key?: string) => ['wf-cockpit-processes', status, key] as const,
  process: (id: string) => ['wf-cockpit-process', id] as const,
}

export function useWfSummary() {
  return useQuery({
    queryKey: wfCockpitKeys.summary,
    queryFn: async () => {
      const { data } = await apiClient.get<WfSummary>('/api/v1/workflow/cockpit/summary')
      return data
    },
    refetchInterval: 30_000,
  })
}

export function useWfProcesses(status?: string, processKey?: string) {
  return useQuery({
    queryKey: wfCockpitKeys.processes(status, processKey),
    queryFn: async () => {
      const { data } = await apiClient.get<WfProcess[]>('/api/v1/workflow/cockpit/processes', {
        params: {
          ...(status ? { status } : {}),
          ...(processKey ? { process_key: processKey } : {}),
        },
      })
      return data
    },
    refetchInterval: 30_000,
  })
}

export function useWfProcess(processInstanceId: string | null) {
  return useQuery({
    queryKey: wfCockpitKeys.process(processInstanceId ?? ''),
    queryFn: async () => {
      if (!processInstanceId) throw new Error('processInstanceId required')
      const { data } = await apiClient.get<WfProcess>(
        `/api/v1/workflow/cockpit/processes/${encodeURIComponent(processInstanceId)}`,
      )
      return data
    },
    enabled: Boolean(processInstanceId),
  })
}

export function useWfReplayRequest() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vars: { processInstanceId: string; requestedBy: string; reason: string }) => {
      const { data } = await apiClient.post(
        `/api/v1/workflow/cockpit/processes/${encodeURIComponent(vars.processInstanceId)}/replay-requests`,
        { requested_by: vars.requestedBy, reason: vars.reason },
      )
      return data
    },
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: wfCockpitKeys.processes() })
      void qc.invalidateQueries({ queryKey: wfCockpitKeys.process(vars.processInstanceId) })
      void qc.invalidateQueries({ queryKey: wfCockpitKeys.summary })
    },
  })
}

export function wfStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: 'Ausstehend',
    running: 'Läuft',
    blocked_external_gate: 'Ext. Gate blockiert',
    failed: 'Fehlgeschlagen',
    completed: 'Abgeschlossen',
    compensated: 'Kompensiert',
  }
  return labels[status] ?? status
}

export function wfStatusVariant(
  status: string,
): 'default' | 'secondary' | 'destructive' | 'outline' {
  if (status === 'completed' || status === 'compensated') return 'default'
  if (status === 'running') return 'secondary'
  if (status === 'failed' || status === 'blocked_external_gate') return 'destructive'
  return 'outline'
}
