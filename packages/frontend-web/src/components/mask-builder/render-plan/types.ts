import type {
  ScreenDomain,
  ScreenCalendarView,
  ScreenContextRail,
  ScreenContextRailSection,
  ScreenDensity,
  ScreenFieldType,
  ScreenFloorplan,
  ScreenLayoutMode,
  ScreenMode,
  ScreenSummaryItem,
  ScreenSummaryPlacement,
  ScreenActionZone,
  ScreenTableProfile,
  ScreenTwinMetricKind,
  ScreenVoiceProvider,
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
  contextRailSections: ScreenContextRailSection[]
  tableProfile: ScreenTableProfile
  summaryPlacement: ScreenSummaryPlacement
  stickyHeader: boolean
  stickyFooter: boolean
  summaryEndpoint?: string
  voice?: {
    enabled: boolean
    provider: ScreenVoiceProvider
  }
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

export interface RenderCalendarLayerPlan {
  key: string
  label: string
  defaultVisible: boolean
}

export interface RenderCalendarPlan {
  endpoint: string
  reprojectEndpoint?: string
  icsTokenEndpoint?: string
  defaultView: ScreenCalendarView
  deadlineBandDays: number
  layers: RenderCalendarLayerPlan[]
}

export interface RenderTwinMetricPlan {
  key: string
  label: string
  kind: ScreenTwinMetricKind
  warnAbove?: number
}

export interface RenderTwinPlan {
  endpoint: string
  planId: string
  cacheTtlSeconds: number
  activateRouteTemplate: string
  activateScreenId?: string
  metrics: RenderTwinMetricPlan[]
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

export interface RenderTableVariant {
  key: string
  label: string
  filters?: Record<string, string>
}

export interface RenderTablePlan {
  key: string
  label: string
  tabKey?: string
  columns: RenderTableColumnPlan[]
  /** Vollstaendige Spaltenbasis fuer Nutzer-Overlays; `columns` kann gefiltert sein. */
  availableColumns?: RenderTableColumnPlan[]
  dataSourceKey?: string
  pageSize: number
  virtualized: boolean
  rowHeight: number
  serverPagination: boolean
  tableProfile: ScreenTableProfile
  rowRouteTemplate?: string
  rowActions?: Array<{
    key: string
    label: string
    dangerLevel?: 'safe' | 'moderate' | 'high' | 'critical' | 'destructive'
    visibleWhen?: { field: string; values: Array<string | number | boolean> }
  }>
  bulkActions?: Array<{
    key: string
    label: string
    dangerLevel?: 'safe' | 'moderate' | 'high' | 'critical' | 'destructive'
  }>
  /** Aktive Nutzer-Variante (UIX-071 Overlay) */
  activeVariant?: string
  /** Nutzer-definierte Varianten (UIX-071 Overlay) */
  customVariants?: RenderTableVariant[]
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
  zone: ScreenActionZone
  keyboardShortcut?: string
}

export interface RenderInteractionPlan {
  enterMovesFocus: boolean
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
  calendar?: RenderCalendarPlan
  twin?: RenderTwinPlan
  visibleTabs: RenderTabPlan[]
  tabContent: Record<string, RenderTabContentPlan>
  rootFieldKeys: string[]
  fieldsByKey: Record<string, RenderFieldPlan>
  fieldsByTab: Record<string, RenderFieldPlan[]>
  rootTableKeys: string[]
  tablesByKey: Record<string, RenderTablePlan>
  tablesByTab: Record<string, RenderTablePlan[]>
  actions: RenderActionPlan[]
  interaction: RenderInteractionPlan
  workflow?: RenderWorkflowPlan
  performance: RenderPerformancePlan
  /** Vom Nutzer eingeklappte Sektionen (UIX-071 Overlay) */
  collapsedSections?: string[]
  /** Overlay-Keys ohne Entsprechung im Plan → Rail-Hinweis "Anpassung pruefen" (UIX-071) */
  overlayInvalidPaths?: string[]
}

export function fieldTypeToComponentKind(type: ScreenFieldType): RenderComponentKind {
  if (type === 'table') return 'text'
  return type
}
