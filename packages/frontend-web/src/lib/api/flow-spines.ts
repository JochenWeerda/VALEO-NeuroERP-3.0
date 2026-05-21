import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { apiClient } from '@/lib/api-client'
import i18n from '@/i18n/config'

// ── Shared types ─────────────────────────────────────────────────────────────

export type FlowSpineTone = 'ok' | 'warning' | 'critical' | 'active'

export interface FlowSpineAction {
  label: string
  href: string
  variant: 'primary' | 'secondary'
  api_path: string
}

export interface FlowSpineNode {
  id: string
  label: string
  status: FlowSpineTone
  icon: string
  metric: string
  submetric: string
  timestamp: string
  insight: string
  detail_rows: Array<{ label: string; value: string }>
  kpis: Array<{ label: string; value: string }>
  documents: Array<{ label: string; href: string }>
  actions: FlowSpineAction[]
  agent: {
    headline: string
    message: string
    reasons: string[]
    actions: string[]
  }
}

export interface CustomerData {
  partner_id: string
  partner_number: string
  name_1: string
  name_2?: string
  street?: string
  house_number?: string
  postal_code?: string
  city?: string
  country?: string
  phone?: string
  email?: string
  debtor_account?: string
  creditor_account?: string
}

export interface FlowSpineWorkspace {
  schema_version: number
  manifest_kind: string
  generated_at: string
  process_key: string
  title: string
  subtitle: string
  instance_label: string
  breadcrumb: string[]
  search_placeholder: string
  mode: string
  user_role: string
  left_navigation: {
    processes: Array<{ key: string; label: string; route_path: string; active: boolean }>
    favorites: string[]
    recent_items: string[]
    role_switches: string[]
  }
  badges: Array<{ label: string; tone: string }>
  focus_node_id: string
  nodes: FlowSpineNode[]
  right_panel: {
    resources: Array<{ label: string; href: string }>
    linked_modules: Array<{ label: string; href: string; api_path: string }>
    domain: string
  }
  footer_cards: Array<{ title: string; items: string[] }>
  instance_id?: string
  case_number?: string
  customer_id?: string
  customer_name?: string
  customer_data?: CustomerData
  lifecycle_status?: FlowSpineLifecycleStatus
  business_status?: string
  active_node_id?: string
  resume_node_id?: string
  resume_route?: string
  resume_payload?: Record<string, unknown>
  assigned_owner?: string
  last_actor?: string
  last_action_label?: string
  last_activity_at?: string
  blocked_until?: string
  completion_reason_code?: string
  cancellation_reason_category?: string
  cancellation_reason_code?: string
  failure_reason_category?: string
  failure_reason_code?: string
  reason_note?: string
  closed_at?: string
  closed_by?: string
  cancelled_at?: string
  cancelled_by?: string
  failed_at?: string
  failed_by?: string
  version_no?: number
  updated_at?: string
}

export interface FlowSpineCatalog {
  schema_version: number
  manifest_kind: string
  generated_at: string
  processes: Array<{
    key: string
    label: string
    route_path: string
    summary: string
    domain: string
  }>
}

export interface FlowSpineInstance {
  instance_id: string
  case_number: string
  process_key: string
  label: string
  created_at: string
  updated_at?: string
  customer_id?: string
  customer_name?: string
  partner_name?: string
  subject?: string
  entry_mode?: string
  lifecycle_status?: FlowSpineLifecycleStatus
  business_status?: string
  node_statuses: Record<string, string>
  active_node_id?: string
  resume_node_id?: string
  resume_route?: string
  resume_payload?: Record<string, unknown>
  assigned_owner?: string
  last_actor?: string
  last_action_label?: string
  last_activity_at?: string
  blocked_until?: string
  completion_reason_code?: string
  cancellation_reason_category?: string
  cancellation_reason_code?: string
  failure_reason_category?: string
  failure_reason_code?: string
  reason_note?: string
  closed_at?: string
  closed_by?: string
  cancelled_at?: string
  cancelled_by?: string
  failed_at?: string
  failed_by?: string
  version_no?: number
  linked_document_id?: string
  linked_document_type?: string
}

export type FlowSpineLifecycleStatus =
  | 'draft'
  | 'in_progress'
  | 'on_hold'
  | 'completed'
  | 'cancelled'
  | 'failed'

export interface FlowSpineInstanceEvent {
  event_id: string
  instance_id: string
  process_key: string
  tenant_id: string
  event_type: string
  from_lifecycle_status?: FlowSpineLifecycleStatus
  to_lifecycle_status?: FlowSpineLifecycleStatus
  from_business_status?: string
  to_business_status?: string
  node_id?: string
  actor_id?: string
  reason_category?: string
  reason_code?: string
  reason_note?: string
  payload: Record<string, unknown>
  created_at: string
}

export interface FlowSpineTimelineResponse {
  instance_id: string
  process_key: string
  tenant_id: string
  events: FlowSpineInstanceEvent[]
}

export interface CreateInstancePayload {
  label?: string
  customer_id?: string
  customer_name?: string
  partner_name?: string
  subject?: string
  entry_mode?: string
  linked_document_id?: string
  linked_document_type?: string
}

export interface TransitionPayload {
  node_id: string
  new_status: FlowSpineTone
  action_label: string
  user_id?: string
}

export interface FlowSpineSavePayload {
  resume_node_id?: string
  resume_route?: string
  resume_payload?: Record<string, unknown>
  business_status?: string
  assigned_owner?: string
  action_label?: string
  note?: string
  user_id?: string
}

export interface FlowSpineResumeResponse extends FlowSpineInstance {
  resume_target: {
    node_id?: string
    route?: string
    payload?: Record<string, unknown>
  }
}

export interface FlowSpineLifecycleActionPayload {
  business_status?: string
  node_id?: string
  assigned_owner?: string
  action_label?: string
  reason_category?: string
  reason_code?: string
  reason_note?: string
  blocked_until?: string
  user_id?: string
}

/** Alias kept for consumers that use the NodeAction name from the spec */
export type NodeAction = FlowSpineAction

/** Standalone KPI entry type */
export interface FlowSpineKpi {
  label: string
  value: string
}

function getActiveLanguage(): string {
  return i18n.resolvedLanguage ?? i18n.language ?? 'de'
}

/**
 * Einige Gateways/BFFs liefern das Manifest als { data: { manifest_kind, ... } };
 * FastAPI liefert das flache JSON. Diese Hilfsfunktion vereinheitlicht den Zugriff.
 */
function normalizeFlowSpineBody<T>(body: unknown): T {
  if (body == null || typeof body !== 'object') {
    throw new Error('Flow-Spine API: Leere oder ungueltige Antwort.')
  }
  const obj = body as Record<string, unknown>
  const nested = obj.data
  if (nested && typeof nested === 'object' && !Array.isArray(nested)) {
    const mk = (nested as Record<string, unknown>).manifest_kind
    if (typeof mk === 'string' && mk.startsWith('FLOW_SPINE_')) {
      return nested as T
    }
  }
  return obj as T
}

export function getFlowSpineWorkspaceQueryKey(
  processKey: string,
  instanceId?: string,
  lang: string = getActiveLanguage(),
) {
  return ['workflow', 'flow-spine', processKey, instanceId ?? 'default', lang] as const
}

// ── Plain fetch helpers (used by FlowSpineWorkspace via useQuery) ─────────────

/** Extrahiert lesbare Fehlermeldung aus Axios/FastAPI-Fehlern (für UI). */
export function getFlowSpineFetchErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status
    const data = err.response?.data as { detail?: unknown } | undefined
    const detail = data?.detail
    if (typeof detail === 'string') return `HTTP ${status ?? '?'}: ${detail}`
    if (detail != null) {
      try {
        return `HTTP ${status ?? '?'}: ${JSON.stringify(detail)}`
      } catch {
        return `HTTP ${status ?? '?'}`
      }
    }
    if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error')) {
      return 'Netzwerkfehler: Backend nicht erreichbar (uvicorn/FastAPI gestartet? Vite-Proxy /api/v1 → Backend?).'
    }
    return err.message || `HTTP ${status ?? '?'}`
  }
  if (err instanceof Error) return err.message
  return String(err)
}

export async function fetchFlowSpineWorkspace(processKey: string, instanceId?: string): Promise<FlowSpineWorkspace> {
  const lang = encodeURIComponent(getActiveLanguage())
  const query = new URLSearchParams({ lang })
  if (instanceId) {
    query.set('instance_id', instanceId)
  }
  const url = `/api/v1/process/flow-spines/${processKey}?${query.toString()}`
  const response = await apiClient.get<FlowSpineWorkspace>(url)
  const body = normalizeFlowSpineBody<FlowSpineWorkspace>(response.data)
  if (!Array.isArray(body.nodes)) {
    throw new Error('Flow-Spine API: Antwort ohne gueltiges nodes-Array (Backend-Vertrag pruefen).')
  }
  return body
}

export async function fetchFlowSpineCatalog(): Promise<FlowSpineCatalog> {
  const lang = encodeURIComponent(getActiveLanguage())
  const response = await apiClient.get<FlowSpineCatalog>(`/api/v1/process/flow-spines/catalog?lang=${lang}`)
  const body = normalizeFlowSpineBody<FlowSpineCatalog>(response.data)
  if (!Array.isArray(body.processes)) {
    throw new Error('Flow-Spine Katalog: Feld processes fehlt oder ist kein Array (Backend-Vertrag pruefen).')
  }
  return body
}

export async function saveFlowSpineResumeCheckpoint(
  processKey: string,
  instanceId: string,
  payload: FlowSpineSavePayload,
): Promise<FlowSpineInstance> {
  const res = await apiClient.post<FlowSpineInstance>(
    `/api/v1/process/flow-spines/${processKey}/instances/${instanceId}/save`,
    payload,
  )
  return res.data
}

// ── React Query hooks ─────────────────────────────────────────────────────────

export function useFlowSpineWorkspace(processKey: string, instanceId?: string) {
  const lang = getActiveLanguage()
  return useQuery<FlowSpineWorkspace>({
    queryKey: getFlowSpineWorkspaceQueryKey(processKey, instanceId, lang),
    queryFn: () => fetchFlowSpineWorkspace(processKey, instanceId),
    staleTime: 30_000,
    retry: false,
  })
}

export function useFlowSpineCatalogHook(options?: { enabled?: boolean }) {
  const lang = getActiveLanguage()
  return useQuery<FlowSpineCatalog>({
    queryKey: ['workflow', 'flow-spine', 'catalog', lang],
    queryFn: fetchFlowSpineCatalog,
    staleTime: 60_000,
    retry: false,
    enabled: options?.enabled !== false,
  })
}

/** Named alias matching the spec — delegates to useFlowSpineCatalogHook */
export function useFlowSpineCatalog(options?: { enabled?: boolean }) {
  return useFlowSpineCatalogHook(options)
}

type FlowSpineInstancesResponse = {
  process_key: string
  total: number
  instances: FlowSpineInstance[]
}

export function useFlowSpineInstances(processKey: string, search?: string, ready = true) {
  return useQuery<FlowSpineInstance[]>({
    queryKey: ['workflow', 'flow-spine', processKey, 'instances', search ?? ''],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (search) params.set('search', search)
      const res = await apiClient.get<FlowSpineInstancesResponse>(
        `/api/v1/process/flow-spines/${processKey}/instances?${params.toString()}`
      )
      return res.data.instances
    },
    retry: false,
    enabled: !!processKey && ready,
    staleTime: 60_000,
    refetchOnWindowFocus: false,
  })
}

export function useCreateFlowSpineInstance(processKey: string) {
  const queryClient = useQueryClient()
  return useMutation<FlowSpineInstance, Error, CreateInstancePayload>({
    mutationFn: async (payload) => {
      const res = await apiClient.post<FlowSpineInstance>(
        `/api/v1/process/flow-spines/${processKey}/instances`,
        payload
      )
      return res.data
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['workflow', 'flow-spine', processKey] })
    },
  })
}

export function useTransitionFlowSpineNode(processKey: string, instanceId: string) {
  const queryClient = useQueryClient()
  return useMutation<FlowSpineInstance, Error, TransitionPayload>({
    mutationFn: async (payload) => {
      const res = await apiClient.post<FlowSpineInstance>(
        `/api/v1/process/flow-spines/${processKey}/instances/${instanceId}/transitions`,
        payload
      )
      return res.data
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['workflow', 'flow-spine', processKey] })
    },
  })
}

export function useSaveFlowSpineInstance(processKey: string, instanceId?: string) {
  const queryClient = useQueryClient()
  return useMutation<FlowSpineInstance, Error, FlowSpineSavePayload>({
    mutationFn: async (payload) => {
      if (!instanceId) throw new Error('instanceId fehlt')
      const res = await apiClient.post<FlowSpineInstance>(
        `/api/v1/process/flow-spines/${processKey}/instances/${instanceId}/save`,
        payload
      )
      return res.data
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['workflow', 'flow-spine', processKey] })
    },
  })
}

export function useResumeFlowSpineInstance(processKey: string, instanceId?: string) {
  const queryClient = useQueryClient()
  return useMutation<FlowSpineResumeResponse, Error, { user_id?: string; action_label?: string }>({
    mutationFn: async (payload) => {
      if (!instanceId) throw new Error('instanceId fehlt')
      const res = await apiClient.post<FlowSpineResumeResponse>(
        `/api/v1/process/flow-spines/${processKey}/instances/${instanceId}/resume`,
        payload
      )
      return res.data
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['workflow', 'flow-spine', processKey] })
    },
  })
}

export function useFlowSpineLifecycleAction(
  processKey: string,
  instanceId: string | undefined,
  action: 'hold' | 'complete' | 'cancel' | 'fail',
) {
  const queryClient = useQueryClient()
  return useMutation<FlowSpineInstance, Error, FlowSpineLifecycleActionPayload>({
    mutationFn: async (payload) => {
      if (!instanceId) throw new Error('instanceId fehlt')
      const res = await apiClient.post<FlowSpineInstance>(
        `/api/v1/process/flow-spines/${processKey}/instances/${instanceId}/${action}`,
        payload
      )
      return res.data
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['workflow', 'flow-spine', processKey] })
    },
  })
}

export function useFlowSpineTimeline(processKey: string, instanceId?: string) {
  return useQuery<FlowSpineTimelineResponse>({
    queryKey: ['workflow', 'flow-spine', processKey, instanceId ?? '', 'timeline'],
    queryFn: async () => {
      const res = await apiClient.get<FlowSpineTimelineResponse>(
        `/api/v1/process/flow-spines/${processKey}/instances/${instanceId}/timeline`
      )
      return res.data
    },
    retry: false,
    enabled: !!processKey && !!instanceId,
  })
}

export function useExecuteFlowSpineAction() {
  return useMutation<unknown, Error, { apiPath: string; payload?: Record<string, unknown> }>({
    mutationFn: async ({ apiPath, payload }) => {
      const res = await apiClient.post(apiPath, payload ?? {})
      return res.data
    },
  })
}

export function useExecuteAgentAction(processKey: string) {
  const queryClient = useQueryClient()
  return useMutation<unknown, Error, { action: string; node_id?: string }>({
    mutationFn: async (payload) => {
      const res = await apiClient.post(
        `/api/v1/process/flow-spines/${processKey}/agent-action`,
        payload
      )
      return res.data
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['workflow', 'flow-spine', processKey] })
    },
  })
}

export function useDeleteFlowSpineInstance(processKey: string) {
  const queryClient = useQueryClient()
  return useMutation<void, Error, string>({
    mutationFn: async (instanceId) => {
      await apiClient.delete(
        `/api/v1/process/flow-spines/${processKey}/instances/${instanceId}`
      )
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['workflow', 'flow-spine', processKey] })
    },
  })
}

// ── Prefetch utilities ────────────────────────────────────────────────────────

/**
 * Prefetch a single workspace into the React Query cache.
 * Call on hover or before navigating to a flow-spine page.
 */
export function prefetchFlowSpineWorkspace(
  queryClient: ReturnType<typeof useQueryClient>,
  processKey: string,
  instanceId?: string,
): Promise<void> {
  const lang = getActiveLanguage()
  return queryClient.prefetchQuery({
    queryKey: getFlowSpineWorkspaceQueryKey(processKey, instanceId, lang),
    queryFn: () => fetchFlowSpineWorkspace(processKey, instanceId),
    staleTime: 5 * 60_000,
  })
}

const ALL_PROCESS_KEYS = [
  'order-to-cash',
  'procure-to-pay',
  'harvest-to-settlement',
  'inventory-to-settlement',
  'contract-to-settlement',
  'complaint-to-resolution',
  'service-to-customer',
  'finance-to-close',
  'compliance-to-report',
] as const

/**
 * Warm the cache for all 9 flow-spine workspaces in the background.
 * Call once on app init or after the catalog loads.
 * Uses staggered requests so it doesn't compete with user-visible fetches.
 */
export function warmFlowSpineCache(
  queryClient: ReturnType<typeof useQueryClient>,
): void {
  const lang = getActiveLanguage()
  // Stagger the prefetches to avoid a burst of 9 parallel requests
  ALL_PROCESS_KEYS.forEach((key, index) => {
    setTimeout(() => {
      void queryClient.prefetchQuery({
        queryKey: getFlowSpineWorkspaceQueryKey(key, undefined, lang),
        queryFn: () => fetchFlowSpineWorkspace(key),
        staleTime: 5 * 60_000,
      })
    }, index * 300) // 300ms stagger between each prefetch
  })
}
