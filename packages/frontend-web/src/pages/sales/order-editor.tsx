/**
 * Auftrags-Erfassung (Verkauf) — Route-Switch Legacy vs. Universal Mask Generator Pilot
 */

import { lazy, Suspense } from 'react'
import { useParams, useSearchParams } from '@/app/routing/typed-router'
import { ENABLE_UNIVERSAL_MASK_SALES_ORDER } from '@/features/sales-masks/sales-order-mask-support'

const OrderEditorLegacyPage = lazy(() => import('./OrderEditorLegacyPage'))
const UniversalSalesOrderPilotPage = lazy(() => import('./UniversalSalesOrderPilotPage'))

export default function SalesOrderEditorPage(): JSX.Element {
  const { id: routeId } = useParams<{ id?: string }>()
  const [searchParams] = useSearchParams()
  const id = routeId ?? searchParams.get('id') ?? undefined
  const isNew = !id || id === 'neu'

  const PageComponent =
    !isNew && ENABLE_UNIVERSAL_MASK_SALES_ORDER
      ? UniversalSalesOrderPilotPage
      : OrderEditorLegacyPage

  return (
    <Suspense fallback={null}>
      <PageComponent />
    </Suspense>
  )
}
