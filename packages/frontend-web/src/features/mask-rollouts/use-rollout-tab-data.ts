import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type RolloutScreenSummary = {
  schema_version: number
  screen_id: string
  title: string
  subtitle?: string
  summary: Record<string, unknown>
  available_tabs?: string[]
  tab_endpoints?: Record<string, string>
  actions?: Array<{ key: string; label: string; permission?: string }>
  performance?: {
    initial_payload_budget_kb?: number
    lookup_min_chars?: number
  }
}

export type RolloutTabDataResponse = {
  tab_key: string
  table_key: string
  items: Record<string, unknown>[]
  page?: number
  limit?: number
  total?: number
}

export const maskRolloutKeys = {
  all: ['mask-rollout'] as const,
  summary: (screenId: string, entityId: string) =>
    [...maskRolloutKeys.all, 'summary', screenId, entityId] as const,
  tab: (screenId: string, entityId: string, tabKey: string, page: number, limit: number) =>
    [...maskRolloutKeys.all, 'tab', screenId, entityId, tabKey, page, limit] as const,
}

export function useRolloutScreenSummary(screenId: string, entityId: string, enabled = true) {
  return useQuery({
    queryKey: maskRolloutKeys.summary(screenId, entityId),
    queryFn: async () => {
      const response = await apiClient.get<RolloutScreenSummary>(
        `/api/v1/mask-rollouts/${screenId}/${entityId}/screen-summary`,
      )
      return response.data
    },
    enabled: enabled && Boolean(screenId && entityId),
    staleTime: 2 * 60 * 1000,
  })
}

export function useRolloutTabData(
  screenId: string,
  entityId: string,
  activeTabKey: string | undefined,
  tabEndpoints: Record<string, string> | undefined,
  page = 1,
  limit = 25,
) {
  const normalizedKey = activeTabKey ?? ''
  const endpoint = normalizedKey !== 'kopf' ? tabEndpoints?.[normalizedKey] : undefined

  return useQuery({
    queryKey: maskRolloutKeys.tab(screenId, entityId, normalizedKey, page, limit),
    queryFn: async () => {
      if (!endpoint) {
        throw new Error('Tab endpoint missing for lazy tab data request')
      }
      const response = await apiClient.get<RolloutTabDataResponse>(endpoint, {
        params: { page, limit },
      })
      return response.data
    },
    enabled: Boolean(screenId && entityId && endpoint),
    staleTime: 2 * 60 * 1000,
  })
}

export function mapRolloutTabDataToTables(
  response: RolloutTabDataResponse | undefined,
): Record<string, Record<string, unknown>[]> {
  if (!response) return {}
  return { [response.table_key]: response.items }
}
