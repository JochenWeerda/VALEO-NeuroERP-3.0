import { Suspense, lazy } from 'react'

const RuntimeLayers = lazy(() =>
  import('@/app/RuntimeLayers').then((module) => ({ default: module.default })),
)

export default function ShortcutBootstrap(): JSX.Element {
  return (
    <Suspense fallback={null}>
      <RuntimeLayers />
    </Suspense>
  )
}
