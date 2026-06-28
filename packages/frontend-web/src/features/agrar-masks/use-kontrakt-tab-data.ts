import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { kontraktKeys } from '@/lib/api/kontrakte'
import { KONTRAKT_PILOT_LAZY_DATA_TABS } from './kontrakt-tab-tables'

export type KontraktTabDataResponse = {
  tab_key: string
  table_key: string
  items: Record<string, unknown>[]
  page?: number
  limit?: number
  total?: number
}

function resolveTabEndpoint(
  tabKey: string,
  tabEndpoints: Record<string, string> | undefined,
): string | undefined {
  if (!tabEndpoints) return undefined
  return tabEndpoints[tabKey]
}

export function useKontraktTabData(
  contractId: string,
  activeTabKey: string | undefined,
  tabEndpoints: Record<string, string> | undefined,
  page = 1,
  limit = 25,
) {
  const normalizedKey = activeTabKey ?? ''
  const endpoint = KONTRAKT_PILOT_LAZY_DATA_TABS.has(normalizedKey)
    ? resolveTabEndpoint(normalizedKey, tabEndpoints)
    : undefined

  return useQuery({
    queryKey: [...kontraktKeys.detail(contractId), 'tab-data', normalizedKey, page, limit],
    queryFn: async () => {
      if (!endpoint) {
        throw new Error('Tab endpoint missing for lazy tab data request')
      }
      const response = await apiClient.get<KontraktTabDataResponse>(endpoint, {
        params: { page, limit },
      })
      return response.data
    },
    enabled: Boolean(contractId && endpoint),
    staleTime: 2 * 60 * 1000,
  })
}

export function mapTabDataToTables(
  response: KontraktTabDataResponse | undefined,
): Record<string, Record<string, unknown>[]> {
  if (!response) return {}
  return { [response.table_key]: response.items }
}
