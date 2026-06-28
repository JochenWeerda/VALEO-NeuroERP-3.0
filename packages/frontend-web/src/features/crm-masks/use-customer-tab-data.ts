import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { crmKeys } from '@/lib/api/crm'
import { CUSTOMER_PILOT_LAZY_DATA_TABS } from './customer-tab-tables'

export type CustomerTabDataResponse = {
  tab_key: string
  table_key: string
  items: Record<string, unknown>[]
}

function resolveTabEndpoint(
  tabKey: string,
  tabEndpoints: Record<string, string> | undefined,
): string | undefined {
  if (!tabEndpoints) return undefined
  return tabEndpoints[tabKey] ?? tabEndpoints[normalizeSummaryTabKey(tabKey)]
}

function normalizeSummaryTabKey(tabKey: string): string {
  const aliases: Record<string, string> = {
    contacts: 'kontakte',
    masterdata: 'stammdaten',
  }
  return aliases[tabKey] ?? tabKey
}

export function useCustomerTabData(
  customerId: string,
  activeTabKey: string | undefined,
  tabEndpoints: Record<string, string> | undefined,
) {
  const normalizedKey = activeTabKey ?? ''
  const hasLazyData =
    CUSTOMER_PILOT_LAZY_DATA_TABS.has(normalizedKey) ||
    CUSTOMER_PILOT_LAZY_DATA_TABS.has(normalizeSummaryTabKey(normalizedKey))
  const endpoint = hasLazyData ? resolveTabEndpoint(normalizedKey, tabEndpoints) : undefined

  return useQuery({
    queryKey: [...crmKeys.customer(customerId), 'tab-data', normalizedKey],
    queryFn: async () => {
      if (!endpoint) {
        throw new Error('Tab endpoint missing for lazy tab data request')
      }
      const response = await apiClient.get<CustomerTabDataResponse>(endpoint)
      return response.data
    },
    enabled: Boolean(customerId && endpoint),
    staleTime: 2 * 60 * 1000,
  })
}

export function mapTabDataToTables(
  response: CustomerTabDataResponse | undefined,
): Record<string, Record<string, unknown>[]> {
  if (!response) return {}
  return { [response.table_key]: response.items }
}
