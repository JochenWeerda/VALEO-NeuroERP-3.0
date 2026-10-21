import { useMemo } from 'react'
import documentPermissions from './beleg-permissions.generated.json'
import actionPermissions from './action-permissions.generated.json'
import { useAuth } from '@/hooks/useAuth'
import type { User } from '@/lib/auth'
import type { ScreenDefinition } from '../schema'

/** UI projection of authenticated rights; server dependencies remain authoritative. */
export function getScreenPermissions(screen: ScreenDefinition | undefined, user: User | null): string[] {
  if (!screen || !user) return []
  const scopes = new Set(user.scopes ?? [])
  const roles = new Set(user.roles ?? [])
  const zeilen = [...(screen.tables ?? []), ...(screen.tabs ?? []).flatMap(tab => tab.tables ?? [])]
    .flatMap(table => table.rowActions ?? [])
  const declared = new Set([...(screen.actions ?? []), ...zeilen].flatMap(action => action.permission ? [action.permission] : []))
  if (screen.creation) declared.add(screen.creation.permission)
  return [...declared].filter(permission => {
    if (permission.startsWith('belege.')) {
      const screens = documentPermissions.screens as Record<string, Record<string, string[]>>
      return (screens[screen.id]?.[permission] ?? []).some(role => roles.has(role))
    }
    if (permission.startsWith('studio.entity.')) {
      const groups = (actionPermissions.generatedEntities as Record<string, string[][]>)[permission]
      return Boolean(groups && groups.length > 0 && groups.every(group => group.some(role => roles.has(role))))
    }
    if (permission.startsWith('platform:')) return scopes.has(permission)
    // Rollen der Kommandowege, aus deren Server-Abhaengigkeiten erzeugt: jede Gruppe braucht eine ihrer Rollen.
    const projected = (actionPermissions.screens as Record<string, Record<string, string[][]>>)[screen.id]?.[permission]
    if (projected) return projected.every(group => group.some(role => roles.has(role)))
    if (permission === 'identity:quota:read') return true // Server returns only own allocations.
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
