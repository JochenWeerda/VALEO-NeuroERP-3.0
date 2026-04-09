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
  widgets: (dashboardId?: string) => [...controllingKeys.all, 'widgets', dashboardId ?? 'all'] as const,
  timeseries: (kpiId?: string) => [...controllingKeys.all, 'timeseries', kpiId ?? 'all'] as const,
  actions: () => [...controllingKeys.all, 'actions'] as const,
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
      const res = await apiClient.get<Record<string, unknown>[]>('/api/v1/controlling/kpis')
      const rows = Array.isArray(res?.data) ? res.data : []
      return rows.map(normalize)
    },
    initialData: [],
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
    initialData: [],
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

export type DashboardWidget = {
  id: string
  dashboard_id: string
  widget_type: string
  title: string
  kpi_id?: string
  position_x: number
  position_y: number
  size_w: number
  size_h: number
}

const normalizeWidget = (row: Record<string, unknown>): DashboardWidget => ({
  id: String(row.id),
  dashboard_id: String(row.dashboard_id ?? ''),
  widget_type: String(row.widget_type ?? ''),
  title: String(row.title ?? ''),
  kpi_id: row.kpi_id ? String(row.kpi_id) : undefined,
  position_x: Number(row.position_x ?? 0),
  position_y: Number(row.position_y ?? 0),
  size_w: Number(row.size_w ?? 4),
  size_h: Number(row.size_h ?? 3),
})

export type WidgetInput = {
  widget_type: string
  title: string
  kpi_id?: string
  position_x?: number
  position_y?: number
  size_w?: number
  size_h?: number
}

export function useDashboardWidgets(dashboardId?: string) {
  return useQuery({
    queryKey: controllingKeys.widgets(dashboardId),
    enabled: Boolean(dashboardId),
    queryFn: async () => {
      const rows = (await apiClient.get<Record<string, unknown>[]>(`/api/v1/controlling/dashboards/${dashboardId}/widgets`)).data
      return rows.map(normalizeWidget)
    },
    initialData: [],
    staleTime: 60_000,
  })
}

export function useCreateWidget(dashboardId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: WidgetInput) => {
      const payload: Payload = {
        data: {
          ...data,
          position_x: data.position_x ?? 0,
          position_y: data.position_y ?? 0,
          size_w: data.size_w ?? 4,
          size_h: data.size_h ?? 3,
          settings: {},
        },
      }
      await apiClient.post(`/api/v1/controlling/dashboards/${dashboardId}/widgets`, payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.widgets(dashboardId) })
    },
  })
}

export function useUpdateWidget() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, dashboardId, data }: { id: string; dashboardId: string; data: WidgetInput }) => {
      const payload: Payload = {
        data: {
          ...data,
          position_x: data.position_x ?? 0,
          position_y: data.position_y ?? 0,
          size_w: data.size_w ?? 4,
          size_h: data.size_h ?? 3,
          settings: {},
        },
      }
      await apiClient.put(`/api/v1/controlling/widgets/${id}`, payload)
      return dashboardId
    },
    onSuccess: (dashboardId) => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.widgets(dashboardId) })
    },
  })
}

export function useDeleteWidget(dashboardId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/controlling/widgets/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.widgets(dashboardId) })
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
    initialData: [],
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

export type ControllingAction = {
  id: string
  kpi_id?: string
  dashboard_id?: string
  title: string
  description?: string
  owner_user_id?: string
  status: string
  due_date?: string
}

const normalizeAction = (row: Record<string, unknown>): ControllingAction => ({
  id: String(row.id),
  kpi_id: row.kpi_id ? String(row.kpi_id) : undefined,
  dashboard_id: row.dashboard_id ? String(row.dashboard_id) : undefined,
  title: String(row.title ?? ''),
  description: row.description ? String(row.description) : undefined,
  owner_user_id: row.owner_user_id ? String(row.owner_user_id) : undefined,
  status: String(row.status ?? 'open'),
  due_date: row.due_date ? String(row.due_date) : undefined,
})

export type ActionInput = {
  kpi_id?: string
  dashboard_id?: string
  title: string
  description?: string
  owner_user_id?: string
  status: string
  due_date?: string
}

export function useControllingActions(status?: string) {
  return useQuery({
    queryKey: controllingKeys.actions(),
    queryFn: async () => {
      const params = new URLSearchParams()
      if (status) params.append('status', status)
      const rows = (await apiClient.get<Record<string, unknown>[]>(`/api/v1/controlling/actions?${String(params)}`)).data
      return rows.map(normalizeAction)
    },
    initialData: [],
    staleTime: 60_000,
  })
}

export function useCreateAction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: ActionInput) => {
      const payload: Payload = { data }
      await apiClient.post('/api/v1/controlling/actions', payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.actions() })
    },
  })
}

export function useUpdateAction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: ActionInput }) => {
      const payload: Payload = { data }
      await apiClient.put(`/api/v1/controlling/actions/${id}`, payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.actions() })
    },
  })
}

export function useDeleteAction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/controlling/actions/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: controllingKeys.actions() })
    },
  })
}

// Aliases for Kostenstellenrechnung page
export const useKostenstellen = useControllingKpis
export const useKostenstellenTimeseries = useKpiTimeseries

// ─── Branchenbenchmark (Gap 047) ───────────────────────────────────────────

export type BenchmarkData = {
  period: { start_date: string | null; end_date: string | null }
  own: Record<string, number>
  branch: Record<string, number>
  comparison: Record<string, { own: number; branch: number | null; deviation_pct: number | null }>
}

export type BenchmarkCategorySummary = {
  kategorie: string
  kennzahl_count: number
  top10_count: number
  improvement_count: number
  avg_score: number
}

export type BenchmarkCatalog = {
  report_id: string
  tenant_id: string
  frequenz: string
  kennzahl_count: number
  category_count: number
  top10_count: number
  improvement_count: number
  trend_series_count: number
  best_metric: string
  weakest_metric: string
  categories: BenchmarkCategorySummary[]
}

export type BenchmarkReadModel = {
  report: {
    top10_kennzahlen?: Array<{ bezeichnung: string; eigenwert: number; einheit?: string }>
    verbesserungspotenzial?: Array<{ bezeichnung: string; eigenwert: number; einheit?: string }>
  }
  catalog: BenchmarkCatalog
  coverage_notes: string[]
  schema_version: number
}

export function useBenchmark(startDate?: string | null, endDate?: string | null) {
  return useQuery({
    queryKey: ['analytics', 'benchmark', startDate ?? '', endDate ?? ''],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (startDate) params.set('start_date', startDate)
      if (endDate) params.set('end_date', endDate)
      const suffix = params.toString() ? `?${params.toString()}` : ''
      const res = await apiClient.get<BenchmarkData>(`/api/v1/analytics/benchmark${suffix}`)
      return res.data
    },
    staleTime: 60 * 1000,
  })
}

export function useBenchmarkReadModel() {
  return useQuery({
    queryKey: ['analytics', 'benchmark-read-model'],
    queryFn: async () => {
      const res = await apiClient.get<BenchmarkReadModel>('/api/v1/benchmark/read-model')
      return res.data
    },
    staleTime: 60 * 1000,
  })
}
