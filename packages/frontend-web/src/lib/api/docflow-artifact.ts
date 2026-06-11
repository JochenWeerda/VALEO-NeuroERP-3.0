import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Artefakt-Upload, Versionierung & Freigabe (DOM-DOC-004.2).
 * Backend: app/api/v1/endpoints/docflow_artifact.py
 */

export type ArtifactItem = {
  artifact_id: string
  artifact_type: string
  file_name: string | null
  sha256: string | null
  version: number
  aktuell: boolean
  freigabe_status: 'entwurf' | 'freigegeben' | 'archiviert' | string
  created_at: string | null
  created_by: string | null
  freigegeben_at: string | null
  freigegeben_by: string | null
}

export type ArtifactList = {
  found: boolean
  detail?: string
  doc_number?: string
  artifacts?: ArtifactItem[]
  summary?: { anzahl: number; freigegeben: number; entwuerfe: number }
}

const BASE = '/api/v1/docflow/evidence/artifacts'

export function useArtifacts(doc: string | null) {
  return useQuery({
    queryKey: ['docflow-artifact', doc],
    enabled: !!doc,
    queryFn: async () => (await apiClient.get<ArtifactList>(BASE, { params: { doc } })).data,
  })
}

export function useUploadArtifact(doc: string | null) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { fileName: string; content: string; artifactType?: string }) =>
      (await apiClient.post<{ ok: boolean; version: number }>(BASE, { doc, ...input })).data,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['docflow-artifact', doc] }) },
  })
}

export function useSetFreigabe(doc: string | null) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { artifactId: string; zielStatus: 'freigegeben' | 'archiviert' }) =>
      (await apiClient.post<{ ok: boolean; freigabe_status: string }>(`${BASE}/${encodeURIComponent(input.artifactId)}/freigabe`, { zielStatus: input.zielStatus })).data,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['docflow-artifact', doc] }) },
  })
}
