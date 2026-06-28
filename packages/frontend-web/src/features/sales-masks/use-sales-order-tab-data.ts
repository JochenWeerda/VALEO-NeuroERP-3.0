import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { salesKeys } from '@/lib/api/sales'
import { SALES_ORDER_PILOT_LAZY_DATA_TABS } from './sales-order-tab-tables'

export type SalesOrderTabDataResponse = {
  tab_key: string
  table_key: string
  items: Record<string, unknown>[]
}

function resolveTabEndpoint(
  tabKey: string,
  tabEndpoints: Record<string, string> | undefined,
): string | undefined {
  if (!tabEndpoints) return undefined
  return tabEndpoints[tabKey]
}

export function useSalesOrderTabData(
  orderId: string,
  activeTabKey: string | undefined,
  tabEndpoints: Record<string, string> | undefined,
) {
  const normalizedKey = activeTabKey ?? ''
  const endpoint = SALES_ORDER_PILOT_LAZY_DATA_TABS.has(normalizedKey)
    ? resolveTabEndpoint(normalizedKey, tabEndpoints)
    : undefined

  return useQuery({
    queryKey: [...salesKeys.order(orderId), 'tab-data', normalizedKey],
    queryFn: async () => {
      if (!endpoint) {
        throw new Error('Tab endpoint missing for lazy tab data request')
      }
      const response = await apiClient.get<SalesOrderTabDataResponse>(endpoint)
      return response.data
    },
    enabled: Boolean(orderId && endpoint),
    staleTime: 2 * 60 * 1000,
  })
}

export function mapTabDataToTables(
  response: SalesOrderTabDataResponse | undefined,
): Record<string, Record<string, unknown>[]> {
  if (!response) return {}
  return { [response.table_key]: response.items }
}
