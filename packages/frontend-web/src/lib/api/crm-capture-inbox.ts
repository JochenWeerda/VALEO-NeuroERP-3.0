import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * KIM Klärfall-Inbox: automatisch erfasste Kontakte (Telefon/E-Mail/WhatsApp),
 * die KEINEM Kunden zugeordnet werden konnten, landen hier (statt verloren zu
 * gehen). Innen-/Aussendienst ordnet sie manuell einem Kunden zu (legt den
 * Kontakt in der Kontakthistorie an) oder verwirft sie.
 * Backend: app/api/v1/endpoints/crm_capture_inbox.py
 */

export type CaptureInboxItem = {
  id: string
  channel: string            // telefon | email | whatsapp | brief | fax
  direction: string          // ein | aus
  peer: string | null
  betreff: string | null
  zusammenfassung: string | null
  content: string | null
  verweis: string | null
  status: 'offen' | 'zugeordnet' | 'verworfen'
  kunden_nr: string | null
  kontakt_id: string | null
  resolved_by: string | null
  resolved_at: string | null
  created_at: string | null
}

export type CaptureInboxResponse = { items: CaptureInboxItem[]; open: number }

const BASE = '/api/v1/crm/kim/capture-inbox'
const keys = { list: (status: string) => ['crm-capture-inbox', status] as const }

export function useCaptureInbox(status = 'offen') {
  return useQuery({
    queryKey: keys.list(status),
    queryFn: async () => {
      const res = await apiClient.get<CaptureInboxResponse>(BASE, { params: { status } })
      return res.data ?? { items: [], open: 0 }
    },
    initialDataUpdatedAt: 0,
  })
}

export function useAssignCapture() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { id: string; kundenNr: string; resolvedBy?: string }) => {
      const { id, ...body } = input
      const res = await apiClient.post<{ status: string }>(
        `${BASE}/${encodeURIComponent(id)}/assign`, body,
      )
      return res.data
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['crm-capture-inbox'] }) },
  })
}

export function useDismissCapture() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { id: string; resolvedBy?: string }) => {
      const { id, ...body } = input
      const res = await apiClient.post<{ status: string }>(
        `${BASE}/${encodeURIComponent(id)}/dismiss`, body,
      )
      return res.data
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['crm-capture-inbox'] }) },
  })
}
