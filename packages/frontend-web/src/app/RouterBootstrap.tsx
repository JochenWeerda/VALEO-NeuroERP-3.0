import { Suspense, lazy } from 'react'
import RouterLayer from '@/app/RouterLayer'

const RuntimeServicesBootstrap = lazy(() =>
  import('@/app/RuntimeServicesBootstrap').then((module) => ({ default: module.default })),
)

export default function RouterBootstrap(): JSX.Element {
  return (
    <Suspense fallback={<RouterLayer />}>
      <RuntimeServicesBootstrap>
        <RouterLayer />
      </RuntimeServicesBootstrap>
    </Suspense>
  )
}
