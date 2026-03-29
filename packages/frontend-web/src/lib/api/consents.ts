import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { authenticatedFetch } from '@/lib/fetch'

// Types
export interface Consent {
  id: string
  contact_id: string
  contact_name?: string
  channel: 'email' | 'sms' | 'phone' | 'postal'
  consent_type: 'marketing' | 'service' | 'required'
  status: 'pending' | 'granted' | 'revoked' | 'expired'
  granted_at?: string
  revoked_at?: string
  expires_at?: string
  source?: string
  ip_address?: string
  consent_text?: string
  version?: string
  created_at?: string
  updated_at?: string
}

export interface Contact {
  id: string
  name: string
  email?: string
  phone?: string
  customer_id?: string
}

// Fetch consents
async function fetchConsents(params?: Record<string, string>): Promise<Consent[]> {
  const searchParams = new URLSearchParams(params)

  try {
    const response = await authenticatedFetch(`/api/v1/crm/consents?${searchParams.toString()}`)

    if (!response.ok) {
      return []
    }

    const result = await response.json()
    return result.data || result.items || result || []
  } catch {
    return []
  }
}

// Fetch single consent
async function fetchConsent(id: string): Promise<Consent | null> {
  try {
    const response = await authenticatedFetch(`/api/v1/crm/consents/${id}`)

    if (!response.ok) {
      return null
    }

    return response.json()
  } catch {
    return null
  }
}

// Fetch contacts for select dropdown
async function fetchContacts(): Promise<Contact[]> {
  try {
    const response = await authenticatedFetch('/api/v1/crm/contacts?limit=500')

    if (!response.ok) {
      return []
    }

    const result = await response.json()
    return result.data || result.items || result || []
  } catch {
    return []
  }
}

// Create consent
async function createConsent(data: Partial<Consent>): Promise<Consent> {
  const response = await authenticatedFetch('/api/v1/crm/consents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error('Failed to create consent')
  }

  return response.json()
}

// Update consent
async function updateConsent(id: string, data: Partial<Consent>): Promise<Consent> {
  const response = await authenticatedFetch(`/api/v1/crm/consents/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error('Failed to update consent')
  }

  return response.json()
}

// Grant consent
async function grantConsent(id: string): Promise<Consent> {
  const response = await authenticatedFetch(`/api/v1/crm/consents/${id}/grant`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error('Failed to grant consent')
  }

  return response.json()
}

// Revoke consent
async function revokeConsent(id: string): Promise<Consent> {
  const response = await authenticatedFetch(`/api/v1/crm/consents/${id}/revoke`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error('Failed to revoke consent')
  }

  return response.json()
}

// Delete consent
async function deleteConsent(id: string): Promise<void> {
  const response = await authenticatedFetch(`/api/v1/crm/consents/${id}`, {
    method: 'DELETE',
  })

  if (!response.ok) {
    throw new Error('Failed to delete consent')
  }
}

// Hooks

export function useConsents(params?: Record<string, string>) {
  return useQuery({
    queryKey: ['consents', params],
    queryFn: () => fetchConsents(params),
    initialData: [],
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

export function useConsent(id: string) {
  return useQuery({
    queryKey: ['consent', id],
    queryFn: () => fetchConsent(id),
    enabled: !!id,
    initialData: null,
  })
}

export function useContactsForConsentSelect() {
  return useQuery({
    queryKey: ['contacts-consent-select'],
    queryFn: fetchContacts,
    initialData: [],
    staleTime: 5 * 60 * 1000, // 5 minutes
    select: (data) => data.map((c) => ({
      value: c.id,
      label: c.email ? `${c.name} (${c.email})` : c.name,
    })),
  })
}

export function useCreateConsent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createConsent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['consents'] })
    },
  })
}

export function useUpdateConsent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Consent> }) =>
      updateConsent(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['consents'] })
      queryClient.invalidateQueries({ queryKey: ['consent', id] })
    },
  })
}

export function useGrantConsent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: grantConsent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['consents'] })
    },
  })
}

export function useRevokeConsent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: revokeConsent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['consents'] })
    },
  })
}

export function useDeleteConsent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteConsent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['consents'] })
    },
  })
}

// Helper to build contact lookup map
export function useContactLookup() {
  const { data: contacts } = useQuery({
    queryKey: ['contacts-lookup'],
    queryFn: fetchContacts,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })

  const lookup = new Map<string, Contact>()
  contacts.forEach((c) => lookup.set(c.id, c))

  return {
    getContactName: (id: string) => lookup.get(id)?.name || id,
    getContactEmail: (id: string) => lookup.get(id)?.email,
    contacts: lookup,
  }
}
