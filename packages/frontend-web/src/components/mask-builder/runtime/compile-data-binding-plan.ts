import type { ScreenDataSource } from '../schema'
import type { RenderPlan } from '../render-plan/types'
import type { DataBindingPlan, EntityBinding, LookupBinding, TableBinding } from './types'
import { resolveEndpoint } from './data-source-resolver'

const DEFAULT_LOOKUP_MIN_CHARS = 2
const DEFAULT_LOOKUP_RESULT_LIMIT = 25
const DEFAULT_LOOKUP_CACHE_TTL_MS = 900_000
const DEFAULT_LOOKUP_DEBOUNCE_MS = 300

function makeVars(entityId?: string, tenantId?: string): Record<string, string> {
  const vars: Record<string, string> = {}
  if (entityId) vars['entity_id'] = entityId
  if (tenantId) vars['tenant_id'] = tenantId
  return vars
}

export function compileDataBindingPlan(
  plan: RenderPlan,
  dataSources: ScreenDataSource[] | undefined,
  tabEndpoints: Record<string, string> | undefined,
  entityId?: string,
  tenantId?: string,
): DataBindingPlan {
  const vars = makeVars(entityId, tenantId)
  const dsMap = new Map((dataSources ?? []).map((ds) => [ds.key, ds]))

  // Entity binding
  const entityDs = dsMap.get('entity')
  const entityBinding: EntityBinding = entityDs
    ? { entityId, entityEndpoint: resolveEndpoint(entityDs.endpoint, vars) }
    : {}

  // Table bindings
  const tableBindings: Record<string, TableBinding> = {}
  for (const [tableKey, tablePlan] of Object.entries(plan.tablesByKey)) {
    const ds = tablePlan.dataSourceKey ? dsMap.get(tablePlan.dataSourceKey) : undefined
    let endpoint = ds ? resolveEndpoint(ds.endpoint, vars) : undefined

    if (!endpoint && tablePlan.tabKey) {
      const tabEndpoint = tabEndpoints?.[tablePlan.tabKey] ?? tabEndpoints?.[tableKey]
      if (tabEndpoint) endpoint = tabEndpoint
    }

    if (!endpoint) {
      // No endpoint resolvable — mark as non-server-queried, log warning
      console.warn(`[mask-runtime] No endpoint for table "${tableKey}" in screen "${plan.screenId}"`)
    }

    tableBindings[tableKey] = {
      tableKey,
      endpoint: endpoint ?? '',
      // Every explicit table data source must be loaded. serverPagination
      // controls paging semantics, not whether the runtime fetches the table.
      requiresServerQuery: Boolean(endpoint),
      staleTimeMs: ds?.staleTimeMs,
    }
  }

  // Lookup bindings
  const lookupBindings: Record<string, LookupBinding> = {}
  for (const [fieldKey, fieldPlan] of Object.entries(plan.fieldsByKey)) {
    if (fieldPlan.componentKind !== 'lookup' || !fieldPlan.dataSourceKey) continue
    const ds = dsMap.get(fieldPlan.dataSourceKey)
    if (!ds) continue
    lookupBindings[fieldKey] = {
      fieldKey,
      lookupEndpoint: resolveEndpoint(ds.endpoint, vars),
      minSearchChars: ds.minSearchChars ?? fieldPlan.minSearchChars ?? DEFAULT_LOOKUP_MIN_CHARS,
      resultLimit: ds.pageSize ?? DEFAULT_LOOKUP_RESULT_LIMIT,
      cacheTtlMs: ds.staleTimeMs ?? DEFAULT_LOOKUP_CACHE_TTL_MS,
      debounceMs: DEFAULT_LOOKUP_DEBOUNCE_MS,
    }
  }

  // Action bindings (stub — endpoints wired in future phase)
  const actionBindings = Object.fromEntries(
    plan.actions.map((action) => [action.key, { actionKey: action.key }]),
  )

  return {
    screenId: plan.screenId,
    entityBinding,
    tableBindings,
    lookupBindings,
    actionBindings,
  }
}
