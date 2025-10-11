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
    all: ["inventory"] as const,
    lots: () => [...queryKeys.inventory.all, "lots"] as const,
    lot: (id: string) => [...queryKeys.inventory.lots(), id] as const,
    movements: () => [...queryKeys.inventory.all, "movements"] as const,
    movement: (filters: Record<string, unknown>) => [...queryKeys.inventory.movements(), filters] as const,
  },
  weighing: {
    all: ["weighing"] as const,
    tickets: () => [...queryKeys.weighing.all, "tickets"] as const,
    ticket: (id: string) => [...queryKeys.weighing.tickets(), id] as const,
    ticketList: (filters: Record<string, unknown>) => [...queryKeys.weighing.tickets(), "list", filters] as const,
  },
  sales: {
    all: ["sales"] as const,
    orders: () => [...queryKeys.sales.all, "orders"] as const,
    order: (id: string) => [...queryKeys.sales.orders(), id] as const,
    orderList: (filters: Record<string, unknown>) => [...queryKeys.sales.orders(), "list", filters] as const,
    invoices: () => [...queryKeys.sales.all, "invoices"] as const,
    invoice: (id: string) => [...queryKeys.sales.invoices(), id] as const,
    invoiceList: (filters: Record<string, unknown>) => [...queryKeys.sales.invoices(), "list", filters] as const,
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
} as const

export const createQueryClient = (): QueryClient => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: DEFAULT_STALE_TIME_MS,
        gcTime: DEFAULT_GC_TIME_MS,
        retry: shouldRetryQuery,
        refetchOnWindowFocus: false,
        refetchOnReconnect: true,
      },
      mutations: {
        retry: false,
      },
    },
  })
}
