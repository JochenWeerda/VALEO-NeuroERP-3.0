import { useMemo } from 'react'
import { useAuth } from '@/hooks/useAuth'
import type { User } from '@/lib/auth'
import type { ScreenDefinition } from '../schema'

/** UI projection of authenticated rights; server dependencies remain authoritative. */
export function getScreenPermissions(screen: ScreenDefinition | undefined, user: User | null): string[] {
  if (!screen || !user) return []
  const scopes = new Set(user.scopes ?? [])
  const roles = new Set(user.roles ?? [])
  const declared = new Set((screen.actions ?? []).flatMap(action => action.permission ? [action.permission] : []))
  if (screen.creation) declared.add(screen.creation.permission)
  return [...declared].filter(permission => {
    if (scopes.has('admin:all') || roles.has('admin')) return true
    if (scopes.has(permission)) return true
    if (permission === 'logistics:read' && scopes.has('logistics:write')) return true
    // Match the canonical lead API's existing role contract, not schema-granted rights.
    if (permission.startsWith('crm.lead.')) {
      return roles.has('CRM_BEARBEITEN') || roles.has('CRM_ADMIN') || roles.has('manager')
    }
    return false
  })
}

export function useScreenPermissions(screen: ScreenDefinition | undefined, requested?: string[]): string[] {
  const { user } = useAuth()
  return useMemo(() => {
    const granted = getScreenPermissions(screen, user)
    return requested ? granted.filter(permission => requested.includes(permission)) : granted
  }, [screen, user, requested])
}
