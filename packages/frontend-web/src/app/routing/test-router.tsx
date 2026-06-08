import {
  RouterContextProvider,
  createMemoryHistory,
  createRootRoute,
  createRouter,
} from '@tanstack/react-router'
import {
  Children,
  isValidElement,
  type ReactNode,
} from 'react'
import {
  TypedParamsContext,
  matchPath,
  useLocation,
} from '@/app/routing/typed-router'

export * from '@/app/routing/typed-router'

type RouteProps = {
  path?: string
  element?: ReactNode
  children?: ReactNode
}

export function Route(_props: RouteProps): null {
  return null
}

export function MemoryRouter({
  children,
  initialEntries = ['/'],
}: {
  children: ReactNode
  initialEntries?: string[]
  future?: unknown
}): JSX.Element {
  const root = createRootRoute({ component: () => null })
  const router = createRouter({
    routeTree: root,
    history: createMemoryHistory({ initialEntries }),
    scrollRestoration: false,
  })
  return <RouterContextProvider router={router}>{children}</RouterContextProvider>
}

export function Routes({ children }: { children: ReactNode }): JSX.Element {
  const location = useLocation()
  for (const child of Children.toArray(children)) {
    if (!isValidElement<RouteProps>(child)) continue
    const match = matchPath({ path: child.props.path ?? '/', end: true }, location.pathname)
    if (match) {
      return (
        <TypedParamsContext.Provider value={match.params}>
          <>{child.props.element ?? child.props.children}</>
        </TypedParamsContext.Provider>
      )
    }
  }
  return <></>
}
