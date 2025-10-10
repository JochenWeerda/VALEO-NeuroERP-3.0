import { type ReactNode, createContext, useContext, useState } from "react"
import * as Toast from "@radix-ui/react-toast"

type Ctx = { push: (msg: string) => void }
const ToastCtx = createContext<Ctx>({ push: () => undefined })
export const useToast = (): Ctx => useContext(ToastCtx)

export function ToastProvider({ children }: { children: ReactNode }): JSX.Element {
  const [open, setOpen] = useState(false)
  const [msg, setMsg] = useState("")
  return (
    <ToastCtx.Provider value={{ push: (m): void => { setMsg(m); setOpen(false); setTimeout(():void => setOpen(true),0) } }}>
      <Toast.Provider swipeDirection="right">
        {children}
        <Toast.Root open={open} onOpenChange={setOpen} className="rounded-xl border bg-background p-3 shadow">
          <Toast.Title className="font-medium">Notification</Toast.Title>
          <Toast.Description className="opacity-80">{msg}</Toast.Description>
        </Toast.Root>
        <Toast.Viewport className="fixed bottom-4 right-4 w-96" />
      </Toast.Provider>
    </ToastCtx.Provider>
  )
}