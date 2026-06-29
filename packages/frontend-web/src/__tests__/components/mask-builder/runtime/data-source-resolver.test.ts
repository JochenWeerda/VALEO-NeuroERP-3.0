import { describe, expect, it } from 'vitest'
import { resolveEndpoint } from '@/components/mask-builder/runtime/data-source-resolver'

describe('resolveEndpoint', () => {
  it('substitutes a single variable', () => {
    expect(resolveEndpoint('/api/v1/crm/customers/{entity_id}', { entity_id: '42' })).toBe(
      '/api/v1/crm/customers/42',
    )
  })

  it('substitutes multiple variables', () => {
    expect(
      resolveEndpoint('/api/v1/{tenant_id}/customers/{entity_id}/tabs', {
        entity_id: 'abc',
        tenant_id: 'tenant1',
      }),
    ).toBe('/api/v1/tenant1/customers/abc/tabs')
  })

  it('replaces unknown variables with empty string', () => {
    expect(resolveEndpoint('/api/v1/customers/{entity_id}', {})).toBe('/api/v1/customers/')
  })

  it('returns template unchanged when no variables present', () => {
    expect(resolveEndpoint('/api/v1/stammdaten/laender', {})).toBe('/api/v1/stammdaten/laender')
  })
})
