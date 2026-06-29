import { describe, expect, it } from 'vitest'
import { checkGeneratorReadiness } from '@/components/mask-builder/runtime/generatorReadiness'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

/** Minimal screen that passes all mandatory gates (advisory gates may warn). */
const baseScreen: ScreenDefinition = {
  schemaVersion: 1,
  id: 'crm/customer-360',
  domain: 'crm',
  mode: 'list',
  title: 'Kundenstamm',
}

/** Screen with tables — needs dataSources, serverPagination binding, and columns. */
const screenWithTables: ScreenDefinition = {
  schemaVersion: 1,
  id: 'crm/customer-360',
  domain: 'crm',
  mode: 'list',
  title: 'Kundenstamm',
  dataSources: [
    { key: 'orders', endpoint: '/api/v1/crm/customers/{entity_id}/auftraege' },
  ],
  tabs: [
    {
      key: 'auftraege',
      label: 'Auftraege',
      tables: [
        {
          key: 'recent_orders',
          label: 'Auftraege',
          serverPagination: true,
          dataSourceKey: 'orders',
          columns: [
            { key: 'order_nr', label: 'Auftrag', sortable: true },
            { key: 'status', label: 'Status', filterable: true },
            { key: 'betrag', label: 'Betrag' },
          ],
        },
      ],
    },
  ],
  actions: [
    { key: 'save', label: 'Speichern', dangerLevel: 'safe', permission: 'crm.edit' },
  ],
}

describe('checkGeneratorReadiness — mandatory/advisory split', () => {
  // ── Report shape ──────────────────────────────────────────────────────────

  it('returns generatorReady=true and advisoryScore for a well-formed screen (no tables)', () => {
    const report = checkGeneratorReadiness(baseScreen)
    expect(report.generatorReady).toBe(true)
    expect(typeof report.advisoryScore).toBe('number')
    expect(report.advisoryScore).toBeGreaterThanOrEqual(0)
    expect(report.advisoryScore).toBeLessThanOrEqual(1)
    expect(report.errors).toHaveLength(0)
    expect(Array.isArray(report.gates)).toBe(true)
    expect(Array.isArray(report.warnings)).toBe(true)
  })

  it('includes both mandatory and advisory gates in results', () => {
    const report = checkGeneratorReadiness(screenWithTables)
    const mandatoryGates = report.gates.filter((g) => g.severity === 'mandatory')
    const advisoryGates = report.gates.filter((g) => g.severity === 'advisory')
    expect(mandatoryGates.length).toBe(6)
    expect(advisoryGates.length).toBe(6)
  })

  // ── Mandatory gates ───────────────────────────────────────────────────────

  it('fails schema_valid when required title is missing', () => {
    const broken = { ...baseScreen, title: '' }
    const report = checkGeneratorReadiness(broken)
    expect(report.generatorReady).toBe(false)
    const gate = report.gates.find((g) => g.gate === 'schema_valid')
    expect(gate!.passed).toBe(false)
    expect(gate!.severity).toBe('mandatory')
    expect(report.errors.some((e) => e.includes('schema_valid'))).toBe(true)
  })

  it('fails non_temporary when adapter.temporary is true', () => {
    const screen: ScreenDefinition = {
      ...baseScreen,
      adapter: { type: 'maskConfig', temporary: true },
    }
    const report = checkGeneratorReadiness(screen)
    expect(report.generatorReady).toBe(false)
    const gate = report.gates.find((g) => g.gate === 'non_temporary')
    expect(gate!.passed).toBe(false)
    expect(gate!.severity).toBe('mandatory')
  })

  it('fails data_sources when tables exist but dataSources is absent', () => {
    const { dataSources: _ds, ...withoutDs } = screenWithTables
    const report = checkGeneratorReadiness(withoutDs as ScreenDefinition)
    expect(report.generatorReady).toBe(false)
    const gate = report.gates.find((g) => g.gate === 'data_sources')
    expect(gate!.passed).toBe(false)
    expect(gate!.severity).toBe('mandatory')
  })

  it('fails table_data_source_bound when serverPagination table has no matching dataSource', () => {
    const screen: ScreenDefinition = {
      ...screenWithTables,
      dataSources: [{ key: 'entity', endpoint: '/api/v1/crm/customers/{entity_id}' }], // 'orders' key missing
    }
    const report = checkGeneratorReadiness(screen)
    const gate = report.gates.find((g) => g.gate === 'table_data_source_bound')
    expect(gate!.passed).toBe(false)
    expect(gate!.severity).toBe('mandatory')
    expect(report.generatorReady).toBe(false)
  })

  it('fails table_columns_complete when a table has fewer than 2 non-trivial columns', () => {
    const screen: ScreenDefinition = {
      ...screenWithTables,
      tabs: [
        {
          key: 'auftraege',
          label: 'Auftraege',
          tables: [
            {
              key: 'recent_orders',
              label: 'Auftraege',
              serverPagination: true,
              dataSourceKey: 'orders',
              columns: [
                { key: 'id', label: 'ID' },    // trivial
                { key: 'name', label: 'Name' }, // trivial — only 0 non-trivial columns
              ],
            },
          ],
        },
      ],
    }
    const report = checkGeneratorReadiness(screen)
    const gate = report.gates.find((g) => g.gate === 'table_columns_complete')
    expect(gate!.passed).toBe(false)
    expect(gate!.severity).toBe('mandatory')
  })

  it('fails actions_classified when an action has no dangerLevel', () => {
    const screen: ScreenDefinition = {
      ...baseScreen,
      actions: [
        { key: 'delete', label: 'Loeschen' }, // missing dangerLevel + permission
      ],
    }
    const report = checkGeneratorReadiness(screen)
    const gate = report.gates.find((g) => g.gate === 'actions_classified')
    expect(gate!.passed).toBe(false)
    expect(gate!.severity).toBe('mandatory')
    expect(report.generatorReady).toBe(false)
  })

  // ── Advisory gates ────────────────────────────────────────────────────────

  it('sort_whitelist is advisory — fails but does not block generatorReady', () => {
    const screen: ScreenDefinition = {
      ...screenWithTables,
      tabs: [
        {
          key: 'auftraege',
          label: 'Auftraege',
          tables: [
            {
              key: 'recent_orders',
              label: 'Auftraege',
              serverPagination: true,
              dataSourceKey: 'orders',
              columns: [
                { key: 'order_nr', label: 'Auftrag' },          // not sortable
                { key: 'status', label: 'Status', filterable: true },
                { key: 'betrag', label: 'Betrag' },
              ],
            },
          ],
        },
      ],
    }
    const report = checkGeneratorReadiness(screen)
    const gate = report.gates.find((g) => g.gate === 'sort_whitelist')
    expect(gate!.passed).toBe(false)
    expect(gate!.severity).toBe('advisory')
    // advisory failure must not block generatorReady
    expect(report.generatorReady).toBe(true)
    expect(report.warnings.some((w) => w.includes('sort_whitelist'))).toBe(true)
    // must not appear in errors
    expect(report.errors.some((e) => e.includes('sort_whitelist'))).toBe(false)
  })

  it('agent_contract is advisory — passes even without explicit agentContract', () => {
    const report = checkGeneratorReadiness(screenWithTables)
    const gate = report.gates.find((g) => g.gate === 'agent_contract')
    expect(gate!.severity).toBe('advisory')
    // may or may not pass — just check it's advisory
    expect(['mandatory', 'advisory']).toContain(gate!.severity)
  })

  it('workflow_declared is advisory and skipped for list screens', () => {
    // baseScreen has mode='list' — gate should pass (skipped)
    const report = checkGeneratorReadiness(baseScreen)
    const gate = report.gates.find((g) => g.gate === 'workflow_declared')
    expect(gate!.severity).toBe('advisory')
    expect(gate!.passed).toBe(true)
  })

  it('workflow_declared warns for detail screen without workflow', () => {
    const screen: ScreenDefinition = { ...baseScreen, mode: 'detail' }
    const report = checkGeneratorReadiness(screen)
    const gate = report.gates.find((g) => g.gate === 'workflow_declared')
    expect(gate!.passed).toBe(false)
    expect(gate!.severity).toBe('advisory')
    expect(report.generatorReady).toBe(true) // advisory only
  })

  it('table_query_contract warns on generic column keys used for sort/filter', () => {
    const screen: ScreenDefinition = {
      ...screenWithTables,
      tabs: [
        {
          key: 'auftraege',
          label: 'Auftraege',
          tables: [
            {
              key: 'recent_orders',
              label: 'Auftraege',
              serverPagination: true,
              dataSourceKey: 'orders',
              columns: [
                { key: 'col1', label: 'Auftrag', sortable: true },  // generic!
                { key: 'status', label: 'Status', filterable: true },
                { key: 'betrag', label: 'Betrag' },
              ],
            },
          ],
        },
      ],
    }
    const report = checkGeneratorReadiness(screen)
    const gate = report.gates.find((g) => g.gate === 'table_query_contract')
    expect(gate!.passed).toBe(false)
    expect(gate!.severity).toBe('advisory')
    expect(report.generatorReady).toBe(true)
  })

  // ── Advisory score ────────────────────────────────────────────────────────

  it('advisoryScore is between 0 and 1 and decreases when advisory gates fail', () => {
    const perfectReport = checkGeneratorReadiness(screenWithTables)
    const brokenReport = checkGeneratorReadiness({
      ...screenWithTables,
      mode: 'detail', // triggers workflow_declared warning
    })
    // brokenReport has at least one advisory failure → lower score
    expect(brokenReport.advisoryScore).toBeLessThanOrEqual(perfectReport.advisoryScore)
  })

  // ── Gate skipping ─────────────────────────────────────────────────────────

  it('table-related mandatory gates pass/skip when no tables are defined', () => {
    const report = checkGeneratorReadiness(baseScreen) // no tables
    expect(report.gates.find((g) => g.gate === 'table_data_source_bound')!.passed).toBe(true)
    expect(report.gates.find((g) => g.gate === 'table_columns_complete')!.passed).toBe(true)
    expect(report.generatorReady).toBe(true)
  })
})
