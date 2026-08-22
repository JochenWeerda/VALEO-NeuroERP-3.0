import type { ReactNode } from 'react'

export type ScreenDomain =
  | 'crm'
  | 'sales'
  | 'inventory'
  | 'finance'
  | 'agrar'
  | 'einkauf'
  | 'lager'
  | 'qualitaet'
  | 'futtermittel'
  | 'procurement'
  | 'logistics'
  | 'hr'
  | 'platform'

export type ScreenMode = 'list' | 'detail' | 'cockpit' | 'workflow' | 'wizard'
export type ScreenLayoutMode = 'desktopDense' | 'tabletTouch' | 'mobileStack'
export type ScreenFloorplan = 'worklist' | 'objectPage' | 'transaction' | 'cockpit' | 'wizard'
export type ScreenDensity = 'comfortable' | 'compact' | 'expertDense'
export type ScreenContextRail = 'none' | 'audit' | 'copilot' | 'workflow' | 'combined'
export type ScreenContextRailSection = 'audit' | 'workflow' | 'copilot' | 'collab'
export type ScreenTableProfile = 'standard' | 'financial' | 'inventory' | 'audit'
export type ScreenSummaryPlacement = 'header' | 'footer'
export type ScreenActionZone = 'header' | 'footer' | 'commit'
export type ScreenVoiceProvider = 'webspeech' | 'server'
export type ScreenAdapterType = 'native' | 'maskConfig' | 'crmMaskJson' | 'formSchema' | 'specialized'
export type ScreenFieldType =
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
  | 'table'
  | 'currency'
  | 'percentage'

export interface ScreenDataSource {
  key: string
  endpoint: string
  method?: 'GET' | 'POST'
  staleTimeMs?: number
  pageSize?: number
  searchParam?: string
  minSearchChars?: number
}

export interface ScreenFieldDefinition {
  key: string
  label: string
  type: ScreenFieldType
  required?: boolean
  readOnly?: boolean
  placeholder?: string
  helpText?: string
  options?: Array<{ value: string | number; label: string }>
  dataSourceKey?: string
  minSearchChars?: number
  renderHint?: 'singleLine' | 'multiLine' | 'compact' | 'touch'
}

export type ScreenColumnRenderKind =
  | 'text'
  | 'number'
  | 'currency'
  | 'date'
  | 'datetime'
  | 'status'
  | 'boolean'

export interface ScreenTableColumn {
  key: string
  label: string
  width?: number
  numeric?: boolean
  sortable?: boolean
  filterable?: boolean
  renderKind?: ScreenColumnRenderKind
  defaultSort?: 'asc' | 'desc'
  render?: (_value: unknown, _row: Record<string, unknown>) => ReactNode
}

export interface ScreenTableDefinition {
  key: string
  label: string
  columns: ScreenTableColumn[]
  dataSourceKey?: string
  pageSize?: number
  virtualized?: boolean
  rowHeight?: number
  serverPagination?: boolean
  /** Declarative row navigation; placeholders such as {id} resolve from row data. */
  rowRouteTemplate?: string
  /** Central, data-driven row actions; rendered by FastTableRenderer. */
  rowActions?: Array<{
    key: string
    label: string
    dangerLevel?: ActionDangerLevel
    visibleWhen?: { field: string; values: Array<string | number | boolean> }
  }>
  /** Selection-based actions; payload contains selectedRows and selectedIds. */
  bulkActions?: Array<{
    key: string
    label: string
    dangerLevel?: ActionDangerLevel
  }>
}

export type ActionDangerLevel = 'safe' | 'moderate' | 'high' | 'critical' | 'destructive'

export interface ScreenActionDefinition {
  key: string
  label: string
  kind?: 'primary' | 'secondary' | 'danger' | 'workflow'
  permission?: string
  disabled?: boolean
  // Action Runtime (Phase 026)
  commandEndpoint?: string
  stubReason?: string
  method?: 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  requiresConfirmation?: boolean
  dangerLevel?: ActionDangerLevel
  idempotencyKey?: string
  auditReasonRequired?: boolean
  humanApprovalRequired?: boolean
  forbiddenForAgents?: boolean
  /** Visual work zone. Defaults to the header for backwards compatibility. */
  zone?: ScreenActionZone
  /** Declarative, screen-local shortcut such as Ctrl+S, Ctrl+P, Escape or F4. */
  keyboardShortcut?: string
}

/** Agent-readable contract for a single screen.
 *  Derived from ScreenDefinition but explicitly versioned for AI consumers. */
export interface AgentMaskContract {
  screenId: string
  domain: ScreenDomain
  schemaVersion: number
  contractVersion: 1
  businessPurpose: string
  primaryEntity: string
  readableFields: string[]
  editableFields: string[]
  sensitiveFields: string[]
  availableActions: Array<{
    key: string
    label: string
    dangerLevel: ActionDangerLevel
    requiresHumanApproval: boolean
    requiresConfirmation: boolean
    permission?: string
  }>
  validationRules: Array<{
    fieldKey: string
    rule: string
    severity: 'blocking' | 'warning' | 'info'
  }>
  workflowRules: Array<{
    fromStatus: string
    toStatus: string
    requiredActions: string[]
    blockedBy?: string[]
  }>
  auditRequirements: Array<{
    actionKey: string
    requiresReason: boolean
    requiresEvidence: boolean
  }>
  recommendedAgentTasks: string[]
  forbiddenAgentTasks: string[]
  testSelectors: Record<string, string>
  examplePrompts: string[]
}

export interface ScreenTabDefinition {
  key: string
  label: string
  lazy?: boolean
  keepAlive?: boolean
  fields?: ScreenFieldDefinition[]
  tables?: ScreenTableDefinition[]
  dataSourceKeys?: string[]
}

export interface ScreenSummaryItem {
  key: string
  label: string
  value: string | number | boolean | null
  tone?: 'neutral' | 'success' | 'warning' | 'danger'
  details?: {
    components?: Array<{
      key: string
      label?: string
      value?: string | number | boolean | null
      co2e_kg?: number
      source_ref?: string
      source?: string
    }>
  }
}

export interface ScreenWorkflowDefinition {
  processKey?: string
  status?: string
  nextActionKey?: string
  auditRequired?: boolean
  evidenceRequired?: boolean
}

/** Worklist-Kachel eines cockpit-Workspaces (UIX-061). */
export interface ScreenTileDefinition {
  key: string
  label: string
  /** Ziel-Maske; das Backend loest targetRoute daraus auf. */
  targetScreenId: string
  /** Vom Backend aufgeloeste Listen-Route (Omnibox-Routen-Bruecke). */
  targetRoute?: string
  /** Query-Filter, die beim Navigieren angehaengt werden. */
  targetFilters?: Record<string, string>
  /** Optionaler Zaehler-Endpoint (count_only); fehlt → reine Navigations-Kachel. */
  countEndpoint?: string
  tone?: 'neutral' | 'warning' | 'danger'
}

/** Saison-Profil: sortiert Kacheln im aktiven Fenster um (kein Inhaltswechsel). */
export interface ScreenSeasonProfile {
  activeFrom?: string
  activeTo?: string
  tileOrderOverride?: string[]
}

export type ScreenCalendarView = 'month' | 'week' | 'agenda'

export interface ScreenCalendarLayerDefinition {
  key: 'finanzen' | 'fristen' | 'crm' | 'logistik' | 'personal' | 'saison'
  label: string
  defaultVisible?: boolean
}

/** Planungskalender-Primitive (UIX-063): Zeitprojektion aus Read-Models. */
export interface ScreenCalendarDefinition {
  endpoint: string
  reprojectEndpoint?: string
  icsTokenEndpoint?: string
  defaultView?: ScreenCalendarView
  deadlineBandDays?: number
  layers: ScreenCalendarLayerDefinition[]
}

export type ScreenTwinMetricKind = 'percent' | 'number' | 'flag' | 'status'

export interface ScreenTwinMetricDefinition {
  key: string
  label: string
  kind: ScreenTwinMetricKind
  warnAbove?: number
}

/** Twin-Panel-Primitive (UIX-081): physische Belegungsansicht aus Read-Model. */
export interface ScreenTwinDefinition {
  endpoint: string
  planId?: string
  cacheTtlSeconds?: number
  activateRouteTemplate?: string
  activateScreenId?: string
  metrics?: ScreenTwinMetricDefinition[]
}

const CONTEXT_RAIL_SECTIONS: ScreenContextRailSection[] = ['audit', 'workflow', 'copilot', 'collab']

export function resolveContextRailSections(
  contextRail: ScreenContextRail = 'combined',
  explicitSections?: ScreenContextRailSection[],
): ScreenContextRailSection[] {
  if (explicitSections && explicitSections.length > 0) {
    const seen = new Set<ScreenContextRailSection>()
    return explicitSections.filter((section) => {
      if (!CONTEXT_RAIL_SECTIONS.includes(section) || seen.has(section)) return false
      seen.add(section)
      return true
    })
  }
  if (contextRail === 'none') return []
  if (contextRail === 'audit') return ['audit']
  if (contextRail === 'workflow') return ['workflow']
  if (contextRail === 'copilot') return ['copilot']
  return ['workflow', 'audit', 'copilot']
}

export interface ScreenDefinition {
  schemaVersion: 1
  id: string
  domain: ScreenDomain
  mode: ScreenMode
  title: string
  subtitle?: string
  permissions?: string[]
  adapter?: {
    type: ScreenAdapterType
    sourceId?: string
    temporary: boolean
    deprecationTarget?: string
  }
  summaryEndpoint?: string
  summary?: ScreenSummaryItem[]
  dataSources?: ScreenDataSource[]
  fields?: ScreenFieldDefinition[]
  tabs?: ScreenTabDefinition[]
  tables?: ScreenTableDefinition[]
  tiles?: ScreenTileDefinition[]
  calendar?: ScreenCalendarDefinition
  twin?: ScreenTwinDefinition
  voice?: {
    enabled?: boolean
    provider?: ScreenVoiceProvider
  }
  seasonProfile?: ScreenSeasonProfile
  actions?: ScreenActionDefinition[]
  interaction?: {
    /** ERP desktop flow: Enter advances to the next eligible form control. */
    enterMovesFocus?: boolean
  }
  workflow?: ScreenWorkflowDefinition
  layout?: {
    preferredMode?: ScreenLayoutMode
    mobileMode?: ScreenLayoutMode
    touchTargetPx?: number
    floorplan?: ScreenFloorplan
    density?: ScreenDensity
    contextRail?: ScreenContextRail
    contextRailSections?: ScreenContextRailSection[]
    tableProfile?: ScreenTableProfile
    summaryPlacement?: ScreenSummaryPlacement
    stickyHeader?: boolean
    stickyFooter?: boolean
  }
  performance?: {
    initialPayloadBudgetKb?: number
    requiresLazyTabs?: boolean
    requiresVirtualTables?: boolean
    lookupMinChars?: number
    bundleGroup?: string
  }
  agentContract?: AgentMaskContract
}

export function validateScreenDefinition(screen: ScreenDefinition): string[] {
  const errors: string[] = []

  if (screen.schemaVersion !== 1) errors.push('schemaVersion must be 1')
  if (!screen.id) errors.push('id is required')
  if (!screen.domain) errors.push('domain is required')
  if (!screen.mode) errors.push('mode is required')
  if (!screen.title) errors.push('title is required')

  if (screen.layout?.floorplan && !['worklist', 'objectPage', 'transaction', 'cockpit', 'wizard'].includes(screen.layout.floorplan)) {
    errors.push(`layout.floorplan is invalid: ${screen.layout.floorplan}`)
  }
  if (screen.layout?.density && !['comfortable', 'compact', 'expertDense'].includes(screen.layout.density)) {
    errors.push(`layout.density is invalid: ${screen.layout.density}`)
  }
  if (screen.layout?.contextRail && !['none', 'audit', 'copilot', 'workflow', 'combined'].includes(screen.layout.contextRail)) {
    errors.push(`layout.contextRail is invalid: ${screen.layout.contextRail}`)
  }
  for (const section of screen.layout?.contextRailSections ?? []) {
    if (!CONTEXT_RAIL_SECTIONS.includes(section)) {
      errors.push(`layout.contextRailSections contains invalid section: ${section}`)
    }
  }
  if (screen.layout?.tableProfile && !['standard', 'financial', 'inventory', 'audit'].includes(screen.layout.tableProfile)) {
    errors.push(`layout.tableProfile is invalid: ${screen.layout.tableProfile}`)
  }
  if (screen.layout?.summaryPlacement && !['header', 'footer'].includes(screen.layout.summaryPlacement)) {
    errors.push(`layout.summaryPlacement is invalid: ${screen.layout.summaryPlacement}`)
  }
  const shortcuts = new Set<string>()
  for (const action of screen.actions ?? []) {
    if (action.zone && !['header', 'footer', 'commit'].includes(action.zone)) {
      errors.push(`action ${action.key} has invalid zone: ${action.zone}`)
    }
    const shortcut = action.keyboardShortcut?.trim().toLowerCase()
    if (action.keyboardShortcut !== undefined && !shortcut) {
      errors.push(`action ${action.key} has an empty keyboardShortcut`)
    } else if (shortcut && shortcuts.has(shortcut)) {
      errors.push(`keyboardShortcut is duplicated: ${action.keyboardShortcut}`)
    } else if (shortcut) {
      shortcuts.add(shortcut)
    }
  }
  if (screen.twin && !screen.twin.endpoint) {
    errors.push('twin.endpoint is required')
  }
  for (const metric of screen.twin?.metrics ?? []) {
    if (!metric.key) errors.push('twin.metrics.key is required')
    if (!metric.label) errors.push(`twin metric ${metric.key || '<unknown>'} requires label`)
    if (!['percent', 'number', 'flag', 'status'].includes(metric.kind)) {
      errors.push(`twin metric ${metric.key || '<unknown>'} has invalid kind: ${metric.kind}`)
    }
  }

  for (const tab of screen.tabs ?? []) {
    if (!tab.key) errors.push('tab.key is required')
    if (!tab.label) errors.push(`tab ${tab.key || '<unknown>'} requires label`)
  }

  for (const table of screen.tables ?? []) {
    if (table.virtualized === true && (table.pageSize ?? 0) > 100) {
      errors.push(`table ${table.key} pageSize must stay <= 100 for generator v1`)
    }
  }

  return errors
}
