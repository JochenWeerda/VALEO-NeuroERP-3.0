import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/** Neuanlage ueber die Anlagemaske, sonst die Objektmaske desselben ID-Raums (/futter/...futtermittel/{id}). */
export default function EinzelfutterStammPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (!id || id === 'new' || id === 'neu') {
    return <UniversalNativeCreatePage screenId="futtermittel/einzelfuttermittel/stamm/new" testId="screen-futter/einzel/stamm/neu" />
  }
  return <UniversalNativeDetailPage screenId="futter/einzel" entityId={id} testId="futter-einzel-stamm" />
}
