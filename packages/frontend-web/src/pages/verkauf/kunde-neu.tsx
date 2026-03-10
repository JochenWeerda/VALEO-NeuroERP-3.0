import { lazy, Suspense } from 'react'
import { ENABLE_CUSTOMER_MASK_BUILDER_FORM } from '@/features/crm-masks/customer-mask-support'

const KundeNeuMaskBuilderPage = lazy(() => import('./kunde-neu/KundeNeuMaskBuilderPage'))
const LegacyKundeNeuPage = lazy(() => import('./kunde-neu/LegacyKundeNeuPage'))

export default function KundeNeuPage(): JSX.Element {
  const PageComponent = ENABLE_CUSTOMER_MASK_BUILDER_FORM
    ? KundeNeuMaskBuilderPage
    : LegacyKundeNeuPage

  return (
    <Suspense fallback={null}>
      <PageComponent />
    </Suspense>
  )
}
