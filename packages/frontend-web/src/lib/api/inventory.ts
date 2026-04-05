/**
 * Inventory API Hooks
 * Error-first fetching without mock fallback data.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type Warehouse = {
  id: string
  code: string
  name: string
  address?: string
  capacity?: number
  used_capacity?: number
  is_active: boolean
  tenant_id: string
  created_at: string
  updated_at: string
}

export type WarehouseCreate = Omit<Warehouse, 'id' | 'created_at' | 'updated_at' | 'tenant_id'>
export type WarehouseUpdate = Partial<WarehouseCreate>

type PaginatedResponse<T> = {
  items: T[]
  total: number
  page: number
  pages: number
  size: number
}

const EMPTY_WAREHOUSE_LIST: PaginatedResponse<Warehouse> = {
  items: [],
  total: 0,
  page: 1,
  pages: 0,
  size: 0,
}

const EMPTY_INVENTUR_LIST: { items: InventurPosition[]; total: number } = {
  items: [],
  total: 0,
}

const EMPTY_WARTESCHLANGE: { items: LKWEintrag[]; total: number } = {
  items: [],
  total: 0,
}

export type LotTrace = {
  lot_id: string
  sku: string
  lot_number: string
  transactions: Array<{
    id: string
    transaction_type: string
    quantity: number
    reference?: string | null
    created_at: string
    from_location_id?: string | null
    to_location_id?: string | null
  }>
}

export const inventoryKeys = {
  all: ['inventory'] as const,
  warehouses: () => [...inventoryKeys.all, 'warehouses'] as const,
  warehouse: (id: string) => [...inventoryKeys.warehouses(), id] as const,
  lotTrace: (id?: string) => [...inventoryKeys.all, 'lot-trace', id] as const,
}

export function useWarehouses(filters?: { is_active?: boolean }) {
  return useQuery({
    queryKey: [...inventoryKeys.warehouses(), filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.is_active !== undefined) params.append('is_active', String(filters.is_active))
      return (await apiClient.get<PaginatedResponse<Warehouse>>(`/api/v1/inventory/warehouses?${String(params)}`)).data
    },
    initialData: EMPTY_WAREHOUSE_LIST,
  })
}

export function useWarehouse(id: string) {
  return useQuery({
    queryKey: inventoryKeys.warehouse(id),
    queryFn: async () => (await apiClient.get<Warehouse>(`/api/v1/inventory/warehouses/${id}`)).data,
    enabled: !!id,
    initialData: null,
  })
}

export function useCreateWarehouse() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: WarehouseCreate) => (await apiClient.post<Warehouse>('/api/v1/inventory/warehouses', data)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: inventoryKeys.warehouses() }),
  })
}

export function useUpdateWarehouse() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: WarehouseUpdate }) => (await apiClient.put<Warehouse>(`/api/v1/inventory/warehouses/${id}`, data)).data,
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.warehouse(variables.id) })
      queryClient.invalidateQueries({ queryKey: inventoryKeys.warehouses() })
    },
  })
}

export function useDeleteWarehouse() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/inventory/warehouses/${id}`)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: inventoryKeys.warehouses() }),
  })
}

export function useLotTrace(lotId?: string) {
  return useQuery({
    queryKey: inventoryKeys.lotTrace(lotId),
    queryFn: async () => (await apiClient.get<LotTrace>(`/api/v1/inventory/lots/${lotId}`)).data,
    enabled: Boolean(lotId),
    initialData: null,
    staleTime: 30_000,
  })
}

export type InventurPosition = {
  id: string
  artikel: string
  lagerort: string
  sollBestand: number
  istBestand: number
  differenz: number
  status: 'offen' | 'gezaehlt' | 'abgeschlossen'
}

export type MhdItem = {
  name: string
  expiryDate: string
  quantity: number
}

export type RennerPennerItem = {
  name: string
  absatz: number
  trend: string
}

export type LKWEintrag = {
  id: string
  position: number
  kennzeichen: string
  lieferant: string
  article_id?: string | null
  artikel: string
  ankunft: string
  wartezeit: number
  status: 'wartend' | 'in-bearbeitung' | 'abgeschlossen' | 'gesperrt'
  lieferschein_nr?: string
  klaerung?: {
    status?: 'offen' | 'freigegeben' | 'gesperrt'
    decision?: 'sonderfreigabe' | 'gesperrt'
    reason?: string
    qp_result?: string
    decided_at?: string
    quality_protocol_id?: string
    updated_at?: string
  } | null
}

export const inventoryExtraKeys = {
  inventur: () => [...inventoryKeys.all, 'inventur'] as const,
  mhd: () => [...inventoryKeys.all, 'mhd'] as const,
  renner: () => [...inventoryKeys.all, 'renner'] as const,
  penner: () => [...inventoryKeys.all, 'penner'] as const,
  warteschlange: () => [...inventoryKeys.all, 'warteschlange'] as const,
}

export function useInventur(filters?: { search?: string }) {
  return useQuery({
    queryKey: [...inventoryExtraKeys.inventur(), filters],
    queryFn: async () => {
      const response = await apiClient.get<{ items: InventurPosition[]; total: number }>('/api/v1/inventory/inventur')
      const payload = response.data
      if (!filters?.search) return payload
      const s = filters.search.toLowerCase()
      const items = payload.items.filter((p) => p.artikel.toLowerCase().includes(s) || p.lagerort.toLowerCase().includes(s))
      return { items, total: items.length }
    },
    initialData: EMPTY_INVENTUR_LIST,
    staleTime: 30 * 1000,
  })
}

export function useCompleteInventurPositions() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (ids: string[]) => {
      await apiClient.post('/api/v1/inventory/inventur/complete', { ids })
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: inventoryExtraKeys.inventur() }),
  })
}

export function useStornierenInventurPosition() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/v1/inventory/inventur/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: inventoryExtraKeys.inventur() }),
  })
}

export function useMhdItems() {
  return useQuery({
    queryKey: inventoryExtraKeys.mhd(),
    queryFn: async () => (await apiClient.get<{ items: MhdItem[] }>('/api/v1/inventory/mhd-warnings')).data.items,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function useRennerItems() {
  return useQuery({
    queryKey: inventoryExtraKeys.renner(),
    queryFn: async () => (await apiClient.get<{ items: RennerPennerItem[] }>('/api/v1/inventory/top-sellers')).data.items,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function usePennerItems() {
  return useQuery({
    queryKey: inventoryExtraKeys.penner(),
    queryFn: async () => (await apiClient.get<{ items: RennerPennerItem[] }>('/api/v1/inventory/slow-movers')).data.items,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function useWarteschlange() {
  return useQuery({
    queryKey: inventoryExtraKeys.warteschlange(),
    queryFn: async () => (await apiClient.get<{ items: LKWEintrag[]; total: number }>('/api/v1/annahme/warteschlange')).data,
    initialData: EMPTY_WARTESCHLANGE,
    staleTime: 15 * 1000,
    refetchInterval: 30 * 1000,
  })
}

export function useWarteschlangeEintrag(id: string | undefined) {
  return useQuery({
    queryKey: [...inventoryExtraKeys.warteschlange(), id],
    queryFn: async () => (await apiClient.get<LKWEintrag>(`/api/v1/annahme/warteschlange/${id}`)).data,
    enabled: !!id,
    initialData: null,
    staleTime: 30 * 1000,
  })
}

export function usePatchWarteschlangeStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      id,
      status,
      klaerung,
    }: {
      id: string
      status?: 'in-bearbeitung' | 'abgeschlossen' | 'gesperrt'
      klaerung?: LKWEintrag['klaerung']
    }) => {
      const payload: Record<string, unknown> = {}
      if (status) payload.status = status
      if (klaerung) payload.klaerung = klaerung
      if (!payload.status && !payload.klaerung) {
        throw new Error('status oder klaerung muss gesetzt sein')
      }
      const { data } = await apiClient.patch<LKWEintrag>(`/api/v1/annahme/warteschlange/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryExtraKeys.warteschlange() })
    },
  })
}

export function useRepairWarteschlangeArticle() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<{ status: string; reason?: string; article_id?: string; artikel?: string }>(
        `/api/v1/annahme/warteschlange/${id}/repair-article`,
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryExtraKeys.warteschlange() })
    },
  })
}
