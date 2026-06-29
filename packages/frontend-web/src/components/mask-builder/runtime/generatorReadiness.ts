/**
 * Phase 030 — Generator Readiness Gates
 *
 * A ScreenDefinition is `generator_ready` only when ALL gates are green:
 *  1. Schema validation passes (validateScreenDefinition)
 *  2. At least one sortable column defined (sort whitelist present)
 *  3. At least one filterable column defined
 *  4. agentContract is attached (either explicit or derivable → always true after Phase 029)
 *  5. dataSources defined when tables exist
 *  6. No temporary adapter flag
 */

import { validateScreenDefinition, type ScreenDefinition } from '../schema'

export type ReadinessGate =
  | 'schema_valid'
  | 'sort_whitelist'
  | 'filter_columns'
  | 'agent_contract'
  | 'data_sources'
  | 'non_temporary'

export interface GateResult {
  gate: ReadinessGate
  passed: boolean
  detail: string
}

export interface GeneratorReadinessReport {
  screenId: string
  generatorReady: boolean
  gates: GateResult[]
  errors: string[]
}

function collectAllTables(screen: ScreenDefinition) {
  const tables = [...(screen.tables ?? [])]
  for (const tab of screen.tabs ?? []) {
    tables.push(...(tab.tables ?? []))
  }
  return tables
}

/**
 * Checks all readiness gates for a ScreenDefinition.
 * `generatorReady` is true only if ALL gates pass.
 */
export function checkGeneratorReadiness(screen: ScreenDefinition): GeneratorReadinessReport {
  const gates: GateResult[] = []

  // Gate 1: schema validation
  const schemaErrors = validateScreenDefinition(screen)
  gates.push({
    gate: 'schema_valid',
    passed: schemaErrors.length === 0,
    detail: schemaErrors.length === 0 ? 'OK' : schemaErrors.join('; '),
  })

  // Gate 2: sort whitelist — at least one sortable column in any table
  const allTables = collectAllTables(screen)
  const hasSortable = allTables.some((t) => t.columns?.some((c) => c.sortable))
  gates.push({
    gate: 'sort_whitelist',
    passed: hasSortable || allTables.length === 0,
    detail: hasSortable
      ? 'OK'
      : allTables.length === 0
      ? 'no tables — gate skipped'
      : 'no sortable columns defined in any table',
  })

  // Gate 3: filterable columns
  const hasFilterable = allTables.some((t) => t.columns?.some((c) => c.filterable))
  gates.push({
    gate: 'filter_columns',
    passed: hasFilterable || allTables.length === 0,
    detail: hasFilterable
      ? 'OK'
      : allTables.length === 0
      ? 'no tables — gate skipped'
      : 'no filterable columns defined in any table',
  })

  // Gate 4: agentContract — always derivable after Phase 029; explicit is better
  const hasExplicitContract = Boolean(screen.agentContract?.businessPurpose)
  gates.push({
    gate: 'agent_contract',
    passed: true, // always derivable by generateAgentMaskContract
    detail: hasExplicitContract ? 'explicit agentContract provided' : 'auto-generated (no explicit contract)',
  })

  // Gate 5: dataSources when tables exist
  const hasTables = allTables.length > 0
  const hasDataSources = (screen.dataSources ?? []).length > 0
  gates.push({
    gate: 'data_sources',
    passed: !hasTables || hasDataSources,
    detail: !hasTables
      ? 'no tables — gate skipped'
      : hasDataSources
      ? 'OK'
      : 'tables exist but no dataSources defined',
  })

  // Gate 6: non-temporary adapter
  const isTemporary = screen.adapter?.temporary === true
  gates.push({
    gate: 'non_temporary',
    passed: !isTemporary,
    detail: isTemporary ? 'adapter.temporary=true — screen is not native yet' : 'OK',
  })

  const failedGates = gates.filter((g) => !g.passed)
  const generatorReady = failedGates.length === 0
  const errors = failedGates.map((g) => `[${g.gate}] ${g.detail}`)

  return { screenId: screen.id, generatorReady, gates, errors }
}
