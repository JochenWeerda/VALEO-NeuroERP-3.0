import { useMutation, useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * GoBD-Exportpaket & DMS-/Paperless-Liveprobe (DOM-DOC-004.4).
 * Backend: app/api/v1/endpoints/docflow_gobd.py
 */

export type GobdManifest = {
  vorgang: string | null
  doc_type: string | null
  status: string | null
  version: number | null
  exportiert_am: string
  exportiert_von: string
  artefakte: Array<{ datei: string | null; sha256: string | null; typ: string | null }>
  anzahl_artefakte: number
  vorgangskette: number
  buchungen: number
  offene_luecken: number
  revisionssicher: boolean
  pruefsumme_sha256: string
}

export type GobdExportResult = { found: boolean; detail?: string; manifest?: GobdManifest }
export type PaperlessProbe = { konfiguriert: boolean; erreichbar: boolean; url: string | null; detail: string }

const BASE = '/api/v1/docflow/evidence'

export function usePaperlessProbe() {
  return useQuery({
    queryKey: ['docflow-gobd', 'paperless'],
    queryFn: async () => (await apiClient.get<PaperlessProbe>(`${BASE}/paperless-probe`)).data,
  })
}

export function useGobdExport() {
  return useMutation({
    mutationFn: async (doc: string) =>
      (await apiClient.post<GobdExportResult>(`${BASE}/gobd-export`, { doc })).data,
  })
}
