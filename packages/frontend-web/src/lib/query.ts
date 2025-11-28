import { type DefaultError, QueryClient } from "@tanstack/react-query"

const ONE_SECOND_MS = 1_000
const SECONDS_PER_MINUTE = 60
const FIVE_MINUTES = 5
const THIRTY_MINUTES = 30
const DEFAULT_STALE_TIME_MS = FIVE_MINUTES * SECONDS_PER_MINUTE * ONE_SECOND_MS
const DEFAULT_GC_TIME_MS = THIRTY_MINUTES * SECONDS_PER_MINUTE * ONE_SECOND_MS
const MAX_RETRY_COUNT = 3
const HTTP_STATUS_BAD_REQUEST = 400
const HTTP_STATUS_INTERNAL_SERVER_ERROR = 500

type AxiosErrorLike = import("axios").AxiosError

const isAxiosError = (error: unknown): error is AxiosErrorLike => {
  if (typeof error !== "object" || error === null) {
    return false
  }
  return (error as Partial<AxiosErrorLike>).isAxiosError === true
}

const shouldRetryQuery = (failureCount: number, error: DefaultError): boolean => {
  if (isAxiosError(error)) {
    const status = error.response?.status ?? 0
    if (status >= HTTP_STATUS_BAD_REQUEST && status < HTTP_STATUS_INTERNAL_SERVER_ERROR) {
      return false
    }
  }

  return failureCount < MAX_RETRY_COUNT
}

export const queryKeys = {
  analytics: {
    kpis: ["analytics", "kpis"] as const,
    cubes: (cubeName: string) => ["analytics", "cubes", cubeName] as const,
  },
  contracts: {
    all: ["contracts"] as const,
    lists: () => [...queryKeys.contracts.all, "list"] as const,
    list: (filters: Record<string, unknown>) => [...queryKeys.contracts.lists(), filters] as const,
    details: () => [...queryKeys.contracts.all, "detail"] as const,
    detail: (id: string) => [...queryKeys.contracts.details(), id] as const,
  },
  inventory: {
    articles: {
      all: ["inventory", "articles"] as const,
      list: () => [...queryKeys.inventory.articles.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.inventory.articles.list(), filters] as const,
      detail: (id: string) => [...queryKeys.inventory.articles.all, "detail", id] as const,
    },
    warehouses: {
      all: ["inventory", "warehouses"] as const,
      list: () => [...queryKeys.inventory.warehouses.all, "list"] as const,
      detail: (id: string) => [...queryKeys.inventory.warehouses.all, "detail", id] as const,
    },
    stockMovements: {
      all: ["inventory", "stock-movements"] as const,
      list: () => [...queryKeys.inventory.stockMovements.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.inventory.stockMovements.list(), filters] as const,
      detail: (id: string) => [...queryKeys.inventory.stockMovements.all, "detail", id] as const,
    },
    physicalInventory: {
      all: ["inventory", "physical-inventory"] as const,
      list: () => [...queryKeys.inventory.physicalInventory.all, "list"] as const,
      detail: (id: string) => [...queryKeys.inventory.physicalInventory.all, "detail", id] as const,
    },
  },
  weighing: {
    all: ["weighing"] as const,
    tickets: () => [...queryKeys.weighing.all, "tickets"] as const,
    ticket: (id: string) => [...queryKeys.weighing.tickets(), id] as const,
    ticketList: (filters: Record<string, unknown>) => [...queryKeys.weighing.tickets(), "list", filters] as const,
  },
  sales: {
    orders: {
      all: ["sales", "orders"] as const,
      list: () => [...queryKeys.sales.orders.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.sales.orders.list(), filters] as const,
      detail: (id: string) => [...queryKeys.sales.orders.all, "detail", id] as const,
    },
    invoices: {
      all: ["sales", "invoices"] as const,
      list: () => [...queryKeys.sales.invoices.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.sales.invoices.list(), filters] as const,
      detail: (id: string) => [...queryKeys.sales.invoices.all, "detail", id] as const,
    },
    deliveries: {
      all: ["sales", "deliveries"] as const,
      list: () => [...queryKeys.sales.deliveries.all, "list"] as const,
      detail: (id: string) => [...queryKeys.sales.deliveries.all, "detail", id] as const,
    },
    quotations: {
      all: ["sales", "quotations"] as const,
      list: () => [...queryKeys.sales.quotations.all, "list"] as const,
      detail: (id: string) => [...queryKeys.sales.quotations.all, "detail", id] as const,
    },
  },
  document: {
    all: ["document"] as const,
    file: (id: string) => [...queryKeys.document.all, "file", id] as const,
  },
  agrar: {
    seeds: {
      all: ["agrar", "seeds"] as const,
      list: () => [...queryKeys.agrar.seeds.all, "list"] as const,
      detail: (id: string) => [...queryKeys.agrar.seeds.all, "detail", id] as const,
    },
    fertilizers: {
      all: ["agrar", "fertilizers"] as const,
      list: () => [...queryKeys.agrar.fertilizers.all, "list"] as const,
      detail: (id: string) => [...queryKeys.agrar.fertilizers.all, "detail", id] as const,
    },
  },
  crm: {
    contacts: {
      all: ["crm", "contacts"] as const,
      list: () => [...queryKeys.crm.contacts.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.crm.contacts.list(), filters] as const,
      detail: (id: string) => [...queryKeys.crm.contacts.all, "detail", id] as const,
    },
    leads: {
      all: ["crm", "leads"] as const,
      list: () => [...queryKeys.crm.leads.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.crm.leads.list(), filters] as const,
      detail: (id: string) => [...queryKeys.crm.leads.all, "detail", id] as const,
    },
    activities: {
      all: ["crm", "activities"] as const,
      list: () => [...queryKeys.crm.activities.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.crm.activities.list(), filters] as const,
      detail: (id: string) => [...queryKeys.crm.activities.all, "detail", id] as const,
    },
    farmProfiles: {
      all: ["crm", "farm-profiles"] as const,
      list: () => [...queryKeys.crm.farmProfiles.all, "list"] as const,
      detail: (id: string) => [...queryKeys.crm.farmProfiles.all, "detail", id] as const,
    },
  },
  finance: {
    chartOfAccounts: {
      all: ["finance", "chart-of-accounts"] as const,
      list: () => [...queryKeys.finance.chartOfAccounts.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.finance.chartOfAccounts.list(), filters] as const,
      detail: (id: string) => [...queryKeys.finance.chartOfAccounts.all, "detail", id] as const,
    },
    journalEntries: {
      all: ["finance", "journal-entries"] as const,
      list: () => [...queryKeys.finance.journalEntries.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.finance.journalEntries.list(), filters] as const,
      detail: (id: string) => [...queryKeys.finance.journalEntries.all, "detail", id] as const,
    },
    bankAccounts: {
      all: ["finance", "bank-accounts"] as const,
      list: () => [...queryKeys.finance.bankAccounts.all, "list"] as const,
      detail: (id: string) => [...queryKeys.finance.bankAccounts.all, "detail", id] as const,
    },
    customers: {
      all: ["finance", "customers"] as const,
      list: () => [...queryKeys.finance.customers.all, "list"] as const,
      detail: (id: string) => [...queryKeys.finance.customers.all, "detail", id] as const,
    },
    suppliers: {
      all: ["finance", "suppliers"] as const,
      list: () => [...queryKeys.finance.suppliers.all, "list"] as const,
      detail: (id: string) => [...queryKeys.finance.suppliers.all, "detail", id] as const,
    },
  },
  purchasing: {
    purchaseOrders: {
      all: ["purchasing", "purchase-orders"] as const,
      list: () => [...queryKeys.purchasing.purchaseOrders.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.purchasing.purchaseOrders.list(), filters] as const,
      detail: (id: string) => [...queryKeys.purchasing.purchaseOrders.all, "detail", id] as const,
    },
    purchaseRequisitions: {
      all: ["purchasing", "purchase-requisitions"] as const,
      list: () => [...queryKeys.purchasing.purchaseRequisitions.all, "list"] as const,
      detail: (id: string) => [...queryKeys.purchasing.purchaseRequisitions.all, "detail", id] as const,
    },
    suppliers: {
      all: ["purchasing", "suppliers"] as const,
      list: () => [...queryKeys.purchasing.suppliers.all, "list"] as const,
      detail: (id: string) => [...queryKeys.purchasing.suppliers.all, "detail", id] as const,
    },
    goodsReceipts: {
      all: ["purchasing", "goods-receipts"] as const,
      list: () => [...queryKeys.purchasing.goodsReceipts.all, "list"] as const,
      detail: (id: string) => [...queryKeys.purchasing.goodsReceipts.all, "detail", id] as const,
    },
  },
  production: {
    productionOrders: {
      all: ["production", "production-orders"] as const,
      list: () => [...queryKeys.production.productionOrders.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.production.productionOrders.list(), filters] as const,
      detail: (id: string) => [...queryKeys.production.productionOrders.all, "detail", id] as const,
    },
    billOfMaterials: {
      all: ["production", "bill-of-materials"] as const,
      list: () => [...queryKeys.production.billOfMaterials.all, "list"] as const,
      detail: (id: string) => [...queryKeys.production.billOfMaterials.all, "detail", id] as const,
    },
    routings: {
      all: ["production", "routings"] as const,
      list: () => [...queryKeys.production.routings.all, "list"] as const,
      detail: (id: string) => [...queryKeys.production.routings.all, "detail", id] as const,
    },
    workCenters: {
      all: ["production", "work-centers"] as const,
      list: () => [...queryKeys.production.workCenters.all, "list"] as const,
      detail: (id: string) => [...queryKeys.production.workCenters.all, "detail", id] as const,
    },
  },
  hr: {
    employees: {
      all: ["hr", "employees"] as const,
      list: () => [...queryKeys.hr.employees.all, "list"] as const,
      listFiltered: (filters: Record<string, unknown>) => [...queryKeys.hr.employees.list(), filters] as const,
      detail: (id: string) => [...queryKeys.hr.employees.all, "detail", id] as const,
    },
    timeTracking: {
      all: ["hr", "time-tracking"] as const,
      list: () => [...queryKeys.hr.timeTracking.all, "list"] as const,
      detail: (id: string) => [...queryKeys.hr.timeTracking.all, "detail", id] as const,
    },
    payroll: {
      all: ["hr", "payroll"] as const,
      list: () => [...queryKeys.hr.payroll.all, "list"] as const,
      detail: (id: string) => [...queryKeys.hr.payroll.all, "detail", id] as const,
    },
    absences: {
      all: ["hr", "absences"] as const,
      list: () => [...queryKeys.hr.absences.all, "list"] as const,
      detail: (id: string) => [...queryKeys.hr.absences.all, "detail", id] as const,
    },
  },
  quality: {
    inspections: {
      all: ["quality", "inspections"] as const,
      list: () => [...queryKeys.quality.inspections.all, "list"] as const,
      detail: (id: string) => [...queryKeys.quality.inspections.all, "detail", id] as const,
    },
    certificates: {
      all: ["quality", "certificates"] as const,
      list: () => [...queryKeys.quality.certificates.all, "list"] as const,
      detail: (id: string) => [...queryKeys.quality.certificates.all, "detail", id] as const,
    },
    nonconformities: {
      all: ["quality", "nonconformities"] as const,
      list: () => [...queryKeys.quality.nonconformities.all, "list"] as const,
      detail: (id: string) => [...queryKeys.quality.nonconformities.all, "detail", id] as const,
    },
  },
  reports: {
    financial: {
      all: ["reports", "financial"] as const,
      balanceSheet: () => [...queryKeys.reports.financial.all, "balance-sheet"] as const,
      profitLoss: () => [...queryKeys.reports.financial.all, "profit-loss"] as const,
      cashFlow: () => [...queryKeys.reports.financial.all, "cash-flow"] as const,
    },
    sales: {
      all: ["reports", "sales"] as const,
      revenue: () => [...queryKeys.reports.sales.all, "revenue"] as const,
      customerAnalysis: () => [...queryKeys.reports.sales.all, "customer-analysis"] as const,
    },
    inventory: {
      all: ["reports", "inventory"] as const,
      stockLevels: () => [...queryKeys.reports.inventory.all, "stock-levels"] as const,
      turnover: () => [...queryKeys.reports.inventory.all, "turnover"] as const,
    },
    production: {
      all: ["reports", "production"] as const,
      efficiency: () => [...queryKeys.reports.production.all, "efficiency"] as const,
      costs: () => [...queryKeys.reports.production.all, "costs"] as const,
    },
  },
} as const

export const mutationKeys = {
  contracts: {
    fix: ["contracts", "fix"] as const,
  },
  weighing: {
    approve: ["weighing", "approve"] as const,
  },
  agrar: {
    seedOrders: {
      create: ["agrar", "seed-orders", "create"] as const,
    },
  },
  crm: {
    contacts: {
      create: ["crm", "contacts", "create"] as const,
      update: ["crm", "contacts", "update"] as const,
      delete: ["crm", "contacts", "delete"] as const,
    },
    leads: {
      create: ["crm", "leads", "create"] as const,
      update: ["crm", "leads", "update"] as const,
      delete: ["crm", "leads", "delete"] as const,
    },
    activities: {
      create: ["crm", "activities", "create"] as const,
      update: ["crm", "activities", "update"] as const,
      delete: ["crm", "activities", "delete"] as const,
    },
    farmProfiles: {
      create: ["crm", "farm-profiles", "create"] as const,
      update: ["crm", "farm-profiles", "update"] as const,
      delete: ["crm", "farm-profiles", "delete"] as const,
    },
  },
} as const

/**
 * Performance-optimierte Query Client Konfiguration
 * 
 * - staleTime: 5 Minuten (Daten gelten als frisch)
 * - gcTime: 30 Minuten (Cache wird nach 30 Min gelöscht)
 * - refetchOnWindowFocus: false (keine Auto-Refetch bei Tab-Wechsel)
 * - refetchOnMount: 'always' nur wenn stale (Standard)
 * - refetchInterval: false (kein automatisches Polling)
 */
export const createQueryClient = (): QueryClient => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: DEFAULT_STALE_TIME_MS,
        gcTime: DEFAULT_GC_TIME_MS,
        retry: shouldRetryQuery,
        refetchOnWindowFocus: false,
        refetchOnReconnect: true,
        refetchOnMount: true,
        // Strukturelles Sharing für bessere Performance bei großen Datenmengen
        structuralSharing: true,
        // Netzwerk-Modus: Online-First mit Fallback auf Cache
        networkMode: 'offlineFirst',
      },
      mutations: {
        retry: false,
        // Netzwerk-Modus für Mutations
        networkMode: 'online',
      },
    },
  })
}

/**
 * Query-Optionen für häufig genutzte Daten (z.B. Stammdaten)
 * Längere Cache-Zeit für selten geänderte Daten
 */
export const LONG_CACHE_OPTIONS = {
  staleTime: 15 * SECONDS_PER_MINUTE * ONE_SECOND_MS, // 15 Minuten
  gcTime: 60 * SECONDS_PER_MINUTE * ONE_SECOND_MS, // 1 Stunde
} as const

/**
 * Query-Optionen für Echtzeit-Daten (z.B. Dashboard)
 * Kürzere Cache-Zeit für häufig geänderte Daten
 */
export const REALTIME_CACHE_OPTIONS = {
  staleTime: 30 * ONE_SECOND_MS, // 30 Sekunden
  gcTime: FIVE_MINUTES * SECONDS_PER_MINUTE * ONE_SECOND_MS, // 5 Minuten
  refetchInterval: 60 * ONE_SECOND_MS, // Alle 60 Sekunden aktualisieren
} as const
