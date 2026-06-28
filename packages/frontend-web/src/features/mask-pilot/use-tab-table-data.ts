import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export interface TabTablePageParams {
  page?: number
  limit?: number
  sort?: string
  q?: string
}

export interface TabTablePageResponse {
  tab_key: string
  table_key: string
  items: Record<string, unknown>[]
  page?: number
  limit?: number
  total?: number
}

export function useTabTableData(
  endpoint: string | undefined,
  queryKeyPrefix: readonly unknown[],
  params: TabTablePageParams = {},
  enabled = true,
) {
  const page = params.page ?? 1
  const limit = Math.min(params.limit ?? 25, 50)

  return useQuery({
    queryKey: [...queryKeyPrefix, 'tab-table', endpoint, page, limit, params.sort, params.q],
    queryFn: async () => {
      if (!endpoint) {
        throw new Error('Tab endpoint missing for table data request')
      }
      const response = await apiClient.get<TabTablePageResponse>(endpoint, {
        params: { page, limit, sort: params.sort, q: params.q },
      })
      return response.data
    },
    enabled: enabled && Boolean(endpoint),
    staleTime: 2 * 60 * 1000,
  })
}

export function mapTabTableResponseToRows(
  response: TabTablePageResponse | undefined,
): Record<string, Record<string, unknown>[]> {
  if (!response) return {}
  return { [response.table_key]: response.items }
}
