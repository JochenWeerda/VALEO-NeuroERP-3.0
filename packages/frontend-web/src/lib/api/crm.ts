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

