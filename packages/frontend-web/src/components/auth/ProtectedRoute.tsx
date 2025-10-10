/**
 * ProtectedRoute Component
 * Route-Protection mit OIDC-Authentication
 */

import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children: ReactNode
  requiredScopes?: string[]
  requiredRoles?: string[]
}

export function ProtectedRoute({ 
  children, 
  requiredScopes = [], 
  requiredRoles = [] 
}: ProtectedRouteProps) {
  const { isAuthenticated, loading, hasScope, hasRole, user } = useAuth()

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  // Not authenticated → Redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Check required scopes
  if (requiredScopes.length > 0) {
    const hasRequiredScope = requiredScopes.some((scope) => hasScope(scope))
    
    if (!hasRequiredScope) {
      return (
        <div className="flex items-center justify-center h-screen">
          <div className="text-center space-y-4">
            <h1 className="text-2xl font-bold text-red-600">Zugriff verweigert</h1>
            <p className="text-muted-foreground">
              Sie haben nicht die erforderlichen Berechtigungen für diese Seite.
            </p>
            <p className="text-sm text-muted-foreground">
              Erforderlich: {requiredScopes.join(' oder ')}
            </p>
            <p className="text-sm text-muted-foreground">
              Ihre Scopes: {user?.scopes?.join(', ') || 'keine'}
            </p>
          </div>
        </div>
      )
    }
  }

  // Check required roles
  if (requiredRoles.length > 0) {
    const hasRequiredRole = requiredRoles.some((role) => hasRole(role))
    
    if (!hasRequiredRole) {
      return (
        <div className="flex items-center justify-center h-screen">
          <div className="text-center space-y-4">
            <h1 className="text-2xl font-bold text-red-600">Zugriff verweigert</h1>
            <p className="text-muted-foreground">
              Sie haben nicht die erforderliche Rolle für diese Seite.
            </p>
            <p className="text-sm text-muted-foreground">
              Erforderlich: {requiredRoles.join(' oder ')}
            </p>
          </div>
        </div>
      )
    }
  }

  // Authenticated & authorized → Render children
  return <>{children}</>
}

