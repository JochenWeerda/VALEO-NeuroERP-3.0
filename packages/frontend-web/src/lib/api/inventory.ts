/**
 * Inventory API Hooks
 * TanStack Query hooks for Warehouse and Stock management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// Types
export type Warehouse = {
  id: string
  code: string
  name: string
  address?: string
  capacity?: number
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

// Query Keys
export const inventoryKeys = {
  all: ['inventory'] as const,
  warehouses: () => [...inventoryKeys.all, 'warehouses'] as const,
  warehouse: (id: string) => [...inventoryKeys.warehouses(), id] as const,
  lotTrace: (id?: string) => [...inventoryKeys.all, 'lot-trace', id] as const,
}

// Warehouse Hooks
export function useWarehouses(filters?: { is_active?: boolean }) {
  return useQuery({
    queryKey: [...inventoryKeys.warehouses(), filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.is_active !== undefined) params.append('is_active', String(filters.is_active))
      
      const response = await apiClient.get<PaginatedResponse<Warehouse>>(
        `/api/v1/inventory/warehouses?${String(params)}`
      )
      return response.data
    },
  })
}

export function useWarehouse(id: string) {
  return useQuery({
    queryKey: inventoryKeys.warehouse(id),
    queryFn: async () => {
      const response = await apiClient.get<Warehouse>(`/api/v1/inventory/warehouses/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useCreateWarehouse() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (data: WarehouseCreate) => {
      const response = await apiClient.post<Warehouse>('/api/v1/inventory/warehouses', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.warehouses() })
    },
  })
}

export function useUpdateWarehouse() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: WarehouseUpdate }) => {
      const response = await apiClient.put<Warehouse>(`/api/v1/inventory/warehouses/${id}`, data)
      return response.data
    },
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.warehouses() })
    },
  })
}

export function useLotTrace(lotId?: string) {
  return useQuery({
    queryKey: inventoryKeys.lotTrace(lotId),
    queryFn: async () => {
      const response = await apiClient.get<LotTrace>(`/api/v1/inventory/lots/${lotId}`)
      return response.data
    },
    enabled: Boolean(lotId),
    staleTime: 30_000,
  })
}

// ── Inventur Types & Hooks ─────────────────────────────────────────────

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
  artikel: string
  ankunft: string
  wartezeit: number
  status: 'wartend' | 'in-bearbeitung' | 'abgeschlossen'
}

// Extended Query Keys
export const inventoryExtraKeys = {
  inventur: () => [...inventoryKeys.all, 'inventur'] as const,
  mhd: () => [...inventoryKeys.all, 'mhd'] as const,
  renner: () => [...inventoryKeys.all, 'renner'] as const,
  penner: () => [...inventoryKeys.all, 'penner'] as const,
  warteschlange: () => [...inventoryKeys.all, 'warteschlange'] as const,
}

// Fallback data
const fallbackInventur: InventurPosition[] = [
  { id: '1', artikel: 'Weizen Premium', lagerort: 'Silo 1', sollBestand: 450, istBestand: 0, differenz: 0, status: 'offen' },
  { id: '2', artikel: 'Sojaschrot 44%', lagerort: 'Halle A', sollBestand: 280, istBestand: 278, differenz: -2, status: 'gezaehlt' },
  { id: '3', artikel: 'NPK 15-15-15', lagerort: 'Halle B', sollBestand: 120, istBestand: 125, differenz: 5, status: 'gezaehlt' },
  { id: '4', artikel: 'Diesel Winterqualität', lagerort: 'Tank 1', sollBestand: 5000, istBestand: 0, differenz: 0, status: 'offen' },
]

const fallbackMhd: MhdItem[] = [
  { name: 'Pflanzenschutzmittel X', expiryDate: '2026-04-15', quantity: 50 },
  { name: 'Saatgutbeize Premium', expiryDate: '2026-05-01', quantity: 25 },
  { name: 'Herbizid Konzentrat', expiryDate: '2026-05-28', quantity: 100 },
]

const fallbackRenner: RennerPennerItem[] = [
  { name: 'Weizen Saatgut Premium', absatz: 450, trend: '+15%' },
  { name: 'Dünger NPK 15-15-15', absatz: 380, trend: '+8%' },
  { name: 'Diesel Winterqualität', absatz: 320, trend: '+5%' },
]

const fallbackPenner: RennerPennerItem[] = [
  { name: 'Ersatzteile Typ B-alt', absatz: 2, trend: '-45%' },
  { name: 'Altbestand Saatgut 2022', absatz: 5, trend: '-30%' },
  { name: 'Spezialdünger Nische', absatz: 8, trend: '-20%' },
]

const fallbackWarteschlange: LKWEintrag[] = [
  { id: '1', position: 1, kennzeichen: 'AB-CD 1234', lieferant: 'Landwirt Schmidt', artikel: 'Weizen', ankunft: '08:30', wartezeit: 15, status: 'in-bearbeitung' },
  { id: '2', position: 2, kennzeichen: 'EF-GH 5678', lieferant: 'Müller Agrar', artikel: 'Raps', ankunft: '08:45', wartezeit: 30, status: 'wartend' },
]

export function useInventur(filters?: { search?: string }) {
  return useQuery({
    queryKey: [...inventoryExtraKeys.inventur(), filters],
    queryFn: async () => {
      try {
        const response = await apiClient.get<{ items: InventurPosition[]; total: number }>(
          '/api/v1/inventory/inventur'
        )
        if (response.data?.items?.length) return response.data
      } catch { /* fallback */ }
      let items = [...fallbackInventur]
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter(p =>
          p.artikel.toLowerCase().includes(s) ||
          p.lagerort.toLowerCase().includes(s)
        )
      }
      return { items, total: items.length }
    },
    staleTime: 30 * 1000,
  })
}

export function useCompleteInventurPositions() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (ids: string[]) => {
      await apiClient.post('/api/v1/inventory/inventur/complete', { ids })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryExtraKeys.inventur() })
    },
  })
}

export function useMhdItems() {
  return useQuery({
    queryKey: inventoryExtraKeys.mhd(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<{ items: MhdItem[] }>('/api/v1/inventory/mhd-warnings')
        if (response.data?.items?.length) return response.data.items
      } catch { /* fallback */ }
      return fallbackMhd
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useRennerItems() {
  return useQuery({
    queryKey: inventoryExtraKeys.renner(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<{ items: RennerPennerItem[] }>('/api/v1/inventory/top-sellers')
        if (response.data?.items?.length) return response.data.items
      } catch { /* fallback */ }
      return fallbackRenner
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function usePennerItems() {
  return useQuery({
    queryKey: inventoryExtraKeys.penner(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<{ items: RennerPennerItem[] }>('/api/v1/inventory/slow-movers')
        if (response.data?.items?.length) return response.data.items
      } catch { /* fallback */ }
      return fallbackPenner
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function useWarteschlange() {
  return useQuery({
    queryKey: inventoryExtraKeys.warteschlange(),
    queryFn: async () => {
      try {
        const response = await apiClient.get<{ items: LKWEintrag[] }>('/api/v1/annahme/warteschlange')
        if (response.data?.items?.length) return response.data
      } catch { /* fallback */ }
      return { items: fallbackWarteschlange, total: fallbackWarteschlange.length }
    },
    staleTime: 15 * 1000,
    refetchInterval: 30 * 1000,
  })
}

