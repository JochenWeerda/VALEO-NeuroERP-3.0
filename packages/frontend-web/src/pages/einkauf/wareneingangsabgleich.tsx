import { useSearchParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'

export default function Page(): JSX.Element {
  const [search] = useSearchParams()
  const order = search.get('bestellung')
  if (order) {
    return <UniversalNativeDetailPage screenId="einkauf/wareneingangsabgleich-detail" entityId={order} testId="wareneingangsabgleich-detail" />
  }

  return (
    <NativeListPage screenId="einkauf/wareneingangsabgleich" testId="screen-einkauf/wareneingangsabgleich" />
  )
}
