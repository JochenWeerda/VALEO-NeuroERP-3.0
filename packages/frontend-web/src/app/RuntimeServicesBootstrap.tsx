import { Suspense, lazy, type ReactNode } from 'react'

const SSEBootstrap = lazy(() =>
  import('@/app/SSEBootstrap').then((module) => ({ default: module.default })),
)
const ToastBootstrap = lazy(() =>
  import('@/app/ToastBootstrap').then((module) => ({ default: module.default })),
)
const ShortcutBootstrap = lazy(() =>
  import('@/app/ShortcutBootstrap').then((module) => ({ default: module.default })),
)

export default function RuntimeServicesBootstrap({ children }: { children: ReactNode }): JSX.Element {
  return (
    <Suspense fallback={<>{children}</>}>
      <SSEBootstrap>
        <ToastBootstrap>
          {children}
          <ShortcutBootstrap />
        </ToastBootstrap>
      </SSEBootstrap>
    </Suspense>
  )
}
