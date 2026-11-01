import { lazy, Suspense } from 'react'
import type { SpecializedComponentProps } from '../types'
import { DomainContractBoundary } from '../intake/domain-runtime'

const RationEditor = lazy(() => import('./ration-editor-surface'))
const RationOptimization = lazy(() => import('./ration-optimization-surface'))
const PortalFeed = lazy(() => import('./portal-feed-surface'))
const MobileFeeding = lazy(() => import('./mobile-feeding-surface'))

const FEED_FIELDS: Record<string, string[]> = {
  'futtermittel/rationseditor': ['ration_id', 'group_id', 'version_no', 'status'],
  'futtermittel/rationsoptimierung': ['feed_id', 'cow_profile', 'optimization_result', 'review_status'],
  'portal/rationsoptimierung': ['view', 'ration_id', 'group_id', 'plan_status'],
  'futtermittel/fuetterungsdokumentation-mobil': ['plan_version_id', 'group_id', 'actual_kg', 'rest_kg', 'tm_pct'],
}

/** Only fixed, native feed contracts may mount domain readers or mutation controls. */
export function FeedWorkbench({ contract, plan }: SpecializedComponentProps): JSX.Element {
  if (!plan || plan.specialized?.type !== 'feed_workbench' || plan.specialized.id !== contract.id
    || (plan.screenId !== contract.id && !plan.screenId.startsWith('tenant/'))
    || !Object.prototype.hasOwnProperty.call(FEED_FIELDS, contract.id)) {
    return <p role="alert">Fütterungsvertrag ist nicht verfügbar.</p>
  }
  const fields = FEED_FIELDS[contract.id]
  const Surface = contract.id === 'futtermittel/rationseditor' ? RationEditor
    : contract.id === 'futtermittel/rationsoptimierung' ? RationOptimization
    : contract.id === 'portal/rationsoptimierung' ? PortalFeed : MobileFeeding
  return <DomainContractBoundary plan={plan} fields={fields}>
    <Suspense fallback={<p role="status">Fütterungsarbeitsplatz wird geladen…</p>}><Surface /></Suspense>
  </DomainContractBoundary>
}
