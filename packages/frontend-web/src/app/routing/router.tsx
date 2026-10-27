import { createRouter } from '@tanstack/react-router'
import { appLayoutRoute, routeTree } from '@/app/routing/route-tree.gen'
import { attachStudioPreviewRoute } from '@/workspace/studio-preview-route'

attachStudioPreviewRoute(appLayoutRoute)

export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
  defaultPreloadStaleTime: 30_000,
  scrollRestoration: true,
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }

  interface StaticDataRouteOption {
    breadcrumb?: string
    module?: string
    legacyPath?: string
  }
}
