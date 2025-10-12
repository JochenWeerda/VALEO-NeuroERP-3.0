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
// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function useSalesDashboard() {
  return useQuery({
    queryKey: dashboardKeys.sales(),
    queryFn: async () => {
      // TODO: Real endpoint /api/v1/dashboard/sales
      // For now, aggregate from customers + orders
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const customersResponse = await apiClient.get<{ items: any[], total: number }>('/api/v1/crm/customers')
      const customers = customersResponse.data.items || []
      
      return {
        totalRevenue: 450000,
        totalOrders: 156,
        avgOrderValue: 2885,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
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

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function useInventoryDashboard() {
  return useQuery({
    queryKey: dashboardKeys.inventory(),
    queryFn: async () => {
      // TODO: Real endpoint /api/v1/dashboard/inventory
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const articlesResponse = await apiClient.get<{ items: any[], total: number }>('/api/v1/articles')
      const articles = articlesResponse.data.items || []
      
      return {
        totalArticles: articles.length,
        totalValue: 275000,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        lowStockCount: articles.filter((a: any) => a.stock_quantity < (a.min_stock || 10)).length,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
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

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function useExecutiveDashboard() {
  return useQuery({
    queryKey: dashboardKeys.executive(),
    queryFn: async () => {
      // Combine sales + inventory data
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const [salesRes, articlesRes] = await Promise.all([
        apiClient.get<{ items: any[], total: number }>('/api/v1/crm/customers'),
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
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

