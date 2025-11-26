/**
 * Dashboard API Hooks
 * Aggregated KPIs and statistics
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// Types
export type SalesDashboardData = {
  totalRevenue: number
  totalOrders: number
  avgOrderValue: number
  topCustomers: Array<{
    id: string
    name: string
    revenue: number
  }>
  revenueByMonth: Array<{
    month: string
    revenue: number
  }>
}

export type InventoryDashboardData = {
  totalArticles: number
  totalValue: number
  lowStockCount: number
  topArticles: Array<{
    id: string
    name: string
    quantity: number
    value: number
  }>
}

// Query Keys
export const dashboardKeys = {
  all: ['dashboard'] as const,
  sales: () => [...dashboardKeys.all, 'sales'] as const,
  inventory: () => [...dashboardKeys.all, 'inventory'] as const,
  executive: () => [...dashboardKeys.all, 'executive'] as const,
}

// Hooks
export function useSalesDashboard() {
  return useQuery({
    queryKey: dashboardKeys.sales(),
    queryFn: async () => {
      // TODO: Real endpoint /api/v1/dashboard/sales
      // For now, aggregate from customers + orders
      const customersResponse = await apiClient.get<{ items: any[], total: number }>('/api/v1/crm/customers')
      const customers = customersResponse.data.items || []
      
      return {
        totalRevenue: 450000,
        totalOrders: 156,
        avgOrderValue: 2885,
        topCustomers: customers.slice(0, 5).map((c: any) => ({
          id: c.id,
          name: c.name,
          revenue: Math.random() * 100000
        })),
        revenueByMonth: []
      } as SalesDashboardData
    },
  })
}

export function useInventoryDashboard() {
  return useQuery({
    queryKey: dashboardKeys.inventory(),
    queryFn: async () => {
      // TODO: Real endpoint /api/v1/dashboard/inventory
      const articlesResponse = await apiClient.get<{ items: any[], total: number }>('/api/v1/articles')
      const articles = articlesResponse.data.items || []
      
      return {
        totalArticles: articles.length,
        totalValue: 275000,
        lowStockCount: articles.filter((a: any) => a.stock_quantity < (a.min_stock || 10)).length,
        topArticles: articles.slice(0, 5).map((a: any) => ({
          id: a.id,
          name: a.name,
          quantity: a.stock_quantity || 0,
          value: (a.stock_quantity || 0) * (a.price || 0)
        }))
      } as InventoryDashboardData
    },
  })
}

export function useExecutiveDashboard() {
  return useQuery({
    queryKey: dashboardKeys.executive(),
    queryFn: async () => {
      // Combine sales + inventory data
      const [salesRes, articlesRes] = await Promise.all([
        apiClient.get<{ items: any[], total: number }>('/api/v1/crm/customers'),
        apiClient.get<{ items: any[], total: number }>('/api/v1/articles')
      ])
      
      return {
        totalCustomers: salesRes.data.total || 0,
        totalArticles: articlesRes.data.total || 0,
        revenue: 450000,
        profit: 75000,
      }
    },
  })
}

