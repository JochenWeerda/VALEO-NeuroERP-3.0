import { describe, expect, it } from 'vitest'
import { checkGeneratorReadiness } from '@/components/mask-builder/runtime/generatorReadiness'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const readyScreen: ScreenDefinition = {
  schemaVersion: 1,
  id: 'crm/customer-360',
  domain: 'crm',
  mode: 'detail',
  title: 'Kundenstamm',
  dataSources: [{ key: 'entity', endpoint: '/api/v1/crm/customers/{entity_id}' }],
  tabs: [
    {
      key: 'auftraege',
      label: 'Auftraege',
      tables: [
        {
          key: 'recent_orders',
          label: 'Auftraege',
          columns: [
            { key: 'order_nr', label: 'Auftrag', sortable: true },
            { key: 'status', label: 'Status', filterable: true },
          ],
        },
      ],
    },
  ],
}

describe('checkGeneratorReadiness', () => {
  it('reports generatorReady for a well-formed screen', () => {
    const report = checkGeneratorReadiness(readyScreen)
    expect(report.generatorReady).toBe(true)
    expect(report.errors).toHaveLength(0)
    expect(report.gates.every((g) => g.passed)).toBe(true)
  })

  it('fails schema_valid when required fields are missing', () => {
    const broken = { ...readyScreen, title: '' }
    const report = checkGeneratorReadiness(broken)
    expect(report.generatorReady).toBe(false)
    const schemaGate = report.gates.find((g) => g.gate === 'schema_valid')
    expect(schemaGate!.passed).toBe(false)
    expect(report.errors.some((e) => e.includes('schema_valid'))).toBe(true)
  })

  it('fails sort_whitelist when table has no sortable columns', () => {
    const screen: ScreenDefinition = {
      ...readyScreen,
      tabs: [
        {
          key: 'auftraege',
          label: 'Auftraege',
          tables: [
            {
              key: 'recent_orders',
              label: 'Auftraege',
              columns: [
                { key: 'order_nr', label: 'Auftrag' },
                { key: 'status', label: 'Status', filterable: true },
              ],
            },
          ],
        },
      ],
    }
    const report = checkGeneratorReadiness(screen)
    const gate = report.gates.find((g) => g.gate === 'sort_whitelist')
    expect(gate!.passed).toBe(false)
  })

  it('skips sort_whitelist and filter_columns gates when no tables', () => {
    const screen: ScreenDefinition = {
      ...readyScreen,
      tabs: undefined,
      dataSources: undefined,
    }
    const report = checkGeneratorReadiness(screen)
    const sortGate = report.gates.find((g) => g.gate === 'sort_whitelist')
    const filterGate = report.gates.find((g) => g.gate === 'filter_columns')
    expect(sortGate!.passed).toBe(true)
    expect(filterGate!.passed).toBe(true)
  })

  it('fails data_sources when tables exist but no dataSources', () => {
    const { dataSources: _ds, ...withoutDs } = readyScreen
    const report = checkGeneratorReadiness(withoutDs as ScreenDefinition)
    const gate = report.gates.find((g) => g.gate === 'data_sources')
    expect(gate!.passed).toBe(false)
  })

  it('fails non_temporary when adapter.temporary is true', () => {
    const screen: ScreenDefinition = {
      ...readyScreen,
      adapter: { type: 'maskConfig', temporary: true },
    }
    const report = checkGeneratorReadiness(screen)
    const gate = report.gates.find((g) => g.gate === 'non_temporary')
    expect(gate!.passed).toBe(false)
  })

  it('agentContract gate is always passed (auto-derivable)', () => {
    const report = checkGeneratorReadiness(readyScreen)
    const gate = report.gates.find((g) => g.gate === 'agent_contract')
    expect(gate!.passed).toBe(true)
  })
})
