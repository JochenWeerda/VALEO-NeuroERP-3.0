/* @refresh reload */
import { StrictMode, Suspense, lazy } from 'react'
import ReactDOM from 'react-dom/client'
import { PageLoader } from '@/app/PageLoader'
import './index.css'

const AppRuntime = lazy(() =>
  import('@/app/AppRuntime').then((module) => ({ default: module.default })),
)

const rootElement = document.getElementById('root')

if (rootElement instanceof HTMLElement) {
  const existingRoot = (rootElement as any).__reactRoot ?? null
  const root = existingRoot ?? ReactDOM.createRoot(rootElement)
  ;(rootElement as any).__reactRoot = root

  root.render(
    <StrictMode>
      <Suspense fallback={<PageLoader />}>
        <AppRuntime />
      </Suspense>
    </StrictMode>,
  )

  if ('serviceWorker' in navigator && import.meta.env.PROD) {
    const swEnabled = (import.meta.env as Record<string, string | undefined>).VITE_ENABLE_SERVICE_WORKER === 'true'
    if (swEnabled) {
      navigator.serviceWorker.register('/sw.js').catch(() => {
        // SW registration failed -- non-critical, app works without it
      })
    }
  }
}
