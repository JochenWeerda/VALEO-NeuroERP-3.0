import { lazy, Suspense } from 'react'
import { Navigate, useLocation } from '@/app/routing/typed-router'
import { ENABLE_CUSTOMER_MASK_BUILDER_FORM } from '@/features/crm-masks/customer-mask-support'

const KundeNeuMaskBuilderPage = lazy(() => import('./kunde-neu/KundeNeuMaskBuilderPage'))

export default function KundeNeuPage(): JSX.Element {
  const location = useLocation()
  if (!ENABLE_CUSTOMER_MASK_BUILDER_FORM) {
    return <Navigate to={`/verkauf/kunde/neu${location.search}`} replace />
  }
  return (
    <Suspense fallback={null}>
      <KundeNeuMaskBuilderPage />
    </Suspense>
  )
}
