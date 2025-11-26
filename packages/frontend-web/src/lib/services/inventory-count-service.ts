/**
 * Inventory Count Service
 * API service for Inventory Count management
 */

import { apiClient } from '../api-client'

// Types
export interface InventoryCount {
  id: string
  tenant_id: string
  warehouse_id: string
  count_date: string
  counted_by: string
  status: 'draft' | 'completed' | 'approved'
  total_items: number
  discrepancies_found: number
  approved_by?: string
  approved_at?: string
  created_at: string
  updated_at: string
}

export interface InventoryCountCreate {
  tenant_id: string
  warehouse_id: string
  count_date?: string
  counted_by: string
  status?: 'draft' | 'completed' | 'approved'
}

export interface InventoryCountUpdate {
  count_date?: string
  counted_by?: string
  status?: 'draft' | 'completed' | 'approved'
  total_items?: number
  discrepancies_found?: number
  approved_by?: string
  approved_at?: string
}

export interface InventoryCountsResponse {
  items: InventoryCount[]
  total: number
  page: number
  size: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

// API Functions
export const inventoryCountService = {
  async getInventoryCounts(params?: {
    warehouse_id?: string
    status?: string
    limit?: number
    offset?: number
    tenant_id?: string
  }) {
    const response = await apiClient.get<InventoryCountsResponse>('/api/v1/inventory/counts', { params })
    return response.data
  },

  async getInventoryCount(id: string) {
    const response = await apiClient.get<InventoryCount>(`/api/v1/inventory/counts/${id}`)
    return response.data
  },

  async createInventoryCount(data: InventoryCountCreate) {
    const response = await apiClient.post<InventoryCount>('/api/v1/inventory/counts', data)
    return response.data
  },

  async updateInventoryCount(id: string, data: InventoryCountUpdate) {
    const response = await apiClient.put<InventoryCount>(`/api/v1/inventory/counts/${id}`, data)
    return response.data
  },

  async deleteInventoryCount(id: string) {
    await apiClient.delete(`/api/v1/inventory/counts/${id}`)
  }
}