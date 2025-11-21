import { type ComponentType, Suspense, lazy } from 'react'
import { type RouteObject, createBrowserRouter } from 'react-router-dom'
import AppLayout from '@/layouts/DashboardLayout'
import { ErrorBoundary } from '@/shared/errors/ErrorBoundary'
import { PageLoader } from '@/app/PageLoader'
import { ENABLE_PROSPECTING_UI } from '@/features/prospecting/feature-flags'
import routeAliasData from './route-aliases.json'

type PageModuleFactory = () => Promise<{ default: ComponentType<unknown> }>
type RouteAliasEntry = {
  module: string
  path?: string
  index?: boolean
}

const pageModules = import.meta.glob<PageModuleFactory>('../pages/**/*.tsx')

const AUTO_ROUTE_IGNORE_PATTERNS: RegExp[] = [
  /\/__tests__\//,
  /\.spec\.tsx$/,
  /\.test\.tsx$/,
  /\.stories\.tsx$/,
]

const lazyComponentCache = new WeakMap<PageModuleFactory, ComponentType<unknown>>()

const routerConfig: RouteObject[] = [
  {
    path: '/',
    element: <AppLayout />,
    children: [...buildAutoRoutes(), ...buildAliasRoutes(routeAliasData.aliases ?? [])],
  },
]

export const router = createBrowserRouter(routerConfig)

function buildAutoRoutes(): RouteObject[] {
  return Object.entries(pageModules)
    .filter(([modulePath]) => isAutoRoutable(modulePath))
    .map(([modulePath, loader]) => createRouteObject(modulePath, loader))
    .sort(compareRouteObjects)
}

function buildAliasRoutes(entries: RouteAliasEntry[]): RouteObject[] {
  const filteredEntries = entries.filter((entry) => ENABLE_PROSPECTING_UI || !isProspectingModule(entry.module))

  return filteredEntries.flatMap((entry) => {
    const moduleKey = resolveModuleKey(entry.module)
    const loader = pageModules[moduleKey]

    if (!loader) {
      throw new Error(`Route-Alias verweist auf unbekanntes Modul: ${entry.module}`)
    }

    const element = createRouteElement(loader)
    if (entry.index) {
      return [{ index: true, element }]
    }
    if (!entry.path) {
      throw new Error(`Route-Alias für ${entry.module} benötigt entweder path oder index.`)
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

function isAutoRoutable(modulePath: string): boolean {
  if (!ENABLE_PROSPECTING_UI && isProspectingModule(modulePath)) {
    return false
  }
  return !AUTO_ROUTE_IGNORE_PATTERNS.some((pattern) => pattern.test(modulePath))
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
