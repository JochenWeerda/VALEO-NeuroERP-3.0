import { createRoute, type AnyRoute } from '@tanstack/react-router'
import { createRouteElement } from '@/app/route-builders/route-elements'
import { WORKSPACE_COMPOSITION_PREVIEW_ROUTE } from '@/studio/workspace-composition-runtime'

/** Relativer TanStack-Pfad unter dem App-Layout. */
export const STUDIO_PREVIEW_ROUTE_SEGMENT = 'studio/workspace-composition-preview'

export function createStudioPreviewRoute(parent: AnyRoute) {
  return createRoute({
    getParentRoute: () => parent,
    path: STUDIO_PREVIEW_ROUTE_SEGMENT,
    component: () =>
      createRouteElement(() => import('@/pages/studio/workspace-composition-preview')),
    staticData: {
      breadcrumb: 'Workspace Composition',
      module: '@/pages/studio/workspace-composition-preview',
      legacyPath: WORKSPACE_COMPOSITION_PREVIEW_ROUTE,
    },
  })
}

function routePath(route: unknown): string | undefined {
  const value = route as { path?: string; options?: { path?: string } }
  return value.path ?? value.options?.path
}

export function attachStudioPreviewRoute(layoutRoute: AnyRoute): void {
  const existing = Array.isArray(layoutRoute.children) ? layoutRoute.children : []
  if (existing.some((child) => routePath(child) === STUDIO_PREVIEW_ROUTE_SEGMENT)) {
    return
  }
  layoutRoute.addChildren([...existing, createStudioPreviewRoute(layoutRoute)])
}
