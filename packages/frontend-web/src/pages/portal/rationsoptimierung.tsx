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
import { FeedingSupplyPage } from '@/features/feed-advice/FeedingSupplyPage'

const ExpertRationWorkspace = lazy(() => import('@/pages/futtermittel/rationsoptimierung'))

/**
 * Einstieg in die Fuetterungsberatung.
 *
 * Das Portal startet direkt in der Rationswerkbank (Spielwiese + Live-Cockpit),
 * weil das der eigentliche Arbeitsplatz der Fachberatung ist. Die rollenorientierte
 * Meridian-Uebersicht bleibt ueber `?mode=cockpit` erreichbar, die aufgabenbezogenen
 * Teilmasken weiterhin ueber `?view=...`.
 */
export default function PortalFeedAdvicePage(): JSX.Element {
  const { search } = useLocation()
  const routeState = useMemo(() => {
    const params = new URLSearchParams(search)
    return {
      cockpit: params.get('mode') === 'cockpit',
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
    return <FeedingSupplyPage />
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

  if (routeState.cockpit) {
    return <UniversalNativeCockpitPage screenId="agrar/feed-advice" testId="feed-advice-cockpit" />
  }

  return (
    <div data-testid="feed-advice-task-workspace">
      <a
        href="/portal/rationsoptimierung?mode=cockpit"
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
