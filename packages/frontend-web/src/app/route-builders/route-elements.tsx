import { Suspense, lazy, type ComponentType } from 'react'
import { ErrorBoundary } from '@/shared/errors/ErrorBoundary'
import { ErrorState } from '@/components/ErrorState'
import { PageLoader } from '@/app/PageLoader'
import type { PageModuleFactory } from '@/app/route-builders/types'

// Cache both the lazy component AND the stable JSX element by factory reference.
// A new lazy() call on each render would cause React to treat the component as a
// different type, resetting the Suspense boundary and showing the spinner on every
// re-render. Caching the JSX element ensures the exact same object reference is
// returned across renders, giving React a stable reconciliation target.
const lazyComponentCache = new WeakMap<PageModuleFactory, ComponentType<unknown>>()
const lazyElementCache = new WeakMap<PageModuleFactory, JSX.Element>()

export function createRouteElement(loader: PageModuleFactory): JSX.Element {
  const cached = lazyElementCache.get(loader)
  if (cached) {
    return cached
  }

  let Component = lazyComponentCache.get(loader)
  if (!Component) {
    Component = lazy(loader)
    lazyComponentCache.set(loader, Component)
  }

  const element = (
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

  lazyElementCache.set(loader, element)
  return element
}
