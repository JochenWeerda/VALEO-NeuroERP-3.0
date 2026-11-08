import { createMemoryHistory, createRouter } from '@tanstack/react-router'
import { describe, expect, it, vi } from 'vitest'
import { routeTree } from '@/app/routing/route-tree.gen'

// Keep the actual generated tree and matching algorithm; omit presentation.
vi.mock('@/app/routing/route-layouts', () => ({
  RootRouteLayout: () => null, AppRouteLayout: () => null,
  PortalRouteLayout: () => null, renderPage: () => null,
}))

describe('actual public authentication route matching', () => {
  it.each(['/login', '/auth/login', '/auth/callback', '/LOGIN', '/auth/Login', '/auth/Callback'])(
    'keeps %s outside the protected ERP layout', path => {
      const router = createRouter({ routeTree, history: createMemoryHistory({ initialEntries: [path] }) })
      const matches = router.matchRoutes(path)
      expect(matches.at(-1)?.routeId.toLowerCase()).toBe(path.toLowerCase())
      expect(matches.some(match => match.routeId.includes('_app'))).toBe(false)
    },
  )

  it('keeps the ordinary ERP dashboard behind the protected layout', () => {
    const router = createRouter({ routeTree, history: createMemoryHistory({ initialEntries: ['/'] }) })
    expect(router.matchRoutes('/').some(match => match.routeId.includes('_app'))).toBe(true)
  })
})
