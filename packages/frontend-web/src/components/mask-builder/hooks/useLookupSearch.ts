import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export interface LookupSearchResult {
  value: string
  label: string
}

export interface UseLookupSearchOptions {
  endpoint?: string
  query: string
  minChars?: number
  limit?: number
  cacheTtlMs?: number
  debounceMs?: number
  enabled?: boolean
}

function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const handle = window.setTimeout(() => setDebounced(value), delayMs)
    return () => window.clearTimeout(handle)
  }, [value, delayMs])

  return debounced
}

export function useLookupSearch({
  endpoint,
  query,
  minChars = 2,
  limit = 25,
  cacheTtlMs = 900_000,
  debounceMs = 300,
  enabled = true,
}: UseLookupSearchOptions) {
  const debouncedQuery = useDebouncedValue(query.trim(), debounceMs)
  const canSearch = enabled && Boolean(endpoint) && debouncedQuery.length >= minChars

  return useQuery({
    queryKey: ['mask-lookup', endpoint, debouncedQuery, limit],
    queryFn: async () => {
      if (!endpoint) return [] as LookupSearchResult[]
      const response = await apiClient.get<LookupSearchResult[] | { items: LookupSearchResult[] }>(endpoint, {
        params: { q: debouncedQuery, limit },
      })
      const payload = response.data
      if (Array.isArray(payload)) return payload.slice(0, limit)
      return (payload.items ?? []).slice(0, limit)
    },
    enabled: canSearch,
    staleTime: cacheTtlMs,
  })
}
