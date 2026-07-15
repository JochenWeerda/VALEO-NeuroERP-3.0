import { lazy, Suspense, useMemo } from 'react'
import { ArrowLeft } from 'lucide-react'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useLocation } from '@/app/routing/typed-router'
import { RationLifecycleWorklist } from '@/features/feed-advice/RationLifecycleWorklist'
import { RationLifecycleDetail } from '@/features/feed-advice/RationLifecycleDetail'
import { FeedControllingPage } from '@/features/feed-advice/FeedControllingPage'
import { FeedingBusinessWorklist } from '@/features/feed-advice/FeedingBusinessWorklist'
import { FeedingGroupDetail } from '@/features/feed-advice/FeedingGroupDetail'
import { FeedingReferenceData } from '@/features/feed-advice/FeedingReferenceData'

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
  const routeState = useMemo(() => {
    const params = new URLSearchParams(search)
    return {
      expert: params.get('mode') === 'expert',
      view: params.get('view'),
      rationId: params.get('ration_id'),
      groupId: params.get('group_id'),
    }
  }, [search])

  if (routeState.view === 'rations') {
    return <RationLifecycleWorklist />
  }

  if (routeState.view === 'ration' && routeState.rationId) {
    return <RationLifecycleDetail rationId={routeState.rationId} />
  }

  if (routeState.view === 'readiness') {
    return (
      <UniversalNativeCockpitPage
        screenId="agrar/feed-readiness"
        testId="feed-readiness-worklist"
        permissions={['futtermittel.rations.update']}
        onAction={(actionKey) => {
          if (actionKey === 'open_inventory') window.location.assign('/futtermittel/einzelfuttermittel-liste')
          if (actionKey === 'open_analyses') window.location.assign('/futtermittel/grundfutteranalysen')
        }}
      />
    )
  }

  if (routeState.view === 'controlling') {
    return <FeedControllingPage />
  }

  if (routeState.view === 'group' && routeState.groupId) {
    return <FeedingGroupDetail groupId={routeState.groupId} />
  }

  if (routeState.view === 'businesses') {
    return <FeedingBusinessWorklist />
  }

  if (routeState.view === 'reference-data') {
    return <FeedingReferenceData />
  }

  if (!routeState.expert) {
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
