/**
 * Admin API Hooks
 * Error-first fetching without mock fallback data.
 */

import { useQuery } from '@tanstack/react-query'
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
