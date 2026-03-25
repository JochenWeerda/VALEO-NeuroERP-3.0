/**
 * Knowledge Core API — Wave 69
 * React Query Hooks für den zentralen Wissensspeicher.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

const BASE = '/api/v1/knowledge'

// ── Types ───────────────────────────────────────────────────────────────────────

export type KnowledgeItem = {
  knowledge_id: string
  titel: string
  typ: string
  status: string
  beschreibung: string
  tags: string[]
  zielrollen: string[]
  agentenfreigabe: boolean
  created_at: string
  updated_at: string
  versionen_count: number
  aktuelle_version: number | null
  vorschau: string
}

export type KnowledgeSearchResult = {
  items: KnowledgeItem[]
  total: number
  query: string
}

export type KnowledgeStats = {
  gesamt: number
  nach_typ: Record<string, number>
  nach_status: Record<string, number>
  nach_format: Record<string, number>
  agentenfreigabe_aktiv: number
}

export type KnowledgeCreatePayload = {
  titel: string
  typ: string
  beschreibung?: string
  tags?: string[]
  zielrollen?: string[]
  agentenfreigabe?: boolean
  initiale_version?: string
  format?: string
}

export type KnowledgeUpdatePayload = {
  knowledge_id: string
  titel?: string
  beschreibung?: string
  tags?: string[]
  zielrollen?: string[]
  status?: string
  agentenfreigabe?: boolean
}

export type KnowledgeAddVersionPayload = {
  knowledge_id: string
  inhalt: string
  format?: string
  quelle?: string
}

// ── List ────────────────────────────────────────────────────────────────────────

export function useKnowledgeList(params?: {
  typ?: string
  status?: string
  search?: string
  limit?: number
}) {
  const searchParams = new URLSearchParams()
  if (params?.typ) searchParams.set('typ', params.typ)
  if (params?.status) searchParams.set('status', params.status)
  if (params?.search) searchParams.set('search', params.search)
  if (params?.limit !== undefined) searchParams.set('limit', String(params.limit))
  const qs = searchParams.toString()

  return useQuery<KnowledgeItem[]>({
    queryKey: ['knowledge', 'list', params],
    queryFn: async () => {
      const { data } = await apiClient.get<KnowledgeItem[]>(`${BASE}/${qs ? `?${qs}` : ''}`)
      return data
    },
    staleTime: 60_000,
  })
}

// ── Single Item ─────────────────────────────────────────────────────────────────

export function useKnowledgeItem(id: string) {
  return useQuery<KnowledgeItem>({
    queryKey: ['knowledge', 'item', id],
    queryFn: async () => {
      const { data } = await apiClient.get<KnowledgeItem>(`${BASE}/${id}`)
      return data
    },
    enabled: Boolean(id),
    staleTime: 60_000,
  })
}

// ── Stats ────────────────────────────────────────────────────────────────────────

export function useKnowledgeStats() {
  return useQuery<KnowledgeStats>({
    queryKey: ['knowledge', 'stats'],
    queryFn: async () => {
      const { data } = await apiClient.get<KnowledgeStats>(`${BASE}/stats`)
      return data
    },
    staleTime: 120_000,
  })
}

// ── Search ───────────────────────────────────────────────────────────────────────

export function useKnowledgeSearch(query: string, enabled = true) {
  return useQuery<KnowledgeSearchResult>({
    queryKey: ['knowledge', 'search', query],
    queryFn: async () => {
      const { data } = await apiClient.get<KnowledgeSearchResult>(
        `${BASE}/search?q=${encodeURIComponent(query)}`
      )
      return data
    },
    enabled: enabled && query.trim().length > 0,
    staleTime: 30_000,
  })
}

// ── Mutations ────────────────────────────────────────────────────────────────────

export function useCreateKnowledge() {
  const queryClient = useQueryClient()
  return useMutation<KnowledgeItem, Error, KnowledgeCreatePayload>({
    mutationFn: async (payload) => {
      const { data } = await apiClient.post<KnowledgeItem>(`${BASE}/`, payload)
      return data
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['knowledge', 'list'] })
      void queryClient.invalidateQueries({ queryKey: ['knowledge', 'stats'] })
    },
  })
}

export function useUpdateKnowledge() {
  const queryClient = useQueryClient()
  return useMutation<KnowledgeItem, Error, KnowledgeUpdatePayload>({
    mutationFn: async ({ knowledge_id, ...rest }) => {
      const { data } = await apiClient.put<KnowledgeItem>(`${BASE}/${knowledge_id}`, rest)
      return data
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ['knowledge', 'list'] })
      void queryClient.invalidateQueries({ queryKey: ['knowledge', 'item', variables.knowledge_id] })
    },
  })
}

export function useArchiveKnowledge() {
  const queryClient = useQueryClient()
  return useMutation<void, Error, string>({
    mutationFn: async (knowledge_id) => {
      await apiClient.delete(`${BASE}/${knowledge_id}`)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['knowledge', 'list'] })
      void queryClient.invalidateQueries({ queryKey: ['knowledge', 'stats'] })
    },
  })
}

export function useAddVersion() {
  const queryClient = useQueryClient()
  return useMutation<KnowledgeItem, Error, KnowledgeAddVersionPayload>({
    mutationFn: async ({ knowledge_id, ...rest }) => {
      const { data } = await apiClient.post<KnowledgeItem>(
        `${BASE}/${knowledge_id}/versionen`,
        rest
      )
      return data
    },
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ['knowledge', 'item', variables.knowledge_id] })
      void queryClient.invalidateQueries({ queryKey: ['knowledge', 'list'] })
    },
  })
}
