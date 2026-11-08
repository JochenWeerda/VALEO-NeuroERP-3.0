import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

export default function MischfuttermittelStammPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (!id || id === 'new' || id === 'neu') {
    return <UniversalNativeCreatePage screenId="futtermittel/mischfuttermittel/stamm/new" testId="feed-misch-create" />
  }
  return <UniversalNativeDetailPage screenId="futtermittel/mischfuttermittel" entityId={id} testId="futtermittel-mischfuttermittel-stamm" />
}
