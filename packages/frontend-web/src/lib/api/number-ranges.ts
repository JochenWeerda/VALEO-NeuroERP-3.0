import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export interface NumberRange {
  id: string
  tenant_id: string
  range_type: string
  prefix: string
  start_number: number
  current_value: number
  digit_count: number
  reserved_prefix_digits: number
  is_active: boolean
  next_number: string | null
}

export interface NumberRangeConfigPayload {
  range_type: string
  prefix: string
  start_number: number
  digit_count: number
  reserved_prefix_digits: number
}

const QUERY_KEY = ['admin', 'number-ranges']

export function useNumberRanges() {
  return useQuery<NumberRange[]>({
    queryKey: QUERY_KEY,
    queryFn: async () => {
      const res = await apiClient.get<NumberRange[]>('/api/v1/admin/number-ranges/')
      return res.data
    },
  })
}

export function useConfigureNumberRange() {
  const queryClient = useQueryClient()
  return useMutation<NumberRange, Error, NumberRangeConfigPayload>({
    mutationFn: async (payload) => {
      const res = await apiClient.post<NumberRange>('/api/v1/admin/number-ranges/', payload)
      return res.data
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: QUERY_KEY })
    },
  })
}

export function usePeekNextNumber(rangeType: string) {
  return useQuery<{ range_type: string; next_number: string }>({
    queryKey: [...QUERY_KEY, rangeType, 'peek'],
    queryFn: async () => {
      const res = await apiClient.get<{ range_type: string; next_number: string }>(
        `/api/v1/admin/number-ranges/${rangeType}/peek`
      )
      return res.data
    },
    enabled: !!rangeType,
    retry: false,
  })
}
