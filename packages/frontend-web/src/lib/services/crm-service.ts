/**
 * CRM Service
 * API service for CRM operations (Contacts, Leads, Activities, Farm Profiles)
 */

import { apiClient } from '../api-client'

// Types
export interface Contact {
  id: string
  name: string
  company: string
  email: string
  phone: string
  type: 'customer' | 'supplier' | 'farmer'
  address?: {
    street: string
    city: string
    zipCode: string
    country: string
  }
  notes?: string
  createdAt: string
  updatedAt: string
}

export interface Lead {
  id: string
  company: string
  contactPerson: string
  email?: string
  phone?: string
  source: string
  potential: number
  priority: 'high' | 'medium' | 'low'
  status: 'new' | 'contacted' | 'qualified' | 'lost'
  assignedTo?: string
  expectedCloseDate?: string
  notes?: string
  createdAt: string
  updatedAt: string
}

export interface Activity {
  id: string
  type: 'meeting' | 'call' | 'email' | 'note' | 'visit' | 'task'
  title: string
  customer: string
  contactPerson: string
  date: string
  status: 'planned' | 'completed' | 'cancelled'
  assignedTo: string
  description?: string | null
  customerId?: string | null
  contactId?: string | null
  opportunityId?: string | null
  version?: number
  overdue?: boolean
  createdBy?: string | null
  updatedBy?: string | null
  mainTopics?: string[]
  ordersPlaced?: string[]
  followUpActions?: string[]
  createdAt: string
  updatedAt: string
}

export interface FarmProfile {
  id: string
  farmName: string
  owner: string
  totalArea: number
  crops: Array<{
    crop: string
    area: number
  }>
  livestock: Array<{
    type: string
    count: number
  }>
  location?: {
    latitude: number
    longitude: number
    address: string
  }
  certifications?: string[]
  notes?: string
  createdAt: string
  updatedAt: string
}

// Helper: API Response (snake_case) zu Frontend Model (camelCase) transformieren
function transformFarmProfile(apiData: Record<string, unknown>): FarmProfile {
  return {
    id: String(apiData.id ?? ''),
    farmName: String(apiData.farm_name ?? apiData.farmName ?? ''),
    owner: String(apiData.owner ?? ''),
    totalArea: Number(apiData.total_area ?? apiData.totalArea ?? 0),
    crops: (apiData.crops as FarmProfile['crops']) || [],
    livestock: (apiData.livestock as FarmProfile['livestock']) || [],
    location: apiData.location as FarmProfile['location'],
    certifications: (apiData.certifications as string[]) || [],
    notes: apiData.notes !== undefined ? String(apiData.notes) : undefined,
    createdAt: String(apiData.created_at ?? apiData.createdAt ?? ''),
    updatedAt: String(apiData.updated_at ?? apiData.updatedAt ?? ''),
  }
}

function transformActivity(apiData: Record<string, unknown>): Activity {
  return {
    id: String(apiData.id ?? ''),
    type: (apiData.type as Activity['type']) || 'note',
    title: String(apiData.title ?? ''),
    customer: String(apiData.customer ?? ''),
    contactPerson: String(apiData.contact_person ?? ''),
    date: String(apiData.date ?? ''),
    status: (apiData.status as Activity['status']) || 'planned',
    assignedTo: String(apiData.assigned_to ?? ''),
    description: apiData.description == null ? null : String(apiData.description),
    customerId: apiData.customer_id == null ? null : String(apiData.customer_id),
    contactId: apiData.contact_id == null ? null : String(apiData.contact_id),
    opportunityId: apiData.opportunity_id == null ? null : String(apiData.opportunity_id),
    version: typeof apiData.version === 'number' ? apiData.version : undefined,
    overdue: apiData.overdue === true,
    createdBy: apiData.created_by == null ? null : String(apiData.created_by),
    updatedBy: apiData.updated_by == null ? null : String(apiData.updated_by),
    mainTopics: ((apiData.main_topics ?? []) as unknown[]).map((item) => String(item)),
    ordersPlaced: ((apiData.orders_placed ?? []) as unknown[]).map((item) => String(item)),
    followUpActions: ((apiData.follow_up_actions ?? []) as unknown[]).map((item) => String(item)),
    createdAt: String(apiData.created_at ?? ''),
    updatedAt: String(apiData.updated_at ?? ''),
  }
}

export type ActivityWrite = Partial<Pick<Activity, 'type' | 'title' | 'customer' | 'contactPerson' | 'date' | 'status' | 'assignedTo' | 'description' | 'customerId' | 'contactId' | 'opportunityId' | 'mainTopics' | 'ordersPlaced' | 'followUpActions'>>

type ActivityIntent = { idempotencyKey: string }
type ActivityVersionedIntent = ActivityIntent & { expectedVersion: number }

function activityPayload(data: ActivityWrite): Record<string, unknown> {
  const names: Record<string, string> = {
    type: 'type', title: 'title', customer: 'customer', contactPerson: 'contact_person',
    date: 'date', status: 'status', assignedTo: 'assigned_to', description: 'description',
    customerId: 'customer_id', contactId: 'contact_id', opportunityId: 'opportunity_id',
    mainTopics: 'main_topics', ordersPlaced: 'orders_placed', followUpActions: 'follow_up_actions',
  }
  const result: Record<string, unknown> = {}
  for (const [key, name] of Object.entries(names)) {
    const value = data[key as keyof ActivityWrite]
    if (value !== undefined) result[name] = key === 'date' && value === '' ? null : key === 'date' && typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value) ? `${value}T00:00:00Z` : value
  }
  return result
}

function requireIntent(options: ActivityIntent): string {
  if (!options?.idempotencyKey?.trim()) throw new Error('Ein Idempotenzschlüssel ist erforderlich.')
  return options.idempotencyKey
}

function requireVersion(options: ActivityVersionedIntent): number {
  if (!Number.isInteger(options?.expectedVersion) || options.expectedVersion < 1) {
    throw new Error('Die aktuelle Version der Aktivität fehlt. Bitte erneut laden.')
  }
  return options.expectedVersion
}

function unwrapItem<T>(payload: unknown): T {
  if (payload && typeof payload === 'object' && 'data' in payload) {
    return payload.data as T
  }
  return payload as T
}

// API Functions
export const crmService = {
  // Contacts
  async getContacts(params?: { search?: string; type?: string; limit?: number; offset?: number }) {
    const response = await apiClient.get<{ items?: Contact[]; data?: Contact[]; total: number }>('/api/v1/crm/contacts', { params })
    const items = response.data.items || response.data.data || []
    return { data: items, total: response.data.total }
  },

  async getContact(id: string) {
    const response = await apiClient.get<Contact>(`/api/v1/crm/contacts/${id}`)
    return unwrapItem<Contact>(response.data)
  },

  async createContact(data: Omit<Contact, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<Contact>('/api/v1/crm/contacts', data)
    return unwrapItem<Contact>(response.data)
  },

  async updateContact(id: string, data: Partial<Omit<Contact, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<Contact>(`/api/v1/crm/contacts/${id}`, data)
    return unwrapItem<Contact>(response.data)
  },

  async deleteContact(id: string) {
    await apiClient.delete(`/api/v1/crm/contacts/${id}`)
  },

  // Leads
  async getLeads(params?: { search?: string; status?: string; priority?: string; limit?: number; offset?: number }) {
    const response = await apiClient.get<{ items?: Lead[]; data?: Lead[]; total: number }>('/api/v1/crm/leads', { params })
    const items = response.data.items || response.data.data || []
    return { data: items, total: response.data.total }
  },

  async getLead(id: string) {
    const response = await apiClient.get<Lead>(`/api/v1/crm/leads/${id}`)
    return unwrapItem<Lead>(response.data)
  },

  // Übernommene CRM-Leads stammen aus dem Lead-Generierung-Funnel (public.crm_leads).
  // Liste (/crm/lead-generierung/leads) und Detail müssen DIESELBE Quelle nutzen,
  // sonst läuft das Detail ins Leere (404 auf /crm/leads/{id}).
  async getFunnelLead(id: string) {
    const response = await apiClient.get<Lead>(`/api/v1/crm/lead-generierung/leads/${id}`)
    return unwrapItem<Lead>(response.data)
  },

  async createLead(data: Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<Lead>('/api/v1/crm/leads', data)
    return unwrapItem<Lead>(response.data)
  },

  async updateLead(id: string, data: Partial<Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<Lead>(`/api/v1/crm/leads/${id}`, data)
    return unwrapItem<Lead>(response.data)
  },

  async deleteLead(id: string) {
    await apiClient.delete(`/api/v1/crm/leads/${id}`)
  },

  // Activities
  async getActivities(params?: { search?: string; type?: string; status?: string; limit?: number; offset?: number }) {
    const response = await apiClient.get<{ items?: Record<string, unknown>[]; total?: number }>('/api/v1/crm/activities', { params })
    const items = response.data.items || []
    return { data: items.map(transformActivity), total: response.data.total || 0 }
  },

  async getActivity(id: string) {
    const response = await apiClient.get<Record<string, unknown>>(`/api/v1/crm/activities/${id}`)
    return transformActivity(unwrapItem<Record<string, unknown>>(response.data))
  },

  async createActivity(data: ActivityWrite, options: ActivityIntent) {
    const response = await apiClient.post<Record<string, unknown>>('/api/v1/crm/activities', { ...activityPayload(data), idempotency_key: requireIntent(options) })
    return transformActivity(unwrapItem<Record<string, unknown>>(response.data))
  },

  async updateActivity(id: string, data: ActivityWrite, options: ActivityVersionedIntent) {
    const response = await apiClient.put<Record<string, unknown>>(`/api/v1/crm/activities/${id}`, { ...activityPayload(data), expected_version: requireVersion(options), idempotency_key: requireIntent(options) })
    return transformActivity(unwrapItem<Record<string, unknown>>(response.data))
  },

  async deleteActivity(id: string, options: ActivityVersionedIntent) {
    await apiClient.delete(`/api/v1/crm/activities/${id}`, { headers: { 'If-Match': `"${requireVersion(options)}"`, 'Idempotency-Key': requireIntent(options) } })
  },

  // Betriebsprofile (Farm Profiles)
  async getFarmProfiles(params?: { search?: string; limit?: number; offset?: number }) {
    try {
      const response = await apiClient.get<{ items: Record<string, unknown>[]; total: number }>('/api/v1/crm/farm-profiles', { params })
      // API gibt { items, total } zurück mit snake_case, Frontend erwartet { data, total } mit camelCase
      const transformedItems = (response.data.items || []).map(transformFarmProfile)
      return { data: transformedItems, total: response.data.total || 0 }
    } catch (_error) {
      // Bei Backend-Fehler (z.B. fehlende Tabelle) leere Liste zurückgeben
      return { data: [], total: 0 }
    }
  },

  async getFarmProfile(id: string) {
    const response = await apiClient.get<Record<string, unknown>>(`/api/v1/crm/farm-profiles/${id}`)
    return transformFarmProfile(unwrapItem<Record<string, unknown>>(response.data))
  },

  async createFarmProfile(data: Omit<FarmProfile, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<Record<string, unknown>>('/api/v1/crm/farm-profiles', data)
    return transformFarmProfile(unwrapItem<Record<string, unknown>>(response.data))
  },

  async updateFarmProfile(id: string, data: Partial<Omit<FarmProfile, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<Record<string, unknown>>(`/api/v1/crm/farm-profiles/${id}`, data)
    return transformFarmProfile(unwrapItem<Record<string, unknown>>(response.data))
  },

  async deleteFarmProfile(id: string) {
    await apiClient.delete(`/api/v1/crm/farm-profiles/${id}`)
  },

  async syncFarmProfileSubResources(
    id: string,
    collections: {
      crops?: Array<{ crop: string; area: number }>
      livestock?: Array<{ type: string; count: number }>
      certifications?: string[]
    },
  ) {
    const syncIndexedList = async <T>(
      basePath: string,
      targetItems: T[],
    ) => {
      const currentResponse = await apiClient.get<T[]>(basePath)
      const currentItems = currentResponse.data || []
      const commonLength = Math.min(currentItems.length, targetItems.length)

      for (let index = 0; index < commonLength; index += 1) {
        await apiClient.put(`${basePath}/${index}`, targetItems[index])
      }
      for (let index = commonLength; index < targetItems.length; index += 1) {
        await apiClient.post(basePath, targetItems[index])
      }
      for (let index = currentItems.length - 1; index >= targetItems.length; index -= 1) {
        await apiClient.delete(`${basePath}/${index}`)
      }
    }

    if (collections.crops) {
      await syncIndexedList(`/api/v1/crm/farm-profiles/${id}/crops`, collections.crops)
    }
    if (collections.livestock) {
      await syncIndexedList(`/api/v1/crm/farm-profiles/${id}/livestock`, collections.livestock)
    }
    if (collections.certifications) {
      await syncIndexedList(
        `/api/v1/crm/farm-profiles/${id}/certifications`,
        collections.certifications.map((value) => ({ value })),
      )
    }
  },

}
