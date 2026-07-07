import { useEffect, useRef } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useFeature } from '@/hooks/useFeature'
import { useUserRole } from '@/hooks/useUserRole'
import { fetchWorkspaceStartpage } from '@/lib/api/mask-registry'

const REDIRECT_MARKER = 'uix061-workspace-redirected'

/**
 * Rollenbasierter Login-Redirect (UIX-061): leitet beim ersten Aufruf der
 * Startseite auf den cockpit-Workspace der Nutzerrolle. Flag-geschuetzt
 * (roleWorkspaces, default off) und einmalig je Session — ohne Zuordnung oder
 * bei deaktiviertem Flag bleibt die bisherige Startseite bestehen.
 */
export function useWorkspaceRedirect(): void {
  const enabled = useFeature('roleWorkspaces')
  const roles = useUserRole()
  const navigate = useNavigate()
  const attempted = useRef(false)

  useEffect(() => {
    if (!enabled || attempted.current) return
    if (sessionStorage.getItem(REDIRECT_MARKER)) return
    if (roles.length === 0) return
    attempted.current = true

    let cancelled = false
    void (async () => {
      for (const role of roles) {
        try {
          const startpage = await fetchWorkspaceStartpage(String(role))
          if (cancelled) return
          if (startpage.route) {
            sessionStorage.setItem(REDIRECT_MARKER, '1')
            navigate(startpage.route)
            return
          }
        } catch {
          // Redirect ist Komfort — Fehler duerfen die Startseite nicht blockieren.
          return
        }
      }
      // Keine Rolle gemappt → Marker setzen, damit wir nicht bei jedem Render erneut fragen.
      sessionStorage.setItem(REDIRECT_MARKER, '1')
    })()

    return () => {
      cancelled = true
    }
  }, [enabled, roles, navigate])
}
