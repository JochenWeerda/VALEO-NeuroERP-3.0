import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { validateScreenDefinition, type ScreenDefinition } from '@/components/mask-builder/schema'
import { compileRenderPlanFromScreenDefinition, invalidateRenderPlanCache } from '@/components/mask-builder/render-plan/schema-compiler'

function definition(): ScreenDefinition {
  return {
    schemaVersion: 1, id: 'tenant/document-version', domain: 'sales', mode: 'detail', title: 'Rechnung',
    layout: { floorplan: 'objectPage', columnNavigation: 'single', contextRail: 'none' },
    fields: [{ key: 'number', label: 'Belegnummer', type: 'text', readOnly: true }],
    documentVariant: {
      family: 'beleg', baseVersion: '1.0.0', baseHash: 'a'.repeat(64), variantId: 'sales_invoice',
      variantVersion: '1.0.0', variantHash: 'b'.repeat(64), materializedHash: 'c'.repeat(64),
    },
  }
}

describe('version binding through the shared renderer', () => {
  it('reports an incomplete origin reference rather than silently displaying it as a valid version', () => {
    const source = definition()
    expect(validateScreenDefinition(source)).toEqual([])
    source.documentVariant!.materializedHash = 'broken'
    expect(validateScreenDefinition(source)).toContain('documentVariant requires an exact valid base and variant binding')
    const malformed = definition()
    malformed.documentVariant!.variantId = {} as unknown as string
    expect(validateScreenDefinition(malformed)).toContain('documentVariant requires an exact valid base and variant binding')
  })

  it('invalidates the render cache even when only the bound variant version changes', () => {
    invalidateRenderPlanCache()
    const first = definition()
    const second = definition()
    second.documentVariant!.variantVersion = '2.0.0'
    second.documentVariant!.materializedHash = 'd'.repeat(64)
    const oldPlan = compileRenderPlanFromScreenDefinition(first)
    const newPlan = compileRenderPlanFromScreenDefinition(second)
    expect(newPlan).not.toBe(oldPlan)
    expect(oldPlan.documentVariant?.variantVersion).toBe('1.0.0')
    expect(newPlan.documentVariant?.variantVersion).toBe('2.0.0')
    second.documentVariant!.variantVersion = '3.0.0'
    expect(newPlan.documentVariant?.variantVersion).toBe('2.0.0')
  })

  it.each(['plan', 'definition'] as const)('exposes the exact resolved reference through the %s path', (path) => {
    invalidateRenderPlanCache()
    const source = definition()
    render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><UniversalMaskRenderer {...(path === 'plan' ? { plan: compileRenderPlanFromScreenDefinition(source) } : { screen: source })} data={{ number: 'TEST-1' }} /></QueryClientProvider>)
    const root = screen.getByTestId('screen-tenant/document-version')
    expect(root).toHaveAttribute('data-document-base-version', '1.0.0')
    expect(root).toHaveAttribute('data-document-variant-id', 'sales_invoice')
    expect(root).toHaveAttribute('data-document-variant-version', '1.0.0')
    expect(root).toHaveAttribute('data-document-materialized-hash', 'c'.repeat(64))
    expect(screen.getByLabelText('Belegnummer')).toHaveValue('TEST-1')
  })
})
