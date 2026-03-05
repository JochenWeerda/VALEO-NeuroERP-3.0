/* @refresh reload */
import { type ComponentType, Suspense, lazy } from 'react'
import { type RouteObject, createBrowserRouter } from 'react-router-dom'
import AppLayout from '@/layouts/DashboardLayout'
import CustomerPortalLayout from '@/layouts/CustomerPortalLayout'
import FibuSuiteLayout from '@/layouts/FibuSuiteLayout'
import { NAV_SECTIONS } from '@/app/navigation/manifest'
import { ErrorBoundary } from '@/shared/errors/ErrorBoundary'
import { PageLoader } from '@/app/PageLoader'
import { ENABLE_PROSPECTING_UI } from '@/features/prospecting/feature-flags'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import routeAliasData from './route-aliases.json'

type PageModule = { default: ComponentType<unknown> }
type PageModuleFactory = () => Promise<PageModule>
type RouteAliasEntry = {
  module: string
  path?: string
  index?: boolean
}

const pageModules = import.meta.glob<PageModule>('../pages/**/*.tsx')
const AUTH_REQUIRED = String((import.meta.env as Record<string, string | undefined>).VITE_AUTH_REQUIRED ?? '').toLowerCase() === 'true'

const AUTO_ROUTE_IGNORE_PATTERNS: RegExp[] = [
  /\/__tests__\//,
  /\.spec\.tsx$/,
  /\.test\.tsx$/,
  /\.stories\.tsx$/,
  /\/finance\/reports\/[^/]+\.tsx$/,
  /\/Dlg[A-Z][^/]*\.tsx$/,
]

const lazyComponentCache = new WeakMap<PageModuleFactory, ComponentType<unknown>>()

const FibuSuiteDashboard = lazy(() =>
  import('@/layouts/FibuSuiteDashboard').then((m) => ({ default: m.default })),
)

/** Suite-Pfad aus aufgelöster Nav-Path (z. B. /fibu/hauptbuch → hauptbuch, /finance/audit-trail → finance/audit-trail). */
function getFibuSuitePath(resolvedPath: string | undefined): string | null {
  if (!resolvedPath || resolvedPath === '/') return null
  const p = resolvedPath.startsWith('/') ? resolvedPath.slice(1) : resolvedPath
  if (p.startsWith('fibu/')) return p.replace('fibu/', '')
  if (p.startsWith('finance/')) return p
  if (p.startsWith('export/')) return p.replace('export/', '')
  if (p.startsWith('pos/')) return p
  return p
}

function buildFibuSuiteChildRoutes(): RouteObject[] {
  const fibu = NAV_SECTIONS.find((s) => s.id === 'fibu')
  const children = fibu?.children ?? []
  const routes: RouteObject[] = []
  for (const child of children) {
    if (!child.module) continue
    const path = getFibuSuitePath(child.path)
    if (!path) continue
    routes.push({ path, element: createRouteElementByModule(child.module) })
  }
  return routes
}

// Separate portal routes from main app routes
function isPortalModule(modulePath: string): boolean {
  return modulePath.includes('/portal/')
}

const routerConfig: RouteObject[] = [
  // Kundenportal mit eigenem Layout
  {
    path: '/portal',
    element: <CustomerPortalLayout />,
    children: buildPortalRoutes(),
  },
  {
    path: '/login',
    element: createRouteElementByModule('@/pages/auth/Login'),
  },
  {
    path: '/auth/login',
    element: createRouteElementByModule('@/pages/auth/Login'),
  },
  {
    path: '/auth/callback',
    element: createRouteElementByModule('@/pages/auth/Callback'),
  },
  // Hauptanwendung
  {
    path: '/',
    element: AUTH_REQUIRED ? (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ) : (
      <AppLayout />
    ),
    children: [
      {
        path: 'fibu-suite',
        element: <FibuSuiteLayout />,
        children: [
          { index: true, element: <Suspense fallback={<PageLoader />}><FibuSuiteDashboard /></Suspense> },
          ...buildFibuSuiteChildRoutes(),
        ],
      },
      ...buildAutoRoutes(),
      ...buildAliasRoutes(routeAliasData.aliases ?? []),
      { path: '*', element: createRouteElementByModule('@/pages/errors/NotFound') },
    ],
  },
]

function buildPortalRoutes(): RouteObject[] {
  return Object.entries(pageModules)
    .filter(([modulePath]) => isPortalModule(modulePath) && isAutoRoutable(modulePath))
    .map(([modulePath, loader]) => {
      const routePath = modulePathToRoutePath(modulePath).replace('portal/', '').replace('portal', '')
      const element = createRouteElement(loader)
      
      // Index route for /portal
      if (routePath === '' || routePath === '/') {
        return { index: true, element }
      }
      
      return { path: routePath, element }
    })
}

export const router = createBrowserRouter(routerConfig, {
  future: {
    v7_relativeSplatPath: true,
    v7_fetcherPersist: true,
    v7_normalizeFormMethod: true,
    v7_partialHydration: true,
    v7_skipActionErrorRevalidation: true,
  },
})

function buildAutoRoutes(): RouteObject[] {
  return Object.entries(pageModules)
    .filter(([modulePath]) => isAutoRoutableMainApp(modulePath))
    .map(([modulePath, loader]) => createRouteObject(modulePath, loader))
    .sort(compareRouteObjects)
}

function buildAliasRoutes(entries: RouteAliasEntry[]): RouteObject[] {
  const filteredEntries = entries.filter((entry) => ENABLE_PROSPECTING_UI || !isProspectingModule(entry.module))

  return filteredEntries.flatMap((entry): RouteObject[] => {
    const moduleKey = resolveModuleKey(entry.module)
    const loader = pageModules[moduleKey]

    if (!loader) {
      throw new Error(`Route alias references unknown module: ${entry.module}`)
    }

    const element = createRouteElement(loader)
    if (!entry.path) {
      if (entry.index) {
        return [{ index: true, element }]
      }
      throw new Error(`Route alias for ${entry.module} requires either path or index.`)
    }

    return [{ path: entry.path, element }]
  })
}

function createRouteObject(modulePath: string, loader: PageModuleFactory): RouteObject {
  const routePath = modulePathToRoutePath(modulePath)
  const element = createRouteElement(loader)

  if (routePath === '/') {
    return { path: '/', element }
  }

  return { path: routePath, element }
}

function modulePathToRoutePath(modulePath: string): string {
  let relativePath = modulePath.replace('../pages/', '').replace(/\.tsx$/, '')
  if (relativePath.endsWith('/index')) {
    relativePath = relativePath.slice(0, -6)
  }
  if (relativePath === 'index' || relativePath === '') {
    return '/'
  }
  return relativePath
}

function resolveModuleKey(modulePath: string): string {
  let resolved = modulePath.replace(/^@\//, '../')
  if (!resolved.startsWith('../')) {
    resolved = `../${resolved}`
  }
  if (!resolved.endsWith('.tsx')) {
    resolved = `${resolved}.tsx`
  }
  return resolved
}

function createRouteElementByModule(modulePath: string): JSX.Element {
  const moduleKey = resolveModuleKey(modulePath)
  const loader = pageModules[moduleKey]
  if (!loader) {
    throw new Error(`Route references unknown module: ${modulePath}`)
  }
  return createRouteElement(loader)
}

function isAutoRoutable(modulePath: string): boolean {
  if (!ENABLE_PROSPECTING_UI && isProspectingModule(modulePath)) {
    return false
  }
  return !AUTO_ROUTE_IGNORE_PATTERNS.some((pattern) => pattern.test(modulePath))
}

function isAutoRoutableMainApp(modulePath: string): boolean {
  // Exclude portal modules from main app routes
  if (isPortalModule(modulePath)) {
    return false
  }
  return isAutoRoutable(modulePath)
}

function compareRouteObjects(a: RouteObject, b: RouteObject): number {
  const pathA = 'path' in a && typeof a.path === 'string' ? a.path : ''
  const pathB = 'path' in b && typeof b.path === 'string' ? b.path : ''
  return pathA.localeCompare(pathB)
}

function createRouteElement(loader: PageModuleFactory): JSX.Element {
  let Component = lazyComponentCache.get(loader)
  if (!Component) {
    Component = lazy(loader)
    lazyComponentCache.set(loader, Component)
  }

  return (
    <ErrorBoundary
      fallback={
        <div className="flex h-96 items-center justify-center">
          <div className="text-center">
            <h2 className="mb-2 text-xl font-semibold text-red-600">Fehler beim Laden der Seite</h2>
            <p className="mb-4 text-muted-foreground">Es ist ein unerwarteter Fehler aufgetreten.</p>
            <button
              onClick={() => window.location.reload()}
              className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              Seite neu laden
            </button>
          </div>
        </div>
      }
    >
      <Suspense fallback={<PageLoader />}>
        <Component />
      </Suspense>
    </ErrorBoundary>
  )
}

function isProspectingModule(moduleSpecifier: string): boolean {
  return moduleSpecifier.includes('/prospecting/')
}

