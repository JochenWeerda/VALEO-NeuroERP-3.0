import { describe, expect, it } from 'vitest'
import { compileDataBindingPlan } from '@/components/mask-builder/runtime/compile-data-binding-plan'
import type { RenderPlan } from '@/components/mask-builder/render-plan/types'

function makeMockPlan(overrides: Partial<RenderPlan> = {}): RenderPlan {
  return {
    cacheKey: 'test',
    screenId: 'crm/customer-360',
    schemaVersion: 1,
    shell: { title: 'Test', domain: 'crm', mode: 'detail', layoutMode: 'desktopDense', mobileMode: 'mobileStack', touchTargetPx: 44 },
    summarySlots: [],
    summaryItems: [],
    visibleTabs: [],
    tabContent: {},
    rootFieldKeys: [],
    fieldsByKey: {},
    fieldsByTab: {},
    rootTableKeys: [],
    tablesByKey: {},
    tablesByTab: {},
    actions: [],
    performance: {
      initialPayloadBudgetKb: 64,
      requiresLazyTabs: true,
      requiresVirtualTables: true,
      lookupMinChars: 2,
      lookupResultLimit: 25,
      lookupCacheTtlMs: 900_000,
      lookupDebounceMs: 300,
    },
    ...overrides,
  }
}

describe('compileDataBindingPlan', () => {
  it('resolves entity binding from dataSources', () => {
    const plan = makeMockPlan()
    const result = compileDataBindingPlan(
      plan,
      [{ key: 'entity', endpoint: '/api/v1/crm/customers/{entity_id}' }],
      undefined,
      '42',
    )
    expect(result.entityBinding.entityEndpoint).toBe('/api/v1/crm/customers/42')
    expect(result.entityBinding.entityId).toBe('42')
  })

  it('resolves table bindings from dataSourceKey', () => {
    const plan = makeMockPlan({
      rootTableKeys: ['kontakte'],
      tablesByKey: {
        kontakte: {
          key: 'kontakte',
          label: 'Kontakte',
          columns: [],
          dataSourceKey: 'kontakte_ds',
          pageSize: 25,
          virtualized: true,
          rowHeight: 52,
          serverPagination: true,
        },
      },
    })
    const result = compileDataBindingPlan(
      plan,
      [{ key: 'kontakte_ds', endpoint: '/api/v1/crm/customers/{entity_id}/tabs/kontakte' }],
      undefined,
      'cust-1',
    )
    expect(result.tableBindings['kontakte'].endpoint).toBe(
      '/api/v1/crm/customers/cust-1/tabs/kontakte',
    )
    expect(result.tableBindings['kontakte'].requiresServerQuery).toBe(true)
  })

  it('falls back to tabEndpoints when dataSourceKey missing', () => {
    const plan = makeMockPlan({
      rootTableKeys: ['auftraege'],
      tablesByKey: {
        auftraege: {
          key: 'auftraege',
          label: 'Auftraege',
          columns: [],
          tabKey: 'auftraege',
          pageSize: 25,
          virtualized: true,
          rowHeight: 52,
          serverPagination: true,
        },
      },
    })
    const result = compileDataBindingPlan(
      plan,
      [],
      { auftraege: '/api/v1/crm/customers/cust-1/tabs/auftraege' },
      'cust-1',
    )
    expect(result.tableBindings['auftraege'].endpoint).toBe(
      '/api/v1/crm/customers/cust-1/tabs/auftraege',
    )
  })

  it('loads endpoint-backed client-paged tables as well', () => {
    const plan = makeMockPlan({
      rootTableKeys: ['trail'],
      tablesByKey: {
        trail: {
          key: 'trail', label: 'Historie', columns: [], dataSourceKey: 'trail',
          pageSize: 100, virtualized: true, rowHeight: 44, serverPagination: false,
        },
      },
    })
    const result = compileDataBindingPlan(
      plan,
      [{ key: 'trail', endpoint: '/api/v1/audit/trail' }],
      undefined,
    )
    expect(result.tableBindings['trail'].requiresServerQuery).toBe(true)
  })

  it('marks table as non-server-queried when no endpoint found', () => {
    const plan = makeMockPlan({
      rootTableKeys: ['orphan'],
      tablesByKey: {
        orphan: {
          key: 'orphan',
          label: 'Orphan',
          columns: [],
          pageSize: 25,
          virtualized: true,
          rowHeight: 52,
          serverPagination: true,
        },
      },
    })
    const result = compileDataBindingPlan(plan, [], undefined, 'cust-1')
    expect(result.tableBindings['orphan'].requiresServerQuery).toBe(false)
  })
})
