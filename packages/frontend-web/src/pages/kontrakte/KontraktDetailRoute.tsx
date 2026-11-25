import { lazy, Suspense } from 'react'
import { useParams } from '@/app/routing/typed-router'
import { ENABLE_UNIVERSAL_MASK_AGRAR_KONTRAKT } from '@/features/agrar-masks/kontrakt-mask-support'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

const FrmKontraktDetail = lazy(() => import('./FrmKontraktDetail'))

/**
 * Bestehende Kontrakte → native Maske agrar/kontrakte (Standard).
 * Neuanlage bleibt Legacy, bis Create-Paritaet geschlossen ist.
 */
export default function KontraktDetailRoute(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  const isExistingContract = Boolean(id && id !== 'neu')

  if (isExistingContract && ENABLE_UNIVERSAL_MASK_AGRAR_KONTRAKT) {
    return <UniversalNativeDetailPage screenId="agrar/kontrakte" entityId={id} testId="agrar-kontrakt" />
  }

  return (
    <Suspense fallback={null}>
      <FrmKontraktDetail />
    </Suspense>
  )
}
