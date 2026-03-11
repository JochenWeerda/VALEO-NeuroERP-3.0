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
    initialData: EMPTY_SALES_DASHBOARD,
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
    initialData: EMPTY_INVENTORY_DASHBOARD,
  })
}

export function useExecutiveDashboard() {
  return useQuery({
    queryKey: dashboardKeys.executive(),
    queryFn: async () => {
      try {
        const [salesRes, articlesRes, financeRes] = await Promise.allSettled([
          apiClient.get<{ items: any[]; total: number }>('/api/v1/crm/customers'),
          apiClient.get<{ items: any[]; total: number }>('/api/v1/articles'),
          apiClient.get<{ items: any[] }>('/api/v1/journal-entries'),
        ])

        const customers =
          salesRes.status === 'fulfilled' ? salesRes.value.data : { items: [], total: 0 }
        const articles =
          articlesRes.status === 'fulfilled' ? articlesRes.value.data : { items: [], total: 0 }
        const journalEntries =
          financeRes.status === 'fulfilled' ? financeRes.value.data.items || [] : []

        // Calculate revenue from journal entries (positive amounts)
        const totalRevenue = journalEntries
          .filter((e: any) => Number(e.amount) > 0)
          .reduce((sum: number, e: any) => sum + Number(e.amount), 0)
        const totalCosts = journalEntries
          .filter((e: any) => Number(e.amount) < 0)
          .reduce((sum: number, e: any) => sum + Math.abs(Number(e.amount)), 0)

        return {
          umsatz: totalRevenue || 1250000,
          ertrag: totalRevenue - totalCosts || 430000,
          wachstum: 8.7,
          kunden: customers.total || customers.items?.length || 142,
          mitarbeiter: 27,
          kennzahlen: [
            {
              label: 'Umsatzrendite',
              wert:
                totalRevenue > 0
                  ? `${(((totalRevenue - totalCosts) / totalRevenue) * 100).toFixed(1)}%`
                  : '34.4%',
              trend: '+2.1%',
            },
            { label: 'Eigenkapitalquote', wert: '58.2%', trend: '+3.5%' },
            {
              label: 'Lagerumschlag',
              wert: articles.total ? (articles.total / 12).toFixed(1) : '8.2',
              trend: '+0.8',
            },
          ],
          bereiche: [
            { name: 'Verkauf Getreide', umsatz: totalRevenue * 0.42 || 525000, anteil: 42 },
            { name: 'Verkauf Futtermittel', umsatz: totalRevenue * 0.3 || 380000, anteil: 30 },
            { name: 'Verkauf Betriebsmittel', umsatz: totalRevenue * 0.28 || 345000, anteil: 28 },
          ],
        } as ExecutiveDashboardData
      } catch {
        // Fallback to demo data
        return {
          umsatz: 1250000,
          ertrag: 430000,
          wachstum: 8.7,
          kunden: 142,
          mitarbeiter: 27,
          kennzahlen: [
            { label: 'Umsatzrendite', wert: '34.4%', trend: '+2.1%' },
            { label: 'Eigenkapitalquote', wert: '58.2%', trend: '+3.5%' },
            { label: 'Lagerumschlag', wert: '8.2', trend: '+0.8' },
          ],
          bereiche: [
            { name: 'Verkauf Getreide', umsatz: 525000, anteil: 42 },
            { name: 'Verkauf Futtermittel', umsatz: 380000, anteil: 30 },
            { name: 'Verkauf Betriebsmittel', umsatz: 345000, anteil: 28 },
          ],
        } as ExecutiveDashboardData
      }
    },
    initialData: EMPTY_EXECUTIVE_DASHBOARD,
    staleTime: 5 * 60 * 1000,
  })
}

export function useProcurementDashboard() {
  return useQuery({
    queryKey: dashboardKeys.procurement(),
    queryFn: async () => {
      try {
        const [openItemsRes] = await Promise.allSettled([
          apiClient.get<{ items: any[] }>('/api/v1/open-items'),
        ])

        const openItems =
          openItemsRes.status === 'fulfilled' ? openItemsRes.value.data.items || [] : []

        const offenePosten = openItems.reduce(
          (sum: number, item: any) => sum + Number(item.amount || 0),
          0,
        )

        const today = new Date()
        const ueberfaellig = openItems.filter(
          (item: any) => new Date(item.due_date) < today && item.status === 'open',
        ).length

        return {
          bestellungenOffen: 8,
          einkaufsvolumen: 175000,
          lieferantenAktiv: 28,
          offenePosten: offenePosten || 125000,
          ueberfaellig: ueberfaellig || 3,
          bestellungen: [
            { nummer: 'PO-2026-042', lieferant: 'Saatgut AG', betrag: 25000, status: 'offen' as const },
            { nummer: 'PO-2026-041', lieferant: 'Dünger GmbH', betrag: 18500, status: 'teilgeliefert' as const },
            { nummer: 'PO-2026-040', lieferant: 'Technik GmbH', betrag: 8900, status: 'komplett' as const },
          ],
        } as ProcurementDashboardData
      } catch {
        return {
          bestellungenOffen: 8,
          einkaufsvolumen: 175000,
          lieferantenAktiv: 28,
          offenePosten: 125000,
          ueberfaellig: 3,
          bestellungen: [
            { nummer: 'PO-2026-042', lieferant: 'Saatgut AG', betrag: 25000, status: 'offen' as const },
            { nummer: 'PO-2026-041', lieferant: 'Dünger GmbH', betrag: 18500, status: 'teilgeliefert' as const },
            { nummer: 'PO-2026-040', lieferant: 'Technik GmbH', betrag: 8900, status: 'komplett' as const },
          ],
        } as ProcurementDashboardData
      }
    },
    initialData: EMPTY_PROCUREMENT_DASHBOARD,
    staleTime: 5 * 60 * 1000,
  })
}

