import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/** Neuanlage ueber die Anlagemaske, sonst die Objektmaske desselben ID-Raums (/futter/...futtermittel/{id}). */
export default function MischfutterStammPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (!id || id === 'new' || id === 'neu') {
    return <UniversalNativeCreatePage screenId="futtermittel/mischfuttermittel/stamm/new" testId="screen-futter/misch/stamm/neu" />
  }
  return <UniversalNativeDetailPage screenId="futter/misch" entityId={id} testId="futter-misch-stamm" />
}
