import type { ReactNode } from 'react'

export type ScreenDomain =
  | 'crm'
  | 'sales'
  | 'inventory'
  | 'finance'
  | 'agrar'
  | 'procurement'
  | 'logistics'
  | 'hr'
  | 'platform'

export type ScreenMode = 'list' | 'detail' | 'cockpit' | 'workflow' | 'wizard'
export type ScreenLayoutMode = 'desktopDense' | 'tabletTouch' | 'mobileStack'
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
}

export type ActionDangerLevel = 'safe' | 'moderate' | 'destructive'

export interface ScreenActionDefinition {
  key: string
  label: string
  kind?: 'primary' | 'secondary' | 'danger'
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
}

export interface ScreenWorkflowDefinition {
  processKey?: string
  status?: string
  nextActionKey?: string
  auditRequired?: boolean
  evidenceRequired?: boolean
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
  actions?: ScreenActionDefinition[]
  workflow?: ScreenWorkflowDefinition
  layout?: {
    preferredMode?: ScreenLayoutMode
    mobileMode?: ScreenLayoutMode
    touchTargetPx?: number
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
