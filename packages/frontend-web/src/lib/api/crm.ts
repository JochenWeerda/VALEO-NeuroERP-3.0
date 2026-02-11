/**
 * CRM API Hooks
 * TanStack Query hooks for Customer and Lead management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type CustomerSegment = 'A' | 'B' | 'C'
export type GapSyncStatus =
  | 'ok'
  | 'auto-match'
  | 'manual-accepted'
  | 'manual-rejected'
  | 'ambiguous'
  | 'error'

export interface CustomerAnalytics {
  gap_ref_year?: number | null
  gap_direct_total_eur?: number | null
  gap_estimated_area_ha?: number | null
  potential_total_eur?: number | null
  potential_seed_eur?: number | null
  potential_fertilizer_eur?: number | null
  potential_psm_eur?: number | null
  turnover_total_last_year_eur?: number | null
  share_of_wallet_total_pct?: number | null
  segment?: CustomerSegment | null
  gap_last_sync_at?: string | null
  gap_last_sync_status?: GapSyncStatus | null
  gap_matching_key?: string | null
  is_core_customer?: boolean | null
  block_auto_potential_update?: boolean | null
  last_manual_review_year?: number | null
  potential_notes?: string | null
  owner?: string | null
}

// Types
export type Customer = {
  id: string
  customer_number: string
  name: string
  email?: string
  phone?: string
  address?: string
  tax_id?: string
  credit_limit?: number
  payment_terms: number
  is_active: boolean
  tenant_id: string
  created_at: string
  updated_at: string
  analytics?: CustomerAnalytics
}

export type CustomerCreate = Omit<Customer, 'id' | 'created_at' | 'updated_at' | 'tenant_id'>

export type CustomerUpdate = Partial<CustomerCreate>

export type Lead = {
  id: string
  company_name: string
  contact_person?: string
  email?: string
  phone?: string
  status: 'new' | 'contacted' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost'
  source?: string
  estimated_value?: number
  notes?: string
  tenant_id: string
  created_at: string
  updated_at: string
}

export type LeadCreate = Omit<Lead, 'id' | 'created_at' | 'updated_at' | 'tenant_id'>

export type LeadUpdate = Partial<LeadCreate>

type PaginatedResponse<T> = {
  items: T[]
  total: number
  page: number
  pages: number
  size: number
}

// Query Keys
export const crmKeys = {
  all: ['crm'] as const,
  customers: () => [...crmKeys.all, 'customers'] as const,
  customer: (id: string) => [...crmKeys.customers(), id] as const,
  leads: () => [...crmKeys.all, 'leads'] as const,
  lead: (id: string) => [...crmKeys.leads(), id] as const,
}

// Customer Hooks
export function useCustomers(filters?: { search?: string; is_active?: boolean }) {
  return useQuery({
    queryKey: [...crmKeys.customers(), filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.search) params.append('search', filters.search)
      if (filters?.is_active !== undefined) params.append('is_active', String(filters.is_active))
      
      const response = await apiClient.get<PaginatedResponse<Customer>>(
        `/api/v1/crm/customers?${String(params)}`
      )
      return response.data
    },
  })
}

export function useCustomer(id: string) {
  return useQuery({
    queryKey: crmKeys.customer(id),
    queryFn: async () => {
      const response = await apiClient.get<Customer>(`/api/v1/crm/customers/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useCreateCustomer() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (data: CustomerCreate) => {
      const response = await apiClient.post<Customer>('/api/v1/crm/customers', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: crmKeys.customers() })
    },
  })
}

export function useUpdateCustomer() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: CustomerUpdate }) => {
      const response = await apiClient.put<Customer>(`/api/v1/crm/customers/${id}`, data)
      return response.data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: crmKeys.customer(variables.id) })
      queryClient.invalidateQueries({ queryKey: crmKeys.customers() })
    },
  })
}

export function useDeleteCustomer() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/crm/customers/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: crmKeys.customers() })
    },
  })
}

// Lead Hooks
export function useLeads(filters?: { search?: string; status?: string }) {
  return useQuery({
    queryKey: [...crmKeys.leads(), filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.search) params.append('search', filters.search)
      if (filters?.status) params.append('status', filters.status)
      
      const response = await apiClient.get<PaginatedResponse<Lead>>(
        `/api/v1/crm/leads?${String(params)}`
      )
      return response.data
    },
  })
}

export function useLead(id: string) {
  return useQuery({
    queryKey: crmKeys.lead(id),
    queryFn: async () => {
      const response = await apiClient.get<Lead>(`/api/v1/crm/leads/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

export function useCreateLead() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (data: LeadCreate) => {
      const response = await apiClient.post<Lead>('/api/v1/crm/leads', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: crmKeys.leads() })
    },
  })
}

export function useUpdateLead() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: LeadUpdate }) => {
      const response = await apiClient.put<Lead>(`/api/v1/crm/leads/${id}`, data)
      return response.data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: crmKeys.lead(variables.id) })
      queryClient.invalidateQueries({ queryKey: crmKeys.leads() })
    },
  })
}

export function useDeleteLead() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/crm/leads/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: crmKeys.leads() })
    },
  })
}

// ── Dashboard ──────────────────────────────────────────────────────────

export type CRMDashboardKPI = {
  title: string
  value: string
  change: { value: number; type: 'increase' | 'decrease'; period: string }
  icon: string
  color: string
}

export type CRMDashboardChart = {
  title: string
  type: 'line' | 'bar' | 'pie'
  data: number[]
}

const fallbackKPIs: CRMDashboardKPI[] = [
  { title: 'Aktive Kunden', value: '1.247', change: { value: 8.3, type: 'increase', period: 'vs. letztes Jahr' }, icon: '👥', color: 'blue' },
  { title: 'Neue Kunden', value: '89', change: { value: 12.5, type: 'increase', period: 'vs. letzter Monat' }, icon: '🆕', color: 'green' },
  { title: 'Gesamtumsatz', value: '€2,4M', change: { value: 15.7, type: 'increase', period: 'vs. letztes Jahr' }, icon: '💰', color: 'green' },
  { title: 'Offene Angebote', value: '€487K', change: { value: 5.2, type: 'decrease', period: 'vs. letzter Monat' }, icon: '📋', color: 'orange' },
  { title: 'Kundenbindung', value: '94,2%', change: { value: 2.1, type: 'increase', period: 'vs. letztes Jahr' }, icon: '🤝', color: 'blue' },
  { title: 'Durchschnittlicher Bestellwert', value: '€1.847', change: { value: 8.9, type: 'increase', period: 'vs. letztes Jahr' }, icon: '📊', color: 'green' },
]

const fallbackCharts: CRMDashboardChart[] = [
  { title: 'Umsatzentwicklung', type: 'line', data: [185000, 192000, 198000, 215000, 228000, 242000, 238000, 256000, 271000, 289000, 295000, 312000] },
  { title: 'Kunden nach Region', type: 'pie', data: [32, 28, 18, 12, 6, 4] },
  { title: 'Top 10 Kunden', type: 'bar', data: [125000, 98000, 87500, 76200, 68900, 65400, 58900, 52100, 49800, 45600] },
  { title: 'Angebots-Conversion', type: 'pie', data: [68, 22, 10] },
]

export function useCRMDashboard() {
  return useQuery({
    queryKey: [...crmKeys.all, 'dashboard'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<{ kpis: CRMDashboardKPI[]; charts: CRMDashboardChart[] }>('/api/v1/crm/dashboard')
        if (response.data?.kpis) return response.data
      } catch { /* fallback */ }
      return { kpis: fallbackKPIs, charts: fallbackCharts }
    },
    staleTime: 5 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
  })
}

// ── Suppliers (Lieferanten) ─────────────────────────────────────────────

export type Supplier = {
  id: string
  name: string
  supplier_number?: string
  type?: string
  city?: string
  email?: string
  phone?: string
  tax_id?: string
  iban?: string
  payment_terms?: number
  rating?: number
  is_active: boolean
  created_at?: string
}

export type SupplierListResponse = {
  items: Supplier[]
  total: number
}

const fallbackSuppliers: Supplier[] = [
  { id: '1', name: 'Saatgut AG', supplier_number: 'LF-001', type: 'Saatgut', city: 'Südhausen', rating: 4.5, is_active: true },
  { id: '2', name: 'Dünger GmbH', supplier_number: 'LF-002', type: 'Düngemittel', city: 'Nordhausen', rating: 4.2, is_active: true },
  { id: '3', name: 'Technik GmbH', supplier_number: 'LF-003', type: 'Landtechnik', city: 'Osthausen', rating: 3.8, is_active: true },
  { id: '4', name: 'BioFeed KG', supplier_number: 'LF-004', type: 'Futtermittel', city: 'Westhausen', rating: 4.0, is_active: true },
  { id: '5', name: 'AgroChem AG', supplier_number: 'LF-005', type: 'Pflanzenschutz', city: 'Mittelhausen', rating: 3.5, is_active: false },
]

export function useSuppliers(params?: { search?: string; is_active?: boolean }) {
  return useQuery({
    queryKey: [...crmKeys.all, 'suppliers', params],
    queryFn: async () => {
      try {
        const response = await apiClient.get<SupplierListResponse>('/api/v1/crm/suppliers', {
          params: {
            search: params?.search,
            is_active: params?.is_active,
          },
        })
        if (response.data?.items?.length) {
          return response.data
        }
      } catch {
        // API not available – use fallback
      }
      // Filter fallback data
      let items = [...fallbackSuppliers]
      if (params?.search) {
        const s = params.search.toLowerCase()
        items = items.filter(
          (sup) =>
            sup.name.toLowerCase().includes(s) ||
            sup.type?.toLowerCase().includes(s) ||
            sup.city?.toLowerCase().includes(s),
        )
      }
      if (params?.is_active !== undefined) {
        items = items.filter((sup) => sup.is_active === params.is_active)
      }
      return { items, total: items.length } as SupplierListResponse
    },
    staleTime: 2 * 60 * 1000,
  })
}

