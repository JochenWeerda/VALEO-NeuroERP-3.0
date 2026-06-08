import { describe, expect, it } from 'vitest'
import {
  appendRouteSearch,
  buildRoute,
  type AppRouteParams,
} from '@/app/routing/route-contract'

describe('typed route contract', () => {
  it('builds static and parameterized deep links', () => {
    expect(buildRoute('/crm')).toBe('/crm')
    expect(buildRoute('/crm/lead/:id', { id: 'lead/42' })).toBe('/crm/lead/lead%2F42')
    expect(buildRoute('/einkauf/rechnung-abgleich/:invoiceId', { invoiceId: 4711 })).toBe(
      '/einkauf/rechnung-abgleich/4711',
    )
    expect(buildRoute('/verify/:domain/:number/:hash', {
      domain: 'invoice',
      number: 'R/42',
      hash: 'abc',
    })).toBe('/verify/invoice/R%2F42/abc')
    expect(appendRouteSearch('/crm', { search: 'Nord', workflowCase: 42 })).toBe(
      '/crm?search=Nord&workflowCase=42',
    )
  })

  it('exposes exact parameter names to TypeScript', () => {
    const params: AppRouteParams<'/agrar/ernte/:id'> = { id: 17 }
    expect(params).toEqual({ id: 17 })

    if (false) {
      // @ts-expect-error Unknown paths must fail during compilation.
      buildRoute('/route-that-does-not-exist')
      // @ts-expect-error Dynamic routes require all declared parameters.
      buildRoute('/crm/lead/:id')
      // @ts-expect-error Parameter names are part of the route contract.
      buildRoute('/crm/lead/:id', { leadId: '42' })
      // @ts-expect-error Generated multi-parameter routes require every parameter.
      buildRoute('/verify/:domain/:number/:hash', { domain: 'invoice', number: 'R-42' })
      // @ts-expect-error Search keys are harvested into a closed union.
      appendRouteSearch('/crm', { arbitraryQueryKey: 'value' })
      // @ts-expect-error Search values must be URL-serializable primitives.
      appendRouteSearch('/crm', { search: { nested: true } })
    }
  })
})
