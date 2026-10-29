import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'
import { useParams } from '@/app/routing/typed-router'

/** Anlagenliste und echte Anlage ueber ihre jeweiligen ScreenDefinitions. */
export default function FibuAnlagenTsxPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (id && id !== 'neu') {
    return <UniversalNativeDetailPage screenId="fibu/anlage" entityId={id} testId="fibu-anlage" />
  }
  return (
    <NativeListPage screenId="fibu/anlagen-liste" testId="screen-fibu/anlagen-liste" />
  )
}
