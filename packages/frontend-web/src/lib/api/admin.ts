/**
 * Admin API Hooks
 * TanStack Query hooks for Audit-Log, Benutzer, Rollen
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────

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

// ── Fallback Data ──────────────────────────────────────────────────────

const fallbackAudit: AuditEntry[] = [
  { id: '1', zeitstempel: '2026-02-10 14:32:15', benutzer: 'admin@valeo.de', aktion: 'Benutzer erstellt', objekt: 'User#42', status: 'erfolg' },
  { id: '2', zeitstempel: '2026-02-10 14:28:03', benutzer: 'sales@valeo.de', aktion: 'Auftrag angelegt', objekt: 'SA-2026-042', status: 'erfolg' },
  { id: '3', zeitstempel: '2026-02-10 14:15:41', benutzer: 'admin@valeo.de', aktion: 'Login fehlgeschlagen', objekt: 'Auth', status: 'fehler' },
]

const fallbackBenutzer: Benutzer[] = [
  { id: '1', name: 'Admin User', email: 'admin@valeo.de', rolle: 'Administrator', status: 'aktiv', letzteAnmeldung: '2026-02-10' },
  { id: '2', name: 'Sales User', email: 'sales@valeo.de', rolle: 'Vertrieb', status: 'aktiv', letzteAnmeldung: '2026-02-09' },
  { id: '3', name: 'Lager User', email: 'lager@valeo.de', rolle: 'Lager', status: 'aktiv', letzteAnmeldung: '2026-02-10' },
]

const fallbackRollen: Rolle[] = [
  { id: '1', name: 'Administrator', beschreibung: 'Vollzugriff', benutzer: 2, rechte: 150 },
  { id: '2', name: 'Vertrieb', beschreibung: 'Verkaufsprozesse', benutzer: 8, rechte: 45 },
  { id: '3', name: 'Einkauf', beschreibung: 'Beschaffung', benutzer: 5, rechte: 38 },
  { id: '4', name: 'Lager', beschreibung: 'Lagerverwaltung', benutzer: 12, rechte: 25 },
]

// ── Hooks ──────────────────────────────────────────────────────────────

export function useAuditLog() {
  return useQuery({
    queryKey: ['admin', 'audit-log'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<AuditEntry[]>('/api/v1/admin/audit-log')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackAudit
    },
    staleTime: 30 * 1000,
  })
}

export function useBenutzer() {
  return useQuery({
    queryKey: ['admin', 'benutzer'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<Benutzer[]>('/api/v1/admin/benutzer')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackBenutzer
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function useRollen() {
  return useQuery({
    queryKey: ['admin', 'rollen'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<Rolle[]>('/api/v1/admin/rollen')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackRollen
    },
    staleTime: 5 * 60 * 1000,
  })
}
