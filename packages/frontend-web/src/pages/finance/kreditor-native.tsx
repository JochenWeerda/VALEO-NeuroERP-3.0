import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder'

export default function KreditorNativePage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="finance/kreditor" entityId={id} testId="finance-kreditor" />
}
