/**
 * Phases 030 + 033 — Generator Readiness Gates
 *
 * A ScreenDefinition is `generator_ready` only when ALL mandatory gates are green.
 *
 * Mandatory gates (block generatorReady):
 *  1. schema_valid           — validateScreenDefinition passes
 *  2. non_temporary          — adapter.temporary !== true
 *  3. data_sources           — dataSources defined when server-pagination tables exist
 *  4. table_data_source_bound — every serverPagination table has a matching dataSource
 *  5. table_columns_complete  — every table has ≥2 non-trivial columns
 *  6. actions_classified      — every action has dangerLevel + permission OR explicit stubReason
 *
 * Advisory gates (reported but do NOT block generatorReady):
 *  7. sort_whitelist          — at least one sortable column per table (advisory)
 *  8. filter_columns          — at least one filterable column per table (advisory)
 *  9. agent_contract          — explicit agentContract (advisory; auto-generated is acceptable)
 * 10. workflow_declared        — process screens declare workflow or explicit noWorkflowReason
 * 11. stable_test_selectors   — screenRoot, submitButton, workflowPanel selectors present
 * 12. table_query_contract    — sortable/filterable columns use stable, non-generic keys
 */

import { validateScreenDefinition, type ScreenDefinition, type ScreenTableDefinition } from '../schema'

export type ReadinessGate =
  // mandatory
  | 'schema_valid'
  | 'non_temporary'
  | 'data_sources'
  | 'table_data_source_bound'
  | 'table_columns_complete'
  | 'actions_classified'
  // advisory
  | 'sort_whitelist'
  | 'filter_columns'
  | 'agent_contract'
  | 'workflow_declared'
  | 'stable_test_selectors'
  | 'table_query_contract'

export type GateSeverity = 'mandatory' | 'advisory'

export interface GateResult {
  gate: ReadinessGate
  severity: GateSeverity
  passed: boolean
  detail: string
}

export interface GeneratorReadinessReport {
  screenId: string
  /** true only when all MANDATORY gates pass */
  generatorReady: boolean
  /** advisory score 0–1 (fraction of advisory gates passed) */
  advisoryScore: number
  gates: GateResult[]
  /** errors from mandatory failed gates */
  errors: string[]
  /** warnings from advisory failed gates */
  warnings: string[]
}

function collectAllTables(screen: ScreenDefinition): ScreenTableDefinition[] {
  const tables = [...(screen.tables ?? [])]
  for (const tab of screen.tabs ?? []) {
    tables.push(...(tab.tables ?? []))
  }
  return tables
}

const TRIVIAL_COLUMN_KEYS = new Set(['id', 'pk', 'uuid', 'key', 'name', 'bezeichnung'])

function isNonTrivialColumn(col: { key: string }): boolean {
  return !TRIVIAL_COLUMN_KEYS.has(col.key.toLowerCase())
}

/**
 * Checks all readiness gates for a ScreenDefinition.
 * `generatorReady` is true only if all MANDATORY gates pass.
 * Advisory gates produce warnings but do not block `generatorReady`.
 */
export function checkGeneratorReadiness(screen: ScreenDefinition): GeneratorReadinessReport {
  const mandatory: GateResult[] = []
  const advisory: GateResult[] = []

  function mand(gate: ReadinessGate, passed: boolean, detail: string) {
    mandatory.push({ gate, severity: 'mandatory', passed, detail })
  }
  function adv(gate: ReadinessGate, passed: boolean, detail: string) {
    advisory.push({ gate, severity: 'advisory', passed, detail })
  }

  const allTables = collectAllTables(screen)
  const serverTables = allTables.filter((t) => t.serverPagination)

  // ── MANDATORY ──────────────────────────────────────────────────────────────

  // 1. schema_valid
  const schemaErrors = validateScreenDefinition(screen)
  mand('schema_valid', schemaErrors.length === 0, schemaErrors.length === 0 ? 'OK' : schemaErrors.join('; '))

  // 2. non_temporary
  const isTemporary = screen.adapter?.temporary === true
  mand('non_temporary', !isTemporary, isTemporary ? 'adapter.temporary=true — screen is not native yet' : 'OK')

  // 3. data_sources — dataSources defined when any table exists
  const hasDataSources = (screen.dataSources ?? []).length > 0
  mand('data_sources',
    allTables.length === 0 || hasDataSources,
    allTables.length === 0 ? 'no tables — gate skipped' : hasDataSources ? 'OK' : 'tables exist but no dataSources defined',
  )

  // 4. table_data_source_bound — every serverPagination table has a matching dataSource
  const dataSourceKeys = new Set((screen.dataSources ?? []).map((ds) => ds.key))
  const unboundTables = serverTables.filter((t) => !t.dataSourceKey || !dataSourceKeys.has(t.dataSourceKey))
  mand('table_data_source_bound',
    serverTables.length === 0 || unboundTables.length === 0,
    unboundTables.length === 0
      ? (serverTables.length === 0 ? 'no serverPagination tables — gate skipped' : 'OK')
      : `tables missing bound dataSource: ${unboundTables.map((t) => t.key).join(', ')}`,
  )

  // 5. table_columns_complete — every table has ≥2 non-trivial columns
  const thinTables = allTables.filter((t) => (t.columns ?? []).filter(isNonTrivialColumn).length < 2)
  mand('table_columns_complete',
    allTables.length === 0 || thinTables.length === 0,
    thinTables.length === 0
      ? (allTables.length === 0 ? 'no tables — gate skipped' : 'OK')
      : `tables with <2 non-trivial columns: ${thinTables.map((t) => t.key).join(', ')}`,
  )

  // 6. actions_classified — every action has dangerLevel + permission OR explicit stubReason
  const actions = screen.actions ?? []
  const unclassifiedActions = actions.filter(
    (a) => !a.dangerLevel || (!a.permission && !('stubReason' in a)),
  )
  mand('actions_classified',
    actions.length === 0 || unclassifiedActions.length === 0,
    unclassifiedActions.length === 0
      ? (actions.length === 0 ? 'no actions — gate skipped' : 'OK')
      : `actions missing dangerLevel or permission: ${unclassifiedActions.map((a) => a.key).join(', ')}`,
  )

  // ── ADVISORY ───────────────────────────────────────────────────────────────

  // 7. sort_whitelist — every table with columns has at least one sortable
  const tablesWithoutSort = allTables.filter((t) => (t.columns ?? []).length > 0 && !(t.columns ?? []).some((c) => c.sortable))
  adv('sort_whitelist',
    allTables.length === 0 || tablesWithoutSort.length === 0,
    tablesWithoutSort.length === 0
      ? (allTables.length === 0 ? 'no tables' : 'OK')
      : `tables with no sortable column: ${tablesWithoutSort.map((t) => t.key).join(', ')}`,
  )

  // 8. filter_columns — at least one filterable column per table
  const tablesWithoutFilter = allTables.filter((t) => (t.columns ?? []).length > 0 && !(t.columns ?? []).some((c) => c.filterable))
  adv('filter_columns',
    allTables.length === 0 || tablesWithoutFilter.length === 0,
    tablesWithoutFilter.length === 0
      ? (allTables.length === 0 ? 'no tables' : 'OK')
      : `tables with no filterable column: ${tablesWithoutFilter.map((t) => t.key).join(', ')}`,
  )

  // 9. agent_contract — explicit agentContract with businessPurpose
  const hasExplicit = Boolean(screen.agentContract?.businessPurpose)
  adv('agent_contract', hasExplicit, hasExplicit ? 'explicit agentContract provided' : 'no explicit agentContract — auto-generated only')

  // 10. workflow_declared — detail/cockpit screens should declare workflow or noWorkflowReason
  const needsWorkflow = screen.mode === 'detail' || screen.mode === 'cockpit'
  const hasWorkflow = Boolean(screen.workflow?.processKey) || Boolean((screen as { noWorkflowReason?: string }).noWorkflowReason)
  adv('workflow_declared',
    !needsWorkflow || hasWorkflow,
    hasWorkflow ? 'OK' : !needsWorkflow ? `mode=${screen.mode} — gate skipped` : 'detail/cockpit screen missing workflow declaration or noWorkflowReason',
  )

  // 11. stable_test_selectors — explicit testSelectors with at least screenRoot
  const hasSelectors = Boolean(screen.agentContract?.testSelectors?.['screenRoot'])
  adv('stable_test_selectors', hasSelectors, hasSelectors ? 'OK' : 'no explicit testSelectors.screenRoot in agentContract (auto-generated)')

  // 12. table_query_contract — sortable/filterable column keys look stable (not generic fallbacks)
  const GENERIC_KEYS = /^(col\d+|column\d+|field\d+|item\d+)$/i
  const genericQueryCols = allTables.flatMap((t) =>
    (t.columns ?? []).filter((c) => (c.sortable || c.filterable) && GENERIC_KEYS.test(c.key)).map((c) => `${t.key}.${c.key}`),
  )
  adv('table_query_contract',
    genericQueryCols.length === 0,
    genericQueryCols.length === 0 ? 'OK' : `generic unstable column keys used for sort/filter: ${genericQueryCols.join(', ')}`,
  )

  // ── Summary ────────────────────────────────────────────────────────────────
  const allGates = [...mandatory, ...advisory]
  const failedMandatory = mandatory.filter((g) => !g.passed)
  const failedAdvisory = advisory.filter((g) => !g.passed)
  const advisoryScore = advisory.length > 0 ? (advisory.length - failedAdvisory.length) / advisory.length : 1

  return {
    screenId: screen.id,
    generatorReady: failedMandatory.length === 0,
    advisoryScore: Math.round(advisoryScore * 100) / 100,
    gates: allGates,
    errors: failedMandatory.map((g) => `[${g.gate}] ${g.detail}`),
    warnings: failedAdvisory.map((g) => `[${g.gate}] ${g.detail}`),
  }
}
