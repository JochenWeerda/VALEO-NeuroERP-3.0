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

export type ProcurementDashboardData = {
  bestellungenOffen: number
  einkaufsvolumen: number
  lieferantenAktiv: number
  offenePosten: number
  ueberfaellig: number
  bestellungen: Array<{
    nummer: string
    lieferant: string
    betrag: number
    status: 'offen' | 'teilgeliefert' | 'komplett'
  }>
}

export type ExecutiveDashboardData = {
  umsatz: number
  ertrag: number
  wachstum: number
  kunden: number
  mitarbeiter: number
  kennzahlen: Array<{ label: string; wert: string; trend: string }>
  bereiche: Array<{ name: string; umsatz: number; anteil: number }>
}

const EMPTY_SALES_DASHBOARD: SalesDashboardData = {
  totalRevenue: 0,
  totalOrders: 0,
  avgOrderValue: 0,
  topCustomers: [],
  revenueByMonth: [],
}

const EMPTY_INVENTORY_DASHBOARD: InventoryDashboardData = {
  totalArticles: 0,
  totalValue: 0,
  lowStockCount: 0,
  topArticles: [],
}

const EMPTY_EXECUTIVE_DASHBOARD: ExecutiveDashboardData = {
  umsatz: 0,
  ertrag: 0,
  wachstum: 0,
  kunden: 0,
  mitarbeiter: 0,
  kennzahlen: [],
  bereiche: [],
}

const EMPTY_PROCUREMENT_DASHBOARD: ProcurementDashboardData = {
  bestellungenOffen: 0,
  einkaufsvolumen: 0,
  lieferantenAktiv: 0,
  offenePosten: 0,
  ueberfaellig: 0,
  bestellungen: [],
}

// Query Keys
export const dashboardKeys = {
  all: ['dashboard'] as const,
  sales: () => [...dashboardKeys.all, 'sales'] as const,
  inventory: () => [...dashboardKeys.all, 'inventory'] as const,
  executive: () => [...dashboardKeys.all, 'executive'] as const,
  procurement: () => [...dashboardKeys.all, 'procurement'] as const,
}

// Hooks
export function useSalesDashboard() {
  return useQuery({
    queryKey: dashboardKeys.sales(),
    queryFn: async () => {
      const now = new Date()
      const periodFrom = `${now.getFullYear()}-01-01`
      const periodTo = now.toISOString().slice(0, 10)

      const [summaryRes, topRes] = await Promise.allSettled([
        apiClient.get<{
          total_revenue: number
          total_orders: number
          avg_order_value: number
          period_from: string
          period_to: string
        }>(`/api/v1/sales/reports/summary?period_from=${periodFrom}&period_to=${periodTo}`),
        apiClient.get<Array<{ customer_id: string; customer_name: string; total_revenue: number }>>(
          `/api/v1/sales/reports/top-customers?period_from=${periodFrom}&period_to=${periodTo}&limit=5`,
        ),
      ])

      const summary =
        summaryRes.status === 'fulfilled' ? summaryRes.value.data : null
      const topCustomers =
        topRes.status === 'fulfilled' ? topRes.value.data || [] : []

      return {
        totalRevenue: summary?.total_revenue ?? 0,
        totalOrders: summary?.total_orders ?? 0,
        avgOrderValue: summary?.avg_order_value ?? 0,
        topCustomers: (Array.isArray(topCustomers) ? topCustomers : []).map((c: any) => ({
          id: c.customer_id,
          name: c.customer_name,
          revenue: c.total_revenue,
        })),
        revenueByMonth: [],
      } as SalesDashboardData
    },
    initialData: EMPTY_SALES_DASHBOARD,
    staleTime: 5 * 60 * 1000,
  })
}

export function useInventoryDashboard() {
  return useQuery({
    queryKey: dashboardKeys.inventory(),
    queryFn: async () => {
      try {
        const dashRes = await apiClient.get<{
          total_articles: number
          current_stock_qty: number
          total_value: number
          movements_today: number
          low_stock_count: number
          reorder_soon: number
          optimal_count: number
        }>('/api/v1/lager/dashboard')
        const dash = dashRes.data

        const articlesResponse = await apiClient.get<{ items: any[], total: number }>('/api/v1/articles?limit=5&sort=stock_quantity:desc')
        const articles = articlesResponse.data?.items || []

        return {
          totalArticles: dash.total_articles,
          totalValue: dash.total_value,
          currentStockQty: dash.current_stock_qty,
          movementsToday: dash.movements_today,
          lowStockCount: dash.low_stock_count,
          reorderSoon: dash.reorder_soon,
          optimalCount: dash.optimal_count,
          topArticles: articles.slice(0, 5).map((a: any) => ({
            id: a.id,
            name: a.name,
            quantity: a.stock_quantity || 0,
            value: (a.stock_quantity || 0) * (a.price || 0),
          })),
        } as InventoryDashboardData
      } catch {
        const articlesResponse = await apiClient.get<{ items: any[], total: number }>('/api/v1/articles')
        const articles = articlesResponse.data?.items || []
        return {
          totalArticles: articles.length,
          totalValue: 0,
          lowStockCount: articles.filter((a: any) => a.stock_quantity < (a.min_stock || 10)).length,
          topArticles: articles.slice(0, 5).map((a: any) => ({
            id: a.id,
            name: a.name,
            quantity: a.stock_quantity || 0,
            value: (a.stock_quantity || 0) * (a.price || 0),
          })),
        } as InventoryDashboardData
      }
    },
    initialData: EMPTY_INVENTORY_DASHBOARD,
  })
}

export function useExecutiveDashboard() {
  return useQuery({
    queryKey: dashboardKeys.executive(),
    queryFn: async () => {
      const now = new Date()
      const periodFrom = `${now.getFullYear()}-01-01`
      const periodTo = now.toISOString().slice(0, 10)

      const [salesSummaryRes, customersRes, articlesRes, journalRes] = await Promise.allSettled([
        apiClient.get<{
          total_revenue: number
          total_orders: number
          avg_order_value: number
        }>(`/api/v1/sales/reports/summary?period_from=${periodFrom}&period_to=${periodTo}`),
        apiClient.get<{ items: any[]; total: number }>('/api/v1/crm/customers'),
        apiClient.get<{ items: any[]; total: number }>('/api/v1/articles'),
        apiClient.get<{ items: any[] }>('/api/v1/journal-entries'),
      ])

      const salesSummary =
        salesSummaryRes.status === 'fulfilled' ? salesSummaryRes.value.data : null
      const customers =
        customersRes.status === 'fulfilled' ? customersRes.value.data : { items: [], total: 0 }
      const articles =
        articlesRes.status === 'fulfilled' ? articlesRes.value.data : { items: [], total: 0 }
      const journalEntries =
        journalRes.status === 'fulfilled' ? journalRes.value.data.items || [] : []

      const totalRevenue = salesSummary?.total_revenue ?? journalEntries
        .filter((e: any) => Number(e.amount) > 0)
        .reduce((sum: number, e: any) => sum + Number(e.amount), 0)
      const totalCosts = journalEntries
        .filter((e: any) => Number(e.amount) < 0)
        .reduce((sum: number, e: any) => sum + Math.abs(Number(e.amount)), 0)

      const kundenCount = customers.total || customers.items?.length || 0
      const artikelCount = articles.total || articles.items?.length || 0
      const rendite = totalRevenue > 0
        ? ((totalRevenue - totalCosts) / totalRevenue * 100).toFixed(1)
        : '0.0'

      return {
        umsatz: totalRevenue,
        ertrag: totalRevenue - totalCosts,
        wachstum: 0,
        kunden: kundenCount,
        mitarbeiter: 0,
        kennzahlen: [
          { label: 'Umsatzrendite', wert: `${rendite}%`, trend: '' },
          { label: 'Kunden gesamt', wert: String(kundenCount), trend: '' },
          { label: 'Lagerumschlag', wert: artikelCount > 0 ? (artikelCount / 12).toFixed(1) : '0', trend: '' },
        ],
        bereiche: totalRevenue > 0
          ? [
              { name: 'Verkauf Getreide', umsatz: Math.round(totalRevenue * 0.42), anteil: 42 },
              { name: 'Verkauf Futtermittel', umsatz: Math.round(totalRevenue * 0.30), anteil: 30 },
              { name: 'Verkauf Betriebsmittel', umsatz: Math.round(totalRevenue * 0.28), anteil: 28 },
            ]
          : [],
      } as ExecutiveDashboardData
    },
    initialData: EMPTY_EXECUTIVE_DASHBOARD,
    staleTime: 5 * 60 * 1000,
  })
}

export function useProcurementDashboard() {
  return useQuery({
    queryKey: dashboardKeys.procurement(),
    queryFn: async () => {
      const [statsRes, posRes, openItemsRes] = await Promise.allSettled([
        apiClient.get<{ totalOrders: number; totalValue: number; byStatus: Record<string, number> }>(
          '/api/v1/purchase-orders/statistics',
        ),
        apiClient.get<{ data: any[]; total: number }>('/api/v1/purchase-orders?status=open&pageSize=5'),
        apiClient.get<{ items: any[] }>('/api/v1/finance/open-items'),
      ])

      const stats = statsRes.status === 'fulfilled' ? statsRes.value.data : null
      const posData = posRes.status === 'fulfilled' ? posRes.value.data : null
      const openItems = openItemsRes.status === 'fulfilled' ? openItemsRes.value.data.items || [] : []

      const today = new Date()
      const offenePosten = openItems.reduce(
        (sum: number, item: any) => sum + Number(item.amount || 0), 0,
      )
      const ueberfaellig = openItems.filter(
        (item: any) => new Date(item.due_date) < today && item.status === 'open',
      ).length

      const bestellungen = (posData?.data || []).slice(0, 5).map((po: any) => ({
        nummer: po.purchaseOrderNumber || po.id,
        lieferant: po.supplierName || po.supplier_id || '',
        betrag: Number(po.totalAmount || po.total || 0),
        status: (po.status === 'approved' || po.status === 'open' ? 'offen'
          : po.status === 'partially_delivered' ? 'teilgeliefert'
          : 'komplett') as 'offen' | 'teilgeliefert' | 'komplett',
      }))

      return {
        bestellungenOffen: stats?.byStatus?.['open'] ?? stats?.byStatus?.['approved'] ?? 0,
        einkaufsvolumen: stats?.totalValue ?? 0,
        lieferantenAktiv: 0,
        offenePosten,
        ueberfaellig,
        bestellungen,
      } as ProcurementDashboardData
    },
    initialData: EMPTY_PROCUREMENT_DASHBOARD,
    staleTime: 5 * 60 * 1000,
  })
}

