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
  type: 'meeting' | 'call' | 'email' | 'note'
  title: string
  customer: string
  contactPerson: string
  date: string
  status: 'planned' | 'completed' | 'overdue'
  assignedTo: string
  description?: string
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
function transformFarmProfile(apiData: any): FarmProfile {
  return {
    id: apiData.id,
    farmName: apiData.farm_name || apiData.farmName || '',
    owner: apiData.owner || '',
    totalArea: apiData.total_area ?? apiData.totalArea ?? 0,
    crops: apiData.crops || [],
    livestock: apiData.livestock || [],
    location: apiData.location,
    certifications: apiData.certifications || [],
    notes: apiData.notes,
    createdAt: apiData.created_at || apiData.createdAt || '',
    updatedAt: apiData.updated_at || apiData.updatedAt || '',
  }
}

function transformActivity(apiData: any): Activity {
  return {
    id: apiData.id,
    type: apiData.type || 'note',
    title: apiData.title || '',
    customer: apiData.customer || apiData.customer_name || '',
    contactPerson: apiData.contact_person || apiData.contactPerson || '',
    date: apiData.date || apiData.scheduled_at || '',
    status: apiData.status || 'planned',
    assignedTo: apiData.assigned_to || apiData.assignedTo || '',
    description: apiData.description,
    mainTopics: (apiData.main_topics || apiData.mainTopics || []).map((item: unknown) => String(item)),
    ordersPlaced: (apiData.orders_placed || apiData.ordersPlaced || []).map((item: unknown) => String(item)),
    followUpActions: (apiData.follow_up_actions || apiData.followUpActions || []).map((item: unknown) => String(item)),
    createdAt: apiData.created_at || apiData.createdAt || '',
    updatedAt: apiData.updated_at || apiData.updatedAt || '',
  }
}

function unwrapItem<T>(payload: any): T {
  if (payload && typeof payload === 'object' && 'data' in payload) {
    return payload.data as T
  }
  return payload as T
}

// API Functions
export const crmService = {
  // Contacts
  async getContacts(params?: { search?: string; type?: string; limit?: number; offset?: number }) {
    const response = await apiClient.get<{ data: Contact[]; total: number }>('/api/v1/crm/contacts', { params })
    return response.data
  },

  async getContact(id: string) {
    const response = await apiClient.get<{ data: Contact }>(`/api/v1/crm/contacts/${id}`)
    return response.data.data
  },

  async createContact(data: Omit<Contact, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<{ data: Contact }>('/api/v1/crm/contacts', data)
    return response.data.data
  },

  async updateContact(id: string, data: Partial<Omit<Contact, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<{ data: Contact }>(`/api/v1/crm/contacts/${id}`, data)
    return response.data.data
  },

  async deleteContact(id: string) {
    await apiClient.delete(`/api/v1/crm/contacts/${id}`)
  },

  // Leads
  async getLeads(params?: { search?: string; status?: string; priority?: string; limit?: number; offset?: number }) {
    const response = await apiClient.get<{ data: Lead[]; total: number }>('/api/v1/crm/leads', { params })
    return response.data
  },

  async getLead(id: string) {
    const response = await apiClient.get<{ data: Lead }>(`/api/v1/crm/leads/${id}`)
    return response.data.data
  },

  async createLead(data: Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<{ data: Lead }>('/api/v1/crm/leads', data)
    return response.data.data
  },

  async updateLead(id: string, data: Partial<Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<{ data: Lead }>(`/api/v1/crm/leads/${id}`, data)
    return response.data.data
  },

  async deleteLead(id: string) {
    await apiClient.delete(`/api/v1/crm/leads/${id}`)
  },

  // Activities
  async getActivities(params?: { search?: string; type?: string; status?: string; limit?: number; offset?: number }) {
    const response = await apiClient.get<{ items?: any[]; total?: number }>('/api/v1/crm/activities', { params })
    const items = response.data.items || []
    return { data: items.map(transformActivity), total: response.data.total || 0 }
  },

  async getActivity(id: string) {
    const response = await apiClient.get<any>(`/api/v1/crm/activities/${id}`)
    return transformActivity(unwrapItem<any>(response.data))
  },

  async createActivity(data: Omit<Activity, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<any>('/api/v1/crm/activities', data)
    return transformActivity(unwrapItem<any>(response.data))
  },

  async updateActivity(id: string, data: Partial<Omit<Activity, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<any>(`/api/v1/crm/activities/${id}`, data)
    return transformActivity(unwrapItem<any>(response.data))
  },

  async deleteActivity(id: string) {
    await apiClient.delete(`/api/v1/crm/activities/${id}`)
  },

  // Betriebsprofile (Farm Profiles)
  async getFarmProfiles(params?: { search?: string; limit?: number; offset?: number }) {
    try {
      const response = await apiClient.get<{ items: any[]; total: number }>('/api/v1/crm/farm-profiles', { params })
      // API gibt { items, total } zurück mit snake_case, Frontend erwartet { data, total } mit camelCase
      const transformedItems = (response.data.items || []).map(transformFarmProfile)
      return { data: transformedItems, total: response.data.total || 0 }
    } catch (_error) {
      // Bei Backend-Fehler (z.B. fehlende Tabelle) leere Liste zurückgeben
      return { data: [], total: 0 }
    }
  },

  async getFarmProfile(id: string) {
    const response = await apiClient.get<any>(`/api/v1/crm/farm-profiles/${id}`)
    return transformFarmProfile(unwrapItem<any>(response.data))
  },

  async createFarmProfile(data: Omit<FarmProfile, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<any>('/api/v1/crm/farm-profiles', data)
    return transformFarmProfile(unwrapItem<any>(response.data))
  },

  async updateFarmProfile(id: string, data: Partial<Omit<FarmProfile, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<any>(`/api/v1/crm/farm-profiles/${id}`, data)
    return transformFarmProfile(unwrapItem<any>(response.data))
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

  async syncActivitySubResources(
    id: string,
    collections: {
      mainTopics?: string[]
      ordersPlaced?: string[]
      followUpActions?: string[]
    },
  ) {
    const syncStringList = async (basePath: string, targetItems: string[]) => {
      const currentResponse = await apiClient.get<string[]>(basePath)
      const currentItems = currentResponse.data || []
      const commonLength = Math.min(currentItems.length, targetItems.length)

      for (let index = 0; index < commonLength; index += 1) {
        await apiClient.put(`${basePath}/${index}`, { value: targetItems[index] })
      }
      for (let index = commonLength; index < targetItems.length; index += 1) {
        await apiClient.post(basePath, { value: targetItems[index] })
      }
      for (let index = currentItems.length - 1; index >= targetItems.length; index -= 1) {
        await apiClient.delete(`${basePath}/${index}`)
      }
    }

    if (collections.mainTopics) {
      await syncStringList(`/api/v1/crm/activities/${id}/main-topics`, collections.mainTopics)
    }
    if (collections.ordersPlaced) {
      await syncStringList(`/api/v1/crm/activities/${id}/orders-placed`, collections.ordersPlaced)
    }
    if (collections.followUpActions) {
      await syncStringList(`/api/v1/crm/activities/${id}/follow-up-actions`, collections.followUpActions)
    }
  },
}
