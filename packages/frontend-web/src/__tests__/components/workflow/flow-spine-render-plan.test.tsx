import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { compileRenderPlan } from '@/components/mask-builder/render-plan/schema-compiler'
import { useUniversalMaskRuntime } from '@/components/mask-builder/runtime/useUniversalMaskRuntime'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const get = vi.hoisted(() => vi.fn(async () => ({ data: {} })))
vi.mock('@/lib/api-client', () => ({ apiClient: { get } }))
const keys = ['order-to-cash', 'procure-to-pay', 'inventory-to-settlement', 'harvest-to-settlement', 'contract-to-settlement', 'complaint-to-resolution', 'service-to-customer', 'finance-to-close', 'compliance-to-report']
function definition(key: string): ScreenDefinition {
  const id = `workflow/flow-spine-${key}`
  return { schemaVersion: 1, id, domain: 'workflow', mode: 'cockpit', title: key,
    adapter: { type: 'native', sourceId: id, temporary: false },
    layout: { floorplan: 'cockpit', density: 'expertDense', contextRail: 'workflow' },
    flowSpineWorkspace: { processKey: key } } as ScreenDefinition
}
describe('Flow Spine RenderPlan contract', () => {
  it.each(keys)('compiles the process key for %s', (key) => {
    expect(compileRenderPlan(definition(key), { screenId: `workflow/flow-spine-${key}`, schemaVersion: 1, auth: { permissions: [] } }).flowSpineWorkspace?.processKey).toBe(key)
  })
  it('rejects an ID and process mismatch', () => {
    const schema = definition('service-to-customer')
    schema.flowSpineWorkspace = { processKey: 'order-to-cash' }
    expect(() => compileRenderPlan(schema, { screenId: schema.id, schemaVersion: 1, auth: { permissions: [] } })).toThrow('Invalid process workspace contract')
  })
  it('does not request a Flow Spine for another screen', async () => {
    get.mockClear()
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const schema = { schemaVersion: 1, id: 'test/ordinary', domain: 'test', mode: 'cockpit', title: 'Test', adapter: { type: 'native', sourceId: 'test/ordinary' } } as ScreenDefinition
    renderHook(() => useUniversalMaskRuntime({ screenId: schema.id, schema }), { wrapper: ({ children }) => <QueryClientProvider client={queryClient}>{children}</QueryClientProvider> })
    await waitFor(() => expect(get.mock.calls.some(([url]) => String(url).includes('/flow-spines'))).toBe(false))
  })
})
