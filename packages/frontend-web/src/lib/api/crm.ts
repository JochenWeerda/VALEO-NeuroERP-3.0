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
  /** Verknüpfter Business-Partner (Verkaufs-Stammdaten), falls gespeichert */
  business_partner_id?: string | null
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

export type CustomerCreate = Omit<Customer, 'id' | 'created_at' | 'updated_at' | 'tenant_id'> & {
  /** Backend erwartet `company_name`; optional, falls nur `name` gesetzt ist. */
  company_name?: string
}

export type CustomerUpdate = Partial<CustomerCreate>

export type CustomerScreenSummary = {
  schema_version: 1
  screen_id: 'crm/customer-360'
  customer_id: string
  tenant_id?: string | null
  title: string
  subtitle?: string | null
  summary: {
    sales_ytd: number
    open_items_total: number
    recent_activity_count: number
    credit_status: 'ok' | 'warning' | string
  }
  badges: Array<{ key: string; label: string; tone?: string }>
  available_tabs: string[]
  tab_endpoints?: Record<string, string>
  actions: Array<{ key: string; label: string; permission?: string }>
  performance: {
    initial_payload_budget_kb: number
    tabs_lazy: boolean
    lookup_min_chars: number
    default_table_limit: number
  }
}

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

const EMPTY_CUSTOMER_LIST: PaginatedResponse<Customer> = {
  items: [],
  total: 0,
  page: 1,
  pages: 0,
  size: 0,
}

const EMPTY_LEAD_LIST: PaginatedResponse<Lead> = {
  items: [],
  total: 0,
  page: 1,
  pages: 0,
  size: 0,
}

const EMPTY_CRM_DASHBOARD: { kpis: CRMDashboardKPI[]; charts: CRMDashboardChart[] } = {
  kpis: [],
  charts: [],
}

const EMPTY_SUPPLIER_LIST: SupplierListResponse = {
  items: [],
  total: 0,
}

// Query Keys
export const crmKeys = {
  all: ['crm'] as const,
  customers: () => [...crmKeys.all, 'customers'] as const,
  customer: (id: string) => [...crmKeys.customers(), id] as const,
  customerScreenSummary: (id: string) => [...crmKeys.customer(id), 'screen-summary'] as const,
  customerTabData: (id: string, tabKey: string) => [...crmKeys.customer(id), 'tab-data', tabKey] as const,
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
        `/api/v1/crm/customers?${String(params)}`,
      )
      return response.data
    },
    initialData: EMPTY_CUSTOMER_LIST,
  })
}

export function useCustomer(id: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: crmKeys.customer(id),
    queryFn: async () => {
      const response = await apiClient.get<Customer>(`/api/v1/crm/customers/${id}`)
      return response.data
    },
    enabled: !!id && (options?.enabled ?? true),
    initialData: null,
  })
}

export function useCustomerScreenSummary(id: string) {
  return useQuery({
    queryKey: crmKeys.customerScreenSummary(id),
    queryFn: async () => {
      const response = await apiClient.get<CustomerScreenSummary>(`/api/v1/crm/customers/${id}/screen-summary`)
      return response.data
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
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

      const response = await apiClient.get<PaginatedResponse<Lead>>(`/api/v1/crm/leads?${String(params)}`)
      return response.data
    },
    initialData: EMPTY_LEAD_LIST,
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
    initialData: null,
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

// Dashboard

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

export function useCRMDashboard() {
  return useQuery({
    queryKey: [...crmKeys.all, 'dashboard'],
    queryFn: async () => {
      const response = await apiClient.get<{ kpis: CRMDashboardKPI[]; charts: CRMDashboardChart[] }>(
        '/api/v1/crm/dashboard',
      )
      return response.data
    },
    initialData: EMPTY_CRM_DASHBOARD,
    staleTime: 5 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
  })
}

// Suppliers (Lieferanten)

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

export function useSuppliers(params?: { search?: string; is_active?: boolean }) {
  return useQuery({
    queryKey: [...crmKeys.all, 'suppliers', params],
    queryFn: async () => {
      const response = await apiClient.get<SupplierListResponse>('/api/v1/crm/suppliers', {
        params: {
          search: params?.search,
          is_active: params?.is_active,
        },
      })
      return response.data
    },
    initialData: EMPTY_SUPPLIER_LIST,
    staleTime: 2 * 60 * 1000,
  })
}
