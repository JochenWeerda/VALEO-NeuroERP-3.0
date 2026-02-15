/**
 * Admin API Hooks
 * Error-first fetching without mock fallback data.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type AuditEntry = {
  id: string
  zeitstempel: string
  benutzer: string
  aktion: string
  objekt: string
  status: 'erfolg' | 'fehler'
}

export type Benutzer = {
  id: string
  name: string
  email: string
  rolle: string
  status: 'aktiv' | 'inaktiv'
  letzteAnmeldung: string
}

export type Rolle = {
  id: string
  name: string
  beschreibung: string
  benutzer: number
  rechte: number
}

export type MonitoringAlert = {
  id: string
  level: 'critical' | 'warning' | 'info'
  type: string
  message: string
  timestamp: string
}

export type MonitoringAlertsResponse = {
  active: number
  critical: number
  warning: number
  system_status: 'online' | 'degraded' | 'offline'
  items: MonitoringAlert[]
}

export type MonitoringRule = {
  id: string
  code: string
  name: string
  metric: string
  level: 'critical' | 'warning' | 'info'
  threshold: number | null
  operator: 'gt' | 'gte' | 'lt' | 'lte' | 'eq' | 'neq'
  active: boolean
  escalation_minutes: number
  channel_ids: string[]
}

export type MonitoringChannel = {
  id: string
  code: string
  name: string
  channel_type: 'email' | 'sms' | 'webhook' | 'chatops'
  target: string
  active: boolean
}

export type SchedulerJob = {
  id: string
  code: string
  name: string
  cron: string
  process: string
  active: boolean
  retry_max: number
  timeout_seconds: number
  channel_ids: string[]
}

export function useAuditLog() {
  return useQuery({
    queryKey: ['admin', 'audit-log'],
    queryFn: async () => (await apiClient.get<AuditEntry[]>('/api/v1/admin/audit-log')).data,
    staleTime: 30 * 1000,
  })
}

export function useBenutzer() {
  return useQuery({
    queryKey: ['admin', 'benutzer'],
    queryFn: async () => (await apiClient.get<Benutzer[]>('/api/v1/admin/benutzer')).data,
    staleTime: 2 * 60 * 1000,
  })
}

export function useRollen() {
  return useQuery({
    queryKey: ['admin', 'rollen'],
    queryFn: async () => (await apiClient.get<Rolle[]>('/api/v1/admin/rollen')).data,
    staleTime: 5 * 60 * 1000,
  })
}

export function useMonitoringAlerts() {
  return useQuery({
    queryKey: ['admin', 'monitoring', 'alerts'],
    queryFn: async () => (await apiClient.get<MonitoringAlertsResponse>('/api/v1/admin/monitoring/alerts')).data,
    staleTime: 30 * 1000,
  })
}

export function useMonitoringRules() {
  return useQuery({
    queryKey: ['admin', 'monitoring', 'rules'],
    queryFn: async () => (await apiClient.get<MonitoringRule[]>('/api/v1/admin/monitoring/rules')).data,
    staleTime: 60 * 1000,
  })
}

export function useMonitoringChannels() {
  return useQuery({
    queryKey: ['admin', 'monitoring', 'channels'],
    queryFn: async () => (await apiClient.get<MonitoringChannel[]>('/api/v1/admin/monitoring/channels')).data,
    staleTime: 60 * 1000,
  })
}

export function useSchedulerJobs() {
  return useQuery({
    queryKey: ['admin', 'monitoring', 'scheduler-jobs'],
    queryFn: async () => (await apiClient.get<SchedulerJob[]>('/api/v1/admin/monitoring/scheduler-jobs')).data,
    staleTime: 60 * 1000,
  })
}

export function useCreateMonitoringRule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Omit<MonitoringRule, 'id'>) => (await apiClient.post<MonitoringRule>('/api/v1/admin/monitoring/rules', payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'monitoring', 'rules'] })
    },
  })
}

export function useUpdateMonitoringRule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: Omit<MonitoringRule, 'id'> }) =>
      (await apiClient.put<MonitoringRule>(`/api/v1/admin/monitoring/rules/${id}`, payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'monitoring', 'rules'] })
    },
  })
}

export function useDeleteMonitoringRule() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/admin/monitoring/rules/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'monitoring', 'rules'] })
    },
  })
}

export function useCreateMonitoringChannel() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Omit<MonitoringChannel, 'id'>) => (await apiClient.post<MonitoringChannel>('/api/v1/admin/monitoring/channels', payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'monitoring', 'channels'] })
    },
  })
}

export function useUpdateMonitoringChannel() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: Omit<MonitoringChannel, 'id'> }) =>
      (await apiClient.put<MonitoringChannel>(`/api/v1/admin/monitoring/channels/${id}`, payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'monitoring', 'channels'] })
    },
  })
}

export function useDeleteMonitoringChannel() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/admin/monitoring/channels/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'monitoring', 'channels'] })
    },
  })
}

export function useCreateSchedulerJob() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: Omit<SchedulerJob, 'id'>) => (await apiClient.post<SchedulerJob>('/api/v1/admin/monitoring/scheduler-jobs', payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'monitoring', 'scheduler-jobs'] })
    },
  })
}

export function useUpdateSchedulerJob() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: Omit<SchedulerJob, 'id'> }) =>
      (await apiClient.put<SchedulerJob>(`/api/v1/admin/monitoring/scheduler-jobs/${id}`, payload)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'monitoring', 'scheduler-jobs'] })
    },
  })
}

export function useDeleteSchedulerJob() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/admin/monitoring/scheduler-jobs/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'monitoring', 'scheduler-jobs'] })
    },
  })
}
