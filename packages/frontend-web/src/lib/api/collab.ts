import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export interface CollabMention {
  user_id: string
  display?: string | null
}

export interface CollabNote {
  id: string
  tenant_id: string
  entity_type: string
  entity_id: string
  body: string
  mentions: CollabMention[]
  created_by: string
  created_at: string
  updated_at: string
  deleted_at?: string | null
}

export interface CreateCollabNoteInput {
  entity_type: string
  entity_id: string
  body: string
  mentions: CollabMention[]
}

export const collabKeys = {
  notes: (entityType: string, entityId: string) => ['collab', 'notes', entityType, entityId] as const,
}

export async function fetchEntityNotes(entityType: string, entityId: string, limit = 50): Promise<CollabNote[]> {
  const response = await apiClient.get<CollabNote[]>('/api/v1/collab/notes', {
    params: { entity_type: entityType, entity_id: entityId, limit },
  })
  return response.data
}

export async function createEntityNote(input: CreateCollabNoteInput): Promise<CollabNote> {
  const response = await apiClient.post<CollabNote>('/api/v1/collab/notes', input)
  return response.data
}

export function useEntityNotes(entityType: string, entityId: string, enabled = true) {
  return useQuery({
    queryKey: collabKeys.notes(entityType, entityId),
    queryFn: () => fetchEntityNotes(entityType, entityId),
    enabled: enabled && entityType.length > 0 && entityId.length > 0,
    staleTime: 15_000,
  })
}
