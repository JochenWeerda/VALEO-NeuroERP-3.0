import { lazy, Suspense } from 'react'
import { useParams } from '@/app/routing/typed-router'
import { ENABLE_UNIVERSAL_MASK_AGRAR_KONTRAKT } from '@/features/agrar-masks/kontrakt-mask-support'

const FrmKontraktDetail = lazy(() => import('./FrmKontraktDetail'))
const UniversalKontraktPilotPage = lazy(() => import('./UniversalKontraktPilotPage'))

export default function KontraktDetailRoute(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  const isExistingContract = Boolean(id && id !== 'neu')

  const PageComponent =
    isExistingContract && ENABLE_UNIVERSAL_MASK_AGRAR_KONTRAKT
      ? UniversalKontraktPilotPage
      : FrmKontraktDetail

  return (
    <Suspense fallback={null}>
      <PageComponent />
    </Suspense>
  )
}
