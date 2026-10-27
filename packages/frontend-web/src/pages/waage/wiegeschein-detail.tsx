import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'
import { useParams } from '@/app/routing/typed-router'

export default function Page(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (id) {
    return <UniversalNativeDetailPage screenId="waage/wiegeschein" entityId={id} testId="waage-wiegeschein" />
  }
  return (
    <NativeListPage screenId="waage/wiegeschein-detail" testId="screen-waage/wiegeschein-detail" />
  )
}
