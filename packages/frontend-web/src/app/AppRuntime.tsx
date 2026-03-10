import { Suspense, lazy, useEffect, useState } from 'react'
import i18n from 'i18next'
import { initI18n } from '@/i18n/config'

const DataBootstrap = lazy(() =>
  import('@/app/DataBootstrap').then((module) => ({ default: module.default })),
)

const RouterBootstrap = lazy(() =>
  import('@/app/RouterBootstrap').then((module) => ({ default: module.default })),
)

export default function AppRuntime(): JSX.Element {
  const [i18nReady, setI18nReady] = useState<boolean>(i18n.isInitialized)

  useEffect(() => {
    void import('@/app/route-prefetch').then((module) => {
      module.prefetchPriorityRoutes()
    })
  }, [])

  useEffect(() => {
    let active = true

    void initI18n().then(() => {
      if (active) {
        setI18nReady(true)
      }
    })

    return () => {
      active = false
    }
  }, [])

  if (!i18nReady) {
    return <div className="min-h-screen bg-background" />
  }

  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <DataBootstrap>
        <RouterBootstrap />
      </DataBootstrap>
    </Suspense>
  )
}
