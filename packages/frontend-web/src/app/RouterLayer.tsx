import { Suspense, lazy } from 'react'

const AppRouterProvider = lazy(() =>
  import('@/app/AppRouterProvider').then((module) => ({ default: module.default })),
)

export default function RouterLayer(): JSX.Element {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <AppRouterProvider />
    </Suspense>
  )
}
