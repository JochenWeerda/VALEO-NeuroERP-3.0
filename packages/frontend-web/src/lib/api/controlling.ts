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
  dashboards: () => [...controllingKeys.all, 'dashboards'] as const,
  timeseries: (kpiId?: string) => [...controllingKeys.all, 'timeseries', kpiId ?? 'all'] as const,
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

export type ControllingDashboard = {
  id: string
  dashboard_code: string
  name: string
  description?: string
  is_active: boolean
}

const normalizeDashboard = (row: Record<string, unknown>): ControllingDashboard => ({
  id: String(row.id),
  dashboard_code: String(row.dashboard_code ?? ''),
  name: String(row.name ?? ''),
  description: row.description ? String(row.description) : undefined,
  is_active: Boolean(row.is_active),
})

export type DashboardInput = {
  dashboard_code: string
  name: string
  description?: string
  is_active: boolean
}

export function useControllingDashboards() {
  return useQuery({
    queryKey: controllingKeys.dashboards(),
    queryFn: async () => {
      const rows = (await apiClient.get<Record<string, unknown>[]>('/api/v1/controlling/dashboards')).data
      return rows.map(normalizeDashboard)
    },
    staleTime: 60_000,
  })
}

export function useCreateDashboard() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: DashboardInput) => {
      const payload: Payload = {
        data: {
          ...data,
          layout: {},
          default_filters: {},
          role_scope: [],
        },
      }
      await apiClient.post('/api/v1/controlling/dashboards', payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.dashboards() })
    },
  })
}

export function useUpdateDashboard() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: DashboardInput }) => {
      const payload: Payload = {
        data: {
          ...data,
          layout: {},
          default_filters: {},
          role_scope: [],
        },
      }
      await apiClient.put(`/api/v1/controlling/dashboards/${id}`, payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.dashboards() })
    },
  })
}

export function useDeleteDashboard() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/controlling/dashboards/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.dashboards() })
    },
  })
}

export type KpiTimeseriesItem = {
  id: string
  kpi_id: string
  period_start: string
  period_end: string
  value: number
  source?: string
}

const normalizeTimeseries = (row: Record<string, unknown>): KpiTimeseriesItem => ({
  id: String(row.id),
  kpi_id: String(row.kpi_id ?? ''),
  period_start: String(row.period_start ?? ''),
  period_end: String(row.period_end ?? ''),
  value: Number(row.value ?? 0),
  source: row.source ? String(row.source) : undefined,
})

export type TimeseriesInput = {
  kpi_id: string
  period_start: string
  period_end: string
  value: number
  source?: string
}

export function useKpiTimeseries(kpiId?: string) {
  return useQuery({
    queryKey: controllingKeys.timeseries(kpiId),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (kpiId) params.append('kpi_id', kpiId)
      const rows = (await apiClient.get<Record<string, unknown>[]>(`/api/v1/controlling/timeseries?${String(params)}`)).data
      return rows.map(normalizeTimeseries)
    },
    staleTime: 60_000,
  })
}

export function useCreateTimeseriesItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: TimeseriesInput) => {
      const payload: Payload = {
        data: {
          ...data,
          dimensions: {},
        },
      }
      await apiClient.post('/api/v1/controlling/timeseries', payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.timeseries() })
    },
  })
}

export function useDeleteTimeseriesItem() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/controlling/timeseries/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.timeseries() })
    },
  })
}
