/**
 * Stock Movement Service
 * API service for Stock Movement management
 */

import { apiClient } from '../api-client'

// Types
export interface StockMovement {
  id: string
  tenant_id: string
  article_id: string
  warehouse_id: string
  movement_type: 'in' | 'out' | 'transfer' | 'adjustment'
  quantity: number
  unit_cost?: number
  unit?: string
  movement_number?: string
  movement_date?: string
  movement_time?: string
  reference_number?: string
  notes?: string
  warehouse_location?: string
  charge?: string
  booking_user?: string
  auto_created?: boolean
  linked_order_id?: string
  previous_stock: number
  new_stock: number
  total_cost?: number
  created_at: string
}

export interface StockMovementCreate {
  article_id: string
  warehouse_id: string
  movement_type: 'in' | 'out' | 'transfer' | 'adjustment'
  quantity: number
  unit_cost?: number
  unit?: string
  movement_number?: string
  movement_date?: string
  movement_time?: string
  reference_number?: string
  notes?: string
  warehouse_location?: string
  charge?: string
  booking_user?: string
  auto_created?: boolean
  linked_order_id?: string
}

export interface StockMovementUpdate {
  movement_number?: string
  movement_date?: string
  movement_time?: string
  unit?: string
  reference_number?: string
  notes?: string
  warehouse_location?: string
  charge?: string
  booking_user?: string
  auto_created?: boolean
  linked_order_id?: string
}

export interface StockMovementsResponse {
  items: StockMovement[]
  total: number
  page: number
  size: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

// API Functions
export const stockMovementService = {
  async getStockMovements(params?: {
    article_id?: string
    warehouse_id?: string
    movement_type?: string
    search?: string
    limit?: number
    skip?: number
    tenant_id?: string
  }) {
    const response = await apiClient.get<StockMovementsResponse>('/api/v1/inventory/stock-movements', { params })
    return response.data
  },

  async getStockMovement(id: string) {
    const response = await apiClient.get<StockMovement>(`/api/v1/inventory/stock-movements/${id}`)
    return response.data
  },

  async createStockMovement(data: StockMovementCreate) {
    const response = await apiClient.post<StockMovement>('/api/v1/inventory/stock-movements', data)
    return response.data
  },

  async updateStockMovement(id: string, data: StockMovementUpdate) {
    const response = await apiClient.put<StockMovement>(`/api/v1/inventory/stock-movements/${id}`, data)
    return response.data
  },

  async deleteStockMovement(id: string) {
    await apiClient.delete(`/api/v1/inventory/stock-movements/${id}`)
  },
}
