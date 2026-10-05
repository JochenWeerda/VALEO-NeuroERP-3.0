import { lazy, Suspense } from 'react'
import { useParams, useSearchParams } from '@/app/routing/typed-router'
import { ENABLE_LEAD_MASK_BUILDER_FORM } from '@/features/crm-masks/lead-mask-support'
import PartyNativePage from '@/pages/crm/party-native'

const LeadMaskDetailPage = lazy(() => import('./lead-detail/LeadMaskDetailPage'))
const LegacyLeadDetailPage = lazy(() => import('./lead-detail/LegacyLeadDetailPage'))

export default function LeadDetailPage(): JSX.Element {
  const { id: routeId } = useParams<{ id?: string }>()
  const [searchParams] = useSearchParams()
  const entityId = routeId ?? searchParams.get('id') ?? undefined

  if (entityId) {
    return <PartyNativePage kind="lead" entityId={entityId} />
  }

  const PageComponent = ENABLE_LEAD_MASK_BUILDER_FORM
    ? LeadMaskDetailPage
    : LegacyLeadDetailPage

  return (
    <Suspense fallback={null}>
      <PageComponent />
    </Suspense>
  )
}
