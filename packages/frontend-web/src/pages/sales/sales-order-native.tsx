import { useParams, useSearchParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

export default function SalesOrderNativePage(): JSX.Element {
  const { id: routeId } = useParams<{ id?: string }>()
  const [searchParams] = useSearchParams()
  const id = routeId ?? searchParams.get('id') ?? undefined
  return <UniversalNativeDetailPage screenId="sales/sales-order" entityId={id} testId="sales-sales-order" />
}
