/**
 * Auftrags-Erfassung (Verkauf) — Route-Switch Legacy vs. native Maske (UniversalMaskRuntime)
 */

import { lazy, Suspense } from 'react'
import { useParams, useSearchParams } from '@/app/routing/typed-router'
import { ENABLE_UNIVERSAL_MASK_SALES_ORDER } from '@/features/sales-masks/sales-order-mask-support'

const OrderEditorLegacyPage = lazy(() => import('./OrderEditorLegacyPage'))
const SalesOrderNativePage = lazy(() => import('./sales-order-native'))

export default function SalesOrderEditorPage(): JSX.Element {
  const { id: routeId } = useParams<{ id?: string }>()
  const [searchParams] = useSearchParams()
  const id = routeId ?? searchParams.get('id') ?? undefined
  const isNew = !id || id === 'neu'

  const PageComponent =
    !isNew && ENABLE_UNIVERSAL_MASK_SALES_ORDER
      ? SalesOrderNativePage
      : OrderEditorLegacyPage

  return (
    <Suspense fallback={null}>
      <PageComponent />
    </Suspense>
  )
}
