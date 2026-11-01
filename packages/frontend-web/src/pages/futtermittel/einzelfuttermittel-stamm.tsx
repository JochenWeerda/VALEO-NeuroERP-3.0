import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

export default function EinzelfuttermittelStammPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (!id || id === 'new' || id === 'neu') {
    return <UniversalNativeCreatePage screenId="futtermittel/einzelfuttermittel/stamm/new" testId="feed-einzel-create" />
  }
  return <UniversalNativeDetailPage screenId="futtermittel/einzelfuttermittel" entityId={id} testId="futtermittel-einzelfuttermittel-stamm" />
}
