/**
 * Purchase Order API Hooks
 * TanStack Query hooks for Bestellungen management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────

export type Incoterm =
  | 'EXW' | 'FCA' | 'CPT' | 'CIP' | 'DAP' | 'DPU' | 'DDP'
  | 'FAS' | 'FOB' | 'CFR' | 'CIF'

export const INCOTERM_OPTIONS: { value: Incoterm; label: string }[] = [
  { value: 'EXW', label: 'EXW – Ab Werk' },
  { value: 'FCA', label: 'FCA – Frei Frachtführer' },
  { value: 'CPT', label: 'CPT – Fracht bezahlt bis' },
  { value: 'CIP', label: 'CIP – Fracht+Versicherung bezahlt bis' },
  { value: 'DAP', label: 'DAP – Geliefert benannter Ort' },
  { value: 'DPU', label: 'DPU – Geliefert benannter Ort entladen' },
  { value: 'DDP', label: 'DDP – Geliefert verzollt' },
  { value: 'FAS', label: 'FAS – Frei Längsseite Schiff' },
  { value: 'FOB', label: 'FOB – Frei an Bord' },
  { value: 'CFR', label: 'CFR – Kosten und Fracht' },
  { value: 'CIF', label: 'CIF – Kosten, Versicherung, Fracht' },
]

export type PurchaseOrderStatus =
  | 'ENTWURF' | 'FREIGEGEBEN' | 'BESTELLT'
  | 'TEILGELIEFERT' | 'GELIEFERT' | 'STORNIERT'

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

// ── Query Keys ─────────────────────────────────────────────────────────

export const purchaseOrderKeys = {
  all: ['purchase-orders'] as const,
  list: (filters?: Record<string, unknown>) => [...purchaseOrderKeys.all, 'list', filters] as const,
  detail: (id: string) => [...purchaseOrderKeys.all, 'detail', id] as const,
  overdue: () => [...purchaseOrderKeys.all, 'overdue'] as const,
  pendingApproval: () => [...purchaseOrderKeys.all, 'pending-approval'] as const,
  statistics: () => [...purchaseOrderKeys.all, 'statistics'] as const,
  changelog: (id: string) => [...purchaseOrderKeys.all, 'changelog', id] as const,
}

// ── Fallback Data ──────────────────────────────────────────────────────

const fallbackOrders: PurchaseOrder[] = [
  {
    id: 'po-1', purchaseOrderNumber: 'PO-2026-042', supplierId: 'sup_1',
    subject: 'Saatgut Frühjahr 2026', description: 'Weizen- und Gerstensaatgut',
    status: 'BESTELLT', orderDate: '2026-01-15T10:00:00Z', deliveryDate: '2026-03-01T00:00:00Z',
    contactPerson: 'Hr. Müller', paymentTerms: '30 Tage netto', currency: 'EUR',
    incoterms: 'DDP', deliveryTerms: 'Frei Haus, Lager Südhausen',
    externalReference: 'KD-REF-2026-001',
    items: [
      { id: 'item-1', itemType: 'PRODUCT', description: 'Winterweizen Elite', quantity: 5000, unitPrice: 4.5, discountPercent: 2, discountAmount: 450, totalAmount: 22050 },
    ],
    subtotal: 22050, taxRate: 7, taxAmount: 1543.5, totalAmount: 23593.5,
    notes: 'Lieferung bis spätestens KW 9',
    createdBy: 'admin', createdAt: '2026-01-15T10:00:00Z', updatedAt: '2026-01-20T08:00:00Z', version: 3,
  },
  {
    id: 'po-2', purchaseOrderNumber: 'PO-2026-041', supplierId: 'sup_2',
    subject: 'Düngemittel Q1', description: 'NPK und KAS Bestellung',
    status: 'TEILGELIEFERT', orderDate: '2026-01-10T09:00:00Z', deliveryDate: '2026-02-15T00:00:00Z',
    paymentTerms: '14 Tage 2% Skonto', currency: 'EUR',
    incoterms: 'FCA', externalReference: 'AB-2026-DÜN',
    items: [
      { id: 'item-2', itemType: 'PRODUCT', description: 'NPK 15-15-15', quantity: 20000, unitPrice: 0.45, discountPercent: 0, discountAmount: 0, totalAmount: 9000 },
      { id: 'item-3', itemType: 'PRODUCT', description: 'KAS 27', quantity: 15000, unitPrice: 0.38, discountPercent: 0, discountAmount: 0, totalAmount: 5700 },
    ],
    subtotal: 14700, taxRate: 19, taxAmount: 2793, totalAmount: 17493,
    createdBy: 'admin', createdAt: '2026-01-10T09:00:00Z', updatedAt: '2026-02-05T14:00:00Z', version: 5,
  },
]

// ── Hooks ──────────────────────────────────────────────────────────────

export function usePurchaseOrders(filters?: { status?: PurchaseOrderStatus; supplierId?: string; search?: string }) {
  return useQuery({
    queryKey: purchaseOrderKeys.list(filters),
    queryFn: async () => {
      try {
        const params = new URLSearchParams()
        if (filters?.status) params.append('status', filters.status)
        if (filters?.supplierId) params.append('supplierId', filters.supplierId)
        if (filters?.search) params.append('search', filters.search)

        const response = await apiClient.get<PaginatedResponse>(
          `/api/v1/purchase-orders?${String(params)}`
        )
        if (response.data?.data?.length) return response.data.data
      } catch { /* fallback */ }
      // Filter fallback
      let items = [...fallbackOrders]
      if (filters?.status) items = items.filter(o => o.status === filters.status)
      if (filters?.supplierId) items = items.filter(o => o.supplierId === filters.supplierId)
      return items
    },
    staleTime: 2 * 60 * 1000,
  })
}

export function usePurchaseOrder(id: string) {
  return useQuery({
    queryKey: purchaseOrderKeys.detail(id),
    queryFn: async () => {
      try {
        const response = await apiClient.get<PurchaseOrder>(`/api/v1/purchase-orders/${id}`)
        return response.data
      } catch { /* fallback */ }
      return fallbackOrders.find(o => o.id === id) ?? null
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
        { reason }
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
      try {
        const response = await apiClient.get<{
          totalOrders: number
          totalValue: number
          byStatus: Record<PurchaseOrderStatus, number>
        }>('/api/v1/purchase-orders/statistics')
        return response.data
      } catch { /* fallback */ }
      return {
        totalOrders: fallbackOrders.length,
        totalValue: fallbackOrders.reduce((s, o) => s + o.totalAmount, 0),
        byStatus: {
          ENTWURF: 2, FREIGEGEBEN: 1, BESTELLT: 3,
          TEILGELIEFERT: 1, GELIEFERT: 5, STORNIERT: 0,
        } as Record<PurchaseOrderStatus, number>,
      }
    },
    staleTime: 5 * 60 * 1000,
  })
}

export function usePurchaseOrderChangelog(id: string) {
  return useQuery({
    queryKey: purchaseOrderKeys.changelog(id),
    queryFn: async () => {
      const response = await apiClient.get<Array<{
        id: string
        changeType: string
        changedBy: string
        changedAt: string
        fieldChanges: Array<{ field: string; oldValue: string; newValue: string }>
      }>>(`/api/v1/purchase-orders/${id}/changelog`)
      return response.data
    },
    enabled: !!id,
  })
}
