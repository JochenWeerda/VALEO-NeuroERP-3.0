import { Outlet } from '@tanstack/react-router'
import { createRouteElementByModule } from '@/app/page-module-loader'
import DashboardLayout from '@/layouts/DashboardLayout'
import CustomerPortalLayout from '@/layouts/CustomerPortalLayout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import FibuSuiteRuntime from '@/app/FibuSuiteRuntime'

export function renderPage(modulePath: string): JSX.Element {
  if (modulePath === '@runtime/fibu-suite') {
    return <FibuSuiteRuntime />
  }
  return createRouteElementByModule(modulePath)
}

export function RootRouteLayout(): JSX.Element {
  return <Outlet />
}

export function AppRouteLayout(): JSX.Element {
  const authRequired =
    String((import.meta.env as Record<string, string | undefined>).VITE_AUTH_REQUIRED ?? '').toLowerCase() === 'true'

  if (!authRequired) {
    return <DashboardLayout />
  }

  return (
    <ProtectedRoute>
      <DashboardLayout />
    </ProtectedRoute>
  )
}

export function PortalRouteLayout(): JSX.Element {
  return <CustomerPortalLayout />
}
