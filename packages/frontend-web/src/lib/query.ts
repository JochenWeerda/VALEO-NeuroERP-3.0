import { type DefaultError, type MutationOptions, QueryClient, type QueryOptions } from '@tanstack/react-query'
import { AxiosError } from 'axios'

import { toast } from '@/hooks/use-toast'

type QueryMeta = {
  suppressToast?: boolean
  errorTitle?: string
  errorMessage?: string
}

type MutationMeta = QueryMeta & {
  successMessage?: string
  successTitle?: string
}

const ONE_SECOND_MS = 1_000
const SECONDS_PER_MINUTE = 60
const FIVE_MINUTES = 5
const THIRTY_MINUTES = 30
const DEFAULT_STALE_TIME_MS = FIVE_MINUTES * SECONDS_PER_MINUTE * ONE_SECOND_MS
const DEFAULT_GC_TIME_MS = THIRTY_MINUTES * SECONDS_PER_MINUTE * ONE_SECOND_MS
const MAX_RETRY_COUNT = 3
const HTTP_STATUS_BAD_REQUEST = 400
const HTTP_STATUS_INTERNAL_SERVER_ERROR = 500

const isAxiosError = (error: unknown): error is AxiosError<{ message?: string }> => {
  return typeof error === 'object' && error !== null && 'isAxiosError' in (error as AxiosError)
}

const resolveErrorMessage = (error: unknown): string => {
  if (isAxiosError(error)) {
    const apiMessage = error.response?.data?.message
    if (typeof apiMessage === 'string' && apiMessage.length > 0) {
      return apiMessage
    }

    const statusText = error.response?.statusText
    if (typeof statusText === 'string' && statusText.length > 0) {
      return statusText
    }
  }

  if (error instanceof Error && error.message.length > 0) {
    return error.message
  }

  return 'Unbekannter Fehler'
}

const shouldSuppressToast = (meta?: unknown): meta is QueryMeta => {
  if (meta === null || meta === undefined) {
    return false
  }

  if (typeof meta !== 'object') {
    return false
  }

  const typedMeta = meta as QueryMeta
  return typedMeta.suppressToast === true
}

const withDefaultTitle = (title: string | undefined, fallback: string): string => {
  if (typeof title === 'string' && title.length > 0) {
    return title
  }

  return fallback
}

export const queryKeys = {
  analytics: {
    kpis: ['analytics', 'kpis'] as const,
    cubes: (cubeName: string) => ['analytics', 'cubes', cubeName] as const,
  },
  contracts: {
    all: ['contracts'] as const,
    lists: () => [...queryKeys.contracts.all, 'list'] as const,
    list: (filters: Record<string, unknown>) => [...queryKeys.contracts.lists(), filters] as const,
    details: () => [...queryKeys.contracts.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.contracts.details(), id] as const,
  },
  inventory: {
    all: ['inventory'] as const,
    lots: () => [...queryKeys.inventory.all, 'lots'] as const,
    lot: (id: string) => [...queryKeys.inventory.lots(), id] as const,
    movements: () => [...queryKeys.inventory.all, 'movements'] as const,
    movement: (filters: Record<string, unknown>) => [...queryKeys.inventory.movements(), filters] as const,
  },
  weighing: {
    all: ['weighing'] as const,
    tickets: () => [...queryKeys.weighing.all, 'tickets'] as const,
    ticket: (id: string) => [...queryKeys.weighing.tickets(), id] as const,
    ticketList: (filters: Record<string, unknown>) => [...queryKeys.weighing.tickets(), 'list', filters] as const,
  },
  sales: {
    all: ['sales'] as const,
    orders: () => [...queryKeys.sales.all, 'orders'] as const,
    order: (id: string) => [...queryKeys.sales.orders(), id] as const,
    orderList: (filters: Record<string, unknown>) => [...queryKeys.sales.orders(), 'list', filters] as const,
    invoices: () => [...queryKeys.sales.all, 'invoices'] as const,
    invoice: (id: string) => [...queryKeys.sales.invoices(), id] as const,
    invoiceList: (filters: Record<string, unknown>) => [...queryKeys.sales.invoices(), 'list', filters] as const,
  },
  document: {
    all: ['document'] as const,
    file: (id: string) => [...queryKeys.document.all, 'file', id] as const,
  },
} as const

export const mutationKeys = {
  contracts: {
    fix: ['contracts', 'fix'] as const,
  },
  weighing: {
    approve: ['weighing', 'approve'] as const,
  },
} as const

const maybeToastQueryError = (error: unknown, meta?: QueryOptions<unknown, DefaultError>['meta']): void => {
  if (shouldSuppressToast(meta)) {
    return
  }

  const parsedMeta = (meta ?? undefined) as QueryMeta | undefined
  const errorTitle = withDefaultTitle(parsedMeta?.errorTitle, 'Fehler beim Laden')
  const description = parsedMeta?.errorMessage ?? resolveErrorMessage(error)

  toast({
    variant: 'destructive',
    title: errorTitle,
    description,
  })
}

const maybeToastMutationError = (
  error: unknown,
  meta?: MutationOptions<unknown, DefaultError>['meta']
): void => {
  if (shouldSuppressToast(meta)) {
    return
  }

  const parsedMeta = (meta ?? undefined) as MutationMeta | undefined
  const errorTitle = withDefaultTitle(parsedMeta?.errorTitle, 'Aktion fehlgeschlagen')
  const description = parsedMeta?.errorMessage ?? resolveErrorMessage(error)

  toast({
    variant: 'destructive',
    title: errorTitle,
    description,
  })
}

const maybeToastMutationSuccess = (meta?: MutationOptions<unknown, DefaultError>['meta']): void => {
  if (!meta || typeof meta !== 'object') {
    return
  }

  const parsedMeta = meta as MutationMeta
  const hasSuccessMessage = typeof parsedMeta.successMessage === 'string' && parsedMeta.successMessage.length > 0
  const hasSuccessTitle = typeof parsedMeta.successTitle === 'string' && parsedMeta.successTitle.length > 0

  if (!hasSuccessMessage && !hasSuccessTitle) {
    return
  }

  toast({
    title: withDefaultTitle(parsedMeta.successTitle, 'Aktion erfolgreich'),
    description: hasSuccessMessage ? parsedMeta.successMessage : undefined,
  })
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

export const createQueryClient = (): QueryClient => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: DEFAULT_STALE_TIME_MS,
        gcTime: DEFAULT_GC_TIME_MS,
        retry: shouldRetryQuery,
        refetchOnWindowFocus: false,
        refetchOnReconnect: true,
        onError: (error, _query, _context, query): void => {
          maybeToastQueryError(error, query?.meta)
        },
      },
      mutations: {
        retry: false,
        onError: (error, _variables, _context, mutation): void => {
          maybeToastMutationError(error, mutation?.meta)
        },
        onSuccess: (_data, _variables, _context, mutation): void => {
          maybeToastMutationSuccess(mutation?.meta)
        },
      },
    },
  })
}

