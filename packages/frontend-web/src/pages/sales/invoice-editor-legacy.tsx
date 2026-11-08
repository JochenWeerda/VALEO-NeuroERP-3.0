import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

export default function Page(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return (
    <UniversalNativeDetailPage screenId="sales/invoice" entityId={id} testId="sales-invoice" />
  )
}
