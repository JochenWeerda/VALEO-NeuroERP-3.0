import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Dokument-Nachweisraum (DOM-DOC-004): GoBD-Artefakt-/Vorgangs-Sicht je Dokument
 * (Artefakte mit SHA-256, Vorgangskette, Buchungen, Lücken). Read-only.
 * Backend: app/api/v1/endpoints/docflow_evidence.py
 */

export type EvidenceDoc = {
  doc_number: string
  doc_type: string
  status: string
  datum: string | null
  brutto: number | null
  artefakte: number
  revisionssicher: boolean
  gebucht: boolean
}

export type Artefakt = { id: string; typ: string; hash: string | null; storage_key: string | null; datei: string | null; created_at: string | null; created_by: string | null }
export type Kettenglied = { relation: string; richtung: string; partner_nr: string | null; partner_typ: string | null }
export type Buchung = { typ: string; journal_entry_id: string | null; betrag: number | null; waehrung: string | null; posted_at: string | null; posted_by: string | null }
export type DocLuecke = { schwere: string; text: string }

export type EvidenceDetail = {
  found: boolean
  detail?: string
  id?: string
  doc_number?: string
  doc_type?: string
  status?: string
  version?: number
  audit?: Record<string, unknown>
  artefakte?: Artefakt[]
  vorgangskette?: Kettenglied[]
  buchungen?: Buchung[]
  luecken?: DocLuecke[]
  summary?: { artefakte: number; revisionssicher: boolean; verkettet: number; gebucht: boolean; offene_luecken: number }
}

export function useEvidenceDocuments(limit = 50) {
  return useQuery({
    queryKey: ['docflow-evidence', 'documents', limit],
    queryFn: async () => {
      const res = await apiClient.get<{ items: EvidenceDoc[] }>('/api/v1/docflow/evidence/documents', { params: { limit } })
      return res.data?.items ?? []
    },
  })
}

export function useEvidenceDetail(doc: string | null) {
  return useQuery({
    queryKey: ['docflow-evidence', 'detail', doc],
    enabled: !!doc,
    queryFn: async () => {
      const res = await apiClient.get<EvidenceDetail>('/api/v1/docflow/evidence/detail', { params: { doc } })
      return res.data
    },
  })
}
