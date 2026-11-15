import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { validateScreenDefinition, type ScreenDefinition } from '@/components/mask-builder/schema'
import { compileRenderPlanFromScreenDefinition, invalidateRenderPlanCache } from '@/components/mask-builder/render-plan/schema-compiler'

const binding = () => ({ family: 'kontrakt', baseVersion: '1.0.0', baseHash: 'a'.repeat(64),
  variantId: 'verkauf', variantVersion: '1.0.0', variantHash: 'b'.repeat(64), materializedHash: 'c'.repeat(64) })

function definition() {
  return { schemaVersion: 1, id: 'tenant/contract-version', domain: 'sales', mode: 'detail', title: 'Kontrakt',
    layout: { floorplan: 'objectPage', columnNavigation: 'single', contextRail: 'none' },
    fields: [{ key: 'number', label: 'Nummer', type: 'text', readOnly: true }], maskVariant: binding(),
  } as ScreenDefinition & { maskVariant: ReturnType<typeof binding> }
}

describe('general mask family version binding', () => {
  it('keeps each immutable origin and changes cache when only the variant version changes', () => {
    invalidateRenderPlanCache()
    const first = definition(), second = definition()
    expect(validateScreenDefinition(first)).toEqual([])
    second.maskVariant.variantVersion = '2.0.0'
    const oldPlan = compileRenderPlanFromScreenDefinition(first)
    const newPlan = compileRenderPlanFromScreenDefinition(second)
    expect(newPlan).not.toBe(oldPlan)
    expect(oldPlan.maskVariant?.variantVersion).toBe('1.0.0')
    expect(newPlan.maskVariant?.variantVersion).toBe('2.0.0')
    second.maskVariant.variantVersion = '3.0.0'
    expect(newPlan.maskVariant?.variantVersion).toBe('2.0.0')
  })

  it.each(['plan', 'definition'] as const)('exposes origin via the %s path', path => {
    invalidateRenderPlanCache()
    const source = definition()
    render(<QueryClientProvider client={new QueryClient()}><UniversalMaskRenderer {...(path === 'plan' ? { plan: compileRenderPlanFromScreenDefinition(source) } : { screen: source })} data={{ number: 'K-1' }} /></QueryClientProvider>)
    const root = screen.getByTestId('screen-tenant/contract-version')
    expect(root).toHaveAttribute('data-mask-family', 'kontrakt')
    expect(root).toHaveAttribute('data-mask-base-version', '1.0.0')
    expect(root).toHaveAttribute('data-mask-variant-id', 'verkauf')
    expect(root).toHaveAttribute('data-mask-variant-version', '1.0.0')
    expect(root).toHaveAttribute('data-mask-materialized-hash', 'c'.repeat(64))
    expect(screen.getByLabelText('Nummer')).toHaveValue('K-1')
  })

  it.each(['beleg', 'A', 'a', 'bad_family', 'a'.repeat(42)])('rejects invalid general family %s', family => {
    const source = definition(); source.maskVariant.family = family
    expect(validateScreenDefinition(source)).toContain('maskVariant requires an exact valid base and variant binding')
    expect(() => compileRenderPlanFromScreenDefinition(source)).toThrow('Invalid mask family binding')
  })

  it('rejects broken hashes and ambiguous document plus general bindings', () => {
    const source = definition(); source.maskVariant.materializedHash = 'broken'
    expect(validateScreenDefinition(source)).toContain('maskVariant requires an exact valid base and variant binding')
    source.maskVariant = JSON.parse(JSON.stringify({ ...binding(), baseVersion: ['1.0.0'] }))
    expect(validateScreenDefinition(source)).toContain('maskVariant requires an exact valid base and variant binding')
    source.maskVariant = binding()
    source.documentVariant = { ...binding(), family: 'beleg' }
    expect(validateScreenDefinition(source)).toContain('documentVariant and maskVariant cannot both be present')
    expect(() => compileRenderPlanFromScreenDefinition(source)).toThrow('Invalid mask family binding')
  })
})
