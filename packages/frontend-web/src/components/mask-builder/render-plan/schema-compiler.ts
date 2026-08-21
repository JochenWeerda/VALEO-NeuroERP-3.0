import {
  resolveContextRailSections,
  type ScreenActionDefinition,
  type ScreenDefinition,
  type ScreenFieldDefinition,
  type ScreenTabDefinition,
  type ScreenTableDefinition,
  type ScreenTableProfile,
  type ScreenTileDefinition,
} from '../schema'
import { buildRenderPlanCacheKey, type CompileContext } from './compile-context'
import { globalRenderPlanCache } from './cache'
import { fieldTypeToComponentKind, type RenderActionPlan, type RenderCalendarPlan, type RenderFieldPlan, type RenderPlan, type RenderTabContentPlan, type RenderTabPlan, type RenderTablePlan, type RenderTilePlan, type RenderTwinPlan } from './types'

const DEFAULT_LOOKUP_MIN_CHARS = 2
const DEFAULT_LOOKUP_RESULT_LIMIT = 25
const DEFAULT_LOOKUP_CACHE_TTL_MS = 900_000
const DEFAULT_LOOKUP_DEBOUNCE_MS = 300
const DEFAULT_PAGE_SIZE = 25
const MAX_PAGE_SIZE = 50

function compileField(
  field: ScreenFieldDefinition,
  order: number,
  tabKey?: string,
  performanceLookupMinChars = DEFAULT_LOOKUP_MIN_CHARS,
): RenderFieldPlan {
  return {
    key: field.key,
    label: field.label,
    componentKind: fieldTypeToComponentKind(field.type),
    dataPath: field.key,
    tabKey,
    order,
    required: field.required ?? false,
    readOnly: field.readOnly ?? false,
    visible: true,
    placeholder: field.placeholder,
    helpText: field.helpText,
    options: field.options,
    dataSourceKey: field.dataSourceKey,
    minSearchChars: field.minSearchChars ?? performanceLookupMinChars,
    renderHint: field.renderHint,
  }
}

function compileTable(
  table: ScreenTableDefinition,
  tableProfile: ScreenTableProfile,
  tabKey?: string,
): RenderTablePlan {
  const pageSize = Math.min(table.pageSize ?? DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE)
  return {
    key: table.key,
    label: table.label,
    tabKey,
    columns: table.columns.map((column) => ({
      key: column.key,
      label: column.label,
      width: column.width,
      numeric: column.numeric,
      sortable: column.sortable,
      filterable: column.filterable,
      renderKind: column.renderKind,
      defaultSort: column.defaultSort,
    })),
    dataSourceKey: table.dataSourceKey,
    pageSize,
    virtualized: table.virtualized ?? true,
    rowHeight: table.rowHeight ?? 52,
    serverPagination: table.serverPagination ?? true,
    tableProfile,
    rowRouteTemplate: table.rowRouteTemplate,
    rowActions: table.rowActions,
  }
}

function filterVisibleTabs(
  tabs: ScreenTabDefinition[],
  availableTabs: string[] | undefined,
): ScreenTabDefinition[] {
  if (!availableTabs || availableTabs.length === 0) return tabs
  const allowed = new Set(availableTabs)
  return tabs.filter((tab) => allowed.has(tab.key))
}

function filterActionsByPermission(
  actions: ScreenActionDefinition[],
  permissions: string[],
): RenderActionPlan[] {
  return actions
    .filter((action) => !action.permission || permissions.includes(action.permission))
    .map((action) => ({
      key: action.key,
      label: action.label,
      kind: action.kind ?? 'secondary',
      disabled: action.disabled ?? false,
      dangerLevel: action.dangerLevel,
      requiresConfirmation: action.requiresConfirmation,
      auditReasonRequired: action.auditReasonRequired,
      humanApprovalRequired: action.humanApprovalRequired,
      zone: action.zone ?? 'header',
      keyboardShortcut: action.keyboardShortcut,
    }))
}

/**
 * Kompiliert cockpit-Kacheln (UIX-061): baut die Ziel-Route inkl. Filter-Query.
 * Die Reihenfolge kommt bereits saisonal sortiert vom Backend; Kacheln ohne
 * aufgeloeste targetRoute werden verworfen (kein toter Link).
 */
export function compileTiles(schema: ScreenDefinition): RenderTilePlan[] {
  const tiles: ScreenTileDefinition[] = schema.tiles ?? []
  const plans: RenderTilePlan[] = []
  for (const tile of tiles) {
    const base = tile.targetRoute ?? ''
    if (!base) continue
    const filters = tile.targetFilters ?? {}
    const query = new URLSearchParams(filters).toString()
    plans.push({
      key: tile.key,
      label: tile.label,
      targetScreenId: tile.targetScreenId,
      targetPath: query ? `${base}${base.includes('?') ? '&' : '?'}${query}` : base,
      countEndpoint: tile.countEndpoint,
      tone: tile.tone ?? 'neutral',
    })
  }
  return plans
}

export function compileCalendar(schema: ScreenDefinition): RenderCalendarPlan | undefined {
  const calendar = schema.calendar
  if (!calendar?.endpoint || calendar.layers.length === 0) return undefined
  return {
    endpoint: calendar.endpoint,
    reprojectEndpoint: calendar.reprojectEndpoint,
    icsTokenEndpoint: calendar.icsTokenEndpoint,
    defaultView: calendar.defaultView ?? 'agenda',
    deadlineBandDays: calendar.deadlineBandDays ?? 14,
    layers: calendar.layers.map((layer) => ({
      key: layer.key,
      label: layer.label,
      defaultVisible: layer.defaultVisible ?? true,
    })),
  }
}

export function compileTwin(schema: ScreenDefinition): RenderTwinPlan | undefined {
  const twin = schema.twin
  if (!twin?.endpoint) return undefined
  return {
    endpoint: twin.endpoint,
    planId: twin.planId ?? schema.id,
    cacheTtlSeconds: twin.cacheTtlSeconds ?? 30,
    activateRouteTemplate: twin.activateRouteTemplate ?? '/lager/silo-zellen/{cellId}',
    activateScreenId: twin.activateScreenId,
    metrics: twin.metrics ?? [
      { key: 'fill_pct', label: 'Fuellstand', kind: 'percent', warnAbove: 90 },
      { key: 'locked', label: 'Gesperrt', kind: 'flag' },
      { key: 'qs_status', label: 'QS', kind: 'status' },
    ],
  }
}

export function compileRenderPlan(
  schema: ScreenDefinition,
  context: CompileContext,
): RenderPlan {
  const cacheKey = buildRenderPlanCacheKey(context)
  const cached = globalRenderPlanCache.get(cacheKey)
  if (cached && cached.screenId === schema.id) {
    return cached
  }

  const lookupMinChars =
    schema.performance?.lookupMinChars ?? DEFAULT_LOOKUP_MIN_CHARS
  const floorplan = schema.layout?.floorplan ?? (
    schema.mode === 'list' ? 'worklist' :
    schema.mode === 'cockpit' ? 'cockpit' :
    schema.mode === 'wizard' ? 'wizard' :
    schema.mode === 'workflow' ? 'transaction' :
    'objectPage'
  )
  const density = schema.layout?.density ?? 'compact'
  const contextRail = schema.layout?.contextRail ?? (floorplan === 'worklist' ? 'none' : 'combined')
  const contextRailSections = resolveContextRailSections(contextRail, schema.layout?.contextRailSections)
  const tableProfile = schema.layout?.tableProfile ?? 'standard'
  const performance = {
    initialPayloadBudgetKb: schema.performance?.initialPayloadBudgetKb ?? 64,
    requiresLazyTabs: schema.performance?.requiresLazyTabs ?? true,
    requiresVirtualTables: schema.performance?.requiresVirtualTables ?? true,
    lookupMinChars,
    lookupResultLimit: DEFAULT_LOOKUP_RESULT_LIMIT,
    lookupCacheTtlMs: DEFAULT_LOOKUP_CACHE_TTL_MS,
    lookupDebounceMs: DEFAULT_LOOKUP_DEBOUNCE_MS,
  }

  const fieldsByKey: Record<string, RenderFieldPlan> = {}
  const fieldsByTab: Record<string, RenderFieldPlan[]> = {}
  const tablesByKey: Record<string, RenderTablePlan> = {}
  const tablesByTab: Record<string, RenderTablePlan[]> = {}
  const tabContent: Record<string, RenderTabContentPlan> = {}

  const rootFields = (schema.fields ?? []).map((field, index) =>
    compileField(field, index, undefined, lookupMinChars),
  )
  for (const field of rootFields) {
    fieldsByKey[field.key] = field
  }

  const rootTables = (schema.tables ?? []).map((table) => compileTable(table, tableProfile))
  for (const table of rootTables) {
    tablesByKey[table.key] = table
  }

  const visibleTabDefs = filterVisibleTabs(schema.tabs ?? [], context.summary?.availableTabs)
  const visibleTabs: RenderTabPlan[] = visibleTabDefs.map((tab, index) => ({
    key: tab.key,
    label: tab.label,
    lazy: tab.lazy ?? true,
    keepAlive: tab.keepAlive ?? true,
    order: index,
  }))

  for (const tab of visibleTabDefs) {
    const tabFields = (tab.fields ?? []).map((field, index) =>
      compileField(field, index, tab.key, lookupMinChars),
    )
    fieldsByTab[tab.key] = tabFields
    for (const field of tabFields) {
      fieldsByKey[field.key] = field
    }

    const tabTables = (tab.tables ?? []).map((table) => compileTable(table, tableProfile, tab.key))
    tablesByTab[tab.key] = tabTables
    for (const table of tabTables) {
      tablesByKey[table.key] = table
    }

    tabContent[tab.key] = {
      tabKey: tab.key,
      fieldKeys: tabFields.map((field) => field.key),
      tableKeys: tabTables.map((table) => table.key),
    }
  }

  const plan: RenderPlan = {
    cacheKey,
    screenId: schema.id,
    schemaVersion: context.schemaVersion,
    shell: {
      title: context.summary?.title ?? schema.title,
      subtitle: context.summary?.subtitle ?? schema.subtitle,
      domain: schema.domain,
      mode: schema.mode,
      layoutMode: schema.layout?.preferredMode ?? 'desktopDense',
      mobileMode: schema.layout?.mobileMode ?? 'mobileStack',
      touchTargetPx: schema.layout?.touchTargetPx ?? 44,
      floorplan,
      density,
      contextRail,
      contextRailSections,
      tableProfile,
      summaryPlacement: schema.layout?.summaryPlacement ?? 'header',
      stickyHeader: schema.layout?.stickyHeader ?? false,
      stickyFooter: schema.layout?.stickyFooter ?? false,
      summaryEndpoint: schema.summaryEndpoint,
      voice: {
        enabled: schema.voice?.enabled ?? true,
        provider: schema.voice?.provider ?? 'webspeech',
      },
    },
    summarySlots: (context.summary?.summaryItems ?? schema.summary ?? []).map((item) => ({
      key: item.key,
      label: item.label,
      tone: item.tone,
    })),
    summaryItems: context.summary?.summaryItems ?? schema.summary ?? [],
    tiles: compileTiles(schema),
    calendar: compileCalendar(schema),
    twin: compileTwin(schema),
    visibleTabs,
    tabContent,
    rootFieldKeys: rootFields.map((field) => field.key),
    fieldsByKey,
    fieldsByTab,
    rootTableKeys: rootTables.map((table) => table.key),
    tablesByKey,
    tablesByTab,
    actions: filterActionsByPermission(schema.actions ?? [], context.auth.permissions),
    interaction: {
      enterMovesFocus: schema.interaction?.enterMovesFocus ?? false,
    },
    workflow: schema.workflow
      ? {
          processKey: schema.workflow.processKey,
          status: schema.workflow.status,
          nextActionKey: schema.workflow.nextActionKey,
          auditRequired: schema.workflow.auditRequired,
          evidenceRequired: schema.workflow.evidenceRequired,
        }
      : undefined,
    performance,
  }

  globalRenderPlanCache.set(cacheKey, plan)
  return plan
}

export function compileRenderPlanFromScreenDefinition(
  schema: ScreenDefinition,
  options: {
    permissions?: string[]
    availableTabs?: string[]
    summaryItems?: CompileContext['summary']
    tenantId?: string
    roleHash?: string
    featureFlags?: Record<string, boolean>
  } = {},
): RenderPlan {
  return compileRenderPlan(schema, {
    screenId: schema.id,
    schemaVersion: schema.schemaVersion,
    summary: {
      title: options.summaryItems?.title ?? schema.title,
      subtitle: options.summaryItems?.subtitle ?? schema.subtitle,
      availableTabs: options.availableTabs,
      summaryItems: options.summaryItems?.summaryItems ?? schema.summary,
      tabEndpoints: options.summaryItems?.tabEndpoints,
    },
    auth: {
      tenantId: options.tenantId,
      roleHash: options.roleHash,
      permissions: options.permissions ?? schema.permissions ?? [],
    },
    featureFlags: { flags: options.featureFlags },
  })
}

export function invalidateRenderPlanCache(cacheKey?: string): void {
  globalRenderPlanCache.invalidate(cacheKey)
}
