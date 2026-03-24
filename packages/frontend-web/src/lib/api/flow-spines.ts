import { apiClient } from '@/lib/api-client'

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

export async function fetchFlowSpineWorkspace(processKey: string): Promise<FlowSpineWorkspace> {
  const response = await apiClient.get<FlowSpineWorkspace>(`/api/v1/process/flow-spines/${processKey}`)
  return response.data
}

export async function fetchFlowSpineCatalog(): Promise<FlowSpineCatalog> {
  const response = await apiClient.get<FlowSpineCatalog>('/api/v1/process/flow-spines/catalog')
  return response.data
}
