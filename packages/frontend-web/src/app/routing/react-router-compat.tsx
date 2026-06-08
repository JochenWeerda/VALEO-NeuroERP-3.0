import {
  Link as TanStackLink,
  Navigate as TanStackNavigate,
  Outlet,
  RouterContextProvider,
  createMemoryHistory,
  createRootRoute,
  createRouter,
  useLocation as useTanStackLocation,
  useBlocker as useTanStackBlocker,
  useNavigate as useTanStackNavigate,
  useRouter,
  useRouterState,
} from '@tanstack/react-router'
import {
  Children,
  createContext,
  isValidElement,
  useCallback,
  useContext,
  useMemo,
  type AnchorHTMLAttributes,
  type ComponentProps,
  type ReactNode,
} from 'react'

type NavigateOptions = {
  replace?: boolean
  state?: unknown
}

const CompatParamsContext = createContext<Record<string, string | undefined> | null>(null)

type To = string | { pathname?: string; search?: string; hash?: string }

function stringifyTo(to: To): string {
  if (typeof to === 'string') return to
  return `${to.pathname ?? ''}${to.search ?? ''}${to.hash ?? ''}` || '/'
}

export function useNavigate(): (to: To | number, options?: NavigateOptions) => void {
  const navigate = useTanStackNavigate()
  const router = useRouter()
  return useCallback(
    (to: To | number, options?: NavigateOptions) => {
      if (typeof to === 'number') {
        router.history.go(to)
        return
      }
      void navigate({
        to: stringifyTo(to) as never,
        replace: options?.replace,
        state: options?.state as never,
      })
    },
    [navigate, router],
  )
}

export function useParams<T extends Record<string, string | undefined> = Record<string, string | undefined>>(): T {
  const compatParams = useContext(CompatParamsContext)
  const matches = useRouterState({ select: (state) => state.matches })
  return (compatParams ?? Object.assign({}, ...matches.map((match) => match.params))) as T
}

export function useLocation(): {
  pathname: string
  search: string
  hash: string
  state: any
  key: string
} {
  const location = useTanStackLocation()
  return {
    pathname: location.pathname,
    search: location.searchStr,
    hash: location.hash,
    state: location.state as unknown,
    key: String((location.state as { key?: string } | undefined)?.key ?? location.href),
  }
}

export function useSearchParams(): [
  URLSearchParams,
  (next: URLSearchParams | Record<string, string> | ((previous: URLSearchParams) => URLSearchParams)) => void,
] {
  const location = useTanStackLocation()
  const navigate = useTanStackNavigate()
  const params = useMemo(() => new URLSearchParams(location.searchStr), [location.searchStr])
  const setParams = useCallback(
    (next: URLSearchParams | Record<string, string> | ((previous: URLSearchParams) => URLSearchParams)) => {
      const resolved = typeof next === 'function' ? next(new URLSearchParams(params)) : next
      const search = resolved instanceof URLSearchParams ? resolved.toString() : new URLSearchParams(resolved).toString()
      void navigate({ to: `${location.pathname}${search ? `?${search}` : ''}` as never })
    },
    [location.pathname, navigate, params],
  )
  return [params, setParams]
}

type LinkProps = Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href'> & {
  to: To
  replace?: boolean
  state?: unknown
}

export function Link({ to, replace, state, ...props }: LinkProps): JSX.Element {
  return <TanStackLink {...(props as ComponentProps<typeof TanStackLink>)} to={stringifyTo(to) as never} replace={replace} state={state as never} />
}

type NavLinkProps = Omit<LinkProps, 'className' | 'children'> & {
  end?: boolean
  className?: string | ((state: { isActive: boolean; isPending: boolean }) => string)
  children?: ReactNode | ((state: { isActive: boolean; isPending: boolean }) => ReactNode)
}

export function NavLink({ className, children, end = false, ...props }: NavLinkProps): JSX.Element {
  const location = useTanStackLocation()
  const target = stringifyTo(props.to).split(/[?#]/, 1)[0] || '/'
  const isActive = end
    ? location.pathname === target
    : target === '/'
      ? location.pathname === '/'
      : location.pathname.startsWith(target)
  const state = { isActive, isPending: false }
  return (
    <TanStackLink
      {...(props as ComponentProps<typeof TanStackLink>)}
      to={stringifyTo(props.to) as never}
      activeOptions={{ exact: false }}
      className={typeof className === 'function' ? className(state) : className}
    >
      {typeof children === 'function' ? children(state) : children}
    </TanStackLink>
  )
}

export function Navigate({ to, replace, state }: { to: To; replace?: boolean; state?: unknown }): JSX.Element {
  return <TanStackNavigate to={stringifyTo(to) as never} replace={replace} state={state as never} />
}

export { Outlet }

type CompatBlockerLocation = {
  pathname: string
}

type CompatShouldBlock = (args: {
  currentLocation: CompatBlockerLocation
  nextLocation: CompatBlockerLocation
}) => boolean | Promise<boolean>

type CompatBlocker = {
  state: 'blocked' | 'unblocked'
  proceed?: () => void
  reset?: () => void
}

export function useBlocker(shouldBlock: CompatShouldBlock): CompatBlocker {
  const blocker = useTanStackBlocker({
    shouldBlockFn: ({ current, next }) =>
      shouldBlock({
        currentLocation: { pathname: current.pathname },
        nextLocation: { pathname: next.pathname },
      }),
    enableBeforeUnload: true,
    withResolver: true,
  })

  return blocker.status === 'blocked'
    ? {
        state: 'blocked',
        proceed: blocker.proceed,
        reset: blocker.reset,
      }
    : { state: 'unblocked' }
}

export function matchPath(
  pattern: string | { path: string; end?: boolean; caseSensitive?: boolean },
  pathname: string,
): { params: Record<string, string>; pathname: string; pathnameBase: string; pattern: unknown } | null {
  const config = typeof pattern === 'string' ? { path: pattern, end: true } : pattern
  const names: string[] = []
  const normalizedPattern =
    pathname.startsWith('/') && !config.path.startsWith('/') ? `/${config.path}` : config.path
  const source = normalizedPattern
    .replace(/[.+?^${}()|[\]\\]/g, '\\$&')
    .replace(/:([A-Za-z0-9_]+)/g, (_match, name) => {
      names.push(name)
      return '([^/]+)'
    })
    .replace(/\\\*/g, '(.*)')
  const regex = new RegExp(`^${source}${config.end === false ? '(?:/|$)' : '/?$'}`, config.caseSensitive ? '' : 'i')
  const match = regex.exec(pathname)
  if (!match) return null
  return {
    params: Object.fromEntries(names.map((name, index) => [name, decodeURIComponent(match[index + 1] ?? '')])),
    pathname: match[0],
    pathnameBase: match[0].replace(/\/$/, '') || '/',
    pattern: config,
  }
}

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
  const memoryRouter = createRouter({
    routeTree: root,
    history: createMemoryHistory({ initialEntries }),
    scrollRestoration: false,
  })
  return <RouterContextProvider router={memoryRouter}>{children}</RouterContextProvider>
}

export function Routes({ children }: { children: ReactNode }): JSX.Element {
  const location = useLocation()
  for (const child of Children.toArray(children)) {
    if (!isValidElement<RouteProps>(child)) continue
    const match = matchPath({ path: child.props.path ?? '/', end: true }, location.pathname)
    if (match) {
      return (
        <CompatParamsContext.Provider value={match.params}>
          <>{child.props.element ?? child.props.children}</>
        </CompatParamsContext.Provider>
      )
    }
  }
  return <></>
}
