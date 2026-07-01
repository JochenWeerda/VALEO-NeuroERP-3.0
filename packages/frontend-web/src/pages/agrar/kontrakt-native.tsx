import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

export default function KontraktNativePage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="agrar/kontrakte" entityId={id} testId="agrar-kontrakt" />
}
