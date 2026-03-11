import { lazy, Suspense } from 'react'
import { ENABLE_LEAD_MASK_BUILDER_FORM } from '@/features/crm-masks/lead-mask-support'

const LeadMaskDetailPage = lazy(() => import('./lead-detail/LeadMaskDetailPage'))
const LegacyLeadDetailPage = lazy(() => import('./lead-detail/LegacyLeadDetailPage'))

export default function LeadDetailPage(): JSX.Element {
  const PageComponent = ENABLE_LEAD_MASK_BUILDER_FORM
    ? LeadMaskDetailPage
    : LegacyLeadDetailPage

  return (
    <Suspense fallback={null}>
      <PageComponent />
    </Suspense>
  )
}
