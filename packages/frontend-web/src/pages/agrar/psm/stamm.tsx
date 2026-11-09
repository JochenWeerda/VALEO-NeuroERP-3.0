import { useParams } from '@/app/routing/typed-router'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/** PSM-Stamm: mit Kennung die Studio-Objektmaske `agrar/psm`, sonst die Mittelliste `agrar/psm-liste`. */
export default function PsmStammPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return id
    ? <UniversalNativeDetailPage screenId="agrar/psm" entityId={id} testId="agrar-psm-stamm" />
    : <NativeListPage screenId="agrar/psm-liste" testId="screen-agrar/psm-liste" />
}
