import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { authenticatedFetch } from '@/lib/fetch'

// Types
export interface Opportunity {
  id: string
  number?: string
  name: string
  customer_id?: string
  customer_name?: string
  contact_id?: string
  contact_name?: string
  owner_id?: string
  assigned_to?: string
  stage: string
  status: string
  amount?: number
  currency?: string
  probability?: number
  expected_revenue?: number
  expected_close_date?: string
  source?: string
  description?: string
  created_at?: string
  updated_at?: string
}

export interface Customer {
  id: string
  name: string
  company?: string
  email?: string
  phone?: string
}

export interface Contact {
  id: string
  name: string
  email?: string
  phone?: string
  customer_id?: string
}

// Fetch opportunities with customer/contact resolution
async function fetchOpportunities(params?: Record<string, string>): Promise<Opportunity[]> {
  const searchParams = new URLSearchParams(params)
  const response = await authenticatedFetch(`/api/crm-sales/opportunities?${searchParams.toString()}`)

  if (!response.ok) {
    throw new Error('Failed to fetch opportunities')
  }

  const result = await response.json()
  const opportunities = result.data || result.items || result || []

  // Enrich with customer names if needed
  return opportunities
}

// Fetch single opportunity
async function fetchOpportunity(id: string): Promise<Opportunity> {
  const response = await authenticatedFetch(`/api/crm-sales/opportunities/${id}`)

  if (!response.ok) {
    throw new Error('Failed to fetch opportunity')
  }

  return response.json()
}

// Fetch customers for select dropdown
async function fetchCustomers(): Promise<Customer[]> {
  try {
    const response = await authenticatedFetch('/api/v1/crm/customers?limit=500')

    if (!response.ok) {
      return []
    }

    const result = await response.json()
    return result.data || result.items || result || []
  } catch {
    return []
  }
}

// Fetch contacts for select dropdown
async function fetchContacts(customerId?: string): Promise<Contact[]> {
  try {
    const url = customerId
      ? `/api/crm-sales/contacts?customer_id=${customerId}&limit=500`
      : '/api/crm-sales/contacts?limit=500'
    const response = await authenticatedFetch(url)

    if (!response.ok) {
      return []
    }

    const result = await response.json()
    return result.data || result.items || result || []
  } catch {
    return []
  }
}

// Create opportunity
async function createOpportunity(data: Partial<Opportunity>): Promise<Opportunity> {
  const response = await authenticatedFetch('/api/crm-sales/opportunities', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error('Failed to create opportunity')
  }

  return response.json()
}

// Update opportunity
async function updateOpportunity(id: string, data: Partial<Opportunity>): Promise<Opportunity> {
  const response = await authenticatedFetch(`/api/crm-sales/opportunities/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error('Failed to update opportunity')
  }

  return response.json()
}

// Delete opportunity
async function deleteOpportunity(id: string): Promise<void> {
  const response = await authenticatedFetch(`/api/crm-sales/opportunities/${id}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error('Failed to delete opportunity')
  }
}

// Hooks

export function useOpportunities(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['opportunities', params],
    queryFn: () => fetchOpportunities(params),
    initialData: [],
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

export function useOpportunity(id: string) {
  return useQuery({
    queryKey: ['opportunity', id],
    queryFn: () => fetchOpportunity(id),
    enabled: !!id,
    initialData: null,
  })
}

export function useCustomersForSelect() {
  return useQuery({
    queryKey: ['customers-select'],
    queryFn: fetchCustomers,
    initialData: [],
    staleTime: 5 * 60 * 1000, // 5 minutes
    select: (data) => data.map((c) => ({
      value: c.id,
      label: c.company ? `${c.name} (${c.company})` : c.name,
    })),
  })
}

export function useContactsForSelect(customerId?: string) {
  return useQuery({
    queryKey: ['contacts-select', customerId],
    queryFn: () => fetchContacts(customerId),
    initialData: [],
    staleTime: 5 * 60 * 1000, // 5 minutes
    select: (data) => data.map((c) => ({
      value: c.id,
      label: c.email ? `${c.name} (${c.email})` : c.name,
    })),
  })
}

export function useCreateOpportunity() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createOpportunity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] })
    },
  })
}

export function useUpdateOpportunity() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Opportunity> }) =>
      updateOpportunity(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] })
      queryClient.invalidateQueries({ queryKey: ['opportunity', id] })
    },
  })
}

export function useDeleteOpportunity() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteOpportunity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] })
    },
  })
}

// Helper to build customer lookup map
export function useCustomerLookup() {
  const { data: customers } = useQuery({
    queryKey: ['customers-lookup'],
    queryFn: fetchCustomers,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })

  const lookup = new Map<string, Customer>()
  customers.forEach((c) => lookup.set(c.id, c))

  return {
    getCustomerName: (id: string) => lookup.get(id)?.name || lookup.get(id)?.company || id,
    customers: lookup,
  }
}
