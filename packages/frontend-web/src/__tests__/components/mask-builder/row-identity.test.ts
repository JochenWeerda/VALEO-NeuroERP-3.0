import { describe, expect, it } from 'vitest'
import { resolveRowRoute } from '@/components/mask-builder/renderers/row-identity'

describe('resolveRowRoute', () => {
  it('ersetzt Pfadsegmente kodiert', () => {
    expect(resolveRowRoute('/lager/stock-movement/{movement_id}', { movement_id: 'mv 1' }))
      .toBe('/lager/stock-movement/mv%201')
  })

  it('laesst eine vollstaendige Quellroute unkodiert', () => {
    expect(resolveRowRoute('{source_route}', { source_route: '/verkauf/lieferschein/1' }))
      .toBe('/verkauf/lieferschein/1')
  })

  it('verwirft Protokoll-relative und leere Quellrouten', () => {
    expect(resolveRowRoute('{source_route}', { source_route: '//evil.example/x' })).toBeUndefined()
    expect(resolveRowRoute('{source_route}', { source_route: '' })).toBeUndefined()
    expect(resolveRowRoute('{source_route}', {})).toBeUndefined()
  })
})
