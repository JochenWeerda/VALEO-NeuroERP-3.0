/**
 * ProtectedRoute Component
 * Route-Protection mit OIDC-Authentication
 */

import { ReactNode } from 'react'
import { Navigate } from '@/app/routing/react-router-compat'
import { Loader2 } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

interface ProtectedRouteProps {
  children: ReactNode
  requiredScopes?: string[]
  requiredRoles?: string[]
}

export function ProtectedRoute({
  children,
  requiredScopes = [],
  requiredRoles = [],
}: ProtectedRouteProps): JSX.Element | null {
  const { isAuthenticated, loading, hasScope, hasRole, user } = useAuth()
  const isLoading = loading === true
  const authenticated = isAuthenticated === true
  // Check if OIDC is actually configured (not just placeholder)
  const discoveryUrl = (import.meta.env.VITE_OIDC_DISCOVERY_URL ?? '')
  const placeholderPatterns = ['your-oidc-provider.com', 'example.com', 'keycloak.example.com', '{tenant-id}', '{domain}', '{application-id}', '{client-id}']
  const oidcConfigured = discoveryUrl.length > 0 && !placeholderPatterns.some(pattern => discoveryUrl.includes(pattern))

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  // Only redirect to login if OIDC is configured and user is not authenticated
  if (!authenticated && oidcConfigured) {
    return <Navigate to="/login" replace />
  }

  // In dev mode without OIDC, allow access even if not "authenticated" (dev token will be used)
  if (!authenticated && !oidcConfigured) {
    // Allow access - dev token will be used automatically
    return <>{children}</>
  }

  if (requiredScopes.length > 0) {
    const hasRequiredScope = requiredScopes.some((scope) => hasScope(scope) === true)

    if (!hasRequiredScope) {
      return (
        <div className="flex h-screen items-center justify-center">
          <div className="space-y-4 text-center">
            <h1 className="text-2xl font-bold text-red-600">Zugriff verweigert</h1>
            <p className="text-muted-foreground">
              Sie haben nicht die erforderlichen Berechtigungen für diese Seite.
            </p>
            <p className="text-sm text-muted-foreground">Erforderlich: {requiredScopes.join(' oder ')}</p>
            <p className="text-sm text-muted-foreground">Ihre Scopes: {(user?.scopes ?? []).join(', ') || 'keine'}</p>
          </div>
        </div>
      )
    }
  }

  if (requiredRoles.length > 0) {
    const hasRequiredRole = requiredRoles.some((role) => hasRole(role) === true)

    if (!hasRequiredRole) {
      return (
        <div className="flex h-screen items-center justify-center">
          <div className="space-y-4 text-center">
            <h1 className="text-2xl font-bold text-red-600">Zugriff verweigert</h1>
            <p className="text-muted-foreground">
              Sie haben nicht die erforderliche Rolle für diese Seite.
            </p>
            <p className="text-sm text-muted-foreground">Erforderlich: {requiredRoles.join(' oder ')}</p>
          </div>
        </div>
      )
    }
  }

  return <>{children}</>
}

