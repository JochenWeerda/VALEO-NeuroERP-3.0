import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

export default function SalesOrderNativePage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="sales/sales-order" entityId={id} testId="sales-sales-order" />
}
