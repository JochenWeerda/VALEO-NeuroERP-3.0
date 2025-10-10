import { apiClient } from '@/lib/axios'

export type SearchDomainKey =
  | 'contracts'
  | 'inventoryLots'
  | 'weighingTickets'
  | 'salesOrders'
  | 'salesInvoices'

export interface GlobalSearchSummary {
  term: string
  completedAt: string
  durationMs: number
  totals: Record<SearchDomainKey, number>
  errors: Partial<Record<SearchDomainKey, string>>
}

const DOMAIN_ENDPOINTS: Record<SearchDomainKey, string> = {
  contracts: '/contracts/api/v1/contracts',
  inventoryLots: '/inventory/api/v1/lots',
  weighingTickets: '/weighing/api/v1/tickets',
  salesOrders: '/sales/api/v1/orders',
  salesInvoices: '/sales/api/v1/invoices',
}

type DomainRequestConfig = {
  key: SearchDomainKey
  url: string
  term: string
}

const DEFAULT_RESULT_LIMIT = 5
const DEFAULT_PAGE_INDEX = 1
const MILLISECONDS_PER_SECOND = 1_000
const SECONDS_PER_MINUTE = 60
const MINUTES_PER_HOUR = 60
const HOURS_PER_DAY = 24
const DEFAULT_LOOKBACK_DAYS = 30

const buildDomainRequests = (term: string): DomainRequestConfig[] => {
  return (Object.keys(DOMAIN_ENDPOINTS) as SearchDomainKey[]).map((key) => ({
    key,
    url: DOMAIN_ENDPOINTS[key],
    term,
  }))
}

const normalizeListPayload = (payload: unknown): unknown[] => {
  if (payload === null || payload === undefined) {
    return []
  }

  if (Array.isArray(payload)) {
    return payload
  }

  if (typeof payload === 'object') {
    const container = payload as Record<string, unknown>

    if (Array.isArray(container.data)) {
      return container.data
    }

    if (Array.isArray(container.items)) {
      return container.items
    }

    if (Array.isArray(container.results)) {
      return container.results
    }
  }

  return []
}

const buildQueryParams = (term: string): Record<string, string | number> => {
  const trimmed = term.trim()
  const params: Record<string, string | number> = {
    q: trimmed,
    search: trimmed,
    query: trimmed,
    term: trimmed,
    limit: DEFAULT_RESULT_LIMIT,
    pageSize: DEFAULT_RESULT_LIMIT,
    page: DEFAULT_PAGE_INDEX,
  }

  const now = new Date()
  const millisecondsLookback =
    DEFAULT_LOOKBACK_DAYS * HOURS_PER_DAY * MINUTES_PER_HOUR * SECONDS_PER_MINUTE * MILLISECONDS_PER_SECOND
  const isoNow = now.toISOString()
  const thirtyDaysAgo = new Date(now.getTime() - millisecondsLookback).toISOString()

  params.fromDate = thirtyDaysAgo
  params.toDate = isoNow

  return params
}

export const performGlobalSearch = async (term: string): Promise<GlobalSearchSummary> => {
  const started = Date.now()
  const requests = buildDomainRequests(term)
  const params = buildQueryParams(term)

  const settled = await Promise.allSettled(
    requests.map(async ({ key, url }) => {
      const payload = await apiClient.get<unknown>(url, { params })
      return {
        key,
        payload,
      }
    })
  )

  const totals: Record<SearchDomainKey, number> = {
    contracts: 0,
    inventoryLots: 0,
    weighingTickets: 0,
    salesOrders: 0,
    salesInvoices: 0,
  }

  const errors: Partial<Record<SearchDomainKey, string>> = {}

  settled.forEach((result, index) => {
    const { key } = requests[index]

    if (result.status === 'fulfilled') {
      const entries = normalizeListPayload(result.value.payload)
      totals[key] = entries.length
    } else {
      const reason = result.reason
      if (typeof reason === 'object' && reason !== null && 'message' in reason) {
        const maybeMessage = (reason as { message?: unknown }).message
        errors[key] = typeof maybeMessage === 'string' && maybeMessage.length > 0 ? maybeMessage : 'Unbekannter Fehler'
      } else {
        errors[key] = 'Unbekannter Fehler'
      }
    }
  })

  const completed = Date.now()

  return {
    term,
    completedAt: new Date(completed).toISOString(),
    durationMs: completed - started,
    totals,
    errors,
  }
}

