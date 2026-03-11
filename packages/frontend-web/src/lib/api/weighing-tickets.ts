import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type WeighingTicket = {
  id: string
  ticket_number: string
  scale_id?: string | null
  vehicle_plate?: string | null
  gross_weight?: number | null
  tare_weight?: number | null
  net_weight?: number | null
  first_weighing_at?: string | null
  second_weighing_at?: string | null
  moisture_pct?: number | null
  protein_pct?: number | null
  impurities_pct?: number | null
  hl_weight?: number | null
  billing_weight?: number | null
  contract_id?: string | null
  allocated_quantity_kg?: number | null
  allocation_status?: string | null
  status: string
  direction: string
  reference_doc?: string | null
  article_group?: string | null
  article_id?: string | null

  notes?: string | null
}

type PageResponse<T> = {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

const EMPTY_WEIGHING_TICKET_PAGE: PageResponse<WeighingTicket> = {
  items: [],
  total: 0,
  page: 1,
  size: 0,
  pages: 0,
  has_next: false,
  has_prev: false,
}

export type WeighingTicketCreateInput = {
  ticket_number: string
  scale_id?: string
  vehicle_plate?: string
  gross_weight?: number
  tare_weight?: number
  net_weight?: number
  moisture_pct?: number
  protein_pct?: number
  impurities_pct?: number
  hl_weight?: number
  billing_weight?: number
  direction?: string
  reference_doc?: string
  article_group?: string
  article_id?: string

  notes?: string
}

export type WeighingTicketUpdateInput = Partial<{
  gross_weight: number
  tare_weight: number
  net_weight: number
  moisture_pct: number
  protein_pct: number
  impurities_pct: number
  hl_weight: number
  billing_weight: number
  vehicle_plate: string
  status: string
  article_group: string
  article_id: string
  notes: string
}>

export type AgrarContract = {
  id: string
  contract_number: string
  article_id: string
  partner_id: string
  remaining_quantity_kg: number
  status: 'open' | 'partially_allocated' | 'fulfilled' | 'cancelled'
}

export type ArticleGroup = {
  warengruppe: string
  count: number
}

export type ArticleItem = {
  id: string
  article_number: string
  name: string
  warengruppe?: string | null
  unit: string
  category: string
}

export function useWeighingTickets(params?: { skip?: number; limit?: number; tenantId?: string }) {
  return useQuery({
    queryKey: ['weighing-tickets', params ?? {}],
    queryFn: async () => {
      const q = new URLSearchParams()
      if (params?.tenantId) q.set('tenant_id', params.tenantId)
      if (params?.skip !== undefined) q.set('skip', String(params.skip))
      if (params?.limit !== undefined) q.set('limit', String(params.limit))
      const endpoint = q.size > 0 ? `/api/v1/weighing-tickets?${q.toString()}` : '/api/v1/weighing-tickets'
      return (await apiClient.get<PageResponse<WeighingTicket>>(endpoint)).data
    },
    initialData: EMPTY_WEIGHING_TICKET_PAGE,
    staleTime: 30 * 1000,
  })
}

export function useCreateWeighingTicket() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: WeighingTicketCreateInput) =>
      (await apiClient.post<WeighingTicket>('/api/v1/weighing-tickets', payload)).data,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['weighing-tickets'] })
    },
  })
}

export function useUpdateWeighingTicket() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: WeighingTicketUpdateInput }) =>
      (await apiClient.put<WeighingTicket>(`/api/v1/weighing-tickets/${encodeURIComponent(id)}`, payload)).data,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['weighing-tickets'] })
    },
  })
}

export function useOpenContracts() {
  return useQuery({
    queryKey: ['agrar-contracts', 'open'],
    queryFn: async () => {
      const data = (await apiClient.get<PageResponse<AgrarContract>>('/api/v1/agrar/contracts?status=open&limit=100')).data
      return data.items
    },
    initialData: [],
    staleTime: 60 * 1000,
  })
}

export function useAllocateContract() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: { ticketId: string; contractId: string; allocationQuantityKg?: number }) =>
      (
        await apiClient.post(`/api/v1/weighing-tickets/${encodeURIComponent(payload.ticketId)}/allocate-contract`, {
          contract_id: payload.contractId,
          allocation_quantity_kg: payload.allocationQuantityKg,
        })
      ).data,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['weighing-tickets'] })
      void qc.invalidateQueries({ queryKey: ['agrar-contracts'] })
    },
  })
}

export function useArticleGroups() {
  return useQuery({
    queryKey: ['weighing-tickets', 'article-groups'],
    queryFn: async () =>
      (await apiClient.get<ArticleGroup[]>('/api/v1/weighing-tickets/article-groups')).data,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function useArticlesByGroup(group: string | null) {
  return useQuery({
    queryKey: ['articles', 'by-group', group],
    queryFn: async () => {
      if (!group) return []
      const data = (
        await apiClient.get<PageResponse<ArticleItem>>(
          `/api/v1/articles?search=${encodeURIComponent(group)}&limit=100`,
        )
      ).data
      return data.items.filter((a) => a.warengruppe === group)
    },
    enabled: !!group,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

