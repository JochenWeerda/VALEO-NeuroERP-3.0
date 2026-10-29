import { createRootRoute, createRoute } from '@tanstack/react-router'
import { describe, expect, it } from 'vitest'
import { router } from '@/app/routing/router'
import { WORKSPACE_COMPOSITION_PREVIEW_ROUTE } from '@/studio/workspace-composition-runtime'
import {
  STUDIO_PREVIEW_ROUTE_SEGMENT,
  attachStudioPreviewRoute,
} from '@/workspace'

describe('studio preview route', () => {
  it('haengt die bestehende Preview-Page additiv unter das App-Layout', () => {
    const root = createRootRoute({ component: () => null })
    const layout = createRoute({ getParentRoute: () => root, id: '_app', component: () => null })
    root.addChildren([layout.addChildren([])])
    attachStudioPreviewRoute(layout)
    attachStudioPreviewRoute(layout)
    const children = layout.children ?? []
    const paths = children.map((child) => {
      const route = child as { path?: string; options?: { path?: string } }
      return route.path ?? route.options?.path
    })
    expect(paths.filter((path) => path === STUDIO_PREVIEW_ROUTE_SEGMENT)).toHaveLength(1)
    expect(`/${STUDIO_PREVIEW_ROUTE_SEGMENT}`).toBe(WORKSPACE_COMPOSITION_PREVIEW_ROUTE)
  })

  it('laesst den generierten Routenbaum stehen und ergaenzt die Preview', () => {
    expect(router.routesByPath['/']).toBeTruthy()
    expect(router.routesByPath[WORKSPACE_COMPOSITION_PREVIEW_ROUTE]).toBeTruthy()
  })
})
