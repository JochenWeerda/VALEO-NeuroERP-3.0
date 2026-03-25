import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
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
  process_key: string
  label: string
  created_at: string
  node_statuses: Record<string, string>
  active_node_id?: string
  linked_document_id?: string
  linked_document_type?: string
}

export interface CreateInstancePayload {
  label: string
  linked_document_id?: string
  linked_document_type?: string
}

export interface TransitionPayload {
  node_id: string
  new_status: FlowSpineTone
  action_label: string
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

// ── Plain fetch helpers (used by FlowSpineWorkspace via useQuery) ─────────────

export async function fetchFlowSpineWorkspace(processKey: string, instanceId?: string): Promise<FlowSpineWorkspace> {
  const lang = encodeURIComponent(getActiveLanguage())
  const query = new URLSearchParams({ lang })
  if (instanceId) {
    query.set('instance_id', instanceId)
  }
  const url = `/api/v1/process/flow-spines/${processKey}?${query.toString()}`
  const response = await apiClient.get<FlowSpineWorkspace>(url)
  return response.data
}

export async function fetchFlowSpineCatalog(): Promise<FlowSpineCatalog> {
  const lang = encodeURIComponent(getActiveLanguage())
  const response = await apiClient.get<FlowSpineCatalog>(`/api/v1/process/flow-spines/catalog?lang=${lang}`)
  return response.data
}

// ── React Query hooks ─────────────────────────────────────────────────────────

export function useFlowSpineWorkspace(processKey: string, instanceId?: string) {
  const lang = getActiveLanguage()
  return useQuery<FlowSpineWorkspace>({
    queryKey: ['workflow', 'flow-spine', processKey, instanceId ?? 'default', lang],
    queryFn: () => fetchFlowSpineWorkspace(processKey, instanceId),
    staleTime: 30_000,
    retry: false,
  })
}

export function useFlowSpineCatalogHook() {
  const lang = getActiveLanguage()
  return useQuery<FlowSpineCatalog>({
    queryKey: ['workflow', 'flow-spine', 'catalog', lang],
    queryFn: fetchFlowSpineCatalog,
    staleTime: 60_000,
    retry: false,
  })
}

/** Named alias matching the spec — delegates to useFlowSpineCatalogHook */
export function useFlowSpineCatalog() {
  return useFlowSpineCatalogHook()
}

export function useFlowSpineInstances(processKey: string) {
  return useQuery<FlowSpineInstance[]>({
    queryKey: ['workflow', 'flow-spine', processKey, 'instances'],
    queryFn: async () => {
      const res = await apiClient.get<FlowSpineInstance[]>(
        `/api/v1/process/flow-spines/${processKey}/instances`
      )
      return res.data
    },
    retry: false,
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
): Promise<void> {
  return queryClient.prefetchQuery({
    queryKey: ['workflow', 'flow-spine', processKey, 'default'],
    queryFn: () => fetchFlowSpineWorkspace(processKey),
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
  // Stagger the prefetches to avoid a burst of 9 parallel requests
  ALL_PROCESS_KEYS.forEach((key, index) => {
    setTimeout(() => {
      void queryClient.prefetchQuery({
        queryKey: ['workflow', 'flow-spine', key, 'default'],
        queryFn: () => fetchFlowSpineWorkspace(key),
        staleTime: 5 * 60_000,
      })
    }, index * 300) // 300ms stagger between each prefetch
  })
}
