import { useParams, useSearchParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

export default function KontraktNativePage(): JSX.Element {
  const { id: routeId } = useParams<{ id?: string }>()
  const [searchParams] = useSearchParams()
  const id = routeId ?? searchParams.get('id') ?? undefined
  return <UniversalNativeDetailPage screenId="agrar/kontrakte" entityId={id} testId="agrar-kontrakt" />
}
