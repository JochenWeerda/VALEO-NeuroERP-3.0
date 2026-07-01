import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

export default function EinzelfuttermittelNativePage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="futtermittel/einzelfuttermittel" entityId={id} testId="futtermittel-einzelfuttermittel" />
}
