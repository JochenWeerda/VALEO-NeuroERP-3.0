import { describe, expect, it, vi, beforeEach } from 'vitest'
import { adaptMaskConfigToScreenDefinition } from '@/components/mask-builder/adapters/mask-config-adapter'
import type { MaskConfig } from '@/components/mask-builder/types'
import {
  compileRenderPlan,
  compileRenderPlanFromScreenDefinition,
  invalidateRenderPlanCache,
} from '@/components/mask-builder/render-plan/schema-compiler'
import { globalRenderPlanCache } from '@/components/mask-builder/render-plan/cache'
import { buildRenderPlanCacheKey } from '@/components/mask-builder/render-plan/compile-context'

const legacyMask: MaskConfig = {
  title: 'Kundenstamm',
  subtitle: 'Compiler Test',
  type: 'object-page',
  tabs: [
    {
      key: 'basis',
      label: 'Basis',
      fields: [
        { name: 'name', label: 'Name', type: 'text', required: true },
        { name: 'hersteller', label: 'Hersteller', type: 'lookup', endpoint: '/api/hersteller' },
      ],
    },
    {
      key: 'kontakte',
      label: 'Kontakte',
      fields: [{ name: 'email', label: 'E-Mail', type: 'text' }],
    },
    {
      key: 'angebote',
      label: 'Angebote',
      fields: [],
    },
  ],
  actions: [
    { key: 'edit', label: 'Bearbeiten', type: 'primary' },
    { key: 'audit', label: 'Audit', type: 'secondary' },
  ],
  api: { baseUrl: '/api/v1/crm/customers', endpoints: {} },
}

function crmSchema() {
  return adaptMaskConfigToScreenDefinition(legacyMask, {
    id: 'crm/customer-360',
    domain: 'crm',
    summaryEndpoint: '/api/v1/crm/customers/cust-1/screen-summary',
  })
}

describe('schema-compiler', () => {
  beforeEach(() => {
    invalidateRenderPlanCache()
  })

  it('compiles CRM schema into a flat RenderPlan with indexed fields and tabs', () => {
    const schema = crmSchema()
    const plan = compileRenderPlanFromScreenDefinition(schema, {
      permissions: ['crm.customer.update'],
      availableTabs: ['basis', 'kontakte'],
    })

    expect(plan.screenId).toBe('crm/customer-360')
    expect(plan.visibleTabs.map((tab) => tab.key)).toEqual(['basis', 'kontakte'])
    expect(plan.fieldsByTab.basis?.map((field) => field.key)).toEqual(['name', 'hersteller'])
    expect(plan.fieldsByKey.hersteller?.componentKind).toBe('lookup')
    expect(plan.fieldsByKey.hersteller?.minSearchChars).toBe(2)
    expect(plan.shell.floorplan).toBe('objectPage')
    expect(plan.shell.density).toBe('compact')
    expect(plan.shell.contextRail).toBe('combined')
    expect(plan.shell.contextRailSections).toEqual(['workflow', 'audit', 'copilot'])
    expect(plan.shell.tableProfile).toBe('standard')
    expect(plan.performance.lookupResultLimit).toBe(25)
    expect(plan.performance.lookupCacheTtlMs).toBe(900_000)
  })

  it('filters actions by permission in the compiler', () => {
    const schema = {
      ...crmSchema(),
      actions: [
        { key: 'edit', label: 'Bearbeiten', kind: 'primary' as const, permission: 'crm.customer.update' },
        { key: 'audit', label: 'Audit', kind: 'secondary' as const, permission: 'crm.audit.read' },
      ],
    }

    const plan = compileRenderPlanFromScreenDefinition(schema, {
      permissions: ['crm.customer.update'],
    })

    expect(plan.actions.map((action) => action.key)).toEqual(['edit'])
  })

  it('defaults tables to virtualized server-paginated plans with pageSize cap 50', () => {
    const schema = {
      ...crmSchema(),
      tabs: [
        {
          key: 'auftraege',
          label: 'Auftraege',
          lazy: true,
          tables: [
            {
              key: 'orders',
              label: 'Auftraege',
              columns: [{ key: 'nr', label: 'Nr.' }],
              pageSize: 100,
            },
          ],
        },
      ],
    }

    const plan = compileRenderPlanFromScreenDefinition(schema, {
      availableTabs: ['auftraege'],
    })

    const table = plan.tablesByTab.auftraege?.[0]
    expect(table?.virtualized).toBe(true)
    expect(table?.serverPagination).toBe(true)
    expect(table?.pageSize).toBe(50)
    expect(table?.tableProfile).toBe('standard')
  })

  it('maps Meridian layout metadata into RenderPlan shell and table profile', () => {
    const schema = {
      ...crmSchema(),
      id: 'finance/ap-invoice',
      domain: 'finance' as const,
      layout: {
        preferredMode: 'desktopDense' as const,
        mobileMode: 'mobileStack' as const,
        touchTargetPx: 44,
        floorplan: 'objectPage' as const,
        density: 'expertDense' as const,
        contextRail: 'audit' as const,
        tableProfile: 'financial' as const,
      },
      tables: [
        {
          key: 'positionen',
          label: 'Positionen',
          columns: [{ key: 'betrag', label: 'Betrag', renderKind: 'currency' as const }],
        },
      ],
    }

    const plan = compileRenderPlanFromScreenDefinition(schema)

    expect(plan.shell.floorplan).toBe('objectPage')
    expect(plan.shell.density).toBe('expertDense')
    expect(plan.shell.contextRail).toBe('audit')
    expect(plan.shell.contextRailSections).toEqual(['audit'])
    expect(plan.shell.tableProfile).toBe('financial')
    expect(plan.tablesByKey.positionen?.tableProfile).toBe('financial')
  })

  it('compiles familiar desktop work patterns without a vendor-specific mode', () => {
    const plan = compileRenderPlanFromScreenDefinition({
      ...crmSchema(),
      layout: {
        preferredMode: 'desktopDense',
        mobileMode: 'mobileStack',
        floorplan: 'transaction',
        density: 'expertDense',
        contextRail: 'combined',
        tableProfile: 'standard',
        summaryPlacement: 'footer',
        stickyHeader: true,
        stickyFooter: true,
      },
      interaction: { enterMovesFocus: true },
      actions: [
        {
          key: 'print',
          label: 'Drucken',
          kind: 'secondary',
          zone: 'footer',
          keyboardShortcut: 'Ctrl+P',
        },
        {
          key: 'save',
          label: 'Speichern',
          kind: 'primary',
          zone: 'commit',
          keyboardShortcut: 'Ctrl+S',
        },
      ],
    })

    expect(plan.shell.summaryPlacement).toBe('footer')
    expect(plan.shell.stickyHeader).toBe(true)
    expect(plan.shell.stickyFooter).toBe(true)
    expect(plan.interaction.enterMovesFocus).toBe(true)
    expect(plan.actions).toEqual(expect.arrayContaining([
      expect.objectContaining({ key: 'print', zone: 'footer', keyboardShortcut: 'Ctrl+P' }),
      expect.objectContaining({ key: 'save', zone: 'commit', keyboardShortcut: 'Ctrl+S' }),
    ]))
  })

  it('compiles voice capability into the RenderPlan shell', () => {
    const plan = compileRenderPlanFromScreenDefinition({
      ...crmSchema(),
      voice: { enabled: true, provider: 'webspeech' },
    })

    expect(plan.shell.voice).toEqual({ enabled: true, provider: 'webspeech' })
  })

  it('compiles twin read-model capability into the RenderPlan', () => {
    const plan = compileRenderPlanFromScreenDefinition({
      ...crmSchema(),
      id: 'lager/leitstand',
      domain: 'lager',
      mode: 'cockpit',
      twin: {
        endpoint: '/api/v1/lager/silo/cells',
        planId: 'lager-leitstand',
        cacheTtlSeconds: 30,
        activateRouteTemplate: '/lager/silo-zellen/{cellId}',
        activateScreenId: 'lager/silo-cell',
        metrics: [
          { key: 'fill_pct', label: 'Fuellstand', kind: 'percent', warnAbove: 90 },
          { key: 'locked', label: 'Gesperrt', kind: 'flag' },
        ],
      },
    })

    expect(plan.twin).toMatchObject({
      endpoint: '/api/v1/lager/silo/cells',
      planId: 'lager-leitstand',
      cacheTtlSeconds: 30,
      activateRouteTemplate: '/lager/silo-zellen/{cellId}',
      activateScreenId: 'lager/silo-cell',
    })
    expect(plan.twin?.metrics.map((metric) => metric.key)).toEqual(['fill_pct', 'locked'])
  })

  it('preserves explicit context rail sections and enables collab opt-in', () => {
    const schema = {
      ...crmSchema(),
      layout: {
        contextRail: 'combined' as const,
        contextRailSections: ['workflow', 'collab', 'audit', 'collab'] as const,
      },
    }

    const plan = compileRenderPlanFromScreenDefinition(schema)

    expect(plan.shell.contextRail).toBe('combined')
    expect(plan.shell.contextRailSections).toEqual(['workflow', 'collab', 'audit'])
  })

  it('caches compiled plans by cache key and reuses without recompilation', () => {
    const schema = crmSchema()
    const context = {
      screenId: schema.id,
      schemaVersion: schema.schemaVersion,
      auth: { permissions: ['crm.customer.update'] },
    }
    const cacheKey = buildRenderPlanCacheKey(context)

    const compileSpy = vi.fn(compileRenderPlan)
    const first = compileSpy(schema, context)
    globalRenderPlanCache.set(cacheKey, first)
    const second = globalRenderPlanCache.get(cacheKey)

    expect(second).toBe(first)
    expect(compileSpy).toHaveBeenCalledTimes(1)
  })
})
