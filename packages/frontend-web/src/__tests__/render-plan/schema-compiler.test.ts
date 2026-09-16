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
    expect(plan.tablesByKey.positionen?.rowHeight).toBe(36)
  })

  it('applies the screen density to root and tab table row heights', () => {
    const plan = compileRenderPlanFromScreenDefinition({
      ...crmSchema(),
      layout: { density: 'expertDense', tableProfile: 'standard' },
      tables: [{
        key: 'rootRows',
        label: 'Root rows',
        rowHeight: 44,
        columns: [{ key: 'name', label: 'Name' }],
      }],
      tabs: [{
        key: 'details',
        label: 'Details',
        tables: [{
          key: 'tabRows',
          label: 'Tab rows',
          rowHeight: 52,
          columns: [{ key: 'name', label: 'Name' }],
        }],
      }],
    })

    expect(plan.tablesByKey.rootRows?.rowHeight).toBe(36)
    expect(plan.tablesByKey.tabRows?.rowHeight).toBe(36)
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

  it('defaults worklist tables to listDetail and keeps booking and object pages single', () => {
    const worklist = compileRenderPlanFromScreenDefinition({
      ...crmSchema(),
      id: 'crm/customer-worklist',
      mode: 'list',
      layout: { floorplan: 'worklist', contextRail: 'none' },
      tables: [{ key: 'customers', label: 'Kunden', columns: [{ key: 'nr', label: 'Nr' }] }],
    })
    expect(worklist.shell.columnNavigation).toBe('listDetail')

    const analytical = compileRenderPlanFromScreenDefinition({
      ...crmSchema(),
      id: 'crm/customer-analytics',
      mode: 'list',
      layout: { floorplan: 'analyticalList', contextRail: 'none' },
      tables: [{ key: 'kpis', label: 'Kennzahlen', columns: [{ key: 'nr', label: 'Nr' }] }],
    })
    expect(analytical.shell.columnNavigation).toBe('listDetail')

    const objectPage = compileRenderPlanFromScreenDefinition({
      ...crmSchema(),
      id: 'crm/customer-object-tables',
      layout: { floorplan: 'objectPage' },
      tables: [{ key: 'orders', label: 'Aufträge', columns: [{ key: 'nr', label: 'Nr' }] }],
    })
    expect(objectPage.shell.columnNavigation).toBe('single')

    const transaction = compileRenderPlanFromScreenDefinition({
      ...crmSchema(),
      id: 'lager/weighing',
      layout: { floorplan: 'transaction', contextRail: 'audit' },
      tables: [{ key: 'lines', label: 'Positionen', columns: [{ key: 'nr', label: 'Nr' }] }],
    })
    expect(transaction.shell.columnNavigation).toBe('single')
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

  it('compiles processChain into shell.processRibbon and degrades unknown chains to warnings', () => {
    const schema = {
      ...crmSchema(),
      processChain: { chainId: 'k2_verkauf', stepKey: 'lieferschein' },
      processChains: {
        k2_verkauf: {
          label: 'Verkauf',
          steps: [
            { key: 'auftrag', label: 'Auftrag', screenId: 'sales/sales-order', routePath: '/verkauf/auftraege' },
            { key: 'lieferschein', label: 'Lieferschein', screenId: 'sales/delivery-note', routePath: '/verkauf/lieferschein-erfassung' },
          ],
        },
      },
    }

    const plan = compileRenderPlanFromScreenDefinition(schema)
    expect(plan.shell.processRibbon?.chainId).toBe('k2_verkauf')
    expect(plan.shell.processRibbon?.steps.map((step) => step.state)).toEqual(['upcoming', 'current'])
    expect(plan.shell.processRibbonWarnings).toBeUndefined()

    const unknown = compileRenderPlanFromScreenDefinition({
      ...crmSchema(),
      id: 'crm/customer-360-unknown-chain',
      processChain: { chainId: 'gibtsnicht', stepKey: 'x' },
      processChains: schema.processChains,
    })
    expect(unknown.shell.processRibbon).toBeUndefined()
    expect(unknown.shell.processRibbonWarnings).toContain('unknown_chain:gibtsnicht')
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
