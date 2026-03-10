import { Suspense, lazy, type ComponentType } from 'react'
import { ErrorBoundary } from '@/shared/errors/ErrorBoundary'
import { ErrorState } from '@/components/ErrorState'
import { PageLoader } from '@/app/PageLoader'
import type { PageModuleFactory } from '@/app/route-builders/types'

const lazyComponentCache = new WeakMap<PageModuleFactory, ComponentType<unknown>>()

export function createRouteElement(loader: PageModuleFactory): JSX.Element {
  let Component = lazyComponentCache.get(loader)
  if (!Component) {
    Component = lazy(loader)
    lazyComponentCache.set(loader, Component)
  }

  return (
    <ErrorBoundary
      fallback={
        <div className="flex h-96 items-center justify-center p-8">
          <div className="w-full max-w-2xl">
            <ErrorState
              error={null}
              title="Fehler beim Laden der Seite"
              message="Die Seite konnte nicht gerendert werden."
              recoveryHint="Laden Sie die Seite neu oder wechseln Sie zur Startseite."
              onReload={() => window.location.reload()}
              onHome={() => {
                window.location.href = '/'
              }}
            />
          </div>
        </div>
      }
    >
      <Suspense fallback={<PageLoader />}>
        <Component />
      </Suspense>
    </ErrorBoundary>
  )
}
