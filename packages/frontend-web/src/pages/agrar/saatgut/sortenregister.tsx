import { useParams } from '@/app/routing/typed-router'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/** Sortenregister und Detail verwenden die jeweiligen Studio-Definitionen. */
export default function AgrarSaatgutSortenregisterTsxPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return id
    ? <UniversalNativeDetailPage screenId="agrar/saatgut/sorte" entityId={id} testId="agrar-sorte-stamm" />
    : <NativeListPage screenId="agrar/saatgut-sortenregister-liste" testId="screen-agrar/saatgut-sortenregister-liste" />
}
