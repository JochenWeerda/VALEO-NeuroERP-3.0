import {
  Link as TanStackLink,
  Navigate as TanStackNavigate,
  Outlet,
  useBlocker as useTanStackBlocker,
  useLocation as useTanStackLocation,
  useNavigate as useTanStackNavigate,
  useRouter,
  useRouterState,
} from '@tanstack/react-router'
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  type AnchorHTMLAttributes,
  type ComponentProps,
  type ReactNode,
} from 'react'
import type {
  AppRouteHref,
  AppRouteParamKey,
  AppSearchKey,
} from '@/app/routing/route-contract'

type NavigateOptions = {
  replace?: boolean
  state?: unknown
}

export const TypedParamsContext = createContext<Record<string, string | undefined> | null>(null)

export type RouteTarget =
  | AppRouteHref
  | {
      pathname?: AppRouteHref
      search?: string
      hash?: string
    }

function stringifyTarget(to: RouteTarget): string {
  if (typeof to === 'string') return to
  return `${to.pathname ?? ''}${to.search ?? ''}${to.hash ?? ''}` || '/'
}

export function useNavigate(): (to: RouteTarget | number, options?: NavigateOptions) => void {
  const navigate = useTanStackNavigate()
  const router = useRouter()
  return useCallback(
    (to: RouteTarget | number, options?: NavigateOptions) => {
      if (typeof to === 'number') {
        router.history.go(to)
        return
      }
      void navigate({
        to: stringifyTarget(to) as never,
        replace: options?.replace,
        state: options?.state as never,
      })
    },
    [navigate, router],
  )
}

export function useParams<
  TParams extends Partial<Record<AppRouteParamKey, string | undefined>> =
    Partial<Record<AppRouteParamKey, string | undefined>>,
>(): TParams {
  const contextParams = useContext(TypedParamsContext)
  const matches = useRouterState({ select: (state) => state.matches })
  return (contextParams ?? Object.assign({}, ...matches.map((match) => match.params))) as TParams
}

export function useLocation(): {
  pathname: string
  search: string
  hash: string
  state: unknown
  key: string
} {
  const location = useTanStackLocation()
  return {
    pathname: location.pathname,
    search: location.searchStr,
    hash: location.hash,
    state: location.state,
    key: String((location.state as { key?: string } | undefined)?.key ?? location.href),
  }
}

export type TypedSearchParams = Omit<URLSearchParams, 'get' | 'getAll' | 'has'> & {
  get(name: AppSearchKey): string | null
  getAll(name: AppSearchKey): string[]
  has(name: AppSearchKey, value?: string): boolean
}

type SearchUpdate =
  | URLSearchParams
  | Partial<Record<AppSearchKey, string>>
  | ((previous: TypedSearchParams) => URLSearchParams)

export function useSearchParams(): [
  TypedSearchParams,
  (next: SearchUpdate, options?: NavigateOptions) => void,
] {
  const location = useTanStackLocation()
  const navigate = useTanStackNavigate()
  const params = useMemo(
    () => new URLSearchParams(location.searchStr) as TypedSearchParams,
    [location.searchStr],
  )
  const setParams = useCallback(
    (next: SearchUpdate, options?: NavigateOptions) => {
      const resolved = typeof next === 'function' ? next(params) : next
      const search =
        resolved instanceof URLSearchParams
          ? resolved.toString()
          : new URLSearchParams(resolved as Record<string, string>).toString()
      void navigate({
        to: `${location.pathname}${search ? `?${search}` : ''}` as never,
        replace: options?.replace,
        state: options?.state as never,
      })
    },
    [location.pathname, navigate, params],
  )
  return [params, setParams]
}

type LinkProps = Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href'> & {
  to: RouteTarget
  replace?: boolean
  state?: unknown
}

export function Link({ to, replace, state, ...props }: LinkProps): JSX.Element {
  return (
    <TanStackLink
      {...(props as ComponentProps<typeof TanStackLink>)}
      to={stringifyTarget(to) as never}
      replace={replace}
      state={state as never}
    />
  )
}

type NavLinkProps = Omit<LinkProps, 'className' | 'children'> & {
  end?: boolean
  className?: string | ((state: { isActive: boolean; isPending: boolean }) => string)
  children?: ReactNode | ((state: { isActive: boolean; isPending: boolean }) => ReactNode)
}

export function NavLink({ className, children, end = false, ...props }: NavLinkProps): JSX.Element {
  const location = useTanStackLocation()
  const target = stringifyTarget(props.to).split(/[?#]/, 1)[0] || '/'
  const isActive = end
    ? location.pathname === target
    : target === '/'
      ? location.pathname === '/'
      : location.pathname.startsWith(target)
  const state = { isActive, isPending: false }
  return (
    <TanStackLink
      {...(props as ComponentProps<typeof TanStackLink>)}
      to={stringifyTarget(props.to) as never}
      activeOptions={{ exact: false }}
      className={typeof className === 'function' ? className(state) : className}
    >
      {typeof children === 'function' ? children(state) : children}
    </TanStackLink>
  )
}

export function Navigate({
  to,
  replace,
  state,
}: {
  to: RouteTarget
  replace?: boolean
  state?: unknown
}): JSX.Element {
  return <TanStackNavigate to={stringifyTarget(to) as never} replace={replace} state={state as never} />
}

export { Outlet }

type BlockerLocation = {
  pathname: string
}

type ShouldBlock = (args: {
  currentLocation: BlockerLocation
  nextLocation: BlockerLocation
}) => boolean | Promise<boolean>

type Blocker = {
  state: 'blocked' | 'unblocked'
  proceed?: () => void
  reset?: () => void
}

export function useBlocker(shouldBlock: ShouldBlock): Blocker {
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
    ? { state: 'blocked', proceed: blocker.proceed, reset: blocker.reset }
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
