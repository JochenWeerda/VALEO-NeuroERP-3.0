/* @refresh reload */
import { Suspense, lazy } from 'react'
import { type RouteObject, createBrowserRouter } from 'react-router-dom'
import { PageLoader } from '@/app/PageLoader'
import { createRouteElement } from '@/app/route-builders/route-elements'
import { ENABLE_PROSPECTING_UI } from '@/features/prospecting/feature-flags'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

const AUTH_REQUIRED = String((import.meta.env as Record<string, string | undefined>).VITE_AUTH_REQUIRED ?? '').toLowerCase() === 'true'

const AppLayout = lazy(() =>
  import('@/layouts/DashboardLayout').then((m) => ({ default: m.default })),
)

const CustomerPortalLayout = lazy(() =>
  import('@/layouts/CustomerPortalLayout').then((m) => ({ default: m.default })),
)

const AppRouteRuntime = lazy(() =>
  import('@/app/AppRouteRuntime').then((m) => ({ default: m.default })),
)

const PortalRouteRuntime = lazy(() =>
  import('@/app/PortalRouteRuntime').then((m) => ({ default: m.default })),
)

const FibuSuiteRuntime = lazy(() =>
  import('@/app/FibuSuiteRuntime').then((m) => ({ default: m.default })),
)

const routerConfig: RouteObject[] = [
  {
    path: '/portal',
    element: <Suspense fallback={<PageLoader />}><CustomerPortalLayout /></Suspense>,
    children: [
      {
        path: '*',
        element: <Suspense fallback={<PageLoader />}><PortalRouteRuntime /></Suspense>,
      },
    ],
  },
  {
    path: '/login',
    element: createRouteElement(() => import('@/pages/auth/Login')),
  },
  {
    path: '/auth/login',
    element: createRouteElement(() => import('@/pages/auth/Login')),
  },
  {
    path: '/auth/callback',
    element: createRouteElement(() => import('@/pages/auth/Callback')),
  },
  {
    path: '/',
    element: AUTH_REQUIRED ? (
      <ProtectedRoute>
        <Suspense fallback={<PageLoader />}><AppLayout /></Suspense>
      </ProtectedRoute>
    ) : (
      <Suspense fallback={<PageLoader />}><AppLayout /></Suspense>
    ),
    children: [
      {
        index: true,
        element: createRouteElement(() => import('@/pages/start-dashboard')),
      },
      {
        path: 'fibu-suite/*',
        element: <Suspense fallback={<PageLoader />}><FibuSuiteRuntime /></Suspense>,
      },
      {
        path: '*',
        element: <Suspense fallback={<PageLoader />}><AppRouteRuntime prospectingEnabled={ENABLE_PROSPECTING_UI} /></Suspense>,
      },
    ],
  },
]

export const router = createBrowserRouter(routerConfig, {
  future: {
    v7_relativeSplatPath: true,
    v7_fetcherPersist: true,
    v7_normalizeFormMethod: true,
    v7_partialHydration: true,
    v7_skipActionErrorRevalidation: true,
  },
})
