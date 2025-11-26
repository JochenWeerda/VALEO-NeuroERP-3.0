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

