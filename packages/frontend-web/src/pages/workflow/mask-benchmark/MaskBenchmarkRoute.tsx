/**
 * E2E/Benchmark-Route: Legacy-Maske oder native Maske (kein Feature-Flag).
 * Pfad: /dev/mask-benchmark/:domain/:variant/:id
 */
import { lazy, Suspense, type ComponentType } from 'react'
import { useParams } from '@/app/routing/typed-router'

const SALES_LEGACY = lazy(() => import('@/pages/sales/OrderEditorLegacyPage'))
const SALES_NATIVE = lazy(() => import('@/pages/sales/sales-order-native'))
const KONTRAKT_LEGACY = lazy(() => import('@/pages/kontrakte/FrmKontraktDetail'))
const KONTRAKT_NATIVE = lazy(() => import('@/pages/agrar/kontrakt-native'))

const COMPONENTS: Record<string, Record<string, ComponentType>> = {
  'sales-order': {
    legacy: SALES_LEGACY,
    pilot: SALES_NATIVE,
  },
  kontrakt: {
    legacy: KONTRAKT_LEGACY,
    pilot: KONTRAKT_NATIVE,
  },
}

export default function MaskBenchmarkRoute(): JSX.Element {
  const { domain, variant, id } = useParams<{ domain?: string; variant?: string; id?: string }>()
  const PageComponent = domain && variant ? COMPONENTS[domain]?.[variant] : undefined

  if (!PageComponent || !domain || !variant || !id) {
    return (
      <div className="p-6 text-sm text-muted-foreground">
        Benchmark-Route ungueltig. Beispiel: /dev/mask-benchmark/sales-order/pilot/bench-order
      </div>
    )
  }

  return (
    <div data-mask-benchmark-domain={domain} data-mask-benchmark-variant={variant} data-mask-benchmark-id={id}>
      <Suspense fallback={<div className="p-4 text-sm text-muted-foreground">Benchmark laedt...</div>}>
        <PageComponent />
      </Suspense>
    </div>
  )
}
