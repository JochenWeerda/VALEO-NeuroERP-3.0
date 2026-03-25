import { Suspense, lazy } from 'react'
import { PageLoader } from '@/app/PageLoader'

const AppRouterProvider = lazy(() =>
  import('@/app/AppRouterProvider').then((module) => ({ default: module.default })),
)

export default function RouterLayer(): JSX.Element {
  return (
    <Suspense fallback={<PageLoader />}>
      <AppRouterProvider />
    </Suspense>
  )
}
