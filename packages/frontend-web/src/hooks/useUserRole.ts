import { useMemo } from 'react'
import type { UserRole } from '@/app/navigation/types'

/**
 * Returns the current user's roles derived from the OIDC token claims.
 * Falls back to an empty array (= all nav items visible) when auth is not
 * yet available or in dev mode without role claims.
 */
export function useUserRole(): UserRole[] {
  return useMemo<UserRole[]>(() => {
    try {
      // Prefer roles from OIDC id_token stored in sessionStorage by oidc-client-ts
      const raw = sessionStorage.getItem('oidc.user') ?? localStorage.getItem('oidc.user')
      if (!raw) return []
      const parsed = JSON.parse(raw) as { profile?: { roles?: UserRole[]; realm_access?: { roles: string[] } } }
      const directRoles = parsed.profile?.roles
      if (directRoles && directRoles.length > 0) return directRoles
      const realmRoles = parsed.profile?.realm_access?.roles
      if (realmRoles) return realmRoles as UserRole[]
      return []
    } catch {
      return []
    }
  }, [])
}
