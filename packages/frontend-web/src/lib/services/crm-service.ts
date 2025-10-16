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
    const response = await apiClient.get<{ data: Activity[]; total: number }>('/api/v1/crm/activities', { params })
    return response.data
  },

  async getActivity(id: string) {
    const response = await apiClient.get<{ data: Activity }>(`/api/v1/crm/activities/${id}`)
    return response.data.data
  },

  async createActivity(data: Omit<Activity, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<{ data: Activity }>('/api/v1/crm/activities', data)
    return response.data.data
  },

  async updateActivity(id: string, data: Partial<Omit<Activity, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<{ data: Activity }>(`/api/v1/crm/activities/${id}`, data)
    return response.data.data
  },

  async deleteActivity(id: string) {
    await apiClient.delete(`/api/v1/crm/activities/${id}`)
  },

  // Farm Profiles
  async getFarmProfiles(params?: { search?: string; limit?: number; offset?: number }) {
    const response = await apiClient.get<{ data: FarmProfile[]; total: number }>('/api/v1/crm/farm-profiles', { params })
    return response.data
  },

  async getFarmProfile(id: string) {
    const response = await apiClient.get<{ data: FarmProfile }>(`/api/v1/crm/farm-profiles/${id}`)
    return response.data.data
  },

  async createFarmProfile(data: Omit<FarmProfile, 'id' | 'createdAt' | 'updatedAt'>) {
    const response = await apiClient.post<{ data: FarmProfile }>('/api/v1/crm/farm-profiles', data)
    return response.data.data
  },

  async updateFarmProfile(id: string, data: Partial<Omit<FarmProfile, 'id' | 'createdAt' | 'updatedAt'>>) {
    const response = await apiClient.put<{ data: FarmProfile }>(`/api/v1/crm/farm-profiles/${id}`, data)
    return response.data.data
  },

  async deleteFarmProfile(id: string) {
    await apiClient.delete(`/api/v1/crm/farm-profiles/${id}`)
  },
}