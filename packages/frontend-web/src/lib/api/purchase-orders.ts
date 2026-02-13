/**
 * Purchase Order API Hooks
 * TanStack Query hooks for Bestellungen management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// Types

export type Incoterm =
  | 'EXW'
  | 'FCA'
  | 'CPT'
  | 'CIP'
  | 'DAP'
  | 'DPU'
  | 'DDP'
  | 'FAS'
  | 'FOB'
  | 'CFR'
  | 'CIF'

export const INCOTERM_OPTIONS: { value: Incoterm; label: string }[] = [
  { value: 'EXW', label: 'EXW - Ab Werk' },
  { value: 'FCA', label: 'FCA - Frei Frachtfuehrer' },
  { value: 'CPT', label: 'CPT - Fracht bezahlt bis' },
  { value: 'CIP', label: 'CIP - Fracht+Versicherung bezahlt bis' },
  { value: 'DAP', label: 'DAP - Geliefert benannter Ort' },
  { value: 'DPU', label: 'DPU - Geliefert benannter Ort entladen' },
  { value: 'DDP', label: 'DDP - Geliefert verzollt' },
  { value: 'FAS', label: 'FAS - Frei Laengsseite Schiff' },
  { value: 'FOB', label: 'FOB - Frei an Bord' },
  { value: 'CFR', label: 'CFR - Kosten und Fracht' },
  { value: 'CIF', label: 'CIF - Kosten, Versicherung, Fracht' },
]

export type PurchaseOrderStatus =
  | 'ENTWURF'
  | 'FREIGEGEBEN'
  | 'BESTELLT'
  | 'TEILGELIEFERT'
  | 'GELIEFERT'
  | 'STORNIERT'

export type PurchaseOrderItem = {
  id: string
  itemType: 'PRODUCT' | 'SERVICE'
  articleId?: string
  description: string
  quantity: number
  unitPrice: number
  discountPercent: number
  discountAmount: number
  totalAmount: number
  deliveryDate?: string
  notes?: string
}

export type PurchaseOrder = {
  id: string
  purchaseOrderNumber: string
  supplierId: string
  subject: string
  description: string
  status: PurchaseOrderStatus
  orderDate: string
  deliveryDate: string
  contactPerson?: string
  paymentTerms?: string
  currency: string
  incoterms?: Incoterm
  deliveryTerms?: string
  externalReference?: string
  items: PurchaseOrderItem[]
  subtotal: number
  taxRate: number
  taxAmount: number
  totalAmount: number
  shippingAddress?: {
    street: string
    postalCode: string
    city: string
    country: string
  }
  notes?: string
  createdBy: string
  createdAt: string
  updatedAt: string
  version: number
  approvedAt?: string
  approvedBy?: string
  orderedAt?: string
  orderedBy?: string
}

export type PurchaseOrderCreate = {
  supplierId: string
  subject: string
  description: string
  deliveryDate: string
  items: Array<{
    itemType: 'PRODUCT' | 'SERVICE'
    articleId?: string
    description: string
    quantity: number
    unitPrice: number
    discountPercent?: number
    deliveryDate?: string
    notes?: string
  }>
  contactPerson?: string
  paymentTerms?: string
  currency?: string
  taxRate?: number
  incoterms?: Incoterm
  deliveryTerms?: string
  externalReference?: string
  shippingAddress?: {
    street: string
    postalCode: string
    city: string
    country: string
  }
  notes?: string
}

export type PurchaseOrderUpdate = Partial<Omit<PurchaseOrderCreate, 'supplierId' | 'items'>>

type PaginatedResponse = {
  data: PurchaseOrder[]
  page: number
  pageSize: number
  total: number
  totalPages: number
}

// Query Keys

export const purchaseOrderKeys = {
  all: ['purchase-orders'] as const,
  list: (filters?: Record<string, unknown>) => [...purchaseOrderKeys.all, 'list', filters] as const,
  detail: (id: string) => [...purchaseOrderKeys.all, 'detail', id] as const,
  overdue: () => [...purchaseOrderKeys.all, 'overdue'] as const,
  pendingApproval: () => [...purchaseOrderKeys.all, 'pending-approval'] as const,
  statistics: () => [...purchaseOrderKeys.all, 'statistics'] as const,
  changelog: (id: string) => [...purchaseOrderKeys.all, 'changelog', id] as const,
}

// Hooks

export function usePurchaseOrders(filters?: {
  status?: PurchaseOrderStatus
  supplierId?: string
  search?: string
}) {
  return useQuery({
    queryKey: purchaseOrderKeys.list(filters),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.status) params.append('status', filters.status)
      if (filters?.supplierId) params.append('supplierId', filters.supplierId)
      if (filters?.search) params.append('search', filters.search)

      const response = await apiClient.get<PaginatedResponse>(`/api/v1/purchase-orders?${String(params)}`)
      return response.data.data
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function usePurchaseOrder(id: string) {
  return useQuery({
    queryKey: purchaseOrderKeys.detail(id),
    queryFn: async () => {
      const response = await apiClient.get<PurchaseOrder>(`/api/v1/purchase-orders/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useCreatePurchaseOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: PurchaseOrderCreate) => {
      const response = await apiClient.post<PurchaseOrder>('/api/v1/purchase-orders', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: purchaseOrderKeys.all })
    },
  })
}

export function useUpdatePurchaseOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: PurchaseOrderUpdate }) => {
      const response = await apiClient.patch<PurchaseOrder>(`/api/v1/purchase-orders/${id}`, data)
      return response.data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: purchaseOrderKeys.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: purchaseOrderKeys.list() })
    },
  })
}

export function useApprovePurchaseOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.post<PurchaseOrder>(`/api/v1/purchase-orders/${id}/approve`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: purchaseOrderKeys.all })
    },
  })
}

export function useCancelPurchaseOrder() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason: string }) => {
      const response = await apiClient.post<PurchaseOrder>(
        `/api/v1/purchase-orders/${id}/cancel-with-reason`,
        { reason },
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: purchaseOrderKeys.all })
    },
  })
}

export function usePurchaseOrderStatistics() {
  return useQuery({
    queryKey: purchaseOrderKeys.statistics(),
    queryFn: async () => {
      const response = await apiClient.get<{
        totalOrders: number
        totalValue: number
        byStatus: Record<PurchaseOrderStatus, number>
      }>('/api/v1/purchase-orders/statistics')
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function usePurchaseOrderChangelog(id: string) {
  return useQuery({
    queryKey: purchaseOrderKeys.changelog(id),
    queryFn: async () => {
      const response = await apiClient.get<
        Array<{
          id: string
          changeType: string
          changedBy: string
          changedAt: string
          fieldChanges: Array<{ field: string; oldValue: string; newValue: string }>
        }>
      >(`/api/v1/purchase-orders/${id}/changelog`)
      return response.data
    },
    enabled: !!id,
  })
}
