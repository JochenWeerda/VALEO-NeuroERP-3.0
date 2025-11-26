/**
 * Warehouse Service
 * API service for Warehouse management
 */

import { apiClient } from '../api-client'

// Types
export interface Warehouse {
  id: string
  tenant_id: string
  warehouse_code: string
  name: string
  address: string
  city: string
  postal_code: string
  country: string
  contact_person?: string
  phone?: string
  email?: string
  warehouse_type: string
  total_capacity?: number
  used_capacity: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface WarehouseCreate {
  tenant_id: string
  warehouse_code: string
  name: string
  address: string
  city: string
  postal_code: string
  country?: string
  contact_person?: string
  phone?: string
  email?: string
  warehouse_type?: string
}

export interface WarehouseUpdate {
  warehouse_code?: string
  name?: string
  address?: string
  city?: string
  postal_code?: string
  country?: string
  contact_person?: string
  phone?: string
  email?: string
  warehouse_type?: string
  is_active?: boolean
}

export interface WarehousesResponse {
  items: Warehouse[]
  total: number
  page: number
  size: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

// API Functions
export const warehouseService = {
  async getWarehouses(params?: {
    search?: string
    limit?: number
    offset?: number
    tenant_id?: string
  }) {
    const response = await apiClient.get<WarehousesResponse>('/api/v1/warehouses', { params })
    return response.data
  },

  async getWarehouse(id: string) {
    const response = await apiClient.get<Warehouse>(`/api/v1/warehouses/${id}`)
    return response.data
  },

  async createWarehouse(data: WarehouseCreate) {
    const response = await apiClient.post<Warehouse>('/api/v1/warehouses', data)
    return response.data
  },

  async updateWarehouse(id: string, data: WarehouseUpdate) {
    const response = await apiClient.put<Warehouse>(`/api/v1/warehouses/${id}`, data)
    return response.data
  },

  async deleteWarehouse(id: string) {
    await apiClient.delete(`/api/v1/warehouses/${id}`)
  }
}