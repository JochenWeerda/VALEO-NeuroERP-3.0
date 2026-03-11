import { Suspense, lazy, type ReactNode, createContext, useContext, useMemo, useRef, useState } from 'react'

type Ctx = { push: (_msg: string) => void }
const ToastCtx = createContext<Ctx>({ push: () => undefined })
export const useToast = (): Ctx => useContext(ToastCtx)

const ToastHost = lazy(() =>
  import('./ToastHost').then((module) => ({ default: module.default })),
)

export function ToastProvider({ children }: { children: ReactNode }): JSX.Element {
  const [open, setOpen] = useState(false)
  const [msg, setMsg] = useState('')
  const openTimer = useRef<number | null>(null)

  const contextValue = useMemo<Ctx>(() => ({
    push: (message): void => {
      setMsg(message)
      setOpen(false)
      if (openTimer.current !== null) {
        window.clearTimeout(openTimer.current)
      }
      openTimer.current = window.setTimeout((): void => setOpen(true), 0)
    },
  }), [])

  return (
    <ToastCtx.Provider value={contextValue}>
      {children}
      <Suspense fallback={null}>
        <ToastHost open={open} message={msg} onOpenChange={setOpen} />
      </Suspense>
    </ToastCtx.Provider>
  )
}
