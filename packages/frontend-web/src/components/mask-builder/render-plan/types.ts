import type {
  ScreenDomain,
  ScreenContextRail,
  ScreenDensity,
  ScreenFieldType,
  ScreenFloorplan,
  ScreenLayoutMode,
  ScreenMode,
  ScreenSummaryItem,
  ScreenTableProfile,
} from '../schema'

export type RenderComponentKind =
  | 'text'
  | 'number'
  | 'date'
  | 'datetime'
  | 'boolean'
  | 'select'
  | 'multiselect'
  | 'textarea'
  | 'file'
  | 'lookup'
  | 'currency'
  | 'percentage'

export interface RenderShellPlan {
  title: string
  subtitle?: string
  domain: ScreenDomain
  mode: ScreenMode
  layoutMode: ScreenLayoutMode
  mobileMode: ScreenLayoutMode
  touchTargetPx: number
  floorplan: ScreenFloorplan
  density: ScreenDensity
  contextRail: ScreenContextRail
  tableProfile: ScreenTableProfile
  summaryEndpoint?: string
}

export interface RenderSummarySlot {
  key: string
  label: string
  tone?: 'neutral' | 'success' | 'warning' | 'danger'
}

export interface RenderTabPlan {
  key: string
  label: string
  lazy: boolean
  keepAlive: boolean
  order: number
}

/** Kompilierte cockpit-Kachel (UIX-061) — navigierbar, optional mit Zaehler. */
export interface RenderTilePlan {
  key: string
  label: string
  /** Aufgeloeste Ziel-Route inkl. angehaengter Filter-Query. */
  targetPath: string
  targetScreenId: string
  countEndpoint?: string
  tone: 'neutral' | 'warning' | 'danger'
}

export interface RenderTabContentPlan {
  tabKey: string
  fieldKeys: string[]
  tableKeys: string[]
}

export interface RenderFieldPlan {
  key: string
  label: string
  componentKind: RenderComponentKind
  dataPath: string
  tabKey?: string
  order: number
  required: boolean
  readOnly: boolean
  visible: boolean
  placeholder?: string
  helpText?: string
  options?: Array<{ value: string | number; label: string }>
  dataSourceKey?: string
  minSearchChars: number
  renderHint?: 'singleLine' | 'multiLine' | 'compact' | 'touch'
}

export type RenderColumnKind =
  | 'text'
  | 'number'
  | 'currency'
  | 'date'
  | 'datetime'
  | 'status'
  | 'boolean'

export interface RenderTableColumnPlan {
  key: string
  label: string
  width?: number
  numeric?: boolean
  sortable?: boolean
  filterable?: boolean
  renderKind?: RenderColumnKind
  defaultSort?: 'asc' | 'desc'
}

export interface RenderTablePlan {
  key: string
  label: string
  tabKey?: string
  columns: RenderTableColumnPlan[]
  dataSourceKey?: string
  pageSize: number
  virtualized: boolean
  rowHeight: number
  serverPagination: boolean
  tableProfile: ScreenTableProfile
}

export interface RenderActionPlan {
  key: string
  label: string
  kind: 'primary' | 'secondary' | 'danger' | 'workflow'
  disabled: boolean
  dangerLevel?: 'safe' | 'moderate' | 'high' | 'critical' | 'destructive'
  requiresConfirmation?: boolean
  auditReasonRequired?: boolean
  humanApprovalRequired?: boolean
}

export interface RenderWorkflowPlan {
  processKey?: string
  status?: string
  nextActionKey?: string
  auditRequired?: boolean
  evidenceRequired?: boolean
}

export interface RenderPerformancePlan {
  initialPayloadBudgetKb: number
  requiresLazyTabs: boolean
  requiresVirtualTables: boolean
  lookupMinChars: number
  lookupResultLimit: number
  lookupCacheTtlMs: number
  lookupDebounceMs: number
}

export interface RenderPlan {
  cacheKey: string
  screenId: string
  schemaVersion: number
  shell: RenderShellPlan
  summarySlots: RenderSummarySlot[]
  summaryItems: ScreenSummaryItem[]
  tiles: RenderTilePlan[]
  visibleTabs: RenderTabPlan[]
  tabContent: Record<string, RenderTabContentPlan>
  rootFieldKeys: string[]
  fieldsByKey: Record<string, RenderFieldPlan>
  fieldsByTab: Record<string, RenderFieldPlan[]>
  rootTableKeys: string[]
  tablesByKey: Record<string, RenderTablePlan>
  tablesByTab: Record<string, RenderTablePlan[]>
  actions: RenderActionPlan[]
  workflow?: RenderWorkflowPlan
  performance: RenderPerformancePlan
}

export function fieldTypeToComponentKind(type: ScreenFieldType): RenderComponentKind {
  if (type === 'table') return 'text'
  return type
}
