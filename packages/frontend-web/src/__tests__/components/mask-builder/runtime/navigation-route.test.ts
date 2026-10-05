import { describe, expect, it } from 'vitest'
import { resolveNavigationRoute } from '@/components/mask-builder/runtime/navigation-route'

describe('resolveNavigationRoute', () => {
  it('opens pflege with the partner id', () => {
    expect(resolveNavigationRoute(
      '/verkauf/kunden-stamm/{business_partner_id}?pflege=1',
      { businessPartnerId: 'bp-42' },
    )).toBe('/verkauf/kunden-stamm/bp-42?pflege=1')
  })

  it('refuses pflege when the partner id is missing', () => {
    expect(resolveNavigationRoute(
      '/verkauf/kunden-stamm/{business_partner_id}?pflege=1',
      { entityId: 'cust-1' },
    )).toBeNull()
  })

  it('fills the entity id placeholder', () => {
    expect(resolveNavigationRoute(
      '/crm/kunden/{entity_id}',
      { entityId: 'cust-1' },
    )).toBe('/crm/kunden/cust-1')
  })
})
