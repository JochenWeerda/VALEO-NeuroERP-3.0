import { lazy, Suspense, useMemo } from 'react'
import { ArrowLeft } from 'lucide-react'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useLocation } from '@/app/routing/typed-router'

const ExpertRationWorkspace = lazy(() => import('@/pages/futtermittel/rationsoptimierung'))

/**
 * Rollenorientierter Einstieg in die Fuetterungsberatung.
 *
 * Das Portal startet bewusst mit einer nativen Meridian-ScreenDefinition. Die
 * rechenintensive Solver-Workbench wird erst fuer eine konkrete Planungs- oder
 * Auswertungsaufgabe geladen. So bleibt der taegliche Einstieg ruhig und mobil
 * bedienbar, waehrend Fachberater die volle Tabellendichte behalten.
 */
export default function PortalFeedAdvicePage(): JSX.Element {
  const { search } = useLocation()
  const taskMode = useMemo(() => {
    const params = new URLSearchParams(search)
    return params.get('mode') === 'expert' || Boolean(params.get('view'))
  }, [search])

  if (!taskMode) {
    return <UniversalNativeCockpitPage screenId="agrar/feed-advice" testId="feed-advice-cockpit" />
  }

  return (
    <div data-testid="feed-advice-task-workspace">
      <a
        href="/portal/rationsoptimierung"
        className="mb-3 inline-flex min-h-touch items-center gap-2 rounded-md px-3 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden="true" />
        Zur Fuetterungsuebersicht
      </a>
      <Suspense fallback={<p className="px-4 py-6 text-sm text-muted-foreground">Planungswerkzeug wird geladen…</p>}>
        <ExpertRationWorkspace />
      </Suspense>
    </div>
  )
}
