import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type KpiDefinition = {
  id: string
  kpi_code: string
  name: string
  description?: string
  formula?: string
  target_value?: number
  unit?: string
  is_active: boolean
}

type Payload = { data: Record<string, unknown> }

export const controllingKeys = {
  all: ['controlling'] as const,
  kpis: () => [...controllingKeys.all, 'kpis'] as const,
}

const toNumberOrUndefined = (value: unknown): number | undefined => {
  const num = Number(value)
  return Number.isFinite(num) ? num : undefined
}

const normalize = (row: Record<string, unknown>): KpiDefinition => ({
  id: String(row.id),
  kpi_code: String(row.kpi_code ?? ''),
  name: String(row.name ?? ''),
  description: row.description ? String(row.description) : undefined,
  formula: row.formula ? String(row.formula) : undefined,
  target_value: toNumberOrUndefined(row.target_value),
  unit: row.unit ? String(row.unit) : undefined,
  is_active: Boolean(row.is_active),
})

export function useControllingKpis() {
  return useQuery({
    queryKey: controllingKeys.kpis(),
    queryFn: async () => {
      const rows = (await apiClient.get<Record<string, unknown>[]>('/api/v1/controlling/kpis')).data
      return rows.map(normalize)
    },
    staleTime: 60_000,
  })
}

export type KpiInput = {
  kpi_code: string
  name: string
  description?: string
  formula?: string
  target_value?: number
  unit?: string
  is_active: boolean
}

export function useCreateKpi() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: KpiInput) => {
      const payload: Payload = { data }
      await apiClient.post('/api/v1/controlling/kpis', payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.kpis() })
    },
  })
}

export function useUpdateKpi() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: KpiInput }) => {
      const payload: Payload = { data }
      await apiClient.put(`/api/v1/controlling/kpis/${id}`, payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.kpis() })
    },
  })
}

export function useDeleteKpi() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/controlling/kpis/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.kpis() })
    },
  })
}
