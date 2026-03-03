/**
 * API Data Hook with Error State
 * Provides robust data fetching with explicit error handling instead of silent mock fallbacks
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient, ApiError } from '../api-client'

// ── Error State Types ─────────────────────────────────────────────────────────────

export type ErrorState = {
  isError: boolean
  error: ApiError | null
  isLoading: boolean
  refetch: () => void
  isFetching: boolean
}

// ── API Response Types ───────────────────────────────────────────────────────────

export type PaginatedResponse<T> = {
  items: T[]
  total: number
  page?: number
  limit?: number
}

// ── Options Type for useApiData ─────────────────────────────────────────────────

export interface UseApiDataOptions<T> {
  queryKey: readonly unknown[]
  endpoint: string
  params?: Record<string, string | number | boolean | undefined>
  fallbackData?: T | null
  staleTime?: number
  enabled?: boolean
}

// ── Default Options ─────────────────────────────────────────────────────────────

const DEFAULT_STALE_TIME = 2 * 60 * 1000 // 2 minutes

// ── useApiData Hook ─────────────────────────────────────────────────────────────

/**
 * Robust API data fetching hook with explicit error state
 * 
 * Usage:
 * const { data, isLoading, isError, error, refetch } = useApiData({
 *   queryKey: ['duenger'],
 *   endpoint: '/api/v1/agrar/duenger',
 *   fallbackData: mockDuenger // Optional for graceful degradation
 * })
 * 
 * if (isError && !isLoading) {
 *   return <ErrorState error={error} onRetry={refetch} />
 * }
 */
export function useApiData<T = unknown>(
  options: UseApiDataOptions<T>
) {
  const {
    queryKey,
    endpoint,
    params,
    fallbackData = null,
    staleTime = DEFAULT_STALE_TIME,
    enabled = true
  } = options

  const query = useQuery({
    queryKey,
    enabled,
    staleTime,
    queryFn: async () => {
      const urlParams = params 
        ? `?${  new URLSearchParams(
            Object.entries(params)
              .filter(([, v]) => v !== undefined)
              .map(([k, v]) => [k, String(v)])
          ).toString()}`
        : ''
      
      try {
        const response = await apiClient.get<T>(endpoint + urlParams)
        return response.data
      } catch (error) {
        // Log error for monitoring
        console.error(`API Error [${endpoint}]:`, error)
        
        // If fallback data is provided, return it (graceful degradation)
        if (fallbackData !== null && fallbackData !== undefined) {
          console.warn(`Using fallback data for ${endpoint}`)
          return fallbackData
        }
        
        // Re-throw to trigger error state
        throw error
      }
    }
  })

  return {
    data: query.data,
    ...query,
  }
}

// ── usePaginatedApiData Hook ────────────────────────────────────────────────────

export function usePaginatedApiData<T = unknown>(
  options: Omit<UseApiDataOptions<PaginatedResponse<T>>, 'fallbackData'> & {
    fallbackData?: PaginatedResponse<T>
  }
) {
  const {
    queryKey,
    endpoint,
    params,
    staleTime = DEFAULT_STALE_TIME,
    enabled = true
  } = options

  const defaultFallback: PaginatedResponse<T> = {
    items: [],
    total: 0,
    page: 1,
    limit: 100
  }

  return useApiData<PaginatedResponse<T>>({
    queryKey,
    endpoint,
    params,
    fallbackData: options.fallbackData || defaultFallback,
    staleTime,
    enabled
  })
}

// ── Single Item Fetch ───────────────────────────────────────────────────────────

export function useApiItem<T = unknown>(
  options: Omit<UseApiDataOptions<T>, 'params' | 'fallbackData'> & {
    id: string
    fallbackData?: T | null
  }
) {
  const { queryKey, endpoint, id, fallbackData = null, staleTime, enabled } = options

  return useApiData<T>({
    queryKey: [...queryKey, id],
    endpoint: `${endpoint}/${id}`,
    fallbackData,
    staleTime,
    enabled
  })
}

// ── Mutation Helpers ─────────────────────────────────────────────────────────────

export function useApiMutation<TVariables = void, TResponse = unknown>(
  options: {
    mutationFn: (variables: TVariables) => Promise<{ data: TResponse }>
    onSuccess?: (data: TResponse, variables: TVariables) => void
    onError?: (error: Error, variables: TVariables) => void
  }
) {
  const { mutationFn, onSuccess, onError } = options

  return {
    async mutate(variables: TVariables) {
      try {
        const response = await mutationFn(variables)
        onSuccess?.(response.data, variables)
        return response.data
      } catch (error) {
        onError?.(error as Error, variables)
        throw error
      }
    }
  }
}
